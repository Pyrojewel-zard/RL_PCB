"""
多线程探索器实现，解决explore_for_expert_targets单核CPU问题
"""
import threading
import queue
import logging
import os
import time
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

class ThreadSafeExplorer:
    """
    线程安全的多线程探索器，用于并行化explore_for_expert_targets
    """
    
    def __init__(self, sac_model, num_workers=4, verbose=0):
        """
        初始化多线程探索器
        
        Args:
            sac_model: SAC模型实例
            num_workers: 工作线程数量
            verbose: 日志详细程度
        """
        self.sac_model = sac_model
        self.num_workers = num_workers
        self.verbose = verbose
        
        # 线程安全锁
        self.env_lock = threading.Lock()  # 环境访问锁
        self.pcb_save_lock = threading.Lock()  # PCB保存锁
        self.progress_lock = threading.Lock()  # 进度更新锁
        
        # 全局计数器
        self.global_step_count = 0
        self.completed_workers = 0
        
        # 日志系统
        if verbose > 0:
            logging.basicConfig(level=logging.INFO, 
                              format='%(asctime)s - %(levelname)s - %(message)s')
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = None
    
    def _log_info(self, message):
        """线程安全的日志输出"""
        if self.logger:
            self.logger.info(message)
        elif self.verbose > 0:
            print(f"[探索器] {message}")
    
    def _save_pcb_thread_safe(self, output_dir, step_id, worker_id, is_reset=False):
        """
        线程安全的PCB文件保存
        
        Args:
            output_dir: 输出目录
            step_id: 步数ID
            worker_id: 工作线程ID
            is_reset: 是否为重置步数
        """
        with self.pcb_save_lock:
            try:
                pcb_output_dir = os.path.join(output_dir, "explore_pcb")
                os.makedirs(pcb_output_dir, exist_ok=True)
                
                if is_reset:
                    filename = f"explore_reset_{step_id}_worker_{worker_id}.pcb"
                else:
                    filename = f"explore_step_{step_id}_worker_{worker_id}.pcb"
                
                self.sac_model.train_env.write_current_pcb_file(
                    path=pcb_output_dir,
                    filename=filename
                )
                
                self._log_info(f"Worker-{worker_id}: 保存PCB文件 {filename}")
                
            except Exception as e:
                self._log_info(f"Worker-{worker_id}: PCB保存失败 - {e}")
    
    def _explore_worker(self, worker_id, steps_per_worker, output_dir, save_pcb_every_n_steps):
        """
        单个工作线程的探索函数
        
        Args:
            worker_id: 工作线程ID
            steps_per_worker: 该线程负责的步数
            output_dir: 输出目录
            save_pcb_every_n_steps: PCB保存频率
        """
        local_step_count = 0
        worker_episode_count = 0
        
        self._log_info(f"Worker-{worker_id}: 开始执行 {steps_per_worker} 步探索")
        
        try:
            while local_step_count < steps_per_worker:
                # 线程安全的环境操作
                with self.env_lock:
                    # 获取当前状态
                    state = self.sac_model.train_env.get_state()
                    
                    # 选择动作
                    action = self.sac_model.select_action(np.array(state), evaluate=False)
                    
                    # 执行动作
                    next_state, reward, done, info = self.sac_model.train_env.step(action)
                    
                    # 更新全局步数计数器
                    with self.progress_lock:
                        self.global_step_count += 1
                        current_global_step = self.global_step_count
                
                local_step_count += 1
                
                # 检查是否需要保存PCB
                if output_dir and (local_step_count % save_pcb_every_n_steps == 0):
                    self._save_pcb_thread_safe(output_dir, current_global_step, worker_id)
                
                # 处理episode结束
                if done:
                    worker_episode_count += 1
                    
                    # 保存重置时的PCB（如果需要）
                    if output_dir:
                        self._save_pcb_thread_safe(output_dir, current_global_step, 
                                                 worker_id, is_reset=True)
                    
                    # 线程安全的环境重置
                    with self.env_lock:
                        self.sac_model.train_env.reset()
                
                # 定期报告进度
                if local_step_count % (save_pcb_every_n_steps * 5) == 0:
                    self._log_info(f"Worker-{worker_id}: 完成 {local_step_count}/{steps_per_worker} 步, "
                                 f"Episode: {worker_episode_count}")
        
        except Exception as e:
            self._log_info(f"Worker-{worker_id}: 执行异常 - {e}")
            raise
        
        finally:
            # 线程完成标记
            with self.progress_lock:
                self.completed_workers += 1
            
            self._log_info(f"Worker-{worker_id}: 完成所有任务 ({local_step_count} 步, "
                         f"{worker_episode_count} episodes)")
    
    def explore(self, total_steps, output_dir=None, save_pcb_every_n_steps=1000):
        """
        多线程探索主函数
        
        Args:
            total_steps: 总探索步数
            output_dir: PCB文件输出目录
            save_pcb_every_n_steps: PCB保存频率
        """
        start_time = time.time()
        
        # 重置计数器
        self.global_step_count = 0
        self.completed_workers = 0
        
        # 计算每个线程的任务分配
        steps_per_worker = total_steps // self.num_workers
        remaining_steps = total_steps % self.num_workers
        
        self._log_info(f"开始多线程探索: {total_steps} 步, {self.num_workers} 个工作线程")
        self._log_info(f"每个线程基础任务: {steps_per_worker} 步")
        
        # 创建输出目录
        if output_dir:
            pcb_output_dir = os.path.join(output_dir, "explore_pcb")
            os.makedirs(pcb_output_dir, exist_ok=True)
        
        # 使用线程池执行并行探索
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            futures = []
            
            for worker_id in range(self.num_workers):
                # 前几个线程处理剩余步数
                worker_steps = steps_per_worker
                if worker_id < remaining_steps:
                    worker_steps += 1
                
                future = executor.submit(
                    self._explore_worker,
                    worker_id,
                    worker_steps,
                    output_dir,
                    save_pcb_every_n_steps
                )
                futures.append(future)
                
                self._log_info(f"启动Worker-{worker_id}: {worker_steps} 步")
            
            # 等待所有线程完成并处理异常
            completed_count = 0
            for future in as_completed(futures):
                try:
                    future.result()  # 获取结果，如果有异常会抛出
                    completed_count += 1
                    self._log_info(f"完成进度: {completed_count}/{self.num_workers} 个线程")
                except Exception as e:
                    self._log_info(f"线程执行失败: {e}")
                    raise
        
        end_time = time.time()
        total_time = end_time - start_time
        
        self._log_info(f"多线程探索完成!")
        self._log_info(f"总步数: {self.global_step_count}, 总时间: {total_time:.2f}秒")
        self._log_info(f"平均速度: {self.global_step_count/total_time:.2f} 步/秒")
        
        return {
            'total_steps': self.global_step_count,
            'total_time': total_time,
            'steps_per_second': self.global_step_count / total_time,
            'num_workers': self.num_workers
        }


def add_multithread_support_to_sac(sac_class):
    """
    为SAC类添加多线程支持的装饰器
    
    Args:
        sac_class: SAC类
    
    Returns:
        增强后的SAC类
    """
    
    # 保存原始的__init__方法
    original_init = sac_class.__init__
    
    def enhanced_init(self, *args, **kwargs):
        # 调用原始初始化
        original_init(self, *args, **kwargs)
        
        # 添加多线程探索器
        num_workers = kwargs.get('num_workers', 4)
        verbose = kwargs.get('verbose', 0)
        self.explorer = ThreadSafeExplorer(self, num_workers=num_workers, verbose=verbose)
        self.env_lock = threading.Lock()
    
    # 替换__init__方法
    sac_class.__init__ = enhanced_init
    
    # 添加增强的explore_for_expert_targets方法
    def enhanced_explore_for_expert_targets(self,
                                          reward_target_exploration_steps=25_000,
                                          output_dir=None,
                                          save_pcb_every_n_steps=1000,
                                          num_workers=None):
        """
        多线程版本的explore_for_expert_targets
        
        Args:
            reward_target_exploration_steps: 探索步数
            output_dir: PCB文件输出目录
            save_pcb_every_n_steps: PCB保存频率
            num_workers: 工作线程数量（None使用默认值）
        """
        # 更新线程数量（如果指定）
        if num_workers is not None:
            self.explorer.num_workers = num_workers
        
        print(f"🚀 启动多线程探索 ({self.explorer.num_workers} 线程)")
        print(f"📊 目标步数: {reward_target_exploration_steps:,}")
        
        # 使用多线程探索器执行探索
        stats = self.explorer.explore(
            total_steps=reward_target_exploration_steps,
            output_dir=output_dir,
            save_pcb_every_n_steps=save_pcb_every_n_steps
        )
        
        print(f"✅ 多线程探索完成!")
        print(f"   实际步数: {stats['total_steps']:,}")
        print(f"   总耗时: {stats['total_time']:.2f}秒")
        print(f"   平均速度: {stats['steps_per_second']:.2f} 步/秒")
        print(f"   线程数: {stats['num_workers']}")
        
        return stats
    
    # 替换原有方法
    sac_class.explore_for_expert_targets = enhanced_explore_for_expert_targets
    
    return sac_class
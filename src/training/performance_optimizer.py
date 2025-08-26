"""
性能优化集成示例
展示如何同时应用多线程和GPU优化来提升RL_PCB训练性能
"""

import os
import sys
import torch
import numpy as np
from multithread_explorer import ThreadSafeExplorer, add_multithread_support_to_sac
from gpu_optimizer import enhance_sac_with_gpu_optimization, GPUOptimizationConfig
from SAC import SAC


class PerformanceOptimizedSAC(SAC):
    """
    性能优化版本的SAC，集成多线程探索和GPU优化
    """
    
    def __init__(self, *args, **kwargs):
        # 提取优化相关参数
        self.enable_multithread = kwargs.pop('enable_multithread', True)
        self.enable_gpu_optimization = kwargs.pop('enable_gpu_optimization', True)
        self.num_workers = kwargs.pop('num_workers', 4)
        self.verbose = kwargs.pop('verbose', 1)
        
        # 调用父类初始化
        super().__init__(*args, **kwargs)
        
        # 应用性能优化
        self._apply_optimizations()
    
    def _apply_optimizations(self):
        """应用所有性能优化"""
        
        if self.verbose > 0:
            print("🔧 正在应用性能优化...")
        
        # 1. 应用GPU优化
        if self.enable_gpu_optimization:
            self._apply_gpu_optimization()
        
        # 2. 应用多线程优化
        if self.enable_multithread:
            self._apply_multithread_optimization()
        
        # 3. 根据硬件配置优化超参数
        self._auto_tune_hyperparameters()
        
        if self.verbose > 0:
            print("✅ 性能优化应用完成!")
    
    def _apply_gpu_optimization(self):
        """应用GPU优化"""
        try:
            enhance_sac_with_gpu_optimization(self, verbose=self.verbose)
            if self.verbose > 0:
                print("✅ GPU优化已启用")
        except Exception as e:
            if self.verbose > 0:
                print(f"⚠️ GPU优化启用失败: {e}")
    
    def _apply_multithread_optimization(self):
        """应用多线程优化"""
        try:
            # 创建多线程探索器
            self.explorer = ThreadSafeExplorer(self, num_workers=self.num_workers, verbose=self.verbose)
            self.env_lock = torch.multiprocessing.Lock() if hasattr(torch, 'multiprocessing') else None
            
            if self.verbose > 0:
                print(f"✅ 多线程优化已启用 ({self.num_workers} 线程)")
        except Exception as e:
            if self.verbose > 0:
                print(f"⚠️ 多线程优化启用失败: {e}")
    
    def _auto_tune_hyperparameters(self):
        """根据硬件自动调优超参数"""
        if not torch.cuda.is_available():
            return
        
        try:
            # 获取GPU内存大小
            gpu_memory_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            
            # 获取推荐设置
            recommended = GPUOptimizationConfig.get_recommended_settings(gpu_memory_gb)
            
            # 应用推荐设置（如果当前值较小）
            if hasattr(self, 'batch_size') and self.batch_size < recommended['batch_size']:
                old_batch_size = self.batch_size
                self.batch_size = recommended['batch_size']
                if self.verbose > 0:
                    print(f"📊 批处理大小优化: {old_batch_size} → {self.batch_size}")
            
            if hasattr(self, 'buffer_size') and self.buffer_size < recommended['buffer_size']:
                old_buffer_size = self.buffer_size
                self.buffer_size = recommended['buffer_size']
                if self.verbose > 0:
                    print(f"💾 缓冲区大小优化: {old_buffer_size:,} → {self.buffer_size:,}")
            
            # 更新工作线程数量
            if hasattr(self, 'explorer') and self.explorer.num_workers < recommended['num_workers']:
                old_workers = self.explorer.num_workers
                self.explorer.num_workers = recommended['num_workers']
                self.num_workers = recommended['num_workers']
                if self.verbose > 0:
                    print(f"🔄 工作线程数优化: {old_workers} → {self.num_workers}")
                    
        except Exception as e:
            if self.verbose > 0:
                print(f"⚠️ 自动调优失败: {e}")
    
    def explore_for_expert_targets(self,
                                 reward_target_exploration_steps=25_000,
                                 output_dir=None,
                                 save_pcb_every_n_steps=1000,
                                 use_multithread=None):
        """
        优化版本的专家目标探索
        
        Args:
            reward_target_exploration_steps: 探索步数
            output_dir: 输出目录
            save_pcb_every_n_steps: PCB保存频率
            use_multithread: 是否使用多线程（None表示使用默认设置）
        """
        if use_multithread is None:
            use_multithread = self.enable_multithread and hasattr(self, 'explorer')
        
        if use_multithread:
            # 使用多线程探索
            if self.verbose > 0:
                print(f"🚀 启动多线程探索 ({self.num_workers} 线程)")
            
            stats = self.explorer.explore(
                total_steps=reward_target_exploration_steps,
                output_dir=output_dir,
                save_pcb_every_n_steps=save_pcb_every_n_steps
            )
            
            if self.verbose > 0:
                print(f"✅ 多线程探索完成! 性能提升: {stats['steps_per_second']:.2f} 步/秒")
        else:
            # 使用原始单线程探索
            if self.verbose > 0:
                print("🐌 使用单线程探索")
            
            super().explore_for_expert_targets(
                reward_target_exploration_steps=reward_target_exploration_steps,
                output_dir=output_dir,
                save_pcb_every_n_steps=save_pcb_every_n_steps
            )
    
    def get_performance_report(self):
        """获取性能报告"""
        report = {
            'optimizations_enabled': {
                'multithread': self.enable_multithread,
                'gpu_optimization': self.enable_gpu_optimization
            },
            'hardware_info': {},
            'configuration': {
                'num_workers': getattr(self, 'num_workers', 'N/A'),
                'batch_size': getattr(self, 'batch_size', 'N/A'),
                'buffer_size': getattr(self, 'buffer_size', 'N/A')
            }
        }
        
        # 获取硬件信息
        if torch.cuda.is_available():
            gpu_props = torch.cuda.get_device_properties(0)
            report['hardware_info']['gpu'] = {
                'name': gpu_props.name,
                'memory_gb': gpu_props.total_memory / (1024**3),
                'compute_capability': f"{gpu_props.major}.{gpu_props.minor}"
            }
        
        # 获取CPU信息
        try:
            import psutil
            report['hardware_info']['cpu'] = {
                'cores': psutil.cpu_count(logical=False),
                'threads': psutil.cpu_count(logical=True),
                'memory_gb': psutil.virtual_memory().total / (1024**3)
            }
        except ImportError:
            pass
        
        # 获取GPU优化器统计信息
        if hasattr(self, 'optimized_trainer'):
            gpu_stats = self.optimized_trainer.get_performance_stats()
            report['gpu_performance'] = gpu_stats
        
        return report
    
    def print_performance_summary(self):
        """打印性能总结"""
        report = self.get_performance_report()
        
        print("\n" + "="*60)
        print("🚀 RL_PCB 性能优化总结")
        print("="*60)
        
        # 优化状态
        print("📋 优化状态:")
        for opt_name, enabled in report['optimizations_enabled'].items():
            status = "✅ 已启用" if enabled else "❌ 未启用"
            print(f"   {opt_name}: {status}")
        
        # 硬件信息
        if 'hardware_info' in report:
            print("\n🔧 硬件信息:")
            if 'gpu' in report['hardware_info']:
                gpu_info = report['hardware_info']['gpu']
                print(f"   GPU: {gpu_info['name']} ({gpu_info['memory_gb']:.1f}GB)")
            if 'cpu' in report['hardware_info']:
                cpu_info = report['hardware_info']['cpu']
                print(f"   CPU: {cpu_info['cores']}核/{cpu_info['threads']}线程 "
                      f"({cpu_info['memory_gb']:.1f}GB RAM)")
        
        # 配置信息
        print("\n⚙️ 优化配置:")
        config = report['configuration']
        for key, value in config.items():
            if value != 'N/A':
                if isinstance(value, int) and value > 1000:
                    print(f"   {key}: {value:,}")
                else:
                    print(f"   {key}: {value}")
        
        # GPU性能统计
        if 'gpu_performance' in report and report['gpu_performance']:
            print("\n📊 GPU性能统计:")
            gpu_perf = report['gpu_performance']
            if 'avg_batch_time' in gpu_perf:
                print(f"   平均批处理时间: {gpu_perf['avg_batch_time']:.4f}秒")
            if 'batches_per_second' in gpu_perf:
                print(f"   批处理速率: {gpu_perf['batches_per_second']:.2f} 批/秒")
        
        print("="*60)


def create_optimized_sac_model(train_env, 
                              hyperparameters,
                              device='cuda',
                              enable_multithread=True,
                              enable_gpu_optimization=True,
                              num_workers=None,
                              verbose=1):
    """
    创建性能优化的SAC模型
    
    Args:
        train_env: 训练环境
        hyperparameters: 超参数
        device: 设备
        enable_multithread: 是否启用多线程
        enable_gpu_optimization: 是否启用GPU优化
        num_workers: 工作线程数（None表示自动选择）
        verbose: 日志详细程度
    
    Returns:
        优化后的SAC模型
    """
    
    # 自动选择工作线程数
    if num_workers is None:
        try:
            import psutil
            cpu_cores = psutil.cpu_count(logical=False)
            num_workers = min(max(2, cpu_cores // 2), 8)  # 2-8个线程
        except ImportError:
            num_workers = 4
    
    # 创建优化的SAC模型
    model = PerformanceOptimizedSAC(
        train_env=train_env,
        hyperparameters=hyperparameters,
        device=device,
        enable_multithread=enable_multithread,
        enable_gpu_optimization=enable_gpu_optimization,
        num_workers=num_workers,
        verbose=verbose
    )
    
    if verbose > 0:
        print(f"\n🎯 性能优化SAC模型创建完成!")
        model.print_performance_summary()
    
    return model


# 使用示例
def example_usage():
    """使用示例"""
    
    print("🚀 RL_PCB 性能优化示例")
    print("-" * 40)
    
    # 假设已有环境和超参数
    # train_env = your_training_environment
    # hyperparameters = your_hyperparameters
    
    # 创建优化模型
    # model = create_optimized_sac_model(
    #     train_env=train_env,
    #     hyperparameters=hyperparameters,
    #     device='cuda',
    #     enable_multithread=True,
    #     enable_gpu_optimization=True,
    #     num_workers=6,
    #     verbose=1
    # )
    
    # 执行优化的专家目标探索
    # model.explore_for_expert_targets(
    #     reward_target_exploration_steps=50_000,
    #     output_dir="./optimized_output",
    #     save_pcb_every_n_steps=1000
    # )
    
    # 执行优化的训练
    # model.learn(
    #     timesteps=1_000_000,
    #     callback=your_callback,
    #     enable_gpu_optimization=True,
    #     adaptive_batch_size=True,
    #     memory_efficient_mode=True
    # )
    
    # 获取性能报告
    # model.print_performance_summary()
    
    # 打印优化指南
    GPUOptimizationConfig.print_optimization_guide()


if __name__ == "__main__":
    example_usage()
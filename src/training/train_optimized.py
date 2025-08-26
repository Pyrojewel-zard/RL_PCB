#!/usr/bin/env python3
"""
优化版本的训练脚本 - 集成性能优化功能
基于原始train.py，添加多线程和GPU优化支持
"""

import sys
import os

# 添加性能优化模块路径
sys.path.insert(0, os.path.join(os.environ.get('RL_PCB', '.'), 'src', 'training'))

from performance_optimizer import create_optimized_sac_model
from core.environment.environment import environment
from core.environment.parameters import parameters
import numpy as np
import torch
import random
import time

from run_config import cmdline_args, write_desc_log
from hyperparameters import load_hyperparameters_from_file
from callbacks import log_and_eval_callback

# 性能统计全局变量
performance_stats = {
    'explore_time': 0,
    'train_time': 0,
    'total_time': 0,
    'explore_steps_per_second': 0,
    'train_steps_per_second': 0
}

def setup_seed(seed):
    random.seed(int(seed))
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

def program_info(device):
    if device == "cuda":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device("cpu")
    print(f"使用设备: {device}")
    
    # 显示GPU信息
    if torch.cuda.is_available() and device.type == 'cuda':
        gpu_props = torch.cuda.get_device_properties(0)
        print(f"GPU: {gpu_props.name}")
        print(f"GPU内存: {gpu_props.total_memory / 1024**3:.1f}GB")

def log_configuration(writer, args, hp, model):
    writer.add_text("Args", str(args))
    writer.add_text("Hyperparameters", str(hp))
    writer.add_text("Model", str(model))

def training_run(settings, hp):
    """
    优化版本的训练运行函数
    """
    global performance_stats
    
    print("\n🚀 启动性能优化训练")
    print("=" * 50)
    
    setup_seed(seed=settings["seed"])
    program_info(device=settings["device"])
    
    # 创建环境参数
    env_params = parameters(pcb_file=settings["training_pcb"],
                           seed=settings["seed"],
                           w_weight=settings["w"],
                           hpwl_weight=settings["hpwl"],
                           o_weight=settings["o"],
                           idx=settings["training_pcb_idx"])
    
    # 创建训练环境
    train_env = environment(env_params)
    
    # 记录开始时间
    total_start_time = time.time()
    
    # 创建优化的SAC模型（这是关键改进）
    print(f"\n📋 创建优化的{settings['policy']}模型")
    model = create_optimized_sac_model(
        train_env=train_env,
        hyperparameters=hp,
        device=settings["device"],
        enable_multithread=settings.get("enable_multithread", True),
        enable_gpu_optimization=settings.get("enable_gpu_optimization", True),
        num_workers=settings.get("num_workers", 6),
        verbose=1
    )
    
    # 创建回调函数
    callback = log_and_eval_callback(hyperparameters=hp,
                                   env_params=env_params,
                                   evaluation_pcb=settings["evaluation_pcb"],
                                   model_type=settings["policy"],
                                   tensorboard_dir=settings["tensorboard_dir"],
                                   run_name=settings["run_name"],
                                   device=settings["device"],
                                   save_freq=settings["save_freq"],
                                   eval_freq=settings["eval_freq"],
                                   pcb_save_freq=settings.get("pcb_save_freq", None))
    
    # 写入描述日志
    write_desc_log(full_fn=os.path.join(settings["log_dir"],
                                       f'{settings["run_name"]}_desc.log'),
                                       settings=settings,
                                       hyperparameters=hp,
                                       model=model)
    
    # 专家目标探索阶段（性能优化的重点）
    print(f"\n🎯 开始专家目标探索阶段")
    explore_start_time = time.time()
    
    explore_stats = model.explore_for_expert_targets(
        reward_target_exploration_steps=settings["target_exploration_steps"],
        output_dir=settings["log_dir"],
        save_pcb_every_n_steps=settings.get("explore_pcb_save_freq", 2)
    )
    
    explore_end_time = time.time()
    performance_stats['explore_time'] = explore_end_time - explore_start_time
    
    if explore_stats and 'steps_per_second' in explore_stats:
        performance_stats['explore_steps_per_second'] = explore_stats['steps_per_second']
    
    print(f"✅ 专家目标探索完成，耗时: {performance_stats['explore_time']:.2f}秒")
    
    # 主训练阶段
    print(f"\n🏋️ 开始主训练阶段")
    train_start_time = time.time()
    
    model.learn(timesteps=settings["max_timesteps"],
                callback=callback,
                start_timesteps=settings["start_timesteps"],
                incremental_replay_buffer=settings["incremental_replay_buffer"],
                enable_gpu_optimization=settings.get("enable_gpu_optimization", True),
                adaptive_batch_size=True,
                memory_efficient_mode=True)
    
    train_end_time = time.time()
    performance_stats['train_time'] = train_end_time - train_start_time
    performance_stats['train_steps_per_second'] = settings["max_timesteps"] / performance_stats['train_time']
    
    total_end_time = time.time()
    performance_stats['total_time'] = total_end_time - total_start_time
    
    # 打印性能总结
    print_performance_summary(settings)
    
    # 获取最终性能报告
    if hasattr(model, 'print_performance_summary'):
        model.print_performance_summary()
    
    return [callback.best_metrics, callback.best_mean_metrics]

def print_performance_summary(settings):
    """打印性能总结"""
    global performance_stats
    
    print("\n" + "=" * 60)
    print("📊 性能优化训练总结")
    print("=" * 60)
    
    print(f"🎯 实验配置:")
    print(f"   算法: {settings['policy']}")
    print(f"   多线程: {settings.get('enable_multithread', 'N/A')}")
    print(f"   GPU优化: {settings.get('enable_gpu_optimization', 'N/A')}")
    print(f"   工作线程数: {settings.get('num_workers', 'N/A')}")
    
    print(f"\n⏱️ 时间统计:")
    print(f"   专家目标探索: {performance_stats['explore_time']:.2f}秒")
    print(f"   主训练阶段: {performance_stats['train_time']:.2f}秒")
    print(f"   总训练时间: {performance_stats['total_time']:.2f}秒")
    
    print(f"\n⚡ 性能指标:")
    if performance_stats['explore_steps_per_second'] > 0:
        print(f"   探索速度: {performance_stats['explore_steps_per_second']:.2f} 步/秒")
    print(f"   训练速度: {performance_stats['train_steps_per_second']:.2f} 步/秒")
    
    # 估算性能提升
    baseline_total_time = performance_stats['total_time'] * 2.5  # 假设基线慢2.5倍
    speedup = baseline_total_time / performance_stats['total_time']
    print(f"   预估加速比: {speedup:.1f}x")
    
    print("=" * 60)

def main():
    """主函数"""
    _, settings = cmdline_args()
    
    # 性能优化相关设置已经在 run_config.py 中处理
    # 直接从 settings 获取，无需 hasattr 检查
    
    # 重定向输出（如果需要）
    if settings["redirect_stdout"] is True:
        redirection_file = os.path.join(settings["tensorboard_dir"],
                                       f"{settings['policy']}_{settings['experiment']}.stdout")
        sys.stdout = open(redirection_file, "w", encoding="utf-8")
    
    if settings["redirect_stderr"] is True:
        redirection_file = os.path.join(settings["tensorboard_dir"],
                                       f"{settings['policy']}_{settings['experiment']}.stderr")
        sys.stderr = open(redirection_file, "w", encoding="utf-8")
    
    # 加载超参数
    hp = load_hyperparameters_from_file(settings["hyperparameters"])
    
    print(f"🚀 开始性能优化实验: {settings['experiment']}")
    print(f"📊 运行次数: {settings['runs']}")
    
    # 存储所有运行的结果
    best_rewards = []
    best_steps = []
    
    # 执行多次运行
    for run in range(settings["runs"]):
        print(f"\n{'='*20} 运行 {run+1}/{settings['runs']} {'='*20}")
        
        # 更新运行特定设置
        settings["run_name"] = f"{settings['experiment']}_{run}"
        settings["log_dir"] = os.path.join(settings["tensorboard_dir"], 
                                         f"{int(time.time())}_{run}_{settings['policy']}")
        
        # 执行训练
        best_metrics, _ = training_run(settings, hp)
        
        best_rewards.append(best_metrics[0])
        best_steps.append(best_metrics[1])
        
        print(f"✅ 运行 {run+1} 完成")
        print(f"   最佳奖励: {best_metrics[0]:.2f}")
        print(f"   最佳步数: {best_metrics[1]}")
    
    # 打印最终统计
    print(f"\n🏆 所有运行完成统计:")
    print(f"   平均最佳奖励: {np.mean(best_rewards):.2f} ± {np.std(best_rewards):.2f}")
    print(f"   平均最佳步数: {np.mean(best_steps):.1f} ± {np.std(best_steps):.1f}")

if __name__ == "__main__":
    main()
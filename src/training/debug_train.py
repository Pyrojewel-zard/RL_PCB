#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试版本的训练脚本
提供多种调试模式和断点设置
"""

import sys
import os
import pdb
import argparse

# 添加项目路径到系统路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.dirname(__file__))

# 设置环境变量
os.environ['RL_PCB'] = '/home/pyrojewel/RL_PCB'
os.environ['PYTHONPATH'] = '/home/pyrojewel/RL_PCB/src/training'

def setup_debug_environment():
    """设置调试环境"""
    print("=" * 60)
    print("🐛 PCB强化学习训练调试器")
    print("=" * 60)
    print(f"项目根目录: {os.environ.get('RL_PCB', 'Not Set')}")
    print(f"Python路径: {os.environ.get('PYTHONPATH', 'Not Set')}")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"Python解释器: {sys.executable}")
    print("=" * 60)

def debug_mode_interactive():
    """交互式调试模式"""
    print("\n🔍 启动交互式调试模式...")
    print("在需要的地方设置断点: pdb.set_trace()")
    
    # 设置全局断点处理
    import signal
    def signal_handler(sig, frame):
        print('\n⚠️  收到中断信号，进入调试模式...')
        pdb.set_trace()
    signal.signal(signal.SIGINT, signal_handler)
    
    # 导入并运行训练脚本
    try:
        from train import main
        print("✅ 成功导入训练模块")
        
        # 在main函数开始处设置断点
        print("\n🔴 在main()函数入口设置断点...")
        pdb.set_trace()
        
        main()
    except Exception as e:
        print(f"❌ 运行出错: {e}")
        pdb.post_mortem()

def debug_mode_step_by_step():
    """单步调试模式"""
    print("\n👣 启动单步调试模式...")
    
    try:
        # 设置sys.settrace来跟踪每一行代码
        import trace
        tracer = trace.Trace(trace=True, count=False)
        
        from train import main
        print("✅ 成功导入训练模块")
        
        tracer.run('main()')
    except Exception as e:
        print(f"❌ 运行出错: {e}")
        pdb.post_mortem()

def debug_mode_specific_function():
    """特定函数调试模式"""
    print("\n🎯 启动特定函数调试模式...")
    
    try:
        from train import training_run, setup_seed, program_info
        
        # 让用户选择要调试的函数
        functions = {
            '1': ('setup_seed', setup_seed),
            '2': ('program_info', program_info),
            '3': ('training_run', training_run),
        }
        
        print("请选择要调试的函数:")
        for key, (name, _) in functions.items():
            print(f"  {key}. {name}")
        
        choice = input("输入选择 (1-3): ").strip()
        
        if choice in functions:
            func_name, func = functions[choice]
            print(f"🔴 在函数 {func_name} 入口设置断点...")
            pdb.set_trace()
            
            # 根据函数类型提供不同的调用方式
            if func_name == 'setup_seed':
                func(42)  # 使用默认种子
            elif func_name == 'program_info':
                func('cuda')  # 使用CUDA设备
            elif func_name == 'training_run':
                print("⚠️  training_run需要完整的设置参数，建议使用完整调试模式")
        else:
            print("❌ 无效选择")
            
    except Exception as e:
        print(f"❌ 运行出错: {e}")
        pdb.post_mortem()

def debug_mode_quick_test():
    """快速测试调试模式 - 最小参数运行"""
    print("\n⚡ 启动快速测试调试模式...")
    
    # 设置最小测试参数
    test_args = [
        '--policy', 'SAC',
        '--target_exploration_steps', '5',
        '--start_timesteps', '10',
        '--max_timesteps', '100',
        '--evaluate_every', '50',
        '--training_pcb', '/home/pyrojewel/RL_PCB/dataset/base/region_8_fixed.pcb',
        '--evaluation_pcb', '/home/pyrojewel/RL_PCB/dataset/base/evaluation.pcb',
        '--tensorboard_dir', '/tmp/debug_tensorboard',
        '-w', '6.0',
        '--hpwl', '2.0',
        '-o', '2.0',
        '--hyperparameters', '/home/pyrojewel/RL_PCB/experiments/00_parameter_exeperiments/hyperparameters/hp_sac.json',
        '--incremental_replay_buffer', 'double',
        '--verbose', '2',
        '--runs', '1',
        '--experiment', 'quick_debug',
        '--device', 'cpu'  # 使用CPU以避免CUDA问题
    ]
    
    # 临时替换sys.argv
    original_argv = sys.argv.copy()
    sys.argv = ['train.py'] + test_args
    
    try:
        from train import main
        print("✅ 成功导入训练模块")
        print("🔴 在main()函数开始处设置断点...")
        pdb.set_trace()
        
        main()
    except Exception as e:
        print(f"❌ 运行出错: {e}")
        pdb.post_mortem()
    finally:
        # 恢复原始参数
        sys.argv = original_argv

def main():
    parser = argparse.ArgumentParser(description='PCB强化学习训练调试器')
    parser.add_argument('--mode', choices=['interactive', 'step', 'function', 'quick'], 
                       default='interactive',
                       help='调试模式: interactive(交互式), step(单步), function(特定函数), quick(快速测试)')
    
    # 如果没有参数，显示菜单
    if len(sys.argv) == 1:
        setup_debug_environment()
        
        print("\n🔧 调试模式选择:")
        print("  1. 交互式调试 (推荐) - 可以在任意位置设置断点")
        print("  2. 单步调试 - 跟踪每一行代码执行")
        print("  3. 特定函数调试 - 调试指定的函数")
        print("  4. 快速测试调试 - 使用最小参数快速测试")
        print("  5. 退出")
        
        choice = input("\n请选择调试模式 (1-5): ").strip()
        
        modes = {
            '1': debug_mode_interactive,
            '2': debug_mode_step_by_step,
            '3': debug_mode_specific_function,
            '4': debug_mode_quick_test,
        }
        
        if choice in modes:
            modes[choice]()
        elif choice == '5':
            print("👋 退出调试器")
            return
        else:
            print("❌ 无效选择")
            return
    else:
        args = parser.parse_args()
        setup_debug_environment()
        
        modes = {
            'interactive': debug_mode_interactive,
            'step': debug_mode_step_by_step,
            'function': debug_mode_specific_function,
            'quick': debug_mode_quick_test,
        }
        
        if args.mode in modes:
            modes[args.mode]()
        else:
            print(f"❌ 未知调试模式: {args.mode}")

if __name__ == "__main__":
    main()

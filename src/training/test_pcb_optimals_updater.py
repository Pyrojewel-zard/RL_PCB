#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PCB Optimals更新工具测试脚本

用于测试PCB optimals更新工具的功能，包括单个文件和批量处理功能。
"""

import os
import sys
import tempfile
import shutil
from pcb_optimals_updater import PCBOptimalsUpdater
from batch_pcb_optimals_updater import BatchPCBOptimalsUpdater


def test_single_pcb_updater():
    """测试单个PCB更新器"""
    print("=== 测试单个PCB更新器 ===")
    
    # 创建测试用的PCB文件路径（这里需要用户提供实际的PCB文件）
    test_pcb_file = input("请输入测试用的PCB文件路径: ").strip()
    
    if not os.path.exists(test_pcb_file):
        print(f"错误: 文件不存在: {test_pcb_file}")
        return False
    
    try:
        # 创建更新器
        updater = PCBOptimalsUpdater()
        
        # 测试加载PCB文件
        print("\n1. 测试加载PCB文件...")
        if not updater.load_pcb_file(test_pcb_file):
            print("加载PCB文件失败")
            return False
        
        # 测试打印optimals摘要
        print("\n2. 测试打印optimals摘要...")
        updater.print_optimals_summary()
        
        # 测试更新optimals值
        print("\n3. 测试更新optimals值...")
        result = updater.update_all_nodes_optimals()
        print(f"更新结果: {result}")
        
        # 测试保存PCB文件
        print("\n4. 测试保存PCB文件...")
        with tempfile.NamedTemporaryFile(suffix='.kicad_pcb', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        if updater.save_pcb_file(output_path):
            print(f"PCB文件已保存到: {output_path}")
            # 清理临时文件
            os.unlink(output_path)
        else:
            print("保存PCB文件失败")
            return False
        
        print("\n✅ 单个PCB更新器测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ 单个PCB更新器测试失败: {e}")
        return False


def test_batch_pcb_updater():
    """测试批量PCB更新器"""
    print("\n=== 测试批量PCB更新器 ===")
    
    # 创建测试用的PCB文件路径列表
    test_pcb_files = []
    while True:
        pcb_file = input("请输入测试用的PCB文件路径 (输入空行结束): ").strip()
        if not pcb_file:
            break
        if os.path.exists(pcb_file):
            test_pcb_files.append(pcb_file)
        else:
            print(f"警告: 文件不存在: {pcb_file}")
    
    if not test_pcb_files:
        print("没有提供有效的PCB文件，跳过批量测试")
        return True
    
    try:
        # 创建临时输出目录
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"使用临时输出目录: {temp_dir}")
            
            # 创建批量更新器
            updater = BatchPCBOptimalsUpdater()
            
            # 测试批量处理
            print(f"\n开始批量处理 {len(test_pcb_files)} 个文件...")
            results = updater.process_pcb_files(test_pcb_files, temp_dir)
            
            # 检查结果
            success_count = sum(1 for r in results if r['success'])
            print(f"\n批量处理结果: {success_count}/{len(results)} 成功")
            
            if success_count == len(results):
                print("✅ 批量PCB更新器测试通过!")
                return True
            else:
                print("❌ 批量PCB更新器测试失败!")
                return False
                
    except Exception as e:
        print(f"❌ 批量PCB更新器测试失败: {e}")
        return False


def test_utility_functions():
    """测试工具函数"""
    print("\n=== 测试工具函数 ===")
    
    try:
        # 测试PCBOptimalsUpdater的初始化
        updater = PCBOptimalsUpdater()
        print("✅ PCBOptimalsUpdater初始化成功")
        
        # 测试BatchPCBOptimalsUpdater的初始化
        batch_updater = BatchPCBOptimalsUpdater()
        print("✅ BatchPCBOptimalsUpdater初始化成功")
        
        print("✅ 工具函数测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ 工具函数测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("=== PCB Optimals更新工具测试 ===")
    
    # 检查环境
    print("1. 检查Python环境...")
    try:
        import pcb
        import pcb_vector_utils
        print("✅ 必要的模块导入成功")
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        print("请确保已激活正确的Python环境: source setup.sh")
        return False
    
    # 测试工具函数
    if not test_utility_functions():
        return False
    
    # 测试单个PCB更新器
    if not test_single_pcb_updater():
        return False
    
    # 测试批量PCB更新器
    if not test_batch_pcb_updater():
        return False
    
    print("\n🎉 所有测试通过!")
    print("\n工具功能验证:")
    print("✅ 模块导入正常")
    print("✅ 工具类初始化正常")
    print("✅ 单个PCB文件处理正常")
    print("✅ 批量PCB文件处理正常")
    print("✅ 文件保存功能正常")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
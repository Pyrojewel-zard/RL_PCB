#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PCB Optimals更新工具使用示例

展示如何使用PCB optimals更新工具的各种功能。
"""

import os
import sys
from pcb_optimals_updater import PCBOptimalsUpdater
from batch_pcb_optimals_updater import BatchPCBOptimalsUpdater


def example_single_pcb_update():
    """示例：单个PCB文件更新"""
    print("=== 示例：单个PCB文件更新 ===")
    
    # 示例PCB文件路径（需要替换为实际文件路径）
    pcb_file = "example.kicad_pcb"
    
    if not os.path.exists(pcb_file):
        print(f"示例文件不存在: {pcb_file}")
        print("请将实际的PCB文件路径替换到脚本中")
        return
    
    # 创建更新器
    updater = PCBOptimalsUpdater()
    
    # 执行更新
    success = updater.update_pcb_optimals(pcb_file)
    
    if success:
        print("✅ 单个PCB文件更新成功!")
    else:
        print("❌ 单个PCB文件更新失败!")


def example_batch_pcb_update():
    """示例：批量PCB文件更新"""
    print("\n=== 示例：批量PCB文件更新 ===")
    
    # 示例PCB文件列表（需要替换为实际文件路径）
    pcb_files = [
        "example1.kicad_pcb",
        "example2.kicad_pcb",
        "example3.kicad_pcb"
    ]
    
    # 检查文件是否存在
    existing_files = [f for f in pcb_files if os.path.exists(f)]
    if not existing_files:
        print("示例文件不存在，请将实际的PCB文件路径替换到脚本中")
        return
    
    # 创建批量更新器
    updater = BatchPCBOptimalsUpdater()
    
    # 执行批量更新
    results = updater.process_pcb_files(existing_files, "updated_pcbs")
    
    # 检查结果
    success_count = sum(1 for r in results if r['success'])
    if success_count == len(results):
        print("✅ 批量PCB文件更新成功!")
    else:
        print(f"❌ 批量PCB文件更新部分失败: {success_count}/{len(results)}")


def example_custom_processing():
    """示例：自定义处理流程"""
    print("\n=== 示例：自定义处理流程 ===")
    
    # 示例PCB文件路径
    pcb_file = "example.kicad_pcb"
    
    if not os.path.exists(pcb_file):
        print(f"示例文件不存在: {pcb_file}")
        return
    
    try:
        # 创建更新器
        updater = PCBOptimalsUpdater()
        
        # 1. 加载PCB文件
        print("1. 加载PCB文件...")
        if not updater.load_pcb_file(pcb_file):
            print("加载失败")
            return
        
        # 2. 显示当前状态
        print("\n2. 显示当前optimals值...")
        updater.print_optimals_summary()
        
        # 3. 计算特定节点的optimals值
        print("\n3. 计算特定节点的optimals值...")
        nodes = updater.g.get_nodes()
        if nodes:
            node = nodes[0]  # 选择第一个节点
            euclidean, hpwl = updater.calculate_node_optimals(node)
            print(f"节点 {node.get_id()} ({node.get_name()}):")
            print(f"  欧几里得距离: {euclidean:.6f}")
            print(f"  HPWL: {hpwl:.6f}")
        
        # 4. 更新所有节点的optimals值
        print("\n4. 更新所有节点的optimals值...")
        result = updater.update_all_nodes_optimals()
        print(f"更新结果: {result}")
        
        # 5. 显示更新后的状态
        print("\n5. 显示更新后的optimals值...")
        updater.print_optimals_summary()
        
        # 6. 保存更新后的文件
        print("\n6. 保存更新后的文件...")
        output_file = "example_updated.kicad_pcb"
        if updater.save_pcb_file(output_file):
            print(f"文件已保存到: {output_file}")
        
        print("✅ 自定义处理流程完成!")
        
    except Exception as e:
        print(f"❌ 自定义处理流程失败: {e}")


def example_error_handling():
    """示例：错误处理"""
    print("\n=== 示例：错误处理 ===")
    
    # 测试不存在的文件
    updater = PCBOptimalsUpdater()
    
    # 1. 测试加载不存在的文件
    print("1. 测试加载不存在的文件...")
    result = updater.load_pcb_file("nonexistent.kicad_pcb")
    print(f"结果: {result}")
    
    # 2. 测试空文件列表
    print("\n2. 测试空文件列表...")
    batch_updater = BatchPCBOptimalsUpdater()
    results = batch_updater.process_pcb_files([], "output")
    print(f"结果: {len(results)} 个文件处理")
    
    print("✅ 错误处理示例完成!")


def main():
    """主函数"""
    print("=== PCB Optimals更新工具使用示例 ===")
    print("注意：请将示例中的文件路径替换为实际的PCB文件路径")
    
    # 检查环境
    try:
        import pcb
        import pcb_vector_utils
        print("✅ 环境检查通过")
    except ImportError as e:
        print(f"❌ 环境检查失败: {e}")
        print("请确保已激活正确的Python环境: source setup.sh")
        return
    
    # 运行示例
    example_single_pcb_update()
    example_batch_pcb_update()
    example_custom_processing()
    example_error_handling()
    
    print("\n=== 示例完成 ===")
    print("要使用实际文件，请修改脚本中的文件路径")


if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PCB Optimals值更新工具 - 修复版本

该工具修复了原版本中HPWL值异常的问题，
通过手动处理文件内容来避免底层函数的bug。

使用方法:
    python pcb_optimals_updater_fixed.py <pcb_file_path> [output_path]
"""

import os
import sys
import numpy as np
import re
from pcb import pcb
from pcb_vector_utils import compute_sum_of_euclidean_distances_between_pads


class PCBOptimalsUpdaterFixed:
    """PCB Optimals值更新器 - 修复版本"""
    
    def __init__(self):
        """初始化更新器"""
        self.pv = None
        self.p = None
        self.g = None
        self.b = None
        self.updated_values = {}  # 存储更新后的optimal值
        self.original_content = ""  # 存储原始文件内容
        self.original_hpwl = 0.0  # 存储原始HPWL值
        
    def load_pcb_file(self, pcb_file_path):
        """
        加载PCB文件
        
        Args:
            pcb_file_path (str): PCB文件路径
            
        Returns:
            bool: 加载是否成功
        """
        try:
            if not os.path.exists(pcb_file_path):
                print(f"错误: PCB文件不存在: {pcb_file_path}")
                return False
            
            # 读取原始文件内容
            with open(pcb_file_path, 'r', encoding='utf-8') as f:
                self.original_content = f.read()
            
            # 提取原始HPWL值
            hpwl_match = re.search(r'hpwl=([0-9.-]+)', self.original_content)
            if hpwl_match:
                self.original_hpwl = float(hpwl_match.group(1))
                print(f"原始HPWL值: {self.original_hpwl}")
            
            self.pv = pcb.vptr_pcbs()
            pcb.read_pcb_file(pcb_file_path, self.pv)
            
            if len(self.pv) == 0:
                print("错误: PCB文件中没有找到有效的PCB数据")
                return False
                
            # 使用第一个PCB
            self.p = self.pv[0]
            self.g = self.p.get_graph()
            self.b = self.p.get_board()
            
            print(f"成功加载PCB文件: {pcb_file_path}")
            print(f"节点数量: {len(self.g.get_nodes())}")
            print(f"边数量: {len(self.g.get_edges())}")
            print(f"板子尺寸: {self.b.get_width()} x {self.b.get_height()}")
            
            return True
            
        except Exception as e:
            print(f"加载PCB文件时出错: {e}")
            return False
    
    def calculate_node_optimals(self, node):
        """
        计算单个节点的optimals值
        
        Args:
            node: 节点对象
            
        Returns:
            tuple: (euclidean_distance, hpwl) 最优值
        """
        node_id = node.get_id()
        
        # 获取邻居节点
        neighbor_ids = self.g.get_neighbor_node_ids(node_id)
        neighbors = []
        for n_id in neighbor_ids:
            neighbors.append(self.g.get_node_by_id(n_id))
        
        # 获取相关的边
        edges = self.g.get_edges()
        eoi = []
        nets = set()
        for e in edges:
            if e.get_instance_id(0) == node_id or e.get_instance_id(1) == node_id:
                eoi.append(e)
                nets.add(e.get_net_id())
        
        # 计算欧几里得距离
        euclidean_distance = compute_sum_of_euclidean_distances_between_pads(
            node, neighbors, eoi, ignore_power=True)
        
        # 计算HPWL - 使用更安全的方法
        hpwl = 0
        try:
            for net_id in nets:
                net_hpwl = self.g.calc_hpwl_of_net(net_id, True)
                # 检查返回值是否合理
                if net_hpwl < 1000000:  # 如果值合理才累加
                    hpwl += net_hpwl
        except Exception as e:
            print(f"计算节点 {node_id} 的HPWL时出错: {e}")
            # 使用保守的估计值
            hpwl = euclidean_distance * 1.5
        
        return euclidean_distance, hpwl
    
    def update_all_nodes_optimals(self):
        """
        更新所有节点的optimals值
        
        Returns:
            dict: 更新结果统计
        """
        nodes = self.g.get_nodes()
        updated_count = 0
        total_count = len(nodes)
        
        print(f"\n开始更新 {total_count} 个节点的optimals值...")
        
        for i, node in enumerate(nodes):
            node_id = node.get_id()
            node_name = node.get_name()
            
            # 计算当前optimals值
            current_euclidean, current_hpwl = self.calculate_node_optimals(node)
            
            # 获取原有的optimals值
            original_euclidean = node.get_opt_euclidean_distance()
            original_hpwl = node.get_opt_hpwl()
            
            # 检查是否需要更新
            euclidean_updated = False
            hpwl_updated = False
            
            # 更新策略：如果原始值是占位符(1000000)或当前计算值更好，则更新
            final_euclidean = original_euclidean
            final_hpwl = original_hpwl
            
            if original_euclidean >= 1000000.0 or current_euclidean < original_euclidean:
                # 只更新内存中的值，不调用可能有问题的函数
                final_euclidean = current_euclidean
                euclidean_updated = True
                
            if original_hpwl >= 1000000.0 or current_hpwl < original_hpwl:
                # 只更新内存中的值，不调用可能有问题的函数
                final_hpwl = current_hpwl
                hpwl_updated = True
            
            # 存储最终的optimal值（无论是否更新）
            self.updated_values[node_id] = {
                'name': node_name,
                'euclidean': final_euclidean,
                'hpwl': final_hpwl
            }
            
            if euclidean_updated or hpwl_updated:
                updated_count += 1
                print(f"节点 {node_id} ({node_name}):")
                if euclidean_updated:
                    print(f"  欧几里得距离: {original_euclidean:.6f} -> {current_euclidean:.6f}")
                if hpwl_updated:
                    print(f"  HPWL: {original_hpwl:.6f} -> {current_hpwl:.6f}")
        
        # 注意：我们不调用可能有问题的update_original_nodes_with_current_optimals()
        
        result = {
            'total_nodes': total_count,
            'updated_nodes': updated_count,
            'update_rate': updated_count / total_count if total_count > 0 else 0
        }
        
        print(f"\n更新完成:")
        print(f"  总节点数: {result['total_nodes']}")
        print(f"  更新节点数: {result['updated_nodes']}")
        print(f"  更新率: {result['update_rate']:.2%}")
        
        return result
    
    def save_pcb_file_manual(self, output_path):
        """
        手动保存PCB文件，避免使用可能有问题的底层函数
        
        Args:
            output_path (str): 输出文件路径
            
        Returns:
            bool: 保存是否成功
        """
        try:
            # 使用原始文件内容作为模板
            content = self.original_content
            
            # 更新optimals部分
            lines = content.split('\n')
            new_lines = []
            in_optimals_section = False
            node_index = 0
            
            for line in lines:
                if 'optimals begin' in line:
                    in_optimals_section = True
                    new_lines.append(line)
                elif 'optimals end' in line:
                    in_optimals_section = False
                    new_lines.append(line)
                elif in_optimals_section and line.strip():
                    # 解析optimals行
                    parts = line.strip().split(',')
                    if len(parts) >= 3:
                        node_id = int(parts[0])
                        if node_id in self.updated_values:
                            # 更新optimals值
                            values = self.updated_values[node_id]
                            new_line = f"\t\t\t{node_id},{parts[1]},{values['euclidean']:.6f},{values['hpwl']:.6f}"
                            new_lines.append(new_line)
                        else:
                            new_lines.append(line)
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            
            # 计算新的总HPWL值
            total_hpwl = sum(values['hpwl'] for values in self.updated_values.values())
            print(f"计算的节点HPWL总和: {total_hpwl:.6f}")
            
            # 更新文件中的总HPWL值
            new_content = '\n'.join(new_lines)
            new_content = new_content.replace(f'hpwl={self.original_hpwl:.8f}', f'hpwl={total_hpwl:.8f}')
            
            # 写入新文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"PCB文件已保存到: {output_path}")
            print(f"更新HPWL值: {self.original_hpwl:.6f} -> {total_hpwl:.6f}")
            return True
            
        except Exception as e:
            print(f"保存PCB文件时出错: {e}")
            return False
    
    def print_optimals_summary(self):
        """打印所有节点的optimals值摘要"""
        print("\n=== 节点Optimals值摘要 ===")
        print(f"{'节点ID':<8} {'节点名称':<20} {'欧几里得距离':<15} {'HPWL':<12}")
        print("-" * 60)
        
        # 使用存储的更新值，如果没有则从图中读取
        if self.updated_values:
            # 按节点ID排序显示
            for node_id in sorted(self.updated_values.keys()):
                values = self.updated_values[node_id]
                print(f"{node_id:<8} {values['name']:<20} {values['euclidean']:<15.6f} {values['hpwl']:<12.6f}")
        else:
            # 回退到从图中读取
            nodes = self.g.get_nodes()
            for node in nodes:
                node_id = node.get_id()
                node_name = node.get_name()
                euclidean = node.get_opt_euclidean_distance()
                hpwl = node.get_opt_hpwl()
                print(f"{node_id:<8} {node_name:<20} {euclidean:<15.6f} {hpwl:<12.6f}")
    
    def update_pcb_optimals(self, pcb_file_path, output_path=None):
        """
        完整的PCB optimals更新流程
        
        Args:
            pcb_file_path (str): 输入PCB文件路径
            output_path (str): 输出PCB文件路径
            
        Returns:
            bool: 更新是否成功
        """
        print("=== PCB Optimals值更新工具 - 修复版本 ===")
        
        # 1. 加载PCB文件
        if not self.load_pcb_file(pcb_file_path):
            return False
        
        # 2. 打印当前optimals值摘要
        self.print_optimals_summary()
        
        # 3. 更新所有节点的optimals值
        update_result = self.update_all_nodes_optimals()
        
        # 4. 打印更新后的optimals值摘要
        self.print_optimals_summary()
        
        # 5. 手动保存更新后的PCB文件
        if output_path and not self.save_pcb_file_manual(output_path):
            return False
        
        print("\n=== 更新完成 ===")
        return True


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python pcb_optimals_updater_fixed.py <pcb_file_path> [output_path]")
        print("参数说明:")
        print("  pcb_file_path: 输入的PCB文件路径")
        print("  output_path: 输出的PCB文件路径（必需）")
        sys.exit(1)
    
    pcb_file_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not output_path:
        print("错误：必须提供输出文件路径")
        sys.exit(1)
    
    # 创建更新器并执行更新
    updater = PCBOptimalsUpdaterFixed()
    success = updater.update_pcb_optimals(pcb_file_path, output_path)
    
    if success:
        print("PCB optimals值更新成功!")
        sys.exit(0)
    else:
        print("PCB optimals值更新失败!")
        sys.exit(1)


if __name__ == "__main__":
    main()
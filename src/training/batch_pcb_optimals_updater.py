#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量PCB Optimals值更新工具

该工具用于批量对多个PCB文件进行optimals值的更新。
基于training文件夹中已有的函数，计算每个节点的最优欧几里得距离和HPWL值。

使用方法:
    python batch_pcb_optimals_updater.py <pcb_file_list> [output_dir]
    python batch_pcb_optimals_updater.py --dir <pcb_directory> [output_dir]
"""

import os
import sys
import glob
import argparse
import numpy as np
from pcb import pcb
from pcb_vector_utils import compute_sum_of_euclidean_distances_between_pads


class BatchPCBOptimalsUpdater:
    """批量PCB Optimals值更新器"""
    
    def __init__(self):
        """初始化更新器"""
        self.results = []
        
    def process_single_pcb(self, pcb_file_path, output_dir=None):
        """
        处理单个PCB文件
        
        Args:
            pcb_file_path (str): PCB文件路径
            output_dir (str): 输出目录
            
        Returns:
            dict: 处理结果
        """
        result = {
            'file_path': pcb_file_path,
            'success': False,
            'error': None,
            'total_nodes': 0,
            'updated_nodes': 0,
            'update_rate': 0.0
        }
        
        try:
            print(f"\n处理文件: {pcb_file_path}")
            
            # 加载PCB文件
            pv = pcb.vptr_pcbs()
            pcb.read_pcb_file(pcb_file_path, pv)
            
            if len(pv) == 0:
                result['error'] = "PCB文件中没有找到有效的PCB数据"
                return result
            
            p = pv[0]
            g = p.get_graph()
            b = p.get_board()
            
            nodes = g.get_nodes()
            total_nodes = len(nodes)
            updated_nodes = 0
            
            print(f"  节点数量: {total_nodes}")
            print(f"  边数量: {len(g.get_edges())}")
            print(f"  板子尺寸: {b.get_width()} x {b.get_height()}")
            
            # 更新每个节点的optimals值
            for node in nodes:
                node_id = node.get_id()
                node_name = node.get_name()
                
                # 获取邻居节点
                neighbor_ids = g.get_neighbor_node_ids(node_id)
                neighbors = []
                for n_id in neighbor_ids:
                    neighbors.append(g.get_node_by_id(n_id))
                
                # 获取相关的边
                edges = g.get_edges()
                eoi = []
                nets = set()
                for e in edges:
                    if e.get_instance_id(0) == node_id or e.get_instance_id(1) == node_id:
                        eoi.append(e)
                        nets.add(e.get_net_id())
                
                # 计算当前optimals值
                current_euclidean = compute_sum_of_euclidean_distances_between_pads(
                    node, neighbors, eoi, ignore_power=True)
                
                current_hpwl = 0
                for net_id in nets:
                    current_hpwl += g.calc_hpwl_of_net(net_id, True)
                
                # 获取原有的optimals值
                original_euclidean = node.get_opt_euclidean_distance()
                original_hpwl = node.get_opt_hpwl()
                
                # 检查是否需要更新
                updated = False
                if current_euclidean < original_euclidean:
                    node.set_opt_euclidean_distance(current_euclidean)
                    updated = True
                    
                if current_hpwl < original_hpwl:
                    node.set_opt_hpwl(current_hpwl)
                    updated = True
                
                if updated:
                    updated_nodes += 1
                    print(f"    节点 {node_id} ({node_name}): 已更新")
            
            # 更新原始节点列表
            g.update_original_nodes_with_current_optimals()
            
            # 保存更新后的PCB文件
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                base_name = os.path.basename(p.get_kicad_pcb2())
                output_path = os.path.join(output_dir, base_name)
            else:
                # 生成备份文件名
                base_name = p.get_kicad_pcb2()
                backup_name = base_name.replace('.kicad_pcb', '_updated.kicad_pcb')
                output_path = backup_name
            
            p.write_pcb_file(output_path)
            
            result['success'] = True
            result['total_nodes'] = total_nodes
            result['updated_nodes'] = updated_nodes
            result['update_rate'] = updated_nodes / total_nodes if total_nodes > 0 else 0
            result['output_path'] = output_path
            
            print(f"  更新完成: {updated_nodes}/{total_nodes} 个节点 ({result['update_rate']:.2%})")
            print(f"  保存到: {output_path}")
            
        except Exception as e:
            result['error'] = str(e)
            print(f"  错误: {e}")
        
        return result
    
    def process_pcb_files(self, pcb_files, output_dir=None):
        """
        批量处理PCB文件
        
        Args:
            pcb_files (list): PCB文件路径列表
            output_dir (str): 输出目录
            
        Returns:
            list: 处理结果列表
        """
        print(f"=== 批量PCB Optimals值更新工具 ===")
        print(f"处理文件数量: {len(pcb_files)}")
        if output_dir:
            print(f"输出目录: {output_dir}")
        
        results = []
        success_count = 0
        
        for i, pcb_file in enumerate(pcb_files, 1):
            print(f"\n[{i}/{len(pcb_files)}] 处理文件: {pcb_file}")
            
            result = self.process_single_pcb(pcb_file, output_dir)
            results.append(result)
            
            if result['success']:
                success_count += 1
        
        # 打印总结
        self.print_summary(results, success_count)
        
        return results
    
    def print_summary(self, results, success_count):
        """打印处理总结"""
        print(f"\n=== 处理总结 ===")
        print(f"总文件数: {len(results)}")
        print(f"成功处理: {success_count}")
        print(f"失败处理: {len(results) - success_count}")
        
        if success_count > 0:
            total_nodes = sum(r['total_nodes'] for r in results if r['success'])
            total_updated = sum(r['updated_nodes'] for r in results if r['success'])
            overall_update_rate = total_updated / total_nodes if total_nodes > 0 else 0
            
            print(f"总节点数: {total_nodes}")
            print(f"总更新节点数: {total_updated}")
            print(f"总体更新率: {overall_update_rate:.2%}")
        
        # 打印失败的文件
        failed_files = [r for r in results if not r['success']]
        if failed_files:
            print(f"\n失败的文件:")
            for result in failed_files:
                print(f"  {result['file_path']}: {result['error']}")


def get_pcb_files_from_directory(directory):
    """从目录中获取所有PCB文件"""
    pcb_files = []
    
    # 支持的PCB文件扩展名
    extensions = ['*.kicad_pcb', '*.pcb']
    
    for ext in extensions:
        pattern = os.path.join(directory, ext)
        pcb_files.extend(glob.glob(pattern))
    
    return sorted(pcb_files)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='批量PCB Optimals值更新工具')
    parser.add_argument('pcb_files', nargs='*', help='PCB文件路径列表')
    parser.add_argument('--dir', help='PCB文件目录')
    parser.add_argument('--output', help='输出目录')
    
    args = parser.parse_args()
    
    pcb_files = []
    
    if args.dir:
        # 从目录中获取PCB文件
        if not os.path.isdir(args.dir):
            print(f"错误: 目录不存在: {args.dir}")
            sys.exit(1)
        
        pcb_files = get_pcb_files_from_directory(args.dir)
        if not pcb_files:
            print(f"错误: 在目录 {args.dir} 中没有找到PCB文件")
            sys.exit(1)
    else:
        # 使用命令行参数中的文件列表
        pcb_files = args.pcb_files
        if not pcb_files:
            print("使用方法:")
            print("  python batch_pcb_optimals_updater.py <pcb_file1> <pcb_file2> ... [output_dir]")
            print("  python batch_pcb_optimals_updater.py --dir <pcb_directory> [output_dir]")
            sys.exit(1)
    
    # 检查文件是否存在
    for pcb_file in pcb_files:
        if not os.path.exists(pcb_file):
            print(f"错误: PCB文件不存在: {pcb_file}")
            sys.exit(1)
    
    # 创建更新器并执行批量更新
    updater = BatchPCBOptimalsUpdater()
    results = updater.process_pcb_files(pcb_files, args.output)
    
    # 检查是否有失败的处理
    failed_count = len([r for r in results if not r['success']])
    
    if failed_count == 0:
        print("\n所有PCB文件处理成功!")
        sys.exit(0)
    else:
        print(f"\n有 {failed_count} 个文件处理失败!")
        sys.exit(1)


if __name__ == "__main__":
    main() 
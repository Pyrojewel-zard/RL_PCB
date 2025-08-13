#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试欧几里得距离为0的问题
"""

import os
import sys
import numpy as np
from pcb import pcb
from pcb_vector_utils import compute_sum_of_euclidean_distances_between_pads
from graph_utils import kicad_rotate


def debug_node_connections(pcb_file_path, target_node_ids):
    """
    调试特定节点的连接信息
    """
    # 加载PCB文件
    pv = pcb.vptr_pcbs()
    pcb.read_pcb_file(pcb_file_path, pv)
    p = pv[0]
    g = p.get_graph()
    
    nodes = g.get_nodes()
    edges = g.get_edges()
    
    for target_id in target_node_ids:
        print(f"\n=== 分析节点 {target_id} ===")
        
        # 找到目标节点
        target_node = None
        for node in nodes:
            if node.get_id() == target_id:
                target_node = node
                break
        
        if target_node is None:
            print(f"未找到节点 {target_id}")
            continue
            
        print(f"节点名称: {target_node.get_name()}")
        print(f"管脚数量: {target_node.get_pin_count()}")
        print(f"位置: {target_node.get_pos()}")
        
        # 获取相关的边
        related_edges = []
        all_nets = set()
        power_edges = []
        non_power_edges = []
        
        for e in edges:
            if e.get_instance_id(0) == target_id or e.get_instance_id(1) == target_id:
                related_edges.append(e)
                all_nets.add(e.get_net_id())
                
                # 检查是否为电源轨
                if e.get_power_rail() > 0:
                    power_edges.append(e)
                else:
                    non_power_edges.append(e)
        
        print(f"总相关边数: {len(related_edges)}")
        print(f"电源轨边数: {len(power_edges)}")
        print(f"非电源轨边数: {len(non_power_edges)}")
        print(f"涉及网络ID: {sorted(all_nets)}")
        
        # 获取邻居节点
        neighbor_ids = g.get_neighbor_node_ids(target_id)
        neighbors = []
        for n_id in neighbor_ids:
            neighbors.append(g.get_node_by_id(n_id))
        print(f"\n邻居节点ID: {neighbor_ids}")
        
        # 输出邻居节点的详细信息
        print(f"\n邻居节点详细信息:")
        for i, neighbor in enumerate(neighbors):
            neighbor_id = neighbor.get_id()
            neighbor_name = neighbor.get_name()
            neighbor_pos = neighbor.get_pos()
            neighbor_size = neighbor.get_size()
            neighbor_pin_count = neighbor.get_pin_count()
            neighbor_orientation = neighbor.get_orientation()
            
            # 计算与目标节点的中心距离
            target_pos = target_node.get_pos()
            center_distance = np.sqrt((target_pos[0] - neighbor_pos[0])**2 + 
                                    (target_pos[1] - neighbor_pos[1])**2)
            
            print(f"  邻居{i} - 节点{neighbor_id} ({neighbor_name}):")
            print(f"    位置: ({neighbor_pos[0]:.3f}, {neighbor_pos[1]:.3f})")
            print(f"    尺寸: ({neighbor_size[0]:.3f}, {neighbor_size[1]:.3f})")
            print(f"    管脚数: {neighbor_pin_count}")
            print(f"    方向: {neighbor_orientation:.1f}度")
            print(f"    与目标节点中心距离: {center_distance:.6f}")
            
            # 找到连接这两个节点的边
            connecting_edges = []
            for e in related_edges:
                if ((e.get_instance_id(0) == target_id and e.get_instance_id(1) == neighbor_id) or
                    (e.get_instance_id(0) == neighbor_id and e.get_instance_id(1) == target_id)):
                    connecting_edges.append(e)
            
            print(f"    连接边数: {len(connecting_edges)}")
            for j, edge in enumerate(connecting_edges):
                pad0_id = edge.get_pad_id(0)
                pad1_id = edge.get_pad_id(1)
                pos0 = edge.get_pos(0)
                pos1 = edge.get_pos(1)
                net_name = edge.get_net_name()
                power_rail = edge.get_power_rail()
                
                # 计算实际的焊盘到焊盘距离
                if edge.get_instance_id(0) == target_id:
                    target_pad_pos = pos0
                    neighbor_pad_pos = pos1
                    target_pad_id = pad0_id
                    neighbor_pad_id = pad1_id
                else:
                    target_pad_pos = pos1
                    neighbor_pad_pos = pos0
                    target_pad_id = pad1_id
                    neighbor_pad_id = pad0_id
                
                # 考虑节点方向的焊盘位置
                rotated_target_pad = kicad_rotate(
                    float(target_pad_pos[0]), 
                    float(target_pad_pos[1]), 
                    target_node.get_orientation())
                
                rotated_neighbor_pad = kicad_rotate(
                    float(neighbor_pad_pos[0]), 
                    float(neighbor_pad_pos[1]), 
                    neighbor.get_orientation())
                
                # 计算实际世界坐标
                actual_target_pad = [
                    target_pos[0] + rotated_target_pad[0],
                    target_pos[1] + rotated_target_pad[1]
                ]
                
                actual_neighbor_pad = [
                    neighbor_pos[0] + rotated_neighbor_pad[0],
                    neighbor_pos[1] + rotated_neighbor_pad[1]
                ]
                
                pad_distance = np.sqrt(
                    (actual_target_pad[0] - actual_neighbor_pad[0])**2 + 
                    (actual_target_pad[1] - actual_neighbor_pad[1])**2)
                
                print(f"      边{j}: pad{target_pad_id} <-> pad{neighbor_pad_id}")
                print(f"        网络: {net_name} (电源轨: {power_rail})")
                print(f"        目标节点焊盘位置: ({actual_target_pad[0]:.3f}, {actual_target_pad[1]:.3f})")
                print(f"        邻居节点焊盘位置: ({actual_neighbor_pad[0]:.3f}, {actual_neighbor_pad[1]:.3f})")
                print(f"        焊盘间距离: {pad_distance:.6f}")
        
        # 详细分析每条边
        print(f"\n边详细信息:")
        for i, e in enumerate(related_edges):
            node0_id = e.get_instance_id(0)
            node1_id = e.get_instance_id(1)
            pad0_id = e.get_pad_id(0)
            pad1_id = e.get_pad_id(1)
            net_id = e.get_net_id()
            net_name = e.get_net_name()
            power_rail = e.get_power_rail()
            
            print(f"  边{i}: 节点{node0_id}[pad{pad0_id}] <-> 节点{node1_id}[pad{pad1_id}]")
            print(f"        网络: {net_id} ({net_name})")
            print(f"        电源轨: {power_rail}")
        
        # 计算欧几里得距离（不忽略电源轨）
        euclidean_with_power = compute_sum_of_euclidean_distances_between_pads(
            target_node, neighbors, related_edges, ignore_power=False)
        
        # 计算欧几里得距离（忽略电源轨）
        euclidean_without_power = compute_sum_of_euclidean_distances_between_pads(
            target_node, neighbors, related_edges, ignore_power=True)
            
        print(f"\n欧几里得距离计算结果:")
        print(f"  包含电源轨: {euclidean_with_power:.6f}")
        print(f"  忽略电源轨: {euclidean_without_power:.6f}")
        
        # 逐管脚分析
        print(f"\n逐管脚分析:")
        pin_count = target_node.get_pin_count()
        for pin_id in range(pin_count):
            pin_edges = []
            for e in related_edges:
                for j in range(2):
                    if (e.get_instance_id(j) == target_id) and (e.get_pad_id(j) == pin_id):
                        pin_edges.append(e)
                        break
            
            pin_power_edges = [e for e in pin_edges if e.get_power_rail() > 0]
            pin_non_power_edges = [e for e in pin_edges if e.get_power_rail() == 0]
            
            print(f"  管脚{pin_id}: 总边数={len(pin_edges)}, 电源轨={len(pin_power_edges)}, 非电源轨={len(pin_non_power_edges)}")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python debug_zero_euclidean.py <pcb_file_path>")
        sys.exit(1)
    
    pcb_file_path = sys.argv[1]
    
    # 调试这三个欧几里得距离为0的节点
    target_node_ids = [11, 14, 19]  # C2502, R2302, C2308
    
    debug_node_connections(pcb_file_path, target_node_ids)


if __name__ == "__main__":
    main()
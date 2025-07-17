#!/usr/bin/env python3
"""
PCB库Python重构使用示例
演示如何使用重构后的PCB和netlist_graph模块
"""

import sys
import os
from pathlib import Path

# 添加pcb_python路径
pcb_python_path = Path(__file__).parent.parent / "pcb_python"
sys.path.insert(0, str(pcb_python_path))

def example_basic_usage():
    """基本使用示例"""
    print("=== 基本使用示例 ===")
    
    try:
        # 导入模块
        from netlist_graph import Graph, Node, Edge, Board, Utils
        
        # 创建图形
        graph = Graph()
        
        # 添加节点
        node1 = Node()
        node1.set_id(0)
        node1.set_name("LED1")
        node1.set_size((3.35, 1.85))
        node1.set_pos((156.31, 50.79))
        graph._V.append(node1)
        
        node2 = Node()
        node2.set_id(1)
        node2.set_name("R1")
        node2.set_size((3.7, 1.9))
        node2.set_pos((151.735, 50.815))
        graph._V.append(node2)
        
        # 添加边
        edge = Edge()
        edge.set_id(0, 0)
        edge.set_name(0, "LED1")
        edge.set_id(1, 1)
        edge.set_name(1, "R1")
        edge.set_net_id(1)
        edge.set_net_name("Net1")
        graph._E.append(edge)
        
        # 打印统计信息
        print(f"节点数量: {len(graph._V)}")
        print(f"边数量: {len(graph._E)}")
        
        # 计算HPWL
        hpwl = graph.calc_hpwl()
        print(f"HPWL: {hpwl:.2f}")
        
        print("基本使用示例完成！")
        
    except Exception as e:
        print(f"基本使用示例失败: {e}")

def example_file_operations():
    """文件操作示例"""
    print("\n=== 文件操作示例 ===")
    
    try:
        # 创建测试数据
        test_data = {
            'nodes': [
                "0,LED1,3.35,1.85,156.31,50.79,0,0,0,2,2,0,4",
                "1,R2,3.7,1.9,151.735,50.815,0,0,0,2,2,0,1"
            ],
            'edges': [
                "4,0,1,1.075,0.95,-0.8625,0,0,6,2,3,0.6,1.2,-1.25,0.95,0,1,\"Net-(C1-Pad1)\",2,0,0"
            ],
            'board': [
                "bb_min_x,100.00000000",
                "bb_min_y,80.00000000", 
                "bb_max_x,120.00000000",
                "bb_max_y,100.00000000",
                "board_name,Test Board"
            ]
        }
        
        # 创建临时文件
        nodes_file = "example_nodes.csv"
        edges_file = "example_edges.csv"
        board_file = "example_board.csv"
        pcb_file = "example_output.pcb"
        
        # 写入测试文件
        with open(nodes_file, 'w') as f:
            for line in test_data['nodes']:
                f.write(line + '\n')
        
        with open(edges_file, 'w') as f:
            for line in test_data['edges']:
                f.write(line + '\n')
        
        with open(board_file, 'w') as f:
            for line in test_data['board']:
                f.write(line + '\n')
        
        print(f"创建了测试文件:")
        print(f"  - {nodes_file}")
        print(f"  - {edges_file}")
        print(f"  - {board_file}")
        
        # 清理文件
        for file in [nodes_file, edges_file, board_file, pcb_file]:
            if os.path.exists(file):
                os.remove(file)
        
        print("文件操作示例完成！")
        
    except Exception as e:
        print(f"文件操作示例失败: {e}")

def example_graph_analysis():
    """图形分析示例"""
    print("\n=== 图形分析示例 ===")
    
    try:
        from netlist_graph import Graph, Utils
        
        # 创建测试图形
        graph = Graph()
        
        # 添加节点
        node_lines = [
            "0,LED1,3.35,1.85,156.31,50.79,0,0,0,2,2,0,4",
            "1,R2,3.7,1.9,151.735,50.815,0,0,0,2,2,0,1",
            "2,R1,3.7,1.9,146.985,50.065,0,0,0,2,2,0,1"
        ]
        
        for line in node_lines:
            graph.add_node_from_string_short(line)
        
        # 添加边
        edge_lines = [
            "4,0,1,1.075,0.95,-0.8625,0,0,6,2,3,0.6,1.2,-1.25,0.95,0,1,\"Net-(C1-Pad1)\",2,0,0",
            "6,0,1,0.6,1.2,-1.25,-0.95,0,6,2,3,0.6,1.2,-1.25,0.95,0,1,\"Net-(C1-Pad1)\",1,0,0"
        ]
        
        for line in edge_lines:
            graph.add_edge_from_string_short(line)
        
        # 分析图形
        print(f"图形统计:")
        print(f"  节点数量: {len(graph._V)}")
        print(f"  边数量: {len(graph._E)}")
        
        # 计算HPWL
        hpwl = graph.calc_hpwl()
        print(f"  HPWL: {hpwl:.2f}")
        
        # 分析节点连接性
        connectivity = graph.get_nodes_connectivity_list()
        print(f"  节点连接性: {connectivity}")
        
        # 分析邻居节点
        for i, node in enumerate(graph._V):
            neighbors = graph.get_neighbor_node_ids(node.get_id())
            print(f"  节点{i}的邻居: {neighbors}")
        
        print("图形分析示例完成！")
        
    except Exception as e:
        print(f"图形分析示例失败: {e}")

def example_utils_functions():
    """工具函数示例"""
    print("\n=== 工具函数示例 ===")
    
    try:
        from netlist_graph import Utils
        
        # 距离计算
        pos1 = (0.0, 0.0)
        pos2 = (3.0, 4.0)
        euclidean = Utils.euclidean_distance(pos1, pos2)
        manhattan = Utils.manhattan_distance(pos1, pos2)
        print(f"欧几里得距离: {euclidean:.2f}")
        print(f"曼哈顿距离: {manhattan:.2f}")
        
        # CSV解析
        line = "1,LED1,3.35,1.85,156.31,50.79,0,0,0,2,2,0,4"
        fields = Utils.parse_csv_line(line)
        print(f"CSV解析: {fields}")
        
        # 数值转换
        print(f"安全浮点数转换: {Utils.safe_float('3.14')}")
        print(f"安全整数转换: {Utils.safe_int('3.14')}")
        
        # HPWL计算
        points = [(0.0, 0.0), (10.0, 5.0), (5.0, 10.0)]
        hpwl = Utils.calculate_hpwl(points)
        print(f"HPWL计算: {hpwl:.2f}")
        
        print("工具函数示例完成！")
        
    except Exception as e:
        print(f"工具函数示例失败: {e}")

def main():
    """主函数"""
    print("PCB库Python重构使用示例")
    print("=" * 50)
    
    # 运行所有示例
    examples = [
        example_basic_usage,
        example_file_operations,
        example_graph_analysis,
        example_utils_functions
    ]
    
    for example in examples:
        try:
            example()
            print()
        except Exception as e:
            print(f"示例执行失败: {e}")
            print()
    
    print("所有示例执行完成！")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
测试netlist_graph的Python实现
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from netlist_graph import Graph, Node, Edge, Board, Optimal, Utils

def test_utils():
    """测试工具类"""
    print("=== 测试Utils类 ===")
    
    # 测试距离计算
    pos1 = (0.0, 0.0)
    pos2 = (3.0, 4.0)
    euclidean = Utils.euclidean_distance(pos1, pos2)
    manhattan = Utils.manhattan_distance(pos1, pos2)
    print(f"欧几里得距离: {euclidean:.2f}")
    print(f"曼哈顿距离: {manhattan:.2f}")
    
    # 测试CSV解析
    line = "1,LED1,3.35,1.85,156.31,50.79,0,0,0,2,2,0,4"
    fields = Utils.parse_csv_line(line)
    print(f"CSV解析: {fields}")
    
    # 测试数值转换
    print(f"安全浮点数转换: {Utils.safe_float('3.14')}")
    print(f"安全整数转换: {Utils.safe_int('3.14')}")
    
    # 测试HPWL计算
    points = [(0.0, 0.0), (10.0, 5.0), (5.0, 10.0)]
    hpwl = Utils.calculate_hpwl(points)
    print(f"HPWL计算: {hpwl:.2f}")

def test_optimal():
    """测试Optimal类"""
    print("\n=== 测试Optimal类 ===")
    
    optimal = Optimal(1, "LED1")
    optimal.set_euclidean_distance(5.0)
    optimal.set_hpwl(10.5)
    
    print(f"Optimal: {optimal}")
    print(f"ID: {optimal.get_id()}")
    print(f"名称: {optimal.get_name()}")
    print(f"欧几里得距离: {optimal.get_euclidean_distance()}")
    print(f"HPWL: {optimal.get_hpwl()}")

def test_node():
    """测试Node类"""
    print("\n=== 测试Node类 ===")
    
    # 创建节点
    node = Node()
    node.set_id(0)
    node.set_name("LED1")
    node.set_size((3.35, 1.85))
    node.set_pos((156.31, 50.79))
    node.set_orientation(0.0)
    node.set_layer(0)
    node.set_is_placed(True)
    node.set_pins(2)
    node.set_pins_smd(2)
    node.set_pins_th(0)
    node.set_type(4)
    
    print(f"节点: {node}")
    print(f"ID: {node.get_id()}")
    print(f"名称: {node.get_name()}")
    print(f"尺寸: {node.get_size()}")
    print(f"位置: {node.get_pos()}")
    print(f"方向: {node.get_orientation()}")
    print(f"面积: {node.get_area():.2f}")
    print(f"引脚数: {node.get_pin_count()}")
    print(f"已放置: {node.get_is_placed()}")
    
    # 测试从字符串创建
    line = "1,R2,3.7,1.9,151.735,50.815,0,0,0,2,2,0,1"
    node2 = Node()
    if node2.create_from_string_short(line) == 0:
        print(f"从字符串创建的节点: {node2}")

def test_edge():
    """测试Edge类"""
    print("\n=== 测试Edge类 ===")
    
    # 创建边
    edge = Edge()
    edge.set_id(0, 4)
    edge.set_name(0, "C1")
    edge.set_pad_id(0, 1)
    edge.set_pad_name(0, "Pad1")
    edge.set_size(0, (1.075, 0.95))
    edge.set_pos(0, (-0.8625, 0))
    edge.set_is_placed(0, True)
    
    edge.set_id(1, 6)
    edge.set_name(1, "U2")
    edge.set_pad_id(1, 2)
    edge.set_pad_name(1, "Pad3")
    edge.set_size(1, (0.6, 1.2))
    edge.set_pos(1, (-1.25, 0.95))
    edge.set_is_placed(1, True)
    
    edge.set_net_id(1)
    edge.set_net_name("Net-(C1-Pad1)")
    edge.set_power_rail(0)
    
    print(f"边: {edge}")
    print(f"网络ID: {edge.get_net_id()}")
    print(f"网络名称: {edge.get_net_name()}")
    print(f"电源轨: {edge.get_power_rail()}")
    print(f"连接: {edge.get_edge_connectivity()}")
    
    # 测试从字符串创建
    line = "4,0,1,1.075,0.95,-0.8625,0,0,6,2,3,0.6,1.2,-1.25,0.95,0,1,\"Net-(C1-Pad1)\",2,0,0"
    edge2 = Edge()
    if edge2.create_from_string_short(line) == 0:
        print(f"从字符串创建的边: {edge2}")

def test_board():
    """测试Board类"""
    print("\n=== 测试Board类 ===")
    
    board = Board()
    board.set_bb_min_x(100.0)
    board.set_bb_min_y(80.0)
    board.set_bb_max_x(120.0)
    board.set_bb_max_y(100.0)
    board._board_name = "Test Board"
    
    print(f"电路板: {board}")
    print(f"边界框: ({board.get_bb_min_x()}, {board.get_bb_min_y()}) to ({board.get_bb_max_x()}, {board.get_bb_max_y()})")
    print(f"尺寸: {board.get_board_size()}")
    print(f"宽度: {board.get_width()}")
    print(f"高度: {board.get_height()}")
    
    # 测试从文件读取
    board2 = Board()
    line = "bb_min_x,100.00000000"
    board2.process_line(line)
    print(f"处理行后的电路板: {board2}")

def test_graph():
    """测试Graph类"""
    print("\n=== 测试Graph类 ===")
    
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
    
    print(f"图形: {graph}")
    print(f"节点数量: {graph.get_number_of_nodes()}")
    print(f"边数量: {graph.get_number_of_edges()}")
    
    # 测试统计信息
    graph.statistics()
    
    # 测试连接性分析
    connectivity = graph.get_nodes_connectivity_list()
    print(f"节点连接性: {connectivity}")
    
    # 测试邻居节点
    neighbors = graph.get_neighbor_node_ids(0)
    print(f"节点0的邻居: {neighbors}")
    
    # 测试特征向量
    if graph.get_number_of_nodes() > 0:
        fv = graph.get_simplified_feature_vector(0)
        print(f"节点0的简化特征向量: {fv}")
    
    # 测试HPWL计算
    hpwl = graph.calc_hpwl()
    print(f"HPWL: {hpwl:.2f}")

def test_file_parsing():
    """测试文件解析"""
    print("\n=== 测试文件解析 ===")
    
    # 创建测试数据
    test_nodes = [
        "0,LED1,3.35,1.85,156.31,50.79,0,0,0,2,2,0,4",
        "1,R2,3.7,1.9,151.735,50.815,0,0,0,2,2,0,1",
        "2,R1,3.7,1.9,146.985,50.065,0,0,0,2,2,0,1"
    ]
    
    test_edges = [
        "4,0,1,1.075,0.95,-0.8625,0,0,6,2,3,0.6,1.2,-1.25,0.95,0,1,\"Net-(C1-Pad1)\",2,0,0",
        "6,0,1,0.6,1.2,-1.25,-0.95,0,6,2,3,0.6,1.2,-1.25,0.95,0,1,\"Net-(C1-Pad1)\",1,0,0"
    ]
    
    # 创建图形
    graph = Graph()
    
    # 解析节点
    for line in test_nodes:
        graph.add_node_from_string_short(line)
    
    # 解析边
    for line in test_edges:
        graph.add_edge_from_string_short(line)
    
    print(f"解析后的图形: {graph}")
    print(f"节点: {[node.get_name() for node in graph.get_nodes()]}")
    print(f"网络: {graph.get_set_net_ids()}")

def main():
    """主测试函数"""
    print("开始测试netlist_graph的Python实现...")
    
    test_utils()
    test_optimal()
    test_node()
    test_edge()
    test_board()
    test_graph()
    test_file_parsing()
    
    print("\n所有测试完成！")

if __name__ == "__main__":
    main() 
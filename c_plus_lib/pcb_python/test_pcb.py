#!/usr/bin/env python3
"""
PCB模块测试脚本
验证PCB模块的各项功能
"""

import os
import sys
import tempfile
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

# 检查是否作为主模块运行
if __name__ == "__main__":
    # 直接导入
    from pcb import PCB, VPtrPCBs, read_pcb_file, write_pcb_file, write_pcb_file_from_individual_files
    from netlist import Graph, Node, Edge, Board
else:
    # 相对导入
from .pcb import PCB, VPtrPCBs, read_pcb_file, write_pcb_file, write_pcb_file_from_individual_files
from .netlist import Graph, Node, Edge, Board

def test_pcb_basic():
    """测试PCB基本功能"""
    print("=== 测试PCB基本功能 ===")
    
    # 创建PCB对象
    pcb = PCB()
    
    # 设置属性
    pcb.set_filename("test.pcb")
    pcb.set_kicad_pcb("test.kicad_pcb")
    pcb.set_parent_kicad_pcb("parent.kicad_pcb")
    pcb.set_id(1)
    
    # 验证属性
    assert pcb.get_filename() == "test.pcb"
    assert pcb.get_kicad_pcb() == "test.kicad_pcb"
    assert pcb.get_parent_kicad_pcb() == "parent.kicad_pcb"
    assert pcb.get_id() == 1
    
    print("✓ PCB基本功能测试通过")

def test_graph_operations():
    """测试图形操作"""
    print("\n=== 测试图形操作 ===")
    
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
    
    # 创建PCB并设置图形
    pcb = PCB()
    pcb.set_graph(graph)
    
    # 验证图形
    g = Graph()
    pcb.get_graph(g)
    assert len(g._V) == 2
    assert len(g._E) == 1
    
    print("✓ 图形操作测试通过")

def test_board_operations():
    """测试电路板操作"""
    print("\n=== 测试电路板操作 ===")
    
    # 创建电路板
    board = Board()
    board.set_bb_min_x(0.0)
    board.set_bb_min_y(0.0)
    board.set_bb_max_x(100.0)
    board.set_bb_max_y(80.0)
    board._board_name = "Test Board"
    
    # 创建PCB并设置电路板
    pcb = PCB()
    pcb.set_board(board)
    
    # 验证电路板
    b = Board()
    pcb.get_board(b)
    assert b.get_bb_min_x() == 0.0
    assert b.get_bb_min_y() == 0.0
    assert b.get_bb_max_x() == 100.0
    assert b.get_bb_max_y() == 80.0
    
    print("✓ 电路板操作测试通过")

def test_file_operations():
    """测试文件操作"""
    print("\n=== 测试文件操作 ===")
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.nodes', delete=False) as f:
        f.write("0,LED1,3.35,1.85,156.31,50.79,0,0,0,2,2,0,4\n")
        f.write("1,R2,3.7,1.9,151.735,50.815,0,0,0,2,2,0,1\n")
        nodes_file = f.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.edges', delete=False) as f:
        f.write("4,0,1,1.075,0.95,-0.8625,0,0,6,2,3,0.6,1.2,-1.25,0.95,0,1,\"Net-(C1-Pad1)\",2,0,0\n")
        edges_file = f.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.board', delete=False) as f:
        f.write("bb_min_x,100.00000000\n")
        f.write("bb_min_y,80.00000000\n")
        f.write("bb_max_x,120.00000000\n")
        f.write("bb_max_y,100.00000000\n")
        f.write("board_name,Test Board\n")
        board_file = f.name
    
    # 创建PCB文件
    pcb_file = tempfile.mktemp(suffix='.pcb')
    
    try:
        # 测试从单独文件创建PCB
        result = write_pcb_file_from_individual_files(
            pcb_file, nodes_file, edges_file, board_file, True
        )
        assert result == 0
        assert os.path.exists(pcb_file)
        
        # 测试读取PCB文件
        pv = VPtrPCBs()
        result = read_pcb_file(pcb_file, pv)
        assert result == 0
        assert len(pv) > 0
        
        print("✓ 文件操作测试通过")
        
    finally:
        # 清理临时文件
        for file in [nodes_file, edges_file, board_file, pcb_file]:
            if os.path.exists(file):
                os.remove(file)

def test_vptr_pcbs():
    """测试VPtrPCBs"""
    print("\n=== 测试VPtrPCBs ===")
    
    pv = VPtrPCBs()
    
    # 添加PCB
    pcb1 = PCB()
    pcb1.set_id(1)
    pcb1.set_filename("test1.pcb")
    
    pcb2 = PCB()
    pcb2.set_id(2)
    pcb2.set_filename("test2.pcb")
    
    pv.append(pcb1)
    pv.append(pcb2)
    
    assert len(pv) == 2
    assert pv[0].get_id() == 1
    assert pv[1].get_id() == 2
    
    print("✓ VPtrPCBs测试通过")

def test_pcb_line_processing():
    """测试PCB行处理"""
    print("\n=== 测试PCB行处理 ===")
    
    pcb = PCB()
    
    # 测试处理各种行
    assert pcb.process_pcb_line(".kicad_pcb=test.kicad_pcb") == 0
    assert pcb.get_kicad_pcb() == "test.kicad_pcb"
    
    assert pcb.process_pcb_line("parent=parent.kicad_pcb") == 0
    assert pcb.get_parent_kicad_pcb() == "parent.kicad_pcb"
    
    assert pcb.process_pcb_line("id=123") == 0
    assert pcb.get_id() == 123
    
    assert pcb.process_pcb_line("generated=1") == 0
    assert pcb.get_generated() == True
    
    print("✓ PCB行处理测试通过")

def main():
    """主测试函数"""
    print("PCB模块测试开始")
    print("=" * 50)
    
    try:
        test_pcb_basic()
        test_graph_operations()
        test_board_operations()
        test_file_operations()
        test_vptr_pcbs()
        test_pcb_line_processing()
        
        print("\n" + "=" * 50)
        print("所有测试通过！✓")
        
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
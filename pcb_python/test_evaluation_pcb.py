#!/usr/bin/env python3
"""
training.pcb文件测试脚本
验证training.pcb文件的读取和分析功能
"""

import os
import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

# 检查是否作为主模块运行
if __name__ == "__main__":
    # 直接导入
    from pcb import PCB, VPtrPCBs, read_pcb_file
    from netlist import Graph, Node, Edge, Board
else:
    # 相对导入
    from .pcb import PCB, VPtrPCBs, read_pcb_file
    from .netlist import Graph, Node, Edge, Board

def test_evaluation_pcb_reading():
    """测试读取training.pcb文件"""
    print("=== 测试training.pcb文件读取 ===")
    
    # 获取training.pcb文件路径
    evaluation_file = Path(__file__).parent / "training.pcb"
    
    if not evaluation_file.exists():
        print(f"❌ 错误：找不到文件 {evaluation_file}")
        return False
    
    print(f"📁 找到training.pcb文件：{evaluation_file}")
    
    # 读取PCB文件
    pv = VPtrPCBs()
    result = read_pcb_file(str(evaluation_file), pv)
    
    if result != 0:
        print(f"❌ 读取文件失败，错误代码：{result}")
        return False
    
    print(f"✅ 成功读取training.pcb文件")
    print(f"📊 包含 {len(pv)} 个PCB对象")
    
    return True

def analyze_evaluation_pcb():
    """分析training.pcb文件的内容"""
    print("\n=== 分析training.pcb文件内容 ===")
    
    evaluation_file = Path(__file__).parent / "training.pcb"
    pv = VPtrPCBs()
    result = read_pcb_file(str(evaluation_file), pv)
    
    if result != 0:
        print(f"❌ 无法读取文件进行分析")
        return
    
    for i, pcb in enumerate(pv):
        print(f"\n🔧 PCB对象 {i+1}:")
        print(f"   文件名: {pcb.get_filename()}")
        print(f"   KiCad PCB: {pcb.get_kicad_pcb()}")
        print(f"   父级PCB: {pcb.get_parent_kicad_pcb()}")
        print(f"   ID: {pcb.get_id()}")
        print(f"   生成状态: {pcb.get_generated()}")
        
        # 获取图形信息
        graph = Graph()
        pcb.get_graph(graph)
        print(f"   节点数量: {len(graph._V)}")
        print(f"   边数量: {len(graph._E)}")
        
        # 获取电路板信息
        board = Board()
        pcb.get_board(board)
        print(f"   电路板边界: ({board.get_bb_min_x():.2f}, {board.get_bb_min_y():.2f}) - ({board.get_bb_max_x():.2f}, {board.get_bb_max_y():.2f})")
        
        # 显示节点详情
        print("   节点详情:")
        for j, node in enumerate(graph._V):
            print(f"     {j}: {node.get_name()} 位置({node.get_pos()[0]:.2f}, {node.get_pos()[1]:.2f}) 尺寸({node.get_size()[0]:.2f}, {node.get_size()[1]:.2f})")
        
        # 显示边详情
        print("   边详情:")
        for j, edge in enumerate(graph._E):
            print(f"     {j}: 连接节点 {edge.get_id(0)} 和 {edge.get_id(1)}, 网络: {edge.get_net_name()}")

def test_pcb_operations():
    """测试PCB操作功能"""
    print("\n=== 测试PCB操作功能 ===")
    
    evaluation_file = Path(__file__).parent / "training.pcb"
    pv = VPtrPCBs()
    result = read_pcb_file(str(evaluation_file), pv)
    
    if result != 0:
        print(f"❌ 无法读取文件进行测试")
        return
    
    if len(pv) == 0:
        print("❌ 没有找到PCB对象")
        return
    
    # 测试第一个PCB对象
    pcb = pv[0]
    
    # 测试属性设置和获取
    print("🔧 测试PCB属性操作:")
    
    # 保存原始值
    original_filename = pcb.get_filename()
    original_id = pcb.get_id()
    
    # 设置新值
    pcb.set_filename("test_modified.pcb")
    pcb.set_id(999)
    
    # 验证设置
    assert pcb.get_filename() == "test_modified.pcb"
    assert pcb.get_id() == 999
    
    # 恢复原始值
    pcb.set_filename(original_filename)
    pcb.set_id(original_id)
    
    print("✅ PCB属性操作测试通过")
    
    # 测试图形操作
    print("🔧 测试图形操作:")
    graph = Graph()
    pcb.get_graph(graph)
    
    # 验证图形完整性
    assert len(graph._V) > 0, "图形应该包含节点"
    assert len(graph._E) > 0, "图形应该包含边"
    
    print(f"✅ 图形操作测试通过 - 节点: {len(graph._V)}, 边: {len(graph._E)}")
    
    # 测试电路板操作
    print("🔧 测试电路板操作:")
    board = Board()
    pcb.get_board(board)
    
    # 验证电路板边界
    assert board.get_bb_min_x() < board.get_bb_max_x(), "电路板边界应该有效"
    assert board.get_bb_min_y() < board.get_bb_max_y(), "电路板边界应该有效"
    
    print("✅ 电路板操作测试通过")

def main():
    """主测试函数"""
    print("training.pcb文件测试开始")
    print("=" * 60)
    
    try:
        # 测试文件读取
        if not test_evaluation_pcb_reading():
            return 1
        
        # 分析文件内容
        analyze_evaluation_pcb()
        
        # 测试PCB操作
        test_pcb_operations()
        
        print("\n" + "=" * 60)
        print("所有测试通过！✅")
        print("training.pcb文件功能正常")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
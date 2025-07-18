#!/usr/bin/env python3
"""
training.pcb文件测试脚本
验证training.pcb文件的读取和分析功能
"""

import os
import sys
from pathlib import Path
from typing import Iterable, cast

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
    evaluation_file = Path(__file__).parent / "evaluation.pcb"
    
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
    
    evaluation_file = Path(__file__).parent / "evaluation.pcb"
    pv = VPtrPCBs()
    result = read_pcb_file(str(evaluation_file), pv)
    
    if result != 0:
        print(f"❌ 无法读取文件进行分析")
        return
    
    for i, pcb in enumerate(cast(Iterable[PCB], pv)):
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
            print(f"     {j}: 连接节点 {edge.get_instance_id(0)} 和 {edge.get_instance_id(1)}, 网络: {edge.get_net_name()}")

def test_pcb_operations():
    """测试PCB操作功能"""
    print("\n=== 测试PCB操作功能 ===")
    
    evaluation_file = Path(__file__).parent / "evaluation.pcb"
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

def test_hpwl():
    """测试HPWL功能"""
    print("\n=== 测试HPWL功能 ===")
    evaluation_file = Path(__file__).parent / "evaluation.pcb"
    pv = VPtrPCBs()
    result = read_pcb_file(str(evaluation_file), pv)
    if result != 0:
        print(f"❌ 无法读取文件进行HPWL测试")
        return
    for i, pcb in enumerate(cast(Iterable[PCB], pv)):
        graph = Graph()
        pcb.get_graph(graph)
        
        print(f"PCB对象 {i+1}:")
        print(f"  原始状态 - 节点总数: {len(graph._V)}, 已放置节点数: {graph.components_placed()}")
        
        # 将所有节点标记为已放置
        for node in graph._V:
            node.set_is_placed(True)
        
        print(f"  标记后 - 已放置节点数: {graph.components_placed()}")
        
        # 计算HPWL
        graph.update_hpwl()
        hpwl = graph.get_hpwl()
        
        print(f"  计算得到的HPWL: {hpwl:.2f}")
        
        # 显示节点位置分布
        if len(graph._V) > 0:
            positions = [node.get_pos() for node in graph._V]
            min_x = min(pos[0] for pos in positions)
            max_x = max(pos[0] for pos in positions)
            min_y = min(pos[1] for pos in positions)
            max_y = max(pos[1] for pos in positions)
            print(f"  位置范围: X({min_x:.2f}, {max_x:.2f}), Y({min_y:.2f}, {max_y:.2f})")

def test_hpwl_per_component():
    """测试每放置一个元件就计算HPWL值"""
    print("\n=== 测试每放置一个元件计算HPWL ===")
    evaluation_file = Path(__file__).parent / "evaluation.pcb"
    pv = VPtrPCBs()
    result = read_pcb_file(str(evaluation_file), pv)
    
    if result != 0:
        print(f"❌ 无法读取文件进行测试")
        return
    
    for i, pcb in enumerate(cast(Iterable[PCB], pv)):
        graph = Graph()
        pcb.get_graph(graph)
        
        print(f"\n🔧 PCB对象 {i+1}:")
        print(f"  节点总数: {len(graph._V)}")
        print(f"  边总数: {len(graph._E)}")
        
        # 重置所有节点为未放置状态
        for node in graph._V:
            node.set_is_placed(False)
        
        print(f"  初始状态 - 已放置节点数: {graph.components_placed()}")
        hpwl_zero = graph.get_hpwl()
        print(f"  初始HPWL: {hpwl_zero:.2f}")
        # 记录HPWL变化
        hpwl_history = []
        placed_components = []
        
        # 逐个放置元件并计算HPWL
        for j, node in enumerate(graph._V):
            node_id = node.get_id()
            node_name = node.get_name()
            node_pos = node.get_pos()
            
            # 放置当前元件
            node.set_is_placed(True)
            
            # 计算当前HPWL (只考虑已放置的元件)
            graph.update_hpwl(do_not_ignore_unplaced=False)
            current_hpwl = graph.get_hpwl()
            
            # 记录信息
            hpwl_history.append(current_hpwl)
            placed_components.append({
                'id': node_id,
                'name': node_name,
                'position': node_pos,
                'hpwl': current_hpwl
            })
            
            # 显示当前状态
            print(f"  📍 放置元件 {j+1}/{len(graph._V)}: {node_name} (ID: {node_id})")
            print(f"     位置: ({node_pos[0]:.2f}, {node_pos[1]:.2f})")
            print(f"     尺寸: ({node.get_size()[0]:.2f}, {node.get_size()[1]:.2f})")
            print(f"     已放置元件数: {graph.components_placed()}")
            print(f"     当前HPWL: {current_hpwl:.2f}")
            
            # 显示HPWL变化趋势
            if j > 0:
                hpwl_change = current_hpwl - hpwl_history[j-1]
                change_symbol = "📈" if hpwl_change > 0 else "📉" if hpwl_change < 0 else "➡️"
                print(f"     HPWL变化: {change_symbol} {hpwl_change:+.2f}")
            
            print()
        
        # 显示最终统计
        print(f"📊 最终统计:")
        print(f"  总元件数: {len(graph._V)}")
        print(f"  已放置元件数: {graph.components_placed()}")
        print(f"  最终HPWL: {hpwl_history[-1]:.2f}")
        
        # 显示HPWL变化趋势
        if len(hpwl_history) > 1:
            print(f"  HPWL变化范围: {min(hpwl_history):.2f} - {max(hpwl_history):.2f}")
            print(f"  HPWL变化幅度: {max(hpwl_history) - min(hpwl_history):.2f}")
        
        # 显示位置分布
        if len(graph._V) > 0:
            positions = [node.get_pos() for node in graph._V]
            min_x = min(pos[0] for pos in positions)
            max_x = max(pos[0] for pos in positions)
            min_y = min(pos[1] for pos in positions)
            max_y = max(pos[1] for pos in positions)
            print(f"  位置分布: X({min_x:.2f}, {max_x:.2f}), Y({min_y:.2f}, {max_y:.2f})")
        
        # 可选：显示每个元件的HPWL贡献
        print(f"\n📋 各元件HPWL贡献详情:")
        for j, component in enumerate(placed_components):
            print(f"  {j+1:2d}. {component['name']:15s} (ID: {component['id']:3d}) - HPWL: {component['hpwl']:8.2f}")

def main():
    """主测试函数"""
    print("evaluation.pcb文件测试开始")
    print("=" * 60)
    try:
        # 测试文件读取
        if not test_evaluation_pcb_reading():
            return 1
        # 分析文件内容
        analyze_evaluation_pcb()
        # 测试PCB操作
        test_pcb_operations()
        # 测试HPWL
        test_hpwl()
        # 测试每放置一个元件计算HPWL
        test_hpwl_per_component()
        print("\n" + "=" * 60)
        print("所有测试通过！✅")
        print("evaluation.pcb文件功能正常")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
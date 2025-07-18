#!/usr/bin/env python3
"""
测试边解析功能
"""

import os
import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

# 检查是否作为主模块运行
if __name__ == "__main__":
    from pcb import PCB, VPtrPCBs, read_pcb_file
    from netlist import Graph, Node, Edge, Board
else:
    from .pcb import PCB, VPtrPCBs, read_pcb_file
    from .netlist import Graph, Node, Edge, Board

def test_edge_parsing():
    """测试边解析功能"""
    print("=== 测试边解析功能 ===")
    
    # 测试evaluation.pcb文件
    evaluation_file = Path(__file__).parent / "evaluation.pcb"
    
    if not evaluation_file.exists():
        print(f"❌ 错误：找不到文件 {evaluation_file}")
        return False
    
    print(f"📁 找到evaluation.pcb文件：{evaluation_file}")
    
    # 读取PCB文件
    pv = VPtrPCBs()
    result = read_pcb_file(str(evaluation_file), pv)
    
    if result != 0:
        print(f"❌ 读取文件失败，错误代码：{result}")
        return False
    
    print(f"✅ 成功读取evaluation.pcb文件")
    print(f"📊 包含 {len(pv)} 个PCB对象")
    
    # 检查每个PCB对象的边
    for i, pcb in enumerate(pv):
        print(f"\n🔧 PCB对象 {i+1}:")
        
        # 获取图形信息
        graph = Graph()
        pcb.get_graph(graph)
        
        print(f"   节点数量: {len(graph._V)}")
        print(f"   边数量: {len(graph._E)}")
        
        if len(graph._E) == 0:
            print("   ⚠️  警告：没有找到边")
            continue
        
        # 显示前几条边的详细信息
        for j, edge in enumerate(graph._E[:3]):  # 只显示前3条边
            print(f"   边 {j}:")
            print(f"     A节点: {edge.get_instance_id(0)} (ID: {edge._a_id}, Pad: {edge._a_pad_name})")
            print(f"     B节点: {edge.get_instance_id(1)} (ID: {edge._b_id}, Pad: {edge._b_pad_name})")
            print(f"     网络: {edge.get_net_name()} (ID: {edge.get_net_id()})")
            print(f"     电源轨: {edge.get_power_rail()}")
            print(f"     A位置: ({edge._a_pos_x:.2f}, {edge._a_pos_y:.2f})")
            print(f"     B位置: ({edge._b_pos_x:.2f}, {edge._b_pos_y:.2f})")
    
    return True

def test_single_edge_parsing():
    """测试单条边的解析"""
    print("\n=== 测试单条边的解析 ===")
    
    # 添加当前目录到路径
    sys.path.insert(0, str(Path(__file__).parent))
    
    # 检查是否作为主模块运行
    if __name__ == "__main__":
        from netlist import Edge
    else:
        from .netlist import Edge
    
    # 测试evaluation.pcb中的第一条边数据
    test_line = "0,0,2,0.90000000,0.95000000,0.77500000,0.00000000,0,1,1,1,0.90000000,0.95000000,-0.77500000,0.00000000,0,1,GND,1"
    
    print(f"测试边数据: {test_line}")
    
    edge = Edge()
    result = edge.create_from_string_long(test_line)
    
    if result == 0:
        print("✅ 边解析成功")
        print(f"   A节点ID: {edge._a_id}")
        print(f"   A节点Pad ID: {edge._a_pad_id}")
        print(f"   A节点Pad名称: {edge._a_pad_name}")
        print(f"   A节点位置: ({edge._a_pos_x:.2f}, {edge._a_pos_y:.2f})")
        print(f"   B节点ID: {edge._b_id}")
        print(f"   B节点Pad ID: {edge._b_pad_id}")
        print(f"   B节点Pad名称: {edge._b_pad_name}")
        print(f"   B节点位置: ({edge._b_pos_x:.2f}, {edge._b_pos_y:.2f})")
        print(f"   网络ID: {edge._net_id}")
        print(f"   网络名称: {edge._net_name}")
        print(f"   电源轨: {edge._power_rail}")
    else:
        print("❌ 边解析失败")
        return False
    
    return True

def main():
    """主测试函数"""
    print("边解析功能测试")
    print("=" * 60)
    
    try:
        # 测试单条边解析
        if not test_single_edge_parsing():
            return 1
        
        # 测试完整文件解析
        if not test_edge_parsing():
            return 1
        
        print("\n" + "=" * 60)
        print("所有测试通过！✅")
        print("边解析功能正常")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
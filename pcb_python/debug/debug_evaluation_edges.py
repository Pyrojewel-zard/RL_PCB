#!/usr/bin/env python3
"""
调试evaluation.pcb文件中的边数据格式
"""

import os
import sys
from pathlib import Path

def analyze_evaluation_edges():
    """分析evaluation.pcb文件中的边数据"""
    print("=== 分析evaluation.pcb文件中的边数据 ===")
    
    evaluation_file = Path(__file__).parent / "evaluation.pcb"
    
    if not evaluation_file.exists():
        print(f"❌ 错误：找不到文件 {evaluation_file}")
        return
    
    print(f"📁 找到evaluation.pcb文件：{evaluation_file}")
    
    # 读取文件并分析边数据
    with open(evaluation_file, 'r') as f:
        lines = f.readlines()
    
    edge_lines = []
    in_edges_section = False
    pcb_count = 0
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        if line == "pcb begin":
            pcb_count += 1
            print(f"\n🔧 PCB对象 {pcb_count}:")
        
        elif line == "edges begin":
            in_edges_section = True
            print(f"   开始读取边数据...")
            continue
        
        elif line == "edges end":
            in_edges_section = False
            print(f"   结束读取边数据，共 {len(edge_lines)} 条边")
            edge_lines = []
            continue
        
        elif in_edges_section and line:
            # 分析边数据格式
            fields = line.split(',')
            print(f"   边数据: {len(fields)} 个字段")
            print(f"   原始行: {line}")
            
            # 尝试解析边数据
            try:
                if len(fields) >= 20:
                    a_id = int(fields[0])
                    a_name = fields[1]
                    a_pad_id = int(fields[2])
                    a_size_x = float(fields[3])
                    a_size_y = float(fields[4])
                    a_pos_x = float(fields[5])
                    a_pos_y = float(fields[6])
                    a_is_placed = int(fields[7]) == 1
                    
                    b_id = int(fields[8])
                    b_name = fields[9]
                    b_pad_id = int(fields[10])
                    b_size_x = float(fields[11])
                    b_size_y = float(fields[12])
                    b_pos_x = float(fields[13])
                    b_pos_y = float(fields[14])
                    b_is_placed = int(fields[15]) == 1
                    
                    net_id = int(fields[16])
                    net_name = fields[17].strip('"') if len(fields) > 17 else ""
                    power_rail = int(fields[18]) if len(fields) > 18 else 0
                    
                    print(f"   ✅ 解析成功:")
                    print(f"      节点A: {a_name}({a_id}) 位置({a_pos_x:.2f}, {a_pos_y:.2f}) 尺寸({a_size_x:.2f}, {a_size_y:.2f})")
                    print(f"      节点B: {b_name}({b_id}) 位置({b_pos_x:.2f}, {b_pos_y:.2f}) 尺寸({b_size_x:.2f}, {b_size_y:.2f})")
                    print(f"      网络: {net_name}({net_id}) 电源轨: {power_rail}")
                else:
                    print(f"   ❌ 字段数量不足: {len(fields)} < 20")
                    
            except Exception as e:
                print(f"   ❌ 解析失败: {e}")
            
            edge_lines.append(line)

def test_edge_parsing():
    """测试边解析功能"""
    print("\n=== 测试边解析功能 ===")
    
    # 添加当前目录到路径
    sys.path.insert(0, str(Path(__file__).parent))
    
    # 检查是否作为主模块运行
    if __name__ == "__main__":
        from pcb import PCB, VPtrPCBs, read_pcb_file
        from netlist import Graph, Node, Edge, Board
    else:
        from .pcb import PCB, VPtrPCBs, read_pcb_file
        from .netlist import Graph, Node, Edge, Board
    
    evaluation_file = Path(__file__).parent / "evaluation.pcb"
    pv = VPtrPCBs()
    result = read_pcb_file(str(evaluation_file), pv)
    
    if result != 0:
        print(f"❌ 无法读取文件")
        return
    
    for i, pcb in enumerate(pv):
        print(f"\n🔧 PCB对象 {i+1}:")
        
        # 获取图形信息
        graph = Graph()
        pcb.get_graph(graph)
        
        print(f"   节点数量: {len(graph._V)}")
        print(f"   边数量: {len(graph._E)}")
        
        # 检查边的详细信息
        for j, edge in enumerate(graph._E):
            print(f"   边 {j}: {edge}")
            print(f"      A节点: {edge.get_instance_id(0)} ({edge.get_pad_name(0)})")
            print(f"      B节点: {edge.get_instance_id(1)} ({edge.get_pad_name(1)})")
            print(f"      网络: {edge.get_net_name()} (ID: {edge.get_net_id()})")
            print(f"      电源轨: {edge.get_power_rail()}")

def main():
    """主函数"""
    print("evaluation.pcb边数据调试")
    print("=" * 60)
    
    try:
        # 分析边数据格式
        analyze_evaluation_edges()
        
        # 测试边解析功能
        test_edge_parsing()
        
        print("\n" + "=" * 60)
        print("调试完成")
        
    except Exception as e:
        print(f"\n❌ 调试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
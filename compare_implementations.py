#!/usr/bin/env python3
"""
对比测试脚本
比较原始C++实现的PCB库和Python实现的结果
"""

import os
import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

# 检查是否作为主模块运行
if __name__ == "__main__":
    # Python实现
    from pcb import PCB, VPtrPCBs, read_pcb_file
    from netlist import Graph, Node, Edge, Board
    
    # 尝试导入原始C++实现
    try:
        from pcb import pcb as originpcb
        ORIGINAL_AVAILABLE = True
        print("✅ 成功导入原始C++ PCB库")
    except ImportError as e:
        ORIGINAL_AVAILABLE = False
        print(f"❌ 无法导入原始C++ PCB库: {e}")
        print("请确保venv环境已激活且原始库已正确安装")
else:
    # 相对导入
    from .pcb import PCB, VPtrPCBs, read_pcb_file
    from .netlist import Graph, Node, Edge, Board
    try:
        from .pcb import pcb as originpcb
        ORIGINAL_AVAILABLE = True
    except ImportError:
        ORIGINAL_AVAILABLE = False

def parse_with_python_implementation():
    """使用Python实现解析evaluation.pcb"""
    print("\n=== Python实现解析结果 ===")
    
    evaluation_file = Path(__file__).parent / "evaluation.pcb"
    if not evaluation_file.exists():
        print(f"❌ 找不到文件: {evaluation_file}")
        return None
    
    pv = VPtrPCBs()
    result = read_pcb_file(str(evaluation_file), pv)
    
    if result != 0:
        print(f"❌ Python实现解析失败，错误代码: {result}")
        return None
    
    print(f"✅ Python实现成功解析，包含 {len(pv)} 个PCB对象")
    
    python_results = []
    for i, pcb in enumerate(pv):
        graph = Graph()
        pcb.get_graph(graph)
        
        # 将所有节点标记为已放置以计算HPWL
        for node in graph._V:
            node.set_is_placed(True)
        
        graph.update_hpwl()
        hpwl = graph.get_hpwl()
        
        result_data = {
            'pcb_id': i,
            'filename': pcb.get_filename(),
            'kicad_pcb': pcb.get_kicad_pcb(),
            'node_count': len(graph._V),
            'edge_count': len(graph._E),
            'hpwl': hpwl,
            'nodes': [(node.get_id(), node.get_name(), node.get_pos(), node.get_size()) for node in graph._V],
            'edges': [(edge.get_instance_id(0), edge.get_instance_id(1), edge.get_net_name(), edge.get_net_id()) for edge in graph._E]
        }
        python_results.append(result_data)
        
        print(f"  PCB {i+1}: 节点={len(graph._V)}, 边={len(graph._E)}, HPWL={hpwl:.2f}")
    
    return python_results

def parse_with_original_implementation():
    """使用原始C++实现解析evaluation.pcb"""
    if not ORIGINAL_AVAILABLE:
        print("❌ 原始C++库不可用，跳过对比")
        return None
    
    print("\n=== 原始C++实现解析结果 ===")
    
    evaluation_file = Path(__file__).parent / "evaluation.pcb"
    if not evaluation_file.exists():
        print(f"❌ 找不到文件: {evaluation_file}")
        return None
    
    try:
        # 使用原始C++库解析
        original_pv = originpcb.VPtrPCBs()
        result = originpcb.read_pcb_file(str(evaluation_file), original_pv)
        
        if result != 0:
            print(f"❌ 原始C++实现解析失败，错误代码: {result}")
            return None
        
        print(f"✅ 原始C++实现成功解析，包含 {len(original_pv)} 个PCB对象")
        
        original_results = []
        for i in range(len(original_pv)):
            pcb = original_pv[i]
            graph = pcb.get_graph()
            
            # 获取HPWL
            hpwl = graph.get_hpwl()
            
            result_data = {
                'pcb_id': i,
                'filename': pcb.get_filename(),
                'kicad_pcb': pcb.get_kicad_pcb(),
                'node_count': graph.get_number_of_nodes(),
                'edge_count': graph.get_number_of_edges(),
                'hpwl': hpwl
            }
            original_results.append(result_data)
            
            print(f"  PCB {i+1}: 节点={graph.get_number_of_nodes()}, 边={graph.get_number_of_edges()}, HPWL={hpwl:.2f}")
        
        return original_results
        
    except Exception as e:
        print(f"❌ 原始C++实现解析出错: {e}")
        return None

def compare_results(python_results, original_results):
    """对比两个实现的结果"""
    print("\n=== 结果对比 ===")
    
    if python_results is None or original_results is None:
        print("❌ 无法进行对比，缺少解析结果")
        return
    
    if len(python_results) != len(original_results):
        print(f"❌ PCB对象数量不匹配: Python={len(python_results)}, 原始={len(original_results)}")
        return
    
    print(f"✅ PCB对象数量匹配: {len(python_results)}")
    
    for i in range(len(python_results)):
        py_data = python_results[i]
        orig_data = original_results[i]
        
        print(f"\nPCB对象 {i+1} 对比:")
        
        # 基本信息对比
        print(f"  文件名: Python='{py_data['filename']}' vs 原始='{orig_data['filename']}'")
        print(f"  KiCad PCB: Python='{py_data['kicad_pcb']}' vs 原始='{orig_data['kicad_pcb']}'")
        
        # 节点和边数量对比
        node_match = py_data['node_count'] == orig_data['node_count']
        edge_match = py_data['edge_count'] == orig_data['edge_count']
        
        print(f"  节点数: Python={py_data['node_count']} vs 原始={orig_data['node_count']} {'✅' if node_match else '❌'}")
        print(f"  边数: Python={py_data['edge_count']} vs 原始={orig_data['edge_count']} {'✅' if edge_match else '❌'}")
        
        # HPWL对比
        hpwl_diff = abs(py_data['hpwl'] - orig_data['hpwl'])
        hpwl_match = hpwl_diff < 0.01  # 允许0.01的误差
        
        print(f"  HPWL: Python={py_data['hpwl']:.2f} vs 原始={orig_data['hpwl']:.2f} {'✅' if hpwl_match else '❌'} (差异={hpwl_diff:.4f})")
        
        if not (node_match and edge_match and hpwl_match):
            print("  ⚠️  发现差异！")
        else:
            print("  ✅ 完全匹配")

def main():
    """主测试函数"""
    print("PCB实现对比测试")
    print("=" * 60)
    
    try:
        # 使用Python实现解析
        python_results = parse_with_python_implementation()
        
        # 使用原始C++实现解析
        original_results = parse_with_original_implementation()
        
        # 对比结果
        compare_results(python_results, original_results)
        
        print("\n" + "=" * 60)
        print("对比测试完成")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
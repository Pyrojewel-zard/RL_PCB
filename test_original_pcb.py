#!/usr/bin/env python3
"""
原始C++ PCB库测试脚本
验证C++ PCB库的解析和功能
"""

import sys
import os
from pathlib import Path

try:
    # 尝试从pcb模块导入pcb对象，该对象是C++库的Python绑定
    from pcb import pcb as original_pcb_lib
    # 从graph模块导入相关类型
    from graph import graph, board, node, edge
    print("✅ 成功导入原始C++ PCB库")
except ImportError as e:
    print(f"❌ 无法导入原始C++ PCB库: {e}")
    print("请确保已激活venv环境并已正确编译C++库。")
    sys.exit(1)

def test_original_pcb_reading():
    """测试读取evaluation.pcb文件"""
    print("=== 测试原始C++库读取evaluation.pcb文件 ===")
    
    # 获取evaluation.pcb文件路径
    evaluation_file = Path(__file__).parent / "evaluation.pcb"
    
    if not evaluation_file.exists():
        print(f"❌ 错误：找不到文件 {evaluation_file}")
        return False
    
    print(f"📁 找到evaluation.pcb文件：{evaluation_file}")
    
    # 读取PCB文件
    pv_objects = original_pcb_lib.vptr_pcbs()
    result = original_pcb_lib.read_pcb_file(str(evaluation_file), pv_objects)
    
    # 检查返回类型，确保它是列表并且至少包含一个元素
    if isinstance(result, list) and len(result) > 0:
        status_code = result[0]
        if status_code == 0:
            print(f"✅ 原始C++库解析成功，状态码: {status_code}")
            print(f"📊 包含 {len(pv_objects)} 个PCB对象")
            return True
        else:
            print(f"❌ 原始C++库解析失败，状态码: {status_code}，文件: {result[1] if len(result) > 1 else 'N/A'}")
            return False
    else:
        print(f"❌ 原始C++库解析返回非预期类型或空结果: {result}")
        return False

def analyze_original_pcb():
    """分析原始C++库解析的evaluation.pcb文件内容"""
    print("\n=== 分析原始C++库解析结果 ===")
    
    evaluation_file = Path(__file__).parent / "evaluation.pcb"
    pv_objects = original_pcb_lib.vptr_pcbs()
    result = original_pcb_lib.read_pcb_file(str(evaluation_file), pv_objects)
    
    if not isinstance(result, list) or len(result) == 0 or result[0] != 0:
        print(f"❌ 无法读取文件进行分析")
        return
    
    for i, pcb_obj in enumerate(pv_objects):
        print(f"\n🔧 PCB对象 {i+1}:")
        print(f"   文件名: {pcb_obj.get_filename()}")
        print(f"   KiCad PCB: {pcb_obj.get_kicad_pcb()}")
        print(f"   父级PCB: {pcb_obj.get_parent_kicad_pcb()}")
        print(f"   ID: {pcb_obj.get_id()}")
        print(f"   生成状态: {pcb_obj.get_generated()}")
        
        # 获取图形信息
        graph = pcb_obj.get_graph()
        if graph and hasattr(graph, 'get_nodes'):
            nodes = graph.get_nodes()
            print(f"   节点数量: {len(nodes)}")
            
            # 显示前3个节点详情
            print("   前3个节点详情:")
            for j, node in enumerate(nodes[:3]):
                pos = node.get_pos()
                size = node.get_size()
                print(f"     {j}: {node.get_name()} 位置({pos[0]:.2f}, {pos[1]:.2f}) 尺寸({size[0]:.2f}, {size[1]:.2f})")
        
        # 获取边信息
        if graph and hasattr(graph, 'get_edges'):
            edges = graph.get_edges()
            print(f"   边数量: {len(edges)}")
            
            # 显示前3个边详情
            print("   前3个边详情:")
            for j, edge in enumerate(edges[:3]):
                print(f"     {j}: 连接节点 {edge.get_instance_id(0)} 和 {edge.get_instance_id(1)}, 网络: {edge.get_net_name()}")
        
        # 获取电路板信息
        board = pcb_obj.get_board()
        if board:
            print(f"   电路板边界: ({board.get_bb_min_x():.2f}, {board.get_bb_min_y():.2f}) - ({board.get_bb_max_x():.2f}, {board.get_bb_max_y():.2f})")

def test_original_pcb_operations():
    """测试原始C++库PCB操作功能"""
    print("\n=== 测试原始C++库PCB操作功能 ===")
    
    evaluation_file = Path(__file__).parent / "evaluation.pcb"
    pv_objects = original_pcb_lib.vptr_pcbs()
    result = original_pcb_lib.read_pcb_file(str(evaluation_file), pv_objects)
    
    if not isinstance(result, list) or len(result) == 0 or result[0] != 0:
        print(f"❌ 无法读取文件进行测试")
        return
    
    if len(pv_objects) == 0:
        print("❌ 没有找到PCB对象")
        return
    
    # 测试第一个PCB对象
    pcb_obj = pv_objects[0]
    
    # 测试属性获取
    print("🔧 测试PCB属性获取:")
    
    # 获取并验证属性
    filename = pcb_obj.get_filename()
    kicad_pcb = pcb_obj.get_kicad_pcb()
    parent_kicad_pcb = pcb_obj.get_parent_kicad_pcb()
    pcb_id = pcb_obj.get_id()
    generated = pcb_obj.get_generated()
    
    print(f"  文件名: {filename}")
    print(f"  KiCad PCB: {kicad_pcb}")
    print(f"  父级KiCad PCB: {parent_kicad_pcb}")
    print(f"  ID: {pcb_id}")
    print(f"  生成状态: {generated}")
    
    # 验证属性不为空（基本验证）
    assert filename is not None, "文件名应该不为空"
    assert kicad_pcb is not None, "KiCad PCB应该不为空"
    assert pcb_id is not None, "ID应该不为空"
    
    print("✅ PCB属性获取测试通过")
    
    # 测试图形操作
    print("🔧 测试图形操作:")
    graph = pcb_obj.get_graph()
    
    if graph and hasattr(graph, 'get_nodes') and hasattr(graph, 'get_edges'):
        nodes = graph.get_nodes()
        edges = graph.get_edges()
        
        # 验证图形完整性
        assert len(nodes) > 0, "图形应该包含节点"
        assert len(edges) > 0, "图形应该包含边"
        
        print(f"✅ 图形操作测试通过 - 节点: {len(nodes)}, 边: {len(edges)}")
    else:
        print("❌ 图形操作测试失败 - 无法获取节点或边")
    
    # 测试电路板操作
    print("🔧 测试电路板操作:")
    board = pcb_obj.get_board()
    
    if board:
        # 验证电路板边界
        assert board.get_bb_min_x() < board.get_bb_max_x(), "电路板边界应该有效"
        assert board.get_bb_min_y() < board.get_bb_max_y(), "电路板边界应该有效"
        
        print("✅ 电路板操作测试通过")
    else:
        print("❌ 电路板操作测试失败 - 无法获取电路板对象")

def test_original_hpwl():
    """测试原始C++库HPWL功能"""
    print("\n=== 测试原始C++库HPWL功能 ===")
    
    evaluation_file = Path(__file__).parent / "evaluation.pcb"
    pv_objects = original_pcb_lib.vptr_pcbs()
    result = original_pcb_lib.read_pcb_file(str(evaluation_file), pv_objects)
    
    if not isinstance(result, list) or len(result) == 0 or result[0] != 0:
        print(f"❌ 无法读取文件进行HPWL测试")
        return
    
    for i, pcb_obj in enumerate(pv_objects):
        graph = pcb_obj.get_graph()
        
        if not graph or not hasattr(graph, 'get_nodes'):
            print(f"PCB对象 {i+1}: 无法获取图形对象")
            continue
        
        nodes = graph.get_nodes()
        print(f"PCB对象 {i+1}:")
        print(f"  节点总数: {len(nodes)}")
        
        # 计算原始已放置节点数
        original_placed_count = 0
        for node in nodes:
            if node.get_isPlaced():
                original_placed_count += 1
        
        print(f"  原始已放置节点数: {original_placed_count}")
        
        # 逐个放置节点并计算HPWL
        print("🔧 逐个放置节点并计算HPWL...")
        for i, node in enumerate(nodes):
            node_id = node.get_id()
            node_name = node.get_name()
            
            # 放置当前节点
            if hasattr(graph, 'place_confirm'):
                # 使用图形的place_confirm方法
                result = graph.place_confirm(node_id)
                if result != 0:
                    print(f"   警告: 节点 {node_name} (ID: {node_id}) 放置确认失败")
                    continue
            elif hasattr(node, 'set_is_placed'):
                node.set_is_placed(True)
            elif hasattr(node, 'set_isPlaced'):
                # C++的set_isPlaced()方法不接受参数，直接调用即可
                node.set_isPlaced()
            else:
                print(f"   警告: 节点 {node_name} 没有可用的放置方法")
                continue
            
            # 计算当前已放置节点数
            current_placed_count = sum(1 for n in nodes if n.get_isPlaced())
            
            # 计算当前HPWL
            current_hpwl = 0.0
            if hasattr(graph, 'update_hpwl'):
                graph.update_hpwl(do_not_ignore_unplaced=True)
                current_hpwl = graph.get_hpwl()
            elif hasattr(graph, 'calc_hpwl'):
                current_hpwl = graph.calc_hpwl(do_not_ignore_unplaced=True)
            elif hasattr(graph, 'get_hpwl'):
                current_hpwl = graph.get_hpwl()
            
            # 显示当前状态
            pos = node.get_pos()
            print(f"   节点{i+1}: {node_name} (ID: {node_id}) 位置({pos[0]:.2f}, {pos[1]:.2f})")
            print(f"     已放置节点: {current_placed_count}/{len(nodes)}")
            print(f"     当前HPWL: {current_hpwl:.2f}")
            print()
        
        # 最终统计
        final_placed_count = sum(1 for node in nodes if node.get_isPlaced())
        print(f"  最终已放置节点数: {final_placed_count}/{len(nodes)}")
        
        # 计算最终HPWL
        final_hpwl = 0.0
        if hasattr(graph, 'update_hpwl'):
            graph.update_hpwl(do_not_ignore_unplaced=True)
            final_hpwl = graph.get_hpwl()
        elif hasattr(graph, 'calc_hpwl'):
            final_hpwl = graph.calc_hpwl(do_not_ignore_unplaced=True)
        elif hasattr(graph, 'get_hpwl'):
            final_hpwl = graph.get_hpwl()
        
        print(f"  最终HPWL: {final_hpwl:.2f}")
        
        # 显示节点位置分布
        if len(nodes) > 0:
            positions = [node.get_pos() for node in nodes]
            min_x = min(pos[0] for pos in positions)
            max_x = max(pos[0] for pos in positions)
            min_y = min(pos[1] for pos in positions)
            max_y = max(pos[1] for pos in positions)
            print(f"  位置范围: X({min_x:.2f}, {max_x:.2f}), Y({min_y:.2f}, {max_y:.2f})")
            
            # 显示所有节点的放置状态
            print("  所有节点放置状态:")
            for j, node in enumerate(nodes):
                pos = node.get_pos()
                placed = node.get_isPlaced()
                print(f"    节点{j+1}: {node.get_name()} 位置({pos[0]:.2f}, {pos[1]:.2f}) 已放置: {placed}")
            
            # 显示放置统计
            placed_count = sum(1 for node in nodes if node.get_isPlaced())
            total_count = len(nodes)
            print(f"  放置统计: {placed_count}/{total_count} ({placed_count/total_count*100:.1f}%)")

def main():
    """主测试函数"""
    print("原始C++ PCB库测试开始")
    print("=" * 60)
    try:
        # 测试文件读取
        if not test_original_pcb_reading():
            return 1
        # 分析文件内容
        analyze_original_pcb()
        # 测试PCB操作
        test_original_pcb_operations()
        # 测试HPWL
        test_original_hpwl()
        print("\n" + "=" * 60)
        print("所有测试通过！✅")
        print("原始C++ PCB库功能正常")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
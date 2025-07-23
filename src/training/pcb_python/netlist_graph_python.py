"""
Netlist Graph Python模块 - 重新导出
保持与原有API的兼容性，重新导出pcb_python中的netlist_graph模块
"""

from netlist import Graph, Node, Edge, Board, Optimal, Utils

# 重新导出所有类
__all__ = [
    'Graph', 'Node', 'Edge', 'Board', 'Optimal', 'Utils'
]

def build_info():
    """打印库的构建信息"""
    print("Netlist Graph Python Library v1.0.0")
    print("纯Python实现，无需C++依赖")
    print("支持网络图分析、节点管理、边连接等功能")

def get_library_version():
    """返回库版本信息"""
    return "1.0.0" 
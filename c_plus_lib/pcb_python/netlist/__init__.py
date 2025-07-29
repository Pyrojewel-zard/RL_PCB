"""
Netlist Graph Library - 纯Python实现
用于处理电路网络图，管理节点和边的连接关系
"""

from .graph import Graph
from .node import Node
from .edge import Edge
from .board import Board
from .optimal import Optimal
from .utils import Utils

__version__ = "1.0.0"
__author__ = "Python Netlist Graph Library"

def build_info():
    """打印库的构建信息"""
    print(f"Netlist Graph Python Library v{__version__}")
    print("纯Python实现，无需C++依赖")
    print("支持网络图分析、节点管理、边连接等功能")

def get_library_version():
    """返回库版本信息"""
    return __version__

# 导出主要类
__all__ = [
    'Graph', 'Node', 'Edge', 'Board', 'Optimal', 'Utils',
    'build_info', 'get_library_version'
] 
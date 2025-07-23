"""
PCB库 - 纯Python实现
用于处理PCB文件格式和电路网络图分析
"""

from .pcb import PCB
from .graph import Graph
from .board import Board
from .node import Node
from .edge import Edge
from .optimal import Optimal

__version__ = "1.0.0"
__author__ = "Python PCB Library"

def build_info():
    """打印库的构建信息"""
    print(f"PCB Python Library v{__version__}")
    print("纯Python实现，无需C++依赖")
    print("支持PCB文件解析、网络图分析、电路板布局等功能")

def get_library_version():
    """返回库版本信息"""
    return __version__

# 导出主要类
__all__ = [
    'PCB', 'Graph', 'Board', 'Node', 'Edge', 'Optimal',
    'build_info', 'get_library_version'
] 
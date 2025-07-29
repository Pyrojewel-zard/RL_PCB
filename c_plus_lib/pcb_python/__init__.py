"""
PCB Python Library - 纯Python实现
对应C++的pcb库，提供PCB文件读写和图形管理功能
"""

from .pcb import (
    PCB, VPtrPCBs, read_pcb_file, write_pcb_file,
    write_pcb_file_from_individual_files, append_pcb_file_from_individual_files,
    write_pcb_file_from_individual_files_and_optimals, append_pcb_file_from_individual_files_and_optimals,
    write_pcb_file_from_graph_and_board, append_pcb_file_from_graph_and_board,
    write_pcb_file_from_pcb, append_pcb_file_from_pcb,
    write_pcb_file_from_graph_and_board_with_params, append_pcb_file_from_graph_and_board_with_params,
    check_for_file_existance
)

from .netlist import Graph, Node, Edge, Board, Optimal, Utils

__version__ = "0.0.12"
__author__ = "PCB Python Library"

def build_info():
    """打印库的构建信息"""
    print(f"PCB Python Library v{__version__}")
    print("纯Python实现，无需C++依赖")
    print("支持PCB文件读写、图形管理等功能")

def get_library_version():
    """返回库版本信息"""
    return __version__

# 导出主要类和函数
__all__ = [
    'PCB', 'VPtrPCBs', 'read_pcb_file', 'write_pcb_file',
    'write_pcb_file_from_individual_files', 'append_pcb_file_from_individual_files',
    'write_pcb_file_from_individual_files_and_optimals', 'append_pcb_file_from_individual_files_and_optimals',
    'write_pcb_file_from_graph_and_board', 'append_pcb_file_from_graph_and_board',
    'write_pcb_file_from_pcb', 'append_pcb_file_from_pcb',
    'write_pcb_file_from_graph_and_board_with_params', 'append_pcb_file_from_graph_and_board_with_params',
    'check_for_file_existance',
    'Graph', 'Node', 'Edge', 'Board', 'Optimal', 'Utils',
    'get_library_version', 'get_build_time', 'get_cpp_standard',
    'build_info', 'build_info_as_string', 'get_library_version_string',
    'dependency_info', 'dependency_info_as_string'
] 
"""
PCB模块 - 纯Python实现
对应C++的pcb.hpp和pcb.cpp，提供PCB文件读写和图形管理功能
"""

import os
import time
from typing import List, Optional, Tuple
from netlist.graph import Graph
from netlist.board import Board

class PCB:
    """PCB类，表示一个PCB文件，包含图形和电路板信息"""
    
    def __init__(self):
        self._file = ""
        self._kicad_pcb = ""
        self._parent_kicad_pcb = ""
        self._generated = False
        self._id = -1
        self._graph = Graph()
        self._board = Board()
    
    def set_kicad_pcb(self, kicad_pcb: str) -> None:
        """设置KiCad PCB文件名"""
        self._kicad_pcb = kicad_pcb
    
    def get_kicad_pcb(self) -> str:
        """获取KiCad PCB文件名"""
        return self._kicad_pcb
    
    def get_kicad_pcb2(self) -> str:
        """获取KiCad PCB文件名（返回副本）"""
        return self._kicad_pcb
    
    def set_parent_kicad_pcb(self, parent_kicad_pcb: str) -> None:
        """设置父KiCad PCB文件名"""
        self._parent_kicad_pcb = parent_kicad_pcb
    
    def get_parent_kicad_pcb(self) -> str:
        """获取父KiCad PCB文件名"""
        return self._parent_kicad_pcb
    
    def get_parent_kicad_pcb2(self) -> str:
        """获取父KiCad PCB文件名（返回副本）"""
        return self._parent_kicad_pcb
    
    def set_filename(self, filename: str) -> None:
        """设置文件名"""
        self._file = filename
    
    def get_filename(self) -> str:
        """获取文件名"""
        return self._file
    
    def get_generated(self) -> bool:
        """获取是否生成标志"""
        return self._generated
    
    def get_graph(self, graph: Graph) -> None:
        """获取图形对象"""
        graph._V = self._graph._V.copy()
        graph._E = self._graph._E.copy()
        graph._graph_name = self._graph._graph_name
        graph._graph_id = self._graph._graph_id
        graph._kicad_pcb_file = self._graph._kicad_pcb_file
        graph._hpwl = self._graph._hpwl
    
    def get_graph_ref(self) -> Graph:
        """获取图形对象引用"""
        return self._graph
    
    def get_board(self, board: Board) -> None:
        """获取电路板对象"""
        board._bb_min_x = self._board._bb_min_x
        board._bb_min_y = self._board._bb_min_y
        board._bb_max_x = self._board._bb_max_x
        board._bb_max_y = self._board._bb_max_y
        board._board_name = self._board._board_name
    
    def get_board_ref(self) -> Board:
        """获取电路板对象引用"""
        return self._board
    
    def set_graph(self, graph: Graph) -> None:
        """设置图形对象"""
        self._graph._V = graph._V.copy()
        self._graph._E = graph._E.copy()
        self._graph._graph_name = graph._graph_name
        self._graph._graph_id = graph._graph_id
        self._graph._kicad_pcb_file = graph._kicad_pcb_file
        self._graph._hpwl = graph._hpwl
    
    def set_board(self, board: Board) -> None:
        """设置电路板对象"""
        self._board._bb_min_x = board._bb_min_x
        self._board._bb_min_y = board._bb_min_y
        self._board._bb_max_x = board._bb_max_x
        self._board._bb_max_y = board._bb_max_y
        self._board._board_name = board._board_name
    
    def set_id(self, id: int) -> None:
        """设置ID"""
        self._id = id
    
    def get_id(self) -> int:
        """获取ID"""
        return self._id
    
    def write_pcb_file_from_individual_files(self, filename: str, nodes: str, 
                                           edges: str, board: str, generated: bool) -> int:
        """从单独文件创建PCB文件"""
        return write_pcb_file_from_individual_files(filename, nodes, edges, board, generated)
    
    def append_pcb_file_from_individual_files(self, filename: str, nodes: str, 
                                            edges: str, board: str, generated: bool) -> int:
        """追加到现有PCB文件"""
        return append_pcb_file_from_individual_files(filename, nodes, edges, board, generated)
    
    def process_board_line(self, line: str) -> int:
        """处理电路板行"""
        return self._board.process_line(line)
    
    def process_pcb_line(self, line: str) -> int:
        """处理PCB行"""
        if "=" not in line:
            return -1
        
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        
        if key == ".kicad_pcb":
            self._kicad_pcb = value
        elif key == "parent":
            self._parent_kicad_pcb = value
        elif key == "id":
            try:
                self._id = int(value)
            except ValueError:
                return -1
        elif key == "generated":
            try:
                self._generated = bool(int(value))
            except ValueError:
                return -1
        
        return 0
    
    def add_edge_to_graph_from_long_line(self, line: str) -> int:
        """从长格式行添加边到图形"""
        return self._graph.add_edge_from_string_long(line)
    
    def add_node_to_graph_from_long_line(self, line: str) -> int:
        """从长格式行添加节点到图形"""
        return self._graph.add_node_from_string_long(line)
    
    def update_node_optimal(self, line: str) -> int:
        """更新节点优化信息"""
        return self._graph.update_node_optimal(line)
    
    def print_graph(self, print_csv: bool) -> None:
        """打印图形信息"""
        self._graph.print(print_csv)
    
    def print_statistics(self) -> None:
        """打印统计信息"""
        print(f"PCB文件: {self._file}")
        print(f"KiCad PCB: {self._kicad_pcb}")
        print(f"父KiCad PCB: {self._parent_kicad_pcb}")
        print(f"生成标志: {self._generated}")
        print(f"ID: {self._id}")
        print("图形统计:")
        self._graph.statistics()
        print("电路板信息:")
        self._board.print()


class VPtrPCBs:
    """PCB指针向量类，用于管理多个PCB对象"""
    
    def __init__(self):
        self._pcbs: List[PCB] = []
    
    def __len__(self) -> int:
        """获取PCB数量"""
        return len(self._pcbs)
    
    def __getitem__(self, index: int) -> PCB:
        """获取指定索引的PCB"""
        return self._pcbs[index]
    
    def append(self, pcb: PCB) -> None:
        """添加PCB"""
        self._pcbs.append(pcb)
    
    def clear(self) -> None:
        """清空所有PCB"""
        self._pcbs.clear()


def check_for_file_existance(filename: str) -> int:
    """检查文件是否存在"""
    if os.path.exists(filename):
        return 0
    return -1


def write_pcb_file_from_individual_files(filename: str, nodes: str, edges: str, 
                                       board: str, generated: bool, pcb_id: int = -1) -> int:
    """从单独文件创建PCB文件"""
    status = -1
    
    # 检查文件扩展名
    print("测试文件扩展名...")
    if filename.endswith(".pcb"):
        print("文件包含'.pcb'扩展名。")
    else:
        print("文件不包含'.pcb'扩展名。")
        filename += ".pcb"
    
    print(f"使用文件名: '{filename}'")
    
    # 创建文件头
    with open(filename, 'w') as file:
        file.write(f"filename={filename}\n")
        file.write(f"timestamp={int(time.time())}\n")
    
    # 追加内容
    status = append_pcb_file_from_individual_files(filename, nodes, edges, board, generated, pcb_id)
    
    return status


def append_pcb_file_from_individual_files(filename: str, nodes: str, edges: str, 
                                        board: str, generated: bool, pcb_id: int = -1) -> int:
    """追加到现有PCB文件"""
    status = -1
    
    # 检查文件是否存在
    print(f"检查文件 '{filename}' ...")
    if check_for_file_existance(filename) == 0:
        print("OK")
    else:
        print("未找到...调用 'write_pcb_file_from_individual_files(...)'")
        return write_pcb_file_from_individual_files(filename, nodes, edges, board, generated, pcb_id)
    
    # 检查输入文件
    for file_path, file_name in [(nodes, "nodes"), (edges, "edges"), (board, "board")]:
        print(f"检查文件 '{file_path}' ...")
        if check_for_file_existance(file_path) == 0:
            print("OK")
        else:
            print("未找到。退出。")
            return status
    
    # 写入PCB内容
    with open(filename, 'a') as file:
        file.write("pcb begin\n")
        file.write(f"\t.kicad_pcb=\n")  # 空值，由调用者设置
        file.write(f"\ttimestamp={int(time.time())}\n")
        if pcb_id != -1:
            file.write(f"\tid={pcb_id}\n")
        file.write("\tgraph begin\n")
        file.write("\t\tnodes begin\n")
        
        # 写入节点
        with open(nodes, 'r') as rd_file:
            for line in rd_file:
                file.write(f"\t\t\t{line.strip()}\n")
        
        file.write("\t\tnodes end\n")
        file.write("\t\tedges begin\n")
        
        # 写入边
        with open(edges, 'r') as rd_file:
            for line in rd_file:
                file.write(f"\t\t\t{line.strip()}\n")
        
        file.write("\t\tedges end\n")
        file.write("\tgraph end\n")
        file.write("\tboard begin\n")
        
        # 写入电路板信息
        with open(board, 'r') as rd_file:
            for line in rd_file:
                file.write(f"\t\t{line.strip()}\n")
        
        file.write("\tboard end\n")
        file.write("pcb end\n")
    
    status = 0
    return status


def write_pcb_file_from_individual_files_and_optimals(filename: str, nodes: str, edges: str, 
                                                    board: str, optimals: str, kicad_pcb: str, 
                                                    generated: bool, pcb_id: int = -1) -> int:
    """从单独文件（包含优化信息）创建PCB文件"""
    status = -1
    
    # 检查文件扩展名
    print("测试文件扩展名...")
    if filename.endswith(".pcb"):
        print("文件包含'.pcb'扩展名。")
    else:
        print("文件不包含'.pcb'扩展名。")
        filename += ".pcb"
    
    print(f"使用文件名: '{filename}'")
    
    # 创建文件头
    with open(filename, 'w') as file:
        file.write(f"filename={filename}\n")
        file.write(f"timestamp={int(time.time())}\n")
    
    # 追加内容
    status = append_pcb_file_from_individual_files_and_optimals(
        filename, nodes, edges, board, optimals, kicad_pcb, generated, pcb_id
    )
    
    return status


def append_pcb_file_from_individual_files_and_optimals(filename: str, nodes: str, edges: str, 
                                                     board: str, optimals: str, kicad_pcb: str, 
                                                     generated: bool, pcb_id: int = -1) -> int:
    """追加到现有PCB文件（包含优化信息）"""
    status = -1
    
    # 检查文件是否存在
    print(f"检查文件 '{filename}' ...")
    if check_for_file_existance(filename) == 0:
        print("OK")
    else:
        print("未找到...调用 'write_pcb_file_from_individual_files_and_optimals(...)'")
        return write_pcb_file_from_individual_files_and_optimals(
            filename, nodes, edges, board, optimals, kicad_pcb, generated, pcb_id
        )
    
    # 检查输入文件
    for file_path, file_name in [(nodes, "nodes"), (edges, "edges"), (board, "board"), (optimals, "optimals")]:
        print(f"检查文件 '{file_path}' ...")
        if check_for_file_existance(file_path) == 0:
            print("OK")
        else:
            print("未找到。退出。")
            return status
    
    # 写入PCB内容
    with open(filename, 'a') as file:
        file.write("pcb begin\n")
        file.write(f"\t.kicad_pcb={kicad_pcb}\n")
        file.write(f"\ttimestamp={int(time.time())}\n")
        if pcb_id != -1:
            file.write(f"\tid={pcb_id}\n")
        file.write("\tgraph begin\n")
        file.write("\t\tnodes begin\n")
        
        # 写入节点
        with open(nodes, 'r') as rd_file:
            for line in rd_file:
                file.write(f"\t\t\t{line.strip()}\n")
        
        file.write("\t\tnodes end\n")
        file.write("\t\toptimals begin\n")
        
        # 写入优化信息
        with open(optimals, 'r') as rd_file:
            for line in rd_file:
                file.write(f"\t\t\t{line.strip()}\n")
        
        file.write("\t\toptimals end\n")
        file.write("\t\tedges begin\n")
        
        # 写入边
        with open(edges, 'r') as rd_file:
            for line in rd_file:
                file.write(f"\t\t\t{line.strip()}\n")
        
        file.write("\t\tedges end\n")
        file.write("\tgraph end\n")
        file.write("\tboard begin\n")
        
        # 写入电路板信息
        with open(board, 'r') as rd_file:
            for line in rd_file:
                file.write(f"\t\t{line.strip()}\n")
        
        file.write("\tboard end\n")
        file.write("pcb end\n")
    
    status = 0
    return status


def read_pcb_file(filename: str, pcb_vector: VPtrPCBs) -> int:
    """读取PCB文件"""
    status = -1
    
    if check_for_file_existance(filename) != 0:
        return status
    
    try:
        with open(filename, 'r') as rd_file:
            pcb_i = None
            nodes = False
            edges = False
            board = False
            pcb_tag = False
            graph_tag = False
            optimals = False
            
            for line in rd_file:
                # 处理缩进
                i = 0
                for i in range(5):
                    if i >= len(line) or line[i] != '\t':
                        break
                
                if i > 3:
                    print("解析错误：读取了5个制表符，但最多只能有3个。")
                    return status
                
                line = line[i:].strip()
                
                if line == "pcb begin":
                    pcb_i = PCB()
                    pcb_tag = True
                    continue
                elif line == "pcb end":
                    pcb_vector.append(pcb_i)
                    pcb_tag = False
                    continue
                elif line == "graph begin":
                    graph_tag = True
                    continue
                elif line == "graph end":
                    graph_tag = False
                    continue
                elif line == "nodes begin":
                    nodes = True
                    continue
                elif line == "nodes end":
                    nodes = False
                    continue
                elif line == "optimals begin":
                    optimals = True
                    continue
                elif line == "optimals end":
                    optimals = False
                    continue
                elif line == "edges begin":
                    edges = True
                    continue
                elif line == "edges end":
                    edges = False
                    continue
                elif line == "board begin":
                    board = True
                    continue
                elif line == "board end":
                    board = False
                    continue
                
                # 处理内容
                if nodes and pcb_i:
                    pcb_i.add_node_to_graph_from_long_line(line)
                
                if optimals and pcb_i:
                    pcb_i.update_node_optimal(line)
                
                if edges and pcb_i:
                    pcb_i.add_edge_to_graph_from_long_line(line)
                
                if board and pcb_i:
                    pcb_i.process_board_line(line)
                
                if pcb_tag and not graph_tag and not board and pcb_i:
                    pcb_i.process_pcb_line(line)
        
        status = 0
        
    except Exception as e:
        print(f"读取PCB文件时出错: {e}")
        status = -1
    
    return status


def write_pcb_file(filename: str, pcb_vector: VPtrPCBs, append: bool = True) -> int:
    """写入PCB文件"""
    status = -1
    
    try:
        mode = 'a' if append else 'w'
        with open(filename, mode) as file:
            for p in pcb_vector:
                g = Graph()
                b = Board()
                p.get_graph(g)
                p.get_board(b)
                
                file.write("pcb begin\n")
                file.write(f"\t.kicad_pcb={p.get_kicad_pcb()}\n")
                file.write(f"\ttimestamp={int(time.time())}\n")
                file.write("\tgraph begin\n")
                file.write(f"\t\thpwl={g.get_hpwl()}\n")
                file.write("\t\tnodes begin\n")
                
                # 写入节点
                nodes = g.get_nodes()
                for n in nodes:
                    line = n.format_string_long()
                    file.write(f"\t\t\t{line}\n")
                
                file.write("\t\tnodes end\n")
                file.write("\t\toptimals begin\n")
                
                # 写入优化信息
                for n in nodes:
                    line = n.get_opt_formatted_string()
                    file.write(f"\t\t\t{line}\n")
                
                file.write("\t\toptimals end\n")
                file.write("\t\tedges begin\n")
                
                # 写入边
                edges = g.get_edges()
                for e in edges:
                    line = e.format_string_long()
                    file.write(f"\t\t\t{line}\n")
                
                file.write("\t\tedges end\n")
                file.write("\tgraph end\n")
                file.write("\tboard begin\n")
                file.write(f"\t\tbb_min_x,{b.get_bb_min_x()}\n")
                file.write(f"\t\tbb_min_y,{b.get_bb_min_y()}\n")
                file.write(f"\t\tbb_max_x,{b.get_bb_max_x()}\n")
                file.write(f"\t\tbb_max_y,{b.get_bb_max_y()}\n")
                file.write("\tboard end\n")
                file.write("pcb end\n")
        
        status = 0
        
    except Exception as e:
        print(f"写入PCB文件时出错: {e}")
        status = -1
    
    return status


def write_pcb_file_from_graph_and_board(filename: str, graph: Graph, board: Board, 
                                       placement_task: bool, placer: str) -> int:
    """从图形和电路板写入PCB文件"""
    status = -1
    
    try:
        with open(filename, 'w') as file:
            file.write("pcb begin\n")
            file.write("\t.kicad_pcb=\n")
            file.write(f"\tgenerated=0\n")
            file.write(f"\tplacement_task={'yes' if placement_task else 'no'}\n")
            file.write(f"\tplacer={placer}\n")
            file.write(f"\ttimestamp={int(time.time())}\n")
            file.write("\tgraph begin\n")
            file.write(f"\t\thpwl={graph.get_hpwl()}\n")
            file.write("\t\tnodes begin\n")
            
            # 写入节点
            nodes = graph.get_nodes()
            for n in nodes:
                line = n.format_string_long()
                file.write(f"\t\t\t{line}\n")
            
            file.write("\t\tnodes end\n")
            file.write("\t\tedges begin\n")
            
            # 写入边
            edges = graph.get_edges()
            for e in edges:
                line = e.format_string_long()
                file.write(f"\t\t\t{line}\n")
            
            file.write("\t\tedges end\n")
            file.write("\tgraph end\n")
            file.write("\tboard begin\n")
            file.write(f"\t\tbb_min_x,{board.get_bb_min_x()}\n")
            file.write(f"\t\tbb_min_y,{board.get_bb_min_y()}\n")
            file.write(f"\t\tbb_max_x,{board.get_bb_max_x()}\n")
            file.write(f"\t\tbb_max_y,{board.get_bb_max_y()}\n")
            file.write("\tboard end\n")
            file.write("pcb end\n")
        
        status = 0
        
    except Exception as e:
        print(f"从图形和电路板写入PCB文件时出错: {e}")
        status = -1
    
    return status


def append_pcb_file_from_graph_and_board(filename: str, graph: Graph, board: Board, 
                                        placement_task: bool, placer: str) -> int:
    """追加图形和电路板到PCB文件"""
    status = -1
    
    try:
        with open(filename, 'a') as file:
            file.write("pcb begin\n")
            file.write("\t.kicad_pcb=\n")
            file.write(f"\tgenerated=0\n")
            file.write(f"\tplacement_task={'yes' if placement_task else 'no'}\n")
            file.write(f"\tplacer={placer}\n")
            file.write(f"\ttimestamp={int(time.time())}\n")
            file.write("\tgraph begin\n")
            file.write(f"\t\thpwl={graph.get_hpwl()}\n")
            file.write("\t\tnodes begin\n")
            
            # 写入节点
            nodes = graph.get_nodes()
            for n in nodes:
                line = n.format_string_long()
                file.write(f"\t\t\t{line}\n")
            
            file.write("\t\tnodes end\n")
            file.write("\t\tedges begin\n")
            
            # 写入边
            edges = graph.get_edges()
            for e in edges:
                line = e.format_string_long()
                file.write(f"\t\t\t{line}\n")
            
            file.write("\t\tedges end\n")
            file.write("\tgraph end\n")
            file.write("\tboard begin\n")
            file.write(f"\t\tbb_min_x,{board.get_bb_min_x()}\n")
            file.write(f"\t\tbb_min_y,{board.get_bb_min_y()}\n")
            file.write(f"\t\tbb_max_x,{board.get_bb_max_x()}\n")
            file.write(f"\t\tbb_max_y,{board.get_bb_max_y()}\n")
            file.write("\tboard end\n")
            file.write("pcb end\n")
        
        status = 0
        
    except Exception as e:
        print(f"追加图形和电路板到PCB文件时出错: {e}")
        status = -1
    
    return status


def write_pcb_file_from_pcb(full_filename: str, pcb_obj: PCB, 
                           global_params: List[Tuple[str, str]], 
                           local_params: List[Tuple[str, str]]) -> int:
    """从PCB对象写入文件"""
    status = -1
    
    try:
        # 检查文件是否存在
        file_exists = os.path.exists(full_filename)
        
        if not file_exists:
            # 创建新文件
            with open(full_filename, 'w') as file:
                file.write(f"filename={full_filename}\n")
                file.write(f"timestamp={int(time.time())}\n")
                
                # 写入全局参数
                for key, value in global_params:
                    file.write(f"{key}={value}\n")
        
        # 追加PCB内容
        status = append_pcb_file_from_pcb(full_filename, pcb_obj, global_params, local_params)
        
    except Exception as e:
        print(f"从PCB对象写入文件时出错: {e}")
        status = -1
    
    return status


def append_pcb_file_from_pcb(full_filename: str, pcb_obj: PCB, 
                            global_params: List[Tuple[str, str]], 
                            local_params: List[Tuple[str, str]]) -> int:
    """追加PCB对象到文件"""
    status = -1
    
    try:
        g = Graph()
        b = Board()
        pcb_obj.get_graph(g)
        pcb_obj.get_board(b)
        
        with open(full_filename, 'a') as file:
            file.write("pcb begin\n")
            file.write(f"\t.kicad_pcb={pcb_obj.get_kicad_pcb()}\n")
            file.write(f"\ttimestamp={int(time.time())}\n")
            file.write("\tgraph begin\n")
            file.write(f"\t\thpwl={g.get_hpwl()}\n")
            file.write("\t\tnodes begin\n")
            
            # 写入节点
            nodes = g.get_nodes()
            for n in nodes:
                line = n.format_string_long()
                file.write(f"\t\t\t{line}\n")
            
            file.write("\t\tnodes end\n")
            file.write("\t\tedges begin\n")
            
            # 写入边
            edges = g.get_edges()
            for e in edges:
                line = e.format_string_long()
                file.write(f"\t\t\t{line}\n")
            
            file.write("\t\tedges end\n")
            file.write("\tgraph end\n")
            file.write("\tboard begin\n")
            file.write(f"\t\tbb_min_x,{b.get_bb_min_x()}\n")
            file.write(f"\t\tbb_min_y,{b.get_bb_min_y()}\n")
            file.write(f"\t\tbb_max_x,{b.get_bb_max_x()}\n")
            file.write(f"\t\tbb_max_y,{b.get_bb_max_y()}\n")
            file.write("\tboard end\n")
            file.write("pcb end\n")
        
        status = 0
        
    except Exception as e:
        print(f"追加PCB对象到文件时出错: {e}")
        status = -1
    
    return status


def write_pcb_file_from_graph_and_board_with_params(filename: str, graph: Graph, board: Board, 
                                                  global_params: List[Tuple[str, str]], 
                                                  local_params: List[Tuple[str, str]]) -> int:
    """从图形和电路板写入PCB文件（带参数）"""
    status = -1
    
    try:
        # 检查文件是否存在
        file_exists = os.path.exists(filename)
        
        if not file_exists:
            # 创建新文件
            with open(filename, 'w') as file:
                file.write(f"filename={filename}\n")
                file.write(f"timestamp={int(time.time())}\n")
                
                # 写入全局参数
                for key, value in global_params:
                    file.write(f"{key}={value}\n")
        
        # 追加内容
        status = append_pcb_file_from_graph_and_board_with_params(
            filename, graph, board, global_params, local_params
        )
        
    except Exception as e:
        print(f"从图形和电路板写入PCB文件（带参数）时出错: {e}")
        status = -1
    
    return status


def append_pcb_file_from_graph_and_board_with_params(filename: str, graph: Graph, board: Board, 
                                                   global_params: List[Tuple[str, str]], 
                                                   local_params: List[Tuple[str, str]]) -> int:
    """追加图形和电路板到PCB文件（带参数）"""
    status = -1
    
    try:
        with open(filename, 'a') as file:
            file.write("pcb begin\n")
            
            # 写入本地参数
            for key, value in local_params:
                file.write(f"\t{key}={value}\n")
            
            file.write(f"\ttimestamp={int(time.time())}\n")
            file.write("\tgraph begin\n")
            file.write(f"\t\thpwl={graph.get_hpwl()}\n")
            file.write("\t\tnodes begin\n")
            
            # 写入节点
            nodes = graph.get_nodes()
            for n in nodes:
                line = n.format_string_long()
                file.write(f"\t\t\t{line}\n")
            
            file.write("\t\tnodes end\n")
            file.write("\t\tedges begin\n")
            
            # 写入边
            edges = graph.get_edges()
            for e in edges:
                line = e.format_string_long()
                file.write(f"\t\t\t{line}\n")
            
            file.write("\t\tedges end\n")
            file.write("\tgraph end\n")
            file.write("\tboard begin\n")
            file.write(f"\t\tbb_min_x,{board.get_bb_min_x()}\n")
            file.write(f"\t\tbb_min_y,{board.get_bb_min_y()}\n")
            file.write(f"\t\tbb_max_x,{board.get_bb_max_x()}\n")
            file.write(f"\t\tbb_max_y,{board.get_bb_max_y()}\n")
            file.write("\tboard end\n")
            file.write("pcb end\n")
        
        status = 0
        
    except Exception as e:
        print(f"追加图形和电路板到PCB文件（带参数）时出错: {e}")
        status = -1
    
    return status


# 版本信息
VERSION_MAJOR = 0
VERSION_MINOR = 0
PATCH_NUMBER = 12


def get_library_version(maj: int, min: int, patch: int) -> int:
    """获取库版本"""
    maj = VERSION_MAJOR
    min = VERSION_MINOR
    patch = PATCH_NUMBER
    return 0


def get_build_time(s: str) -> int:
    """获取构建时间"""
    s = __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return 0


def get_cpp_standard(s: str) -> int:
    """获取C++标准"""
    s = "Python 3.6+"
    return 0


def build_info() -> int:
    """打印构建信息"""
    print(f"PCB Python Library v{VERSION_MAJOR}.{VERSION_MINOR}.{PATCH_NUMBER}")
    print("纯Python实现，无需C++依赖")
    print("支持PCB文件读写、图形管理等功能")
    return 0


def build_info_as_string() -> str:
    """返回构建信息字符串"""
    return f"PCB Python Library v{VERSION_MAJOR}.{VERSION_MINOR}.{PATCH_NUMBER}"


def get_library_version_string() -> str:
    """返回库版本字符串"""
    return f"v{VERSION_MAJOR}.{VERSION_MINOR}.{PATCH_NUMBER}"


def dependency_info() -> int:
    """打印依赖信息"""
    print("PCB Python Library 依赖:")
    print("- Python 3.6+")
    print("- 标准库: os, time, typing")
    print("- 内部模块: netlist")
    return 0


def dependency_info_as_string() -> str:
    """返回依赖信息字符串"""
    return "PCB Python Library 依赖: Python 3.6+, 标准库, 内部模块netlist" 
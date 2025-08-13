"""
Edge类 - 表示电路图中的边（连接）
对应C++的edge.hpp
"""

from typing import Tuple, Optional
from .utils import Utils

class Edge:
    """表示电路图中的边（连接）"""
    
    def __init__(self):
        # 节点A的信息
        self._a_id = -1
        self._a_name = ""
        self._a_pad_id = -1
        self._a_pad_name = ""
        self._a_size_x = 0.0
        self._a_size_y = 0.0
        self._a_pos_x = 0.0
        self._a_pos_y = 0.0
        self._a_is_placed = False
        
        # 节点B的信息
        self._b_id = -1
        self._b_name = ""
        self._b_pad_id = -1
        self._b_pad_name = ""
        self._b_size_x = 0.0
        self._b_size_y = 0.0
        self._b_pos_x = 0.0
        self._b_pos_y = 0.0
        self._b_is_placed = False
        
        # 网络信息
        self._net_id = -1
        self._net_name = ""
        self._power_rail = 0
    
    def create_from_string_short(self, s: str) -> int:
        """从短格式字符串创建边"""
        try:
            fields = Utils.parse_csv_line(s)
            if len(fields) < 20:
                return -1
            
            # 节点A信息
            self._a_id = Utils.safe_int(fields[0])
            self._a_name = fields[1]
            self._a_pad_id = Utils.safe_int(fields[2])
            self._a_size_x = Utils.safe_float(fields[3])
            self._a_size_y = Utils.safe_float(fields[4])
            self._a_pos_x = Utils.safe_float(fields[5])
            self._a_pos_y = Utils.safe_float(fields[6])
            self._a_is_placed = Utils.safe_int(fields[7]) == 1
            
            # 节点B信息
            self._b_id = Utils.safe_int(fields[8])
            self._b_name = fields[9]
            self._b_pad_id = Utils.safe_int(fields[10])
            self._b_size_x = Utils.safe_float(fields[11])
            self._b_size_y = Utils.safe_float(fields[12])
            self._b_pos_x = Utils.safe_float(fields[13])
            self._b_pos_y = Utils.safe_float(fields[14])
            self._b_is_placed = Utils.safe_int(fields[15]) == 1
            
            # 网络信息
            self._net_id = Utils.safe_int(fields[16])
            self._net_name = fields[17].strip('"') if len(fields) > 17 else ""
            self._power_rail = Utils.safe_int(fields[18]) if len(fields) > 18 else 0
            
            return 0
        except Exception:
            return -1
    
    def create_from_string_long(self, s: str) -> int:
        """从长格式字符串创建边"""
        try:
            fields = Utils.parse_csv_line(s)
            
            # 检查字段数量，支持19字段的标准格式
            if len(fields) < 19:
                return -1
            
            # 节点A信息
            self._a_id = Utils.safe_int(fields[0])
            self._a_pad_id = Utils.safe_int(fields[1])
            self._a_pad_name = fields[2]
            self._a_size_x = Utils.safe_float(fields[3])
            self._a_size_y = Utils.safe_float(fields[4])
            self._a_pos_x = Utils.safe_float(fields[5])
            self._a_pos_y = Utils.safe_float(fields[6])
            self._a_is_placed = Utils.safe_int(fields[7]) == 1
            
            # 节点B信息
            self._b_id = Utils.safe_int(fields[8])
            self._b_pad_id = Utils.safe_int(fields[9])
            self._b_pad_name = fields[10]
            self._b_size_x = Utils.safe_float(fields[11])
            self._b_size_y = Utils.safe_float(fields[12])
            self._b_pos_x = Utils.safe_float(fields[13])
            self._b_pos_y = Utils.safe_float(fields[14])
            self._b_is_placed = Utils.safe_int(fields[15]) == 1
            
            # 网络信息
            self._net_id = Utils.safe_int(fields[16])
            self._net_name = fields[17].strip('"') if len(fields) > 17 else ""
            self._power_rail = Utils.safe_int(fields[18]) if len(fields) > 18 else 0
            
            # 设置节点名称（从pad_name推断）
            self._a_name = f"Node_{self._a_id}"
            self._b_name = f"Node_{self._b_id}"
            
            return 0
        except Exception:
            return -1
    
    def get_net_id(self) -> int:
        """获取网络ID"""
        return self._net_id
    
    def get_net_name(self) -> str:
        """获取网络名称"""
        return self._net_name
    
    def get_power_rail(self) -> int:
        """获取电源轨信息"""
        return self._power_rail
    
    def get_instance_id(self, node: int) -> int:
        """获取指定节点的实例ID"""
        return self._b_id if node else self._a_id
    
    def get_instance_is_placed(self, node: int) -> bool:
        """获取指定节点的放置状态"""
        return self._b_is_placed if node else self._a_is_placed
    
    def get_pad_name(self, node: int) -> str:
        """获取指定节点的焊盘名称"""
        return self._b_pad_name if node else self._a_pad_name
    
    def get_pad_id(self, node: int) -> int:
        """获取指定节点的焊盘ID"""
        return self._b_pad_id if node else self._a_pad_id
    
    def get_edge_connectivity(self) -> Tuple[int, int]:
        """获取边的连接信息"""
        return (self._a_id, self._b_id)
    
    def get_size(self, node_id: int) -> Tuple[float, float]:
        """获取指定节点的尺寸"""
        if node_id == self._a_id:
            return (self._a_size_x, self._a_size_y)
        elif node_id == self._b_id:
            return (self._b_size_x, self._b_size_y)
        else:
            return (0.0, 0.0)
    
    def set_size(self, node_id: int, size: Tuple[float, float]) -> int:
        """设置指定节点的尺寸"""
        if node_id == self._a_id:
            self._a_size_x, self._a_size_y = size
        elif node_id == self._b_id:
            self._b_size_x, self._b_size_y = size
        else:
            return -1
        return 0
    
    def get_pos(self, node_id: int) -> Tuple[float, float]:
        """获取指定节点的位置"""
        if node_id == self._a_id:
            return (self._a_pos_x, self._a_pos_y)
        elif node_id == self._b_id:
            return (self._b_pos_x, self._b_pos_y)
        else:
            return (0.0, 0.0)
    
    def set_pos(self, node_id: int, pos: Tuple[float, float]) -> int:
        """设置指定节点的位置"""
        if node_id == self._a_id:
            self._a_pos_x, self._a_pos_y = pos
        elif node_id == self._b_id:
            self._b_pos_x, self._b_pos_y = pos
        else:
            return -1
        return 0
    
    def print_to_console(self, format_long: bool) -> None:
        """打印边信息到控制台"""
        if format_long:
            print(f"Edge: {self._a_name}({self._a_id}) -> {self._b_name}({self._b_id}), "
                  f"Net: {self._net_name}({self._net_id}), Power: {self._power_rail}")
        else:
            print(f"{self._a_id},{self._a_name},{self._a_pad_id},{self._a_size_x:.6f},{self._a_size_y:.6f},"
                  f"{self._a_pos_x:.6f},{self._a_pos_y:.6f},{1 if self._a_is_placed else 0},"
                  f"{self._b_id},{self._b_name},{self._b_pad_id},{self._b_size_x:.6f},{self._b_size_y:.6f},"
                  f"{self._b_pos_x:.6f},{self._b_pos_y:.6f},{1 if self._b_is_placed else 0},"
                  f"{self._net_id},\"{self._net_name}\",{self._power_rail}")
    
    def print(self, print_csv: bool) -> int:
        """打印边信息"""
        self.print_to_console(not print_csv)
        return 0
    
    def format_string_long(self) -> str:
        """格式化长字符串"""
        line = f"{self._a_id},{self._a_name},{self._a_pad_id},{self._a_size_x:.6f},{self._a_size_y:.6f},"
        line += f"{self._a_pos_x:.6f},{self._a_pos_y:.6f},{1 if self._a_is_placed else 0},"
        line += f"{self._b_id},{self._b_name},{self._b_pad_id},{self._b_size_x:.6f},{self._b_size_y:.6f},"
        line += f"{self._b_pos_x:.6f},{self._b_pos_y:.6f},{1 if self._b_is_placed else 0},"
        line += f"{self._net_id},\"{self._net_name}\",{self._power_rail}"
        return line
    
    # 设置器方法
    def set_id(self, node: int, node_id: int) -> None:
        """设置指定节点的ID"""
        if node:
            self._b_id = node_id
        else:
            self._a_id = node_id
    
    def set_name(self, node: int, name: str) -> None:
        """设置指定节点的名称"""
        if node:
            self._b_name = name
        else:
            self._a_name = name
    
    def set_pad_id(self, node: int, pad_id: int) -> None:
        """设置指定节点的焊盘ID"""
        if node:
            self._b_pad_id = pad_id
        else:
            self._a_pad_id = pad_id
    
    def set_pad_name(self, node: int, pad_name: str) -> None:
        """设置指定节点的焊盘名称"""
        if node:
            self._b_pad_name = pad_name
        else:
            self._a_pad_name = pad_name
    
    def set_is_placed(self, node: int, is_placed: bool) -> None:
        """设置指定节点的放置状态"""
        if node:
            self._b_is_placed = is_placed
        else:
            self._a_is_placed = is_placed
    
    def set_net_id(self, net_id: int) -> None:
        """设置网络ID"""
        self._net_id = net_id
    
    def set_net_name(self, net_name: str) -> None:
        """设置网络名称"""
        self._net_name = net_name
    
    def set_power_rail(self, power_rail: int) -> None:
        """设置电源轨信息"""
        self._power_rail = power_rail
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"Edge({self._a_name}({self._a_id}) -> {self._b_name}({self._b_id}), Net: {self._net_name})"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return self.__str__() 
    def get_node_id_a(self):
     return self._a_id

    def get_node_id_b(self):
     return self._b_id
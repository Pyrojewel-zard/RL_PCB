"""
Node类 - 表示电路图中的节点（组件）
对应C++的node.hpp
"""

from typing import Tuple, List, Optional
from .optimal import Optimal
from .utils import Utils

class Node:
    """表示电路图中的节点（组件）"""
    
    def __init__(self):
        self._id = -1
        self._name = ""
        self._size_x = 0.0
        self._size_y = 0.0
        self._pos_x = 0.0
        self._pos_y = 0.0
        self._orientation = 0.0
        self._layer = 0
        self._is_placed = False
        self._pins = 0
        self._pins_smd = 0
        self._pins_th = 0
        self._type = 0
        self._neighbors = []  # List of (neighbor_id, connections) tuples
        self._optimal = Optimal()
    
    def create_from_string_short(self, s: str) -> int:
        """从短格式字符串创建节点"""
        try:
            fields = Utils.parse_csv_line(s)
            if len(fields) < 12:
                return -1
            
            self._id = Utils.safe_int(fields[0])
            self._name = fields[1]
            self._size_x = Utils.safe_float(fields[2])
            self._size_y = Utils.safe_float(fields[3])
            self._pos_x = Utils.safe_float(fields[4])
            self._pos_y = Utils.safe_float(fields[5])
            self._orientation = Utils.safe_float(fields[6])
            self._layer = Utils.safe_int(fields[7])
            self._is_placed = Utils.safe_int(fields[8]) == 1
            self._pins = Utils.safe_int(fields[9])
            self._pins_smd = Utils.safe_int(fields[10])
            self._pins_th = Utils.safe_int(fields[11])
            self._type = Utils.safe_int(fields[12]) if len(fields) > 12 else 0
            
            # 设置optimal信息
            self._optimal.set_id(self._id)
            self._optimal.set_name(self._name)
            
            return 0
        except Exception:
            return -1
    
    def create_from_string_long(self, s: str) -> int:
        """从长格式字符串创建节点"""
        # 长格式与短格式相同，暂时使用相同实现
        return self.create_from_string_short(s)
    
    def get_id(self) -> int:
        """获取节点ID"""
        return self._id
    
    def get_name(self) -> str:
        """获取节点名称"""
        return self._name
    
    def get_size(self) -> Tuple[float, float]:
        """获取节点尺寸"""
        return (self._size_x, self._size_y)
    
    def set_size(self, size: Tuple[float, float]) -> int:
        """设置节点尺寸"""
        self._size_x, self._size_y = size
        return 0
    
    def get_pos(self) -> Tuple[float, float]:
        """获取节点位置"""
        return (self._pos_x, self._pos_y)
    
    def set_pos(self, pos: Tuple[float, float]) -> int:
        """设置节点位置"""
        self._pos_x, self._pos_y = pos
        return 0
    
    def get_layer(self) -> int:
        """获取层信息"""
        return self._layer
    
    def get_type(self) -> int:
        """获取类型"""
        return self._type
    
    def get_pin_count(self) -> int:
        """获取引脚总数"""
        return self._pins
    
    def get_smd_pin_count(self) -> int:
        """获取SMD引脚数"""
        return self._pins_smd
    
    def get_th_pin_count(self) -> int:
        """获取通孔引脚数"""
        return self._pins_th
    
    def get_is_placed(self) -> bool:
        """获取是否已放置"""
        return self._is_placed
    
    def set_is_placed_flag(self) -> int:
        """设置为已放置"""
        self._is_placed = True
        return 0
    
    def unset_is_placed_flag(self) -> int:
        """设置为未放置"""
        self._is_placed = False
        return 0
    
    def set_orientation(self, orientation: float) -> None:
        """设置方向角度"""
        self._orientation = Utils.normalize_angle(orientation)
    
    def get_orientation(self) -> float:
        """获取方向角度"""
        return self._orientation
    
    def set_neighbors(self, neighbors: List[Tuple[int, int]]) -> int:
        """设置邻居节点列表"""
        self._neighbors = neighbors
        return 0
    
    def get_neighbors(self) -> List[Tuple[int, int]]:
        """获取邻居节点列表"""
        return self._neighbors.copy()
    
    def get_inst_bb_coords(self, grid_resolution: float) -> Tuple[int, int, int, int]:
        """获取实例边界框坐标（网格化）"""
        x_min = int(self._pos_x / grid_resolution)
        y_min = int(self._pos_y / grid_resolution)
        x_max = int((self._pos_x + self._size_x) / grid_resolution)
        y_max = int((self._pos_y + self._size_y) / grid_resolution)
        return (x_min, x_max, y_min, y_max)
    
    def get_inst_bb_centre_size(self, grid_resolution: float) -> Tuple[int, int, int, int]:
        """获取实例边界框中心坐标和尺寸（网格化）"""
        x_min, x_max, y_min, y_max = self.get_inst_bb_coords(grid_resolution)
        x_center = (x_min + x_max) // 2
        y_center = (y_min + y_max) // 2
        x_size = x_max - x_min
        y_size = y_max - y_min
        return (x_center, y_center, x_size, y_size)
    
    def print_to_console(self, format_long: bool) -> None:
        """打印节点信息到控制台"""
        if format_long:
            print(f"Node(id={self._id}, name='{self._name}', "
                  f"size=({self._size_x:.6f}, {self._size_y:.6f}), "
                  f"pos=({self._pos_x:.6f}, {self._pos_y:.6f}), "
                  f"orientation={self._orientation:.2f}, "
                  f"layer={self._layer}, placed={self._is_placed}, "
                  f"pins={self._pins}, type={self._type})")
        else:
            print(f"{self._id},{self._name},{self._size_x:.6f},{self._size_y:.6f},"
                  f"{self._pos_x:.6f},{self._pos_y:.6f},{self._orientation:.2f},"
                  f"{self._layer},{1 if self._is_placed else 0},{self._pins},"
                  f"{self._pins_smd},{self._pins_th},{self._type}")
    
    def print(self, print_csv: bool) -> None:
        """打印节点信息"""
        self.print_to_console(not print_csv)
    
    def format_string_long(self, line: str) -> int:
        """格式化长字符串"""
        line = f"{self._id},{self._name},{self._size_x:.6f},{self._size_y:.6f},"
        line += f"{self._pos_x:.6f},{self._pos_y:.6f},{self._orientation:.2f},"
        line += f"{self._layer},{1 if self._is_placed else 0},{self._pins},"
        line += f"{self._pins_smd},{self._pins_th},{self._type}"
        return 0
    
    def get_area(self) -> float:
        """获取节点面积"""
        return self._size_x * self._size_y
    
    # Optimal相关方法
    def set_opt_id(self, node_id: int) -> int:
        """设置optimal的ID"""
        return self._optimal.set_id(node_id)
    
    def set_opt_name(self, name: str) -> int:
        """设置optimal的名称"""
        return self._optimal.set_name(name)
    
    def set_opt_euclidean_distance(self, distance: float) -> int:
        """设置optimal的欧几里得距离"""
        return self._optimal.set_euclidean_distance(distance)
    
    def set_opt_hpwl(self, hpwl: float) -> int:
        """设置optimal的HPWL"""
        return self._optimal.set_hpwl(hpwl)
    
    def get_opt_id(self) -> int:
        """获取optimal的ID"""
        return self._optimal.get_id()
    
    def get_opt_name(self) -> str:
        """获取optimal的名称"""
        return self._optimal.get_name()
    
    def get_opt_euclidean_distance(self) -> float:
        """获取optimal的欧几里得距离"""
        return self._optimal.get_euclidean_distance()
    
    def get_opt_hpwl(self) -> float:
        """获取optimal的HPWL"""
        return self._optimal.get_hpwl()
    
    def get_opt_formatted_string(self, s: str) -> int:
        """获取optimal的格式化字符串"""
        return self._optimal.format_string(s)
    
    # 设置器方法
    def set_id(self, node_id: int) -> None:
        """设置节点ID"""
        self._id = node_id
        self._optimal.set_id(node_id)
    
    def set_name(self, name: str) -> None:
        """设置节点名称"""
        self._name = name
        self._optimal.set_name(name)
    
    def set_layer(self, layer: int) -> None:
        """设置层信息"""
        self._layer = layer
    
    def set_is_placed(self, is_placed: bool) -> None:
        """设置放置状态"""
        self._is_placed = is_placed
    
    def set_pins(self, pins: int) -> None:
        """设置引脚总数"""
        self._pins = pins
    
    def set_pins_smd(self, pins_smd: int) -> None:
        """设置SMD引脚数"""
        self._pins_smd = pins_smd
    
    def set_pins_th(self, pins_th: int) -> None:
        """设置通孔引脚数"""
        self._pins_th = pins_th
    
    def set_type(self, node_type: int) -> None:
        """设置节点类型"""
        self._type = node_type
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"Node(id={self._id}, name='{self._name}', pos=({self._pos_x:.2f}, {self._pos_y:.2f}))"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return self.__str__() 
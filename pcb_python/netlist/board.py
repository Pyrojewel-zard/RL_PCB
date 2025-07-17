"""
Board类 - 表示电路板信息
对应C++的board.hpp
"""

from typing import Tuple, List
from .utils import Utils

class Board:
    """表示电路板信息"""
    
    def __init__(self):
        self._bb_min_x = 0.0
        self._bb_min_y = 0.0
        self._bb_max_x = 0.0
        self._bb_max_y = 0.0
        self._board_name = ""
        self._board_id = 0
        self._kicad_pcb_file = ""
    
    def get_bb_min_x(self) -> float:
        """获取边界框最小X坐标"""
        return self._bb_min_x
    
    def get_bb_min_y(self) -> float:
        """获取边界框最小Y坐标"""
        return self._bb_min_y
    
    def get_bb_max_x(self) -> float:
        """获取边界框最大X坐标"""
        return self._bb_max_x
    
    def get_bb_max_y(self) -> float:
        """获取边界框最大Y坐标"""
        return self._bb_max_y
    
    def set_bb_min_x(self, val: float) -> None:
        """设置边界框最小X坐标"""
        self._bb_min_x = val
    
    def set_bb_min_y(self, val: float) -> None:
        """设置边界框最小Y坐标"""
        self._bb_min_y = val
    
    def set_bb_max_x(self, val: float) -> None:
        """设置边界框最大X坐标"""
        self._bb_max_x = val
    
    def set_bb_max_y(self, val: float) -> None:
        """设置边界框最大Y坐标"""
        self._bb_max_y = val
    
    def get_board_size(self) -> Tuple[float, float]:
        """获取电路板尺寸 (宽度, 高度)"""
        width = abs(self._bb_max_x - self._bb_min_x)
        height = abs(self._bb_max_y - self._bb_min_y)
        return (width, height)
    
    def process_line(self, line: str) -> int:
        """解析一行文本并更新电路板参数"""
        try:
            line = line.strip()
            if not line or line.startswith('#'):
                return 0
            
            fields = Utils.parse_csv_line(line)
            if len(fields) < 2:
                return -1
            
            key = fields[0].strip()
            value = fields[1].strip()
            
            if key == "bb_min_x":
                self._bb_min_x = Utils.safe_float(value)
            elif key == "bb_min_y":
                self._bb_min_y = Utils.safe_float(value)
            elif key == "bb_max_x":
                self._bb_max_x = Utils.safe_float(value)
            elif key == "bb_max_y":
                self._bb_max_y = Utils.safe_float(value)
            elif key == "board_name":
                self._board_name = value
            elif key == "board_id":
                self._board_id = Utils.safe_int(value)
            elif key == "kicad_pcb_file":
                self._kicad_pcb_file = value
            else:
                # 忽略未知字段
                pass
            
            return 0
        except Exception:
            return -1
    
    def write_to_file(self, filename: str) -> int:
        """将电路板信息写入文件"""
        try:
            with open(filename, 'w') as f:
                f.write(f"bb_min_x,{Utils.format_float(self._bb_min_x)}\n")
                f.write(f"bb_min_y,{Utils.format_float(self._bb_min_y)}\n")
                f.write(f"bb_max_x,{Utils.format_float(self._bb_max_x)}\n")
                f.write(f"bb_max_y,{Utils.format_float(self._bb_max_y)}\n")
                if self._board_name:
                    f.write(f"board_name,{self._board_name}\n")
                if self._board_id > 0:
                    f.write(f"board_id,{self._board_id}\n")
                if self._kicad_pcb_file:
                    f.write(f"kicad_pcb_file,{self._kicad_pcb_file}\n")
            return 0
        except Exception:
            return -1
    
    def print(self) -> None:
        """打印电路板信息到控制台"""
        print(f"Board: {self._board_name}")
        print(f"  Bounding Box: ({self._bb_min_x:.6f}, {self._bb_min_y:.6f}) to ({self._bb_max_x:.6f}, {self._bb_max_y:.6f})")
        width, height = self.get_board_size()
        print(f"  Size: {width:.6f} x {height:.6f}")
        print(f"  ID: {self._board_id}")
        if self._kicad_pcb_file:
            print(f"  KiCad PCB File: {self._kicad_pcb_file}")
    
    def get_width(self) -> float:
        """获取电路板宽度"""
        return abs(self._bb_max_x - self._bb_min_x)
    
    def get_height(self) -> float:
        """获取电路板高度"""
        return abs(self._bb_max_y - self._bb_min_y)
    
    def __str__(self) -> str:
        """字符串表示"""
        width, height = self.get_board_size()
        return f"Board({self._board_name}, size={width:.2f}x{height:.2f})"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return self.__str__()


def process_board_file(board_file: str, board: Board) -> int:
    """处理电路板文件"""
    try:
        with open(board_file, 'r') as f:
            for line in f:
                if board.process_line(line) != 0:
                    return -1
        return 0
    except Exception:
        return -1


def get_fields(s: str) -> List[str]:
    """获取CSV字段"""
    return Utils.parse_csv_line(s) 
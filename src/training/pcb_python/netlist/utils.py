"""
工具类 - 提供通用的工具函数
对应C++的utils.hpp
"""

import math
from typing import Tuple, List, Any

class Utils:
    """工具类，提供各种辅助函数"""
    
    @staticmethod
    def euclidean_distance(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """计算两点间的欧几里得距离"""
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    @staticmethod
    def manhattan_distance(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """计算两点间的曼哈顿距离"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    @staticmethod
    def parse_csv_line(line: str) -> List[str]:
        """解析CSV格式的行"""
        return [field.strip() for field in line.split(',')]
    
    @staticmethod
    def format_float(value: float, precision: int = 8) -> str:
        """格式化浮点数"""
        return f"{value:.{precision}f}"
    
    @staticmethod
    def is_numeric(value: str) -> bool:
        """检查字符串是否为数字"""
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def safe_float(value: str, default: float = 0.0) -> float:
        """安全地将字符串转换为浮点数"""
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def safe_int(value: str, default: int = 0) -> int:
        """安全地将字符串转换为整数"""
        try:
            return int(float(value))  # 先转float再转int，处理"1.0"这种情况
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def clamp(value: float, min_val: float, max_val: float) -> float:
        """将值限制在指定范围内"""
        return max(min_val, min(value, max_val))
    
    @staticmethod
    def normalize_angle(angle: float) -> float:
        """标准化角度到0-360度范围"""
        while angle >= 360:
            angle -= 360
        while angle < 0:
            angle += 360
        return angle
    
    @staticmethod
    def get_bounding_box(points: List[Tuple[float, float]]) -> Tuple[float, float, float, float]:
        """计算点集的边界框 (min_x, min_y, max_x, max_y)"""
        if not points:
            return (0.0, 0.0, 0.0, 0.0)
        
        min_x = min(p[0] for p in points)
        min_y = min(p[1] for p in points)
        max_x = max(p[0] for p in points)
        max_y = max(p[1] for p in points)
        
        return (min_x, min_y, max_x, max_y)
    
    @staticmethod
    def calculate_hpwl(points: List[Tuple[float, float]]) -> float:
        """计算半周长线长 (Half-Perimeter Wire Length)"""
        if not points:
            return 0.0
        
        min_x = min(p[0] for p in points)
        min_y = min(p[1] for p in points)
        max_x = max(p[0] for p in points)
        max_y = max(p[1] for p in points)
        
        return (max_x - min_x) + (max_y - min_y) 
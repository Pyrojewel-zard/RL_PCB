"""
Optimal类 - 存储节点的优化信息
对应C++的optimal.hpp
"""

from typing import Optional

class Optimal:
    """存储节点的优化信息，包括位置、HPWL等"""
    
    def __init__(self, node_id: int = -1, name: str = ""):
        self._id = node_id
        self._name = name
        self._euclidean_distance = 0.0
        self._hpwl = 0.0
    
    def set_id(self, node_id: int) -> int:
        """设置节点ID"""
        self._id = node_id
        return 0
    
    def get_id(self) -> int:
        """获取节点ID"""
        return self._id
    
    def set_name(self, name: str) -> int:
        """设置节点名称"""
        self._name = name
        return 0
    
    def get_name(self) -> str:
        """获取节点名称"""
        return self._name
    
    def set_euclidean_distance(self, distance: float) -> int:
        """设置欧几里得距离"""
        self._euclidean_distance = distance
        return 0
    
    def get_euclidean_distance(self) -> float:
        """获取欧几里得距离"""
        return self._euclidean_distance
    
    def set_hpwl(self, hpwl: float) -> int:
        """设置HPWL值"""
        self._hpwl = hpwl
        return 0
    
    def get_hpwl(self) -> float:
        """获取HPWL值"""
        return self._hpwl
    
    def format_string(self, s: str = None) -> str:
        """格式化字符串输出，返回PCB文件格式的optimal字符串"""
        formatted = f"{self._id},{self._name},{self._euclidean_distance:.6f},{self._hpwl:.6f}"
        return formatted
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"Optimal(id={self._id}, name='{self._name}', " \
               f"euclidean_distance={self._euclidean_distance:.6f}, " \
               f"hpwl={self._hpwl:.6f})"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return self.__str__() 
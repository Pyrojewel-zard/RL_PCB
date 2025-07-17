"""
Graph类 - 表示电路网络图
对应C++的graph.hpp，这是最核心的类
"""

from typing import List, Tuple, Set, Optional
from .node import Node
from .edge import Edge
from .board import Board
from .utils import Utils

class Graph:
    """表示电路网络图，管理节点和边的连接关系"""
    
    # 枚举定义
    COMPONENT = 0
    PADD = 1
    
    SHORT = 0
    LONG = 1
    
    def __init__(self):
        self._V_original = []  # 原始节点列表（不可修改）
        self._V = []           # 当前节点列表
        self._E = []           # 边列表
        self._graph_name = ""
        self._graph_id = 0
        self._kicad_pcb_file = ""
        self._hpwl = 0.0
    
    def add_node_from_string_short(self, s: str) -> int:
        """从短格式字符串添加节点"""
        node = Node()
        if node.create_from_string_short(s) == 0:
            self._V.append(node)
            return 0
        return -1
    
    def add_node_from_string_long(self, s: str) -> int:
        """从长格式字符串添加节点"""
        node = Node()
        if node.create_from_string_long(s) == 0:
            self._V.append(node)
            return 0
        return -1
    
    def add_edge_from_string_short(self, s: str) -> int:
        """从短格式字符串添加边"""
        edge = Edge()
        if edge.create_from_string_short(s) == 0:
            self._E.append(edge)
            return 0
        return -1
    
    def add_edge_from_string_long(self, s: str) -> int:
        """从长格式字符串添加边"""
        edge = Edge()
        if edge.create_from_string_long(s) == 0:
            self._E.append(edge)
            return 0
        return -1
    
    def get_node_name_by_id(self, node_id: int) -> str:
        """根据ID获取节点名称"""
        for node in self._V:
            if node.get_id() == node_id:
                return node.get_name()
        return ""
    
    def get_set_net_ids(self) -> Set[int]:
        """获取所有网络ID的集合"""
        net_ids = set()
        for edge in self._E:
            net_ids.add(edge.get_net_id())
        return net_ids
    
    def statistics(self) -> int:
        """打印图形统计信息"""
        print(f"Graph Statistics:")
        print(f"  Nodes: {len(self._V)}")
        print(f"  Edges: {len(self._E)}")
        print(f"  Nets: {len(self.get_set_net_ids())}")
        return 0
    
    def get_nodes_connectivity_list(self, power_rail: int = 0) -> List[Tuple[int, int]]:
        """获取节点连接性列表，按连接数降序排列"""
        connectivity = {}
        for edge in self._E:
            if edge.get_power_rail() == power_rail:
                a_id, b_id = edge.get_edge_connectivity()
                connectivity[a_id] = connectivity.get(a_id, 0) + 1
                connectivity[b_id] = connectivity.get(b_id, 0) + 1
        
        # 按连接数降序排列
        return sorted(connectivity.items(), key=lambda x: x[1], reverse=True)
    
    def get_nodes_area_list(self) -> List[Tuple[int, float]]:
        """获取节点面积列表，按面积降序排列"""
        areas = []
        for node in self._V:
            area = node.get_area()
            areas.append((node.get_id(), area))
        
        # 按面积降序排列
        return sorted(areas, key=lambda x: x[1], reverse=True)
    
    def get_neighbor_nodes_connectivity_list(self, node_id: int, power_rail: int = 0) -> List[Tuple[int, int]]:
        """获取指定节点的邻居连接性列表"""
        connectivity = {}
        for edge in self._E:
            if edge.get_power_rail() == power_rail:
                a_id, b_id = edge.get_edge_connectivity()
                if a_id == node_id:
                    connectivity[b_id] = connectivity.get(b_id, 0) + 1
                elif b_id == node_id:
                    connectivity[a_id] = connectivity.get(a_id, 0) + 1
        
        # 按连接数降序排列
        return sorted(connectivity.items(), key=lambda x: x[1], reverse=True)
    
    def embed_neighbour_nodes(self) -> int:
        """嵌入邻居节点信息"""
        for node in self._V:
            neighbors = self.get_neighbor_nodes_connectivity_list(node.get_id())
            node.set_neighbors(neighbors)
        return 0
    
    def get_neighbor_node_ids(self, node_id: int, power_rail: int = 0, ignore_self_loops: bool = True) -> Set[int]:
        """获取指定节点的邻居ID集合"""
        neighbors = set()
        for edge in self._E:
            if edge.get_power_rail() == power_rail:
                a_id, b_id = edge.get_edge_connectivity()
                if a_id == node_id:
                    if not ignore_self_loops or b_id != node_id:
                        neighbors.add(b_id)
                elif b_id == node_id:
                    if not ignore_self_loops or a_id != node_id:
                        neighbors.add(a_id)
        return neighbors
    
    def get_average_pad_position(self, node_id: int) -> List[Tuple[int, float, float, int, float, float]]:
        """计算指定节点的平均焊盘位置"""
        # 简化实现，返回空列表
        return []
    
    def get_node_by_id(self, node_id: int) -> Optional[Node]:
        """根据ID获取节点"""
        for node in self._V:
            if node.get_id() == node_id:
                return node
        return None
    
    def get_edges_by_power_rail(self, power_rail: int, abstraction_type: int) -> Set[Tuple[int, int]]:
        """根据电源轨获取边集合"""
        edges = set()
        for edge in self._E:
            if edge.get_power_rail() == power_rail:
                a_id, b_id = edge.get_edge_connectivity()
                edges.add((a_id, b_id))
        return edges
    
    def get_edges_by_net_id(self, net_id: int, abstraction_type: int) -> Set[Tuple[int, int]]:
        """根据网络ID获取边集合"""
        edges = set()
        for edge in self._E:
            if edge.get_net_id() == net_id:
                a_id, b_id = edge.get_edge_connectivity()
                edges.add((a_id, b_id))
        return edges
    
    def get_edges_by_instance_id(self, instance_id: int, power_rail: int) -> Set[Tuple[int, int]]:
        """根据实例ID获取边集合"""
        edges = set()
        for edge in self._E:
            if edge.get_power_rail() == power_rail:
                a_id, b_id = edge.get_edge_connectivity()
                if a_id == instance_id or b_id == instance_id:
                    edges.add((a_id, b_id))
        return edges
    
    def get_all_edges_by_instance_id(self, instance_id: int, power_rail: int) -> List[Edge]:
        """根据实例ID获取所有边"""
        edges = []
        for edge in self._E:
            if edge.get_power_rail() == power_rail:
                a_id, b_id = edge.get_edge_connectivity()
                if a_id == instance_id or b_id == instance_id:
                    edges.append(edge)
        return edges
    
    def partial_graph(self, filename: str, power_rail: int, unique: bool) -> int:
        """生成部分图形"""
        # 简化实现
        return 0
    
    def net_graphviz(self, filename: str, net_id: int, abstraction_type: int) -> int:
        """生成网络图形"""
        # 简化实现
        return 0
    
    def instance_graphviz(self, filename: str, instance_id: int, power_rail: int) -> int:
        """生成实例图形"""
        # 简化实现
        return 0
    
    def instance_pads_graphviz(self, filename: str, instance_id: int, power_rail: int) -> int:
        """生成实例焊盘图形"""
        # 简化实现
        return 0
    
    def partial_graph_gml(self, filename: str, power_rail: int, unique: bool) -> int:
        """生成GML格式的部分图形"""
        # 简化实现
        return 0
    
    def normalize(self) -> int:
        """标准化图形"""
        # 简化实现
        return 0
    
    def get_feature_vector(self, node_id: int, max_neighbors: int = 0) -> List[float]:
        """获取特征向量"""
        node = self.get_node_by_id(node_id)
        if not node:
            return []
        
        # 简化实现，返回基本特征
        features = []
        pos = node.get_pos()
        size = node.get_size()
        features.extend([pos[0], pos[1], size[0], size[1], node.get_orientation(), node.get_pin_count()])
        
        # 添加邻居信息
        neighbors = self.get_neighbor_nodes_connectivity_list(node_id)
        if max_neighbors > 0:
            neighbors = neighbors[:max_neighbors]
        
        for neighbor_id, connections in neighbors:
            neighbor = self.get_node_by_id(neighbor_id)
            if neighbor:
                n_pos = neighbor.get_pos()
                n_size = neighbor.get_size()
                features.extend([n_pos[0], n_pos[1], n_size[0], n_size[1], neighbor.get_orientation(), connections])
        
        return features
    
    def get_simplified_feature_vector(self, node_id: int, max_neighbors: int = 0) -> List[float]:
        """获取简化的特征向量"""
        node = self.get_node_by_id(node_id)
        if not node:
            return []
        
        # 简化特征：位置、面积、引脚数
        features = []
        pos = node.get_pos()
        area = node.get_area()
        features.extend([pos[0], pos[1], area, node.get_pin_count()])
        
        # 添加邻居信息
        neighbors = self.get_neighbor_nodes_connectivity_list(node_id)
        if max_neighbors > 0:
            neighbors = neighbors[:max_neighbors]
        
        for neighbor_id, connections in neighbors:
            neighbor = self.get_node_by_id(neighbor_id)
            if neighbor:
                n_pos = neighbor.get_pos()
                n_area = neighbor.get_area()
                features.extend([n_pos[0], n_pos[1], n_area, connections])
        
        return features
    
    def print_feature_vector(self, fv: List[float]) -> int:
        """打印特征向量"""
        print("Feature Vector:", fv)
        return 0
    
    def print_simplified_feature_vector(self, fv: List[float]) -> int:
        """打印简化的特征向量"""
        print("Simplified Feature Vector:", fv)
        return 0
    
    def normalize_feature_vector(self, fv: List[float], grid_x: float, grid_y: float) -> int:
        """标准化特征向量"""
        if len(fv) < 6:
            return -1
        
        # 标准化位置
        fv[0] /= grid_x
        fv[1] /= grid_y
        
        # 标准化尺寸
        max_size = max(fv[2], fv[3])
        if max_size > 0:
            fv[2] /= max_size
            fv[3] /= max_size
        
        # 标准化引脚数
        max_pins = max(fv[4], 1)
        fv[4] /= max_pins
        
        return 0
    
    def normalize_simplified_feature_vector(self, fv: List[float], grid_x: float, grid_y: float) -> int:
        """标准化简化的特征向量"""
        if len(fv) < 4:
            return -1
        
        # 标准化位置
        fv[0] /= grid_x
        fv[1] /= grid_y
        
        # 标准化面积
        max_area = max(fv[2], 1.0)
        fv[2] /= max_area
        
        # 标准化引脚数
        max_pins = max(fv[3], 1)
        fv[3] /= max_pins
        
        return 0
    
    def get_dimensions_of_largest_component(self) -> Tuple[float, float]:
        """获取最大组件的尺寸"""
        max_area = 0.0
        max_x = 0.0
        max_y = 0.0
        
        for node in self._V:
            area = node.get_area()
            if area > max_area:
                max_area = area
                size = node.get_size()
                max_x, max_y = size
        
        return (max_x, max_y)
    
    def get_largest_x_size(self) -> float:
        """获取最大X尺寸"""
        max_x = 0.0
        for node in self._V:
            size = node.get_size()
            max_x = max(max_x, size[0])
        return max_x
    
    def get_largest_y_size(self) -> float:
        """获取最大Y尺寸"""
        max_y = 0.0
        for node in self._V:
            size = node.get_size()
            max_y = max(max_y, size[1])
        return max_y
    
    def get_largest_pin_count(self) -> int:
        """获取最大引脚数"""
        max_pins = 0
        for node in self._V:
            max_pins = max(max_pins, node.get_pin_count())
        return max_pins
    
    def get_number_of_nodes(self) -> int:
        """获取节点数量"""
        return len(self._V)
    
    def get_number_of_edges(self) -> int:
        """获取边数量"""
        return len(self._E)
    
    def get_nodes(self) -> List[Node]:
        """获取节点列表"""
        return self._V.copy()
    
    def get_edges(self) -> List[Edge]:
        """获取边列表"""
        return self._E.copy()
    
    def set_component_origin_to_zero(self, board: Board) -> int:
        """设置组件原点为零"""
        # 简化实现
        return 0
    
    def reset_component_origin(self, board: Board) -> int:
        """重置组件原点"""
        # 简化实现
        return 0
    
    def set_original_component_origin(self, board: Board) -> int:
        """设置原始组件原点"""
        # 简化实现
        return 0
    
    def get_nets_associated_with_instance(self, instance_id: int, power_rail: int) -> Set[int]:
        """获取与实例关联的网络"""
        nets = set()
        for edge in self._E:
            if edge.get_power_rail() == power_rail:
                a_id, b_id = edge.get_edge_connectivity()
                if a_id == instance_id or b_id == instance_id:
                    nets.add(edge.get_net_id())
        return nets
    
    def calc_hpwl(self, do_not_ignore_unplaced: bool = False) -> float:
        """计算HPWL"""
        if not do_not_ignore_unplaced:
            # 只考虑已放置的节点
            placed_nodes = [node for node in self._V if node.get_is_placed()]
        else:
            placed_nodes = self._V
        
        if not placed_nodes:
            return 0.0
        
        # 计算边界框
        min_x = min(node.get_pos()[0] for node in placed_nodes)
        max_x = max(node.get_pos()[0] for node in placed_nodes)
        min_y = min(node.get_pos()[1] for node in placed_nodes)
        max_y = max(node.get_pos()[1] for node in placed_nodes)
        
        return (max_x - min_x) + (max_y - min_y)
    
    def calc_full_hpwl(self) -> float:
        """计算完整HPWL"""
        return self.calc_hpwl(True)
    
    def get_hpwl(self) -> float:
        """获取HPWL"""
        return self._hpwl
    
    def set_hpwl(self, hpwl: float) -> None:
        """设置HPWL"""
        self._hpwl = hpwl
    
    def update_hpwl(self, do_not_ignore_unplaced: bool = False) -> None:
        """更新HPWL"""
        self._hpwl = self.calc_hpwl(do_not_ignore_unplaced)
    
    def components_placed(self) -> int:
        """获取已放置的组件数量"""
        return sum(1 for node in self._V if node.get_is_placed())
    
    def components_to_place(self) -> int:
        """获取待放置的组件数量"""
        return sum(1 for node in self._V if not node.get_is_placed())
    
    def graph_placement_completion(self) -> float:
        """获取图形放置完成度"""
        if not self._V:
            return 0.0
        return self.components_placed() / len(self._V)
    
    def print_graph_placement_status(self) -> None:
        """打印图形放置状态"""
        placed = self.components_placed()
        total = len(self._V)
        completion = self.graph_placement_completion()
        print(f"Placement Status: {placed}/{total} ({completion:.2%})")
    
    def write_nodes_to_file(self, filename: str, format_type: int) -> int:
        """将节点写入文件"""
        try:
            with open(filename, 'w') as f:
                for node in self._V:
                    if format_type == self.LONG:
                        node.print_to_console(True)
                    else:
                        node.print_to_console(False)
            return 0
        except Exception:
            return -1
    
    def write_edges_to_file(self, filename: str, format_type: int) -> int:
        """将边写入文件"""
        try:
            with open(filename, 'w') as f:
                for edge in self._E:
                    if format_type == self.LONG:
                        edge.print_to_console(True)
                    else:
                        edge.print_to_console(False)
            return 0
        except Exception:
            return -1
    
    def write_optimals_to_file(self, filename: str) -> int:
        """将优化信息写入文件"""
        try:
            with open(filename, 'w') as f:
                for node in self._V:
                    optimal = node._optimal
                    f.write(f"{optimal.get_id()},{optimal.get_name()},"
                           f"{optimal.get_euclidean_distance():.6f},{optimal.get_hpwl():.6f}\n")
            return 0
        except Exception:
            return -1
    
    def update_node_optimal(self, line: str) -> int:
        """更新节点优化信息"""
        try:
            fields = Utils.parse_csv_line(line)
            if len(fields) >= 4:
                node_id = Utils.safe_int(fields[0])
                node = self.get_node_by_id(node_id)
                if node:
                    node.set_opt_name(fields[1])
                    node.set_opt_euclidean_distance(Utils.safe_float(fields[2]))
                    node.set_opt_hpwl(Utils.safe_float(fields[3]))
                    return 0
            return -1
        except Exception:
            return -1
    
    def print(self, print_csv: bool) -> None:
        """打印图形信息"""
        print(f"Graph: {self._graph_name}")
        print(f"  Nodes: {len(self._V)}")
        print(f"  Edges: {len(self._E)}")
        print(f"  HPWL: {self._hpwl:.6f}")
        
        if print_csv:
            print("Nodes:")
            for node in self._V:
                node.print(True)
            print("Edges:")
            for edge in self._E:
                edge.print(True)
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"Graph({self._graph_name}, nodes={len(self._V)}, edges={len(self._E)})"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return self.__str__() 
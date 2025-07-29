# Graph类 C++与Python对应关系

## 概述

Graph类是netlist_graph库的核心类，表示电路网络图，管理节点和边的连接关系，提供图形分析、特征向量生成、HPWL计算等功能。

## 文件对应关系

| C++文件 | Python文件 | 说明 |
|---------|------------|------|
| `include/graph.hpp` | `netlist_graph/graph.py` | 图形类实现 |

## 类定义对比

### C++版本 (graph.hpp)

```cpp
class graph
{
private:
    std::vector<node> _V;    // 原始节点列表（不可修改）
    std::vector<node> V;     // 当前节点列表
    std::vector<edge> E;     // 边列表
    std::string graph_name;
    uint32_t graph_id;
    std::string kicad_pcb_file;
    double hpwl;

public:
    graph(void);
    // ... 方法声明
};
```

### Python版本 (graph.py)

```python
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
```

## 成员变量对应关系

| C++成员变量 | Python成员变量 | 类型 | 说明 |
|-------------|----------------|------|------|
| `_V` | `_V_original` | `vector<node>` | 原始节点列表（不可修改） |
| `V` | `_V` | `vector<node>` | 当前节点列表 |
| `E` | `_E` | `vector<edge>` | 边列表 |
| `graph_name` | `_graph_name` | `string` | 图形名称 |
| `graph_id` | `_graph_id` | `uint32_t` | 图形ID |
| `kicad_pcb_file` | `_kicad_pcb_file` | `string` | KiCad PCB文件名 |
| `hpwl` | `_hpwl` | `double` | 半周长线长 |

## 枚举定义

| C++枚举 | Python枚举 | 值 | 说明 |
|---------|------------|----|------|
| `COMPONENT` | `COMPONENT` | 0 | 组件抽象 |
| `PADD` | `PADD` | 1 | 焊盘抽象 |
| `SHORT` | `SHORT` | 0 | 短格式 |
| `LONG` | `LONG` | 1 | 长格式 |

## 方法对应关系

### 构造函数

| C++方法 | Python方法 | 功能 |
|---------|------------|------|
| `graph(void)` | `__init__(self)` | 默认构造函数 |

**C++实现：**
```cpp
graph(void) {
    graph_name = "";
    graph_id = 0;
    kicad_pcb_file = "";
    hpwl = 0.0;
}
```

**Python实现：**
```python
def __init__(self):
    self._V_original = []
    self._V = []
    self._E = []
    self._graph_name = ""
    self._graph_id = 0
    self._kicad_pcb_file = ""
    self._hpwl = 0.0
```

### 节点管理方法

| C++方法 | Python方法 | 功能 | 参数 | 返回值 |
|---------|------------|------|------|--------|
| `add_node_from_string_short()` | `add_node_from_string_short()` | 从短格式字符串添加节点 | `string` | `int8_t` |
| `add_node_from_string_long()` | `add_node_from_string_long()` | 从长格式字符串添加节点 | `string` | `int8_t` |
| `get_number_of_nodes()` | `get_number_of_nodes()` | 获取节点数量 | 无 | `int` |
| `get_nodes()` | `get_nodes()` | 获取节点列表 | 无 | `vector<node>` |

**C++实现：**
```cpp
int8_t add_node_from_string_short(std::string s) {
    node n;
    if (n.create_from_string_short(s) == 0) {
        V.push_back(n);
        return 0;
    }
    return -1;
}

int get_number_of_nodes() { return V.size(); }
std::vector<node> get_nodes() { return V; }
```

**Python实现：**
```python
def add_node_from_string_short(self, s: str) -> int:
    node = Node()
    if node.create_from_string_short(s) == 0:
        self._V.append(node)
        return 0
    return -1

def get_number_of_nodes(self) -> int:
    return len(self._V)

def get_nodes(self) -> List[Node]:
    return self._V.copy()
```

### 边管理方法

| C++方法 | Python方法 | 功能 | 参数 | 返回值 |
|---------|------------|------|------|--------|
| `add_edge_from_string_short()` | `add_edge_from_string_short()` | 从短格式字符串添加边 | `string` | `int8_t` |
| `add_edge_from_string_long()` | `add_edge_from_string_long()` | 从长格式字符串添加边 | `string` | `int8_t` |
| `get_number_of_edges()` | `get_number_of_edges()` | 获取边数量 | 无 | `int` |
| `get_edges()` | `get_edges()` | 获取边列表 | 无 | `vector<edge>` |

**C++实现：**
```cpp
int8_t add_edge_from_string_short(std::string s) {
    edge e;
    if (e.create_from_string_short(s) == 0) {
        E.push_back(e);
        return 0;
    }
    return -1;
}

int get_number_of_edges() { return E.size(); }
std::vector<edge> get_edges() { return E; }
```

**Python实现：**
```python
def add_edge_from_string_short(self, s: str) -> int:
    edge = Edge()
    if edge.create_from_string_short(s) == 0:
        self._E.append(edge)
        return 0
    return -1

def get_number_of_edges(self) -> int:
    return len(self._E)

def get_edges(self) -> List[Edge]:
    return self._E.copy()
```

### 节点查询方法

| C++方法 | Python方法 | 功能 | 参数 | 返回值 |
|---------|------------|------|------|--------|
| `get_node_name_by_id()` | `get_node_name_by_id()` | 根据ID获取节点名称 | `int id` | `string` |
| `get_node_by_id()` | `get_node_by_id()` | 根据ID获取节点 | `int id` | `node*` |

**C++实现：**
```cpp
std::string get_node_name_by_id(int id) {
    for (const auto& node : V) {
        if (node.get_id() == id) {
            return node.get_name();
        }
    }
    return "";
}

node* get_node_by_id(int id) {
    for (auto& node : V) {
        if (node.get_id() == id) {
            return &node;
        }
    }
    return nullptr;
}
```

**Python实现：**
```python
def get_node_name_by_id(self, node_id: int) -> str:
    for node in self._V:
        if node.get_id() == node_id:
            return node.get_name()
    return ""

def get_node_by_id(self, node_id: int) -> Optional[Node]:
    for node in self._V:
        if node.get_id() == node_id:
            return node
    return None
```

### 网络分析方法

| C++方法 | Python方法 | 功能 | 参数 | 返回值 |
|---------|------------|------|------|--------|
| `get_set_net_ids()` | `get_set_net_ids()` | 获取所有网络ID集合 | 无 | `set<int>` |
| `get_edges_by_net_id()` | `get_edges_by_net_id()` | 根据网络ID获取边集合 | `(int net_id, int type)` | `set<pair<int,int>>` |
| `get_edges_by_power_rail()` | `get_edges_by_power_rail()` | 根据电源轨获取边集合 | `(int power_rail, int type)` | `set<pair<int,int>>` |

**C++实现：**
```cpp
std::set<int> get_set_net_ids() {
    std::set<int> net_ids;
    for (const auto& edge : E) {
        net_ids.insert(edge.get_net_id());
    }
    return net_ids;
}

std::set<std::pair<int,int>> get_edges_by_net_id(int net_id, ABSTRACTION type) {
    std::set<std::pair<int,int>> edges;
    for (const auto& edge : E) {
        if (edge.get_net_id() == net_id) {
            edges.insert(edge.get_edge_connectivity());
        }
    }
    return edges;
}
```

**Python实现：**
```python
def get_set_net_ids(self) -> Set[int]:
    net_ids = set()
    for edge in self._E:
        net_ids.add(edge.get_net_id())
    return net_ids

def get_edges_by_net_id(self, net_id: int, abstraction_type: int) -> Set[Tuple[int, int]]:
    edges = set()
    for edge in self._E:
        if edge.get_net_id() == net_id:
            a_id, b_id = edge.get_edge_connectivity()
            edges.add((a_id, b_id))
    return edges
```

### 连接性分析方法

| C++方法 | Python方法 | 功能 | 参数 | 返回值 |
|---------|------------|------|------|--------|
| `get_nodes_connectivity_list()` | `get_nodes_connectivity_list()` | 获取节点连接性列表 | `int power_rail` | `vector<pair<int,int>>` |
| `get_neighbor_nodes_connectivity_list()` | `get_neighbor_nodes_connectivity_list()` | 获取邻居连接性列表 | `(int id, int power_rail)` | `vector<pair<int,int>>` |
| `get_neighbor_node_ids()` | `get_neighbor_node_ids()` | 获取邻居节点ID集合 | `(int id, int power_rail, bool ignore_self_loops)` | `set<int>` |

**C++实现：**
```cpp
std::vector<std::pair<int,int>> get_nodes_connectivity_list(int power_rail) {
    std::map<int, int> connectivity;
    for (const auto& edge : E) {
        if (edge.get_power_rail() == power_rail) {
            auto conn = edge.get_edge_connectivity();
            connectivity[conn.first]++;
            connectivity[conn.second]++;
        }
    }
    
    std::vector<std::pair<int,int>> result;
    for (const auto& pair : connectivity) {
        result.push_back(pair);
    }
    std::sort(result.begin(), result.end(), 
              [](const auto& a, const auto& b) { return a.second > b.second; });
    return result;
}
```

**Python实现：**
```python
def get_nodes_connectivity_list(self, power_rail: int = 0) -> List[Tuple[int, int]]:
    connectivity = {}
    for edge in self._E:
        if edge.get_power_rail() == power_rail:
            a_id, b_id = edge.get_edge_connectivity()
            connectivity[a_id] = connectivity.get(a_id, 0) + 1
            connectivity[b_id] = connectivity.get(b_id, 0) + 1
    
    # 按连接数降序排列
    return sorted(connectivity.items(), key=lambda x: x[1], reverse=True)
```

### HPWL计算方法

| C++方法 | Python方法 | 功能 | 参数 | 返回值 |
|---------|------------|------|------|--------|
| `calc_hpwl()` | `calc_hpwl()` | 计算HPWL | `bool do_not_ignore_unplaced` | `double` |
| `calc_full_hpwl()` | `calc_full_hpwl()` | 计算完整HPWL | 无 | `double` |
| `get_hpwl()` | `get_hpwl()` | 获取HPWL | 无 | `double` |
| `set_hpwl()` | `set_hpwl()` | 设置HPWL | `double hpwl` | 无 |
| `update_hpwl()` | `update_hpwl()` | 更新HPWL | `bool do_not_ignore_unplaced` | 无 |

**C++实现：**
```cpp
double calc_hpwl(bool do_not_ignore_unplaced = false) {
    std::vector<node> nodes_to_consider;
    
    if (do_not_ignore_unplaced) {
        nodes_to_consider = V;
    } else {
        for (const auto& node : V) {
            if (node.get_isPlaced()) {
                nodes_to_consider.push_back(node);
            }
        }
    }
    
    if (nodes_to_consider.empty()) return 0.0;
    
    double min_x = nodes_to_consider[0].get_pos().first;
    double max_x = nodes_to_consider[0].get_pos().first;
    double min_y = nodes_to_consider[0].get_pos().second;
    double max_y = nodes_to_consider[0].get_pos().second;
    
    for (const auto& node : nodes_to_consider) {
        auto pos = node.get_pos();
        min_x = std::min(min_x, pos.first);
        max_x = std::max(max_x, pos.first);
        min_y = std::min(min_y, pos.second);
        max_y = std::max(max_y, pos.second);
    }
    
    return (max_x - min_x) + (max_y - min_y);
}
```

**Python实现：**
```python
def calc_hpwl(self, do_not_ignore_unplaced: bool = False) -> float:
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
```

### 特征向量方法

| C++方法 | Python方法 | 功能 | 参数 | 返回值 |
|---------|------------|------|------|--------|
| `get_feature_vector()` | `get_feature_vector()` | 获取特征向量 | `(int id, vector<double>& fv, int MAX_NEIGHBORS)` | `int` |
| `get_simplified_feature_vector()` | `get_simplified_feature_vector()` | 获取简化特征向量 | `(int id, vector<double>& fv, int MAX_NEIGHBORS)` | `int` |
| `normalize_feature_vector()` | `normalize_feature_vector()` | 标准化特征向量 | `(vector<double>& fv, double grd_x, double grd_y)` | `int` |

**C++实现：**
```cpp
int get_simplified_feature_vector(int id, std::vector<double> &fv, int MAX_NEIGHBORS=0) {
    node* n = get_node_by_id(id);
    if (!n) return -1;
    
    fv.clear();
    auto pos = n->get_pos();
    double area = n->get_area();
    fv.push_back(pos.first);
    fv.push_back(pos.second);
    fv.push_back(area);
    fv.push_back(n->get_pin_count());
    
    // 添加邻居信息
    auto neighbors = get_neighbor_nodes_connectivity_list(id);
    if (MAX_NEIGHBORS > 0 && neighbors.size() > MAX_NEIGHBORS) {
        neighbors.resize(MAX_NEIGHBORS);
    }
    
    for (const auto& neighbor : neighbors) {
        node* neighbor_node = get_node_by_id(neighbor.first);
        if (neighbor_node) {
            auto n_pos = neighbor_node->get_pos();
            double n_area = neighbor_node->get_area();
            fv.push_back(n_pos.first);
            fv.push_back(n_pos.second);
            fv.push_back(n_area);
            fv.push_back(neighbor.second);
        }
    }
    
    return 0;
}
```

**Python实现：**
```python
def get_simplified_feature_vector(self, node_id: int, max_neighbors: int = 0) -> List[float]:
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
```

### 文件操作方法

| C++方法 | Python方法 | 功能 | 参数 | 返回值 |
|---------|------------|------|------|--------|
| `write_nodes_to_file()` | `write_nodes_to_file()` | 将节点写入文件 | `(string filename, int format)` | `int` |
| `write_edges_to_file()` | `write_edges_to_file()` | 将边写入文件 | `(string filename, int format)` | `int` |
| `write_optimals_to_file()` | `write_optimals_to_file()` | 将优化信息写入文件 | `string filename` | `int` |

**C++实现：**
```cpp
int write_nodes_to_file(std::string filename, FILE_FORMAT format) {
    std::ofstream file(filename);
    if (!file.is_open()) return -1;
    
    for (const auto& node : V) {
        if (format == SHORT) {
            file << node.get_id() << "," << node.get_name() << ","
                 << node.get_size().first << "," << node.get_size().second << ","
                 << node.get_pos().first << "," << node.get_pos().second << ","
                 << node.get_orientation() << "," << node.get_layer() << ","
                 << (node.get_isPlaced() ? 1 : 0) << "," << node.get_pin_count() << ","
                 << node.get_smd_pin_count() << "," << node.get_th_pin_count() << ","
                 << node.get_type() << std::endl;
        } else {
            // 长格式输出
            node.print_to_console(true);
        }
    }
    return 0;
}
```

**Python实现：**
```python
def write_nodes_to_file(self, filename: str, format_type: int) -> int:
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
```

### 统计和输出方法

| C++方法 | Python方法 | 功能 | 参数 | 返回值 |
|---------|------------|------|------|--------|
| `statistics()` | `statistics()` | 打印图形统计信息 | 无 | `int` |
| `print()` | `print()` | 打印图形信息 | `bool print_csv` | 无 |

**C++实现：**
```cpp
int statistics() {
    std::cout << "Graph Statistics:" << std::endl;
    std::cout << "  Nodes: " << V.size() << std::endl;
    std::cout << "  Edges: " << E.size() << std::endl;
    std::cout << "  Nets: " << get_set_net_ids().size() << std::endl;
    return 0;
}
```

**Python实现：**
```python
def statistics(self) -> int:
    print(f"Graph Statistics:")
    print(f"  Nodes: {len(self._V)}")
    print(f"  Edges: {len(self._E)}")
    print(f"  Nets: {len(self.get_set_net_ids())}")
    return 0
```

## 主要差异

### 1. 内存管理

**C++版本：**
- 使用STL容器管理数据
- 需要手动管理内存
- 使用引用和指针

**Python版本：**
- 使用Python列表管理数据
- 自动垃圾回收
- 使用值传递

### 2. 算法实现

**C++版本：**
- 使用STL算法库
- 手动实现排序和查找
- 更精细的内存控制

**Python版本：**
- 使用Python内置函数
- 列表推导式简化代码
- 更简洁的实现

### 3. 错误处理

**C++版本：**
- 返回错误码
- 使用异常处理
- 需要检查返回值

**Python版本：**
- 抛出异常
- 使用try-except
- 更友好的错误信息

## 性能对比

| 操作 | C++性能 | Python性能 | 说明 |
|------|---------|------------|------|
| 图形构建 | 快 | 中等 | Python对象创建开销 |
| 节点查询 | 快 | 中等 | Python循环开销 |
| 边遍历 | 快 | 中等 | Python迭代开销 |
| HPWL计算 | 快 | 中等 | Python数值计算开销 |
| 特征向量生成 | 快 | 中等 | Python列表操作开销 |

## 使用建议

1. **选择C++版本**：当需要最高性能、大规模图形处理时
2. **选择Python版本**：当需要快速开发、原型设计时
3. **混合使用**：可以用C++实现核心算法，Python实现业务逻辑 
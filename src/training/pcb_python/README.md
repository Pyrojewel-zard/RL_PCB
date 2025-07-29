# Netlist Graph Python库

这是 `netlist_graph` C++库的纯Python实现，用于处理电路网络图，管理节点和边的连接关系。

## 功能特性

- **纯Python实现**：无需C++依赖，易于安装和使用
- **完整的API兼容性**：与原始C++库保持API兼容
- **电路网络图处理**：支持节点、边、网络的管理
- **图形分析功能**：连接性分析、特征向量生成、HPWL计算
- **文件格式支持**：支持.nodes、.edges、.board文件格式

## 安装

无需安装，直接使用Python文件即可：

```bash
# 将netlist_graph文件夹添加到Python路径
export PYTHONPATH=$PYTHONPATH:/path/to/pcb_python
```

## 快速开始

### 基本使用

```python
from netlist_graph import Graph, Node, Edge, Board

# 创建图形
graph = Graph()

# 添加节点
node = Node()
node.set_id(0)
node.set_name("LED1")
node.set_size((3.35, 1.85))
node.set_pos((156.31, 50.79))
graph._V.append(node)

# 添加边
edge = Edge()
edge.set_id(0, 4)
edge.set_id(1, 6)
edge.set_net_id(1)
edge.set_net_name("Net1")
graph._E.append(edge)

# 分析图形
print(f"节点数量: {graph.get_number_of_nodes()}")
print(f"边数量: {graph.get_number_of_edges()}")
print(f"HPWL: {graph.calc_hpwl():.2f}")
```

### 从文件读取

```python
from netlist_graph import Graph

# 创建图形
graph = Graph()

# 从.nodes文件读取节点
with open("nodes.txt", "r") as f:
    for line in f:
        graph.add_node_from_string_short(line.strip())

# 从.edges文件读取边
with open("edges.txt", "r") as f:
    for line in f:
        graph.add_edge_from_string_short(line.strip())

# 分析图形
graph.statistics()
```

### 图形分析

```python
# 获取节点连接性
connectivity = graph.get_nodes_connectivity_list()
print("节点连接性:", connectivity)

# 获取邻居节点
neighbors = graph.get_neighbor_node_ids(0)
print("节点0的邻居:", neighbors)

# 生成特征向量
fv = graph.get_simplified_feature_vector(0)
print("特征向量:", fv)
```

## 核心类

### Graph类

主要的图形管理类，包含以下主要方法：

- `add_node_from_string_short()`: 从短格式字符串添加节点
- `add_edge_from_string_short()`: 从短格式字符串添加边
- `get_nodes_connectivity_list()`: 获取节点连接性列表
- `get_neighbor_node_ids()`: 获取邻居节点ID
- `calc_hpwl()`: 计算HPWL（半周长线长）
- `get_feature_vector()`: 生成特征向量

### Node类

表示电路图中的节点（组件），包含：

- 基本信息：ID、名称、尺寸、位置
- 电气特性：引脚数、类型、层信息
- 优化信息：欧几里得距离、HPWL

### Edge类

表示电路图中的边（连接），包含：

- 连接信息：两个节点的ID和名称
- 网络信息：网络ID、名称、电源轨
- 位置信息：焊盘位置和尺寸

### Board类

表示电路板信息，包含：

- 边界框信息：最小/最大坐标
- 尺寸信息：宽度、高度
- 文件关联：KiCad PCB文件

### Utils类

工具类，提供通用功能：

- 距离计算：欧几里得距离、曼哈顿距离
- 文件解析：CSV解析、数值转换
- 几何计算：HPWL计算、边界框计算

## 文件格式

### .nodes文件格式

每行包含一个节点的信息：
```
ID,名称,尺寸X,尺寸Y,位置X,位置Y,方向,层,已放置,引脚总数,SMD引脚数,通孔引脚数,类型
```

示例：
```
0,LED1,3.35,1.85,156.31,50.79,0,0,0,2,2,0,4
```

### .edges文件格式

每行包含一个边的信息：
```
节点A_ID,节点A名称,节点A焊盘ID,节点A尺寸X,节点A尺寸Y,节点A位置X,节点A位置Y,节点A已放置,节点B_ID,节点B名称,节点B焊盘ID,节点B尺寸X,节点B尺寸Y,节点B位置X,节点B位置Y,节点B已放置,网络ID,网络名称,电源轨
```

示例：
```
4,0,1,1.075,0.95,-0.8625,0,0,6,2,3,0.6,1.2,-1.25,0.95,0,1,"Net-(C1-Pad1)",2,0,0
```

### .board文件格式

包含电路板边界信息：
```
bb_min_x,100.00000000
bb_min_y,80.00000000
bb_max_x,120.00000000
bb_max_y,100.00000000
```

## 测试

运行测试文件验证功能：

```bash
python test_netlist_graph.py
```

## 与C++版本的差异

1. **性能**：Python版本在性能上可能不如C++版本，但对于大多数应用场景已经足够
2. **内存管理**：Python自动管理内存，无需手动释放
3. **错误处理**：Python版本提供更友好的错误信息
4. **扩展性**：更容易添加新功能和修改现有功能

## 贡献

欢迎提交Issue和Pull Request来改进这个Python实现。

## 许可证

本项目遵循原C++项目的许可证条款。 
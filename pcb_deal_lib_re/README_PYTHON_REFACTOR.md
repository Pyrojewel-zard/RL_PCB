# PCB库Python重构

## 概述

本项目将原有的C++实现的PCB库重构为纯Python实现，基于`pcb_python`中的`netlist_graph`模块。

## 重构内容

### 1. PCB模块重构 (`pcb/pcb_python.py`)

**功能：**
- PCB文件读写
- 图形和电路板信息管理
- 从单独文件创建PCB文件
- PCB文件追加功能

**主要类：**
- `PCB`: 表示一个PCB文件，包含图形和电路板信息
- `VPtrPCBs`: PCB指针向量类，用于管理多个PCB对象

**主要方法：**
- `read_pcb_file()`: 读取PCB文件
- `write_pcb_file()`: 写入PCB文件
- `write_pcb_file_from_individual_files()`: 从单独文件创建PCB文件
- `append_pcb_file_from_individual_files()`: 追加到现有PCB文件
- `get_graph()` / `set_graph()`: 获取/设置图形信息
- `get_board()` / `set_board()`: 获取/设置电路板信息

### 2. Netlist Graph模块重构 (`netlist_graph/netlist_graph_python.py`)

**功能：**
- 重新导出`pcb_python`中的`netlist_graph`模块
- 保持API兼容性
- 提供图形分析功能

**导出的类：**
- `Graph`: 图形类，管理节点和边
- `Node`: 节点类，表示电路组件
- `Edge`: 边类，表示连接关系
- `Board`: 电路板类，管理电路板信息
- `Optimal`: 优化信息类
- `Utils`: 工具类

### 3. 主模块重构 (`pcb/main_python.py`)

**功能：**
- 演示重构后的功能
- 展示如何使用新的Python模块
- 提供完整的示例代码

**演示内容：**
- PCB文件创建
- PCB文件读取
- 图形分析
- 统计信息显示

### 4. 解析器模块重构 (`pcb/parse_graph_from_pcb_file_python.py`)

**功能：**
- 解析PCB文件并提取图形信息
- 处理节点和边数据
- 计算HPWL等指标

**主要函数：**
- `parse_pcb_file()`: 解析PCB文件
- `main()`: 主函数，提供示例

## 使用方法

### 基本使用

```python
# 导入模块
from pcb_python import PCB, VPtrPCBs, read_pcb_file
from netlist_graph_python import Graph, Node, Edge, Board

# 创建PCB对象
p = PCB()

# 读取PCB文件
result = p.read_pcb_file("example.pcb")

# 获取图形和电路板信息
g = Graph()
b = Board()
p.get_graph(g)
p.get_board(b)

# 分析图形
g.statistics()
hpwl = g.calc_hpwl()
```

### 从单独文件创建PCB

```python
# 从节点、边、电路板文件创建PCB
nodes_file = "nodes.csv"
edges_file = "edges.csv"
board_file = "board.csv"
output_file = "output.pcb"

result = p.write_pcb_file_from_individual_files(
    output_file, nodes_file, edges_file, board_file, True
)
```

### 使用VPtrPCBs

```python
# 创建PCB向量
pv = VPtrPCBs()

# 读取PCB文件到向量
read_pcb_file("example.pcb", pv)

# 访问第一个PCB
if len(pv) > 0:
    pcb = pv[0]
    pcb.print_statistics()
```

## 文件格式

### PCB文件格式

PCB文件采用分段格式：

```
[GRAPH]
graph_name,example_graph
graph_id,1
kicad_pcb_file,example.kicad_pcb

[BOARD]
bb_min_x,0.00000000
bb_min_y,0.00000000
bb_max_x,100.00000000
bb_max_y,80.00000000
board_name,Example Board

[NODES]
0,LED1,3.35,1.85,156.31,50.79,0,0,0,2,2,0,4
1,R2,3.7,1.9,151.735,50.815,0,0,0,2,2,0,1

[EDGES]
4,0,1,1.075,0.95,-0.8625,0,0,6,2,3,0.6,1.2,-1.25,0.95,0,1,"Net-(C1-Pad1)",2,0,0
```

### 节点文件格式

每行包含：`ID,名称,宽度,高度,X坐标,Y坐标,方向,层,已放置,引脚数,SMD引脚数,通孔引脚数,类型`

### 边文件格式

每行包含：`节点A_ID,节点A名称,节点A焊盘ID,节点A宽度,节点A高度,节点A_X,节点A_Y,节点A已放置,节点B_ID,节点B名称,节点B焊盘ID,节点B宽度,节点B高度,节点B_X,节点B_Y,节点B已放置,网络ID,网络名称,电源轨`

## 优势

1. **纯Python实现**: 无需C++编译，跨平台兼容
2. **易于维护**: Python代码更易读、调试和修改
3. **丰富的生态系统**: 可以利用Python的丰富库
4. **快速开发**: Python开发效率更高
5. **向后兼容**: 保持与原有API的兼容性

## 依赖

- Python 3.6+
- `pcb_python`模块（包含`netlist_graph`）

## 测试

运行测试脚本：

```bash
# 测试主模块
python pcb/main_python.py

# 测试解析器
python pcb/parse_graph_from_pcb_file_python.py
```

## 注意事项

1. 确保`pcb_python`模块路径正确
2. 文件路径使用相对路径或绝对路径
3. 处理异常情况，如文件不存在等
4. 注意内存使用，大文件可能需要优化

## 未来改进

1. 添加更多图形分析算法
2. 优化大文件处理性能
3. 添加可视化功能
4. 增加单元测试覆盖
5. 添加更多文档和示例 
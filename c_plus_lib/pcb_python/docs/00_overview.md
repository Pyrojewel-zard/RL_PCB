# PCB Netlist库 C++与Python对应关系总览

## 概述

本文档详细描述了`pcb_netlist`目录下核心类的C++和Python实现对应关系。该库主要用于PCB电路网络图处理，包含节点、边、图形、电路板等核心概念。

## 库结构对比

### C++版本结构

```
pcb_netlist/
├── include/
│   ├── utils.hpp          # 工具函数
│   ├── optimal.hpp        # 优化信息类
│   ├── node.hpp          # 节点类
│   ├── edge.hpp          # 边类
│   ├── board.hpp         # 电路板类
│   └── graph.hpp         # 图形类
├── src/
│   └── *.cpp             # C++实现文件
└── swig/
    └── *.i               # SWIG接口文件
```

### Python版本结构

```
pcb_python/
├── netlist_graph/
│   ├── __init__.py       # 包初始化
│   ├── utils.py          # 工具类
│   ├── optimal.py        # 优化信息类
│   ├── node.py           # 节点类
│   ├── edge.py           # 边类
│   ├── board.py          # 电路板类
│   └── graph.py          # 图形类
├── test_netlist_graph.py # 测试脚本
└── README.md             # 使用说明
```

## 核心类对应关系

| C++类 | Python类 | 主要功能 | 文档链接 |
|-------|----------|----------|----------|
| `utils` | `Utils` | 工具函数、距离计算、文件解析 | [Utils对比](./01_utils_comparison.md) |
| `optimal` | `Optimal` | 优化信息存储、指标管理 | [Optimal对比](./05_optimal_comparison.md) |
| `node` | `Node` | 电路节点、组件信息管理 | [Node对比](./02_node_comparison.md) |
| `edge` | `Edge` | 电路连接、网络信息管理 | [Edge对比](./03_edge_comparison.md) |
| `board` | `Board` | 电路板、几何信息管理 | [Board对比](./06_board_comparison.md) |
| `graph` | `Graph` | 网络图、连接性分析 | [Graph对比](./04_graph_comparison.md) |

## 主要特性对比

### 1. 语言特性

| 特性 | C++版本 | Python版本 | 说明 |
|------|---------|------------|------|
| 类型系统 | 强类型、编译时检查 | 动态类型、运行时检查 | Python更灵活但性能较低 |
| 内存管理 | 手动管理 | 自动垃圾回收 | Python更安全但开销更大 |
| 错误处理 | 异常处理、错误码 | 异常处理 | Python异常处理更友好 |
| 模板/泛型 | 模板支持 | 类型提示 | C++模板更强大 |

### 2. 性能特征

| 操作类型 | C++性能 | Python性能 | 推荐使用 |
|----------|---------|------------|----------|
| 数值计算 | 极快 | 中等 | C++ |
| 字符串处理 | 快 | 快 | 相当 |
| 对象创建 | 快 | 中等 | C++ |
| 文件I/O | 快 | 快 | 相当 |
| 图形算法 | 快 | 中等 | C++ |

### 3. 开发效率

| 开发方面 | C++版本 | Python版本 | 说明 |
|----------|---------|------------|------|
| 代码简洁性 | 中等 | 高 | Python语法更简洁 |
| 调试便利性 | 中等 | 高 | Python调试更友好 |
| 原型开发 | 慢 | 快 | Python适合快速原型 |
| 维护性 | 中等 | 高 | Python代码更易维护 |

## 数据流对比

### C++版本数据流

```cpp
// 创建图形
graph g;
// 添加节点
node n;
n.create_from_string_short("1,resistor,1.0,2.0,10.0,20.0,0.0,1,1,2,1,1,0");
g.add_node_from_string_short("1,resistor,1.0,2.0,10.0,20.0,0.0,1,1,2,1,1,0");
// 添加边
edge e;
e.create_from_string_short("1,resistor,1,1.0,2.0,10.0,20.0,1,2,capacitor,2,2.0,3.0,30.0,40.0,1,1,net1,0");
g.add_edge_from_string_short("1,resistor,1,1.0,2.0,10.0,20.0,1,2,capacitor,2,2.0,3.0,30.0,40.0,1,1,net1,0");
// 计算HPWL
double hpwl = g.calc_hpwl();
```

### Python版本数据流

```python
# 创建图形
g = Graph()
# 添加节点
node = Node()
node.create_from_string_short("1,resistor,1.0,2.0,10.0,20.0,0.0,1,1,2,1,1,0")
g.add_node_from_string_short("1,resistor,1.0,2.0,10.0,20.0,0.0,1,1,2,1,1,0")
# 添加边
edge = Edge()
edge.create_from_string_short("1,resistor,1,1.0,2.0,10.0,20.0,1,2,capacitor,2,2.0,3.0,30.0,40.0,1,1,net1,0")
g.add_edge_from_string_short("1,resistor,1,1.0,2.0,10.0,20.0,1,2,capacitor,2,2.0,3.0,30.0,40.0,1,1,net1,0")
# 计算HPWL
hpwl = g.calc_hpwl()
```

## 使用场景建议

### 选择C++版本的场景

1. **高性能要求**：需要处理大规模电路网络图
2. **实时系统**：需要低延迟的响应
3. **资源受限**：内存和CPU资源有限
4. **系统级编程**：需要与底层系统交互
5. **数值计算密集**：大量数学计算和优化算法

### 选择Python版本的场景

1. **快速原型**：需要快速验证算法和概念
2. **脚本处理**：自动化数据处理和分析
3. **研究开发**：算法研究和实验
4. **集成开发**：与其他Python库集成
5. **教学演示**：代码更易理解和教学

### 混合使用策略

1. **核心算法用C++**：将性能关键的算法用C++实现
2. **业务逻辑用Python**：用Python实现高层业务逻辑
3. **SWIG接口**：通过SWIG将C++代码包装为Python模块
4. **数据交换**：通过文件或内存共享数据

## 迁移指南

### 从C++迁移到Python

1. **语法转换**：
   - `std::vector` → `list`
   - `std::string` → `str`
   - `std::pair` → `tuple`
   - 指针 → 对象引用

2. **内存管理**：
   - 删除手动内存管理代码
   - 使用Python的自动垃圾回收

3. **错误处理**：
   - 将错误码改为异常处理
   - 使用`try-except`块

4. **类型声明**：
   - 添加类型提示（可选）
   - 使用`typing`模块

### 从Python迁移到C++

1. **类型声明**：
   - 添加明确的类型声明
   - 使用模板和泛型

2. **内存管理**：
   - 添加手动内存管理
   - 使用智能指针

3. **错误处理**：
   - 将异常改为错误码
   - 添加返回值检查

4. **性能优化**：
   - 使用引用传递
   - 避免不必要的拷贝

## 测试和验证

### 功能测试

两个版本都应该通过相同的功能测试：

```python
# 测试用例示例
def test_basic_functionality():
    # 创建图形
    g = Graph()
    
    # 添加节点
    g.add_node_from_string_short("1,resistor,1.0,2.0,10.0,20.0,0.0,1,1,2,1,1,0")
    
    # 验证节点数量
    assert g.get_number_of_nodes() == 1
    
    # 验证节点信息
    node = g.get_node_by_id(1)
    assert node.get_name() == "resistor"
    assert node.get_size() == (1.0, 2.0)
```

### 性能测试

```python
# 性能测试示例
import time

def performance_test():
    # 测试大规模数据处理
    g = Graph()
    
    start_time = time.time()
    
    # 添加大量节点和边
    for i in range(10000):
        g.add_node_from_string_short(f"{i},component{i},1.0,1.0,{i},{i},0.0,1,1,1,0,1,0")
    
    end_time = time.time()
    print(f"Processing time: {end_time - start_time:.2f} seconds")
```

## 总结

C++和Python版本各有优势：

- **C++版本**：适合高性能、大规模数据处理
- **Python版本**：适合快速开发、原型设计和研究

建议根据具体需求选择合适的版本，或者采用混合策略以获得最佳效果。

## 相关文档

- [Utils类对比](./01_utils_comparison.md)
- [Node类对比](./02_node_comparison.md)
- [Edge类对比](./03_edge_comparison.md)
- [Graph类对比](./04_graph_comparison.md)
- [Optimal类对比](./05_optimal_comparison.md)
- [Board类对比](./06_board_comparison.md) 
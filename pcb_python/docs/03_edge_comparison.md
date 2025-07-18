# Edge类 C++与Python对应关系

## 概述

Edge类表示电路图中的边（连接），包含两个节点之间的连接信息、网络信息和位置信息。

## 文件对应关系

| C++文件 | Python文件 | 说明 |
|---------|------------|------|
| `include/edge.hpp` | `netlist_graph/edge.py` | 边类实现 |

## 类定义对比

### C++版本 (edge.hpp)

```cpp
class edge
{
private:
    // 节点A的信息
    int a_id;
    std::string a_name;
    int a_pad_id;
    std::string a_pad_name;
    double a_size_x;
    double a_size_y;
    double a_pos_x;
    double a_pos_y;
    bool a_isPlaced;
    
    // 节点B的信息
    int b_id;
    std::string b_name;
    int b_pad_id;
    std::string b_pad_name;
    double b_size_x;
    double b_size_y;
    double b_pos_x;
    double b_pos_y;
    bool b_isPlaced;
    
    // 网络信息
    int net_id;
    std::string net_name;
    int power_rail;

public:
    edge(void);
    // ... 方法声明
};
```

### Python版本 (edge.py)

```python
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
```

## 成员变量对应关系

### 节点A信息

| C++成员变量 | Python成员变量 | 类型 | 说明 |
|-------------|----------------|------|------|
| `a_id` | `_a_id` | `int` | 节点A的ID |
| `a_name` | `_a_name` | `string` | 节点A的名称 |
| `a_pad_id` | `_a_pad_id` | `int` | 节点A的焊盘ID |
| `a_pad_name` | `_a_pad_name` | `string` | 节点A的焊盘名称 |
| `a_size_x, a_size_y` | `_a_size_x, _a_size_y` | `double` | 节点A的尺寸 |
| `a_pos_x, a_pos_y` | `_a_pos_x, _a_pos_y` | `double` | 节点A的位置 |
| `a_isPlaced` | `_a_is_placed` | `bool` | 节点A是否已放置 |

### 节点B信息

| C++成员变量 | Python成员变量 | 类型 | 说明 |
|-------------|----------------|------|------|
| `b_id` | `_b_id` | `int` | 节点B的ID |
| `b_name` | `_b_name` | `string` | 节点B的名称 |
| `b_pad_id` | `_b_pad_id` | `int` | 节点B的焊盘ID |
| `b_pad_name` | `_b_pad_name` | `string` | 节点B的焊盘名称 |
| `b_size_x, b_size_y` | `_b_size_x, _b_size_y` | `double` | 节点B的尺寸 |
| `b_pos_x, b_pos_y` | `_b_pos_x, _b_pos_y` | `double` | 节点B的位置 |
| `b_isPlaced` | `_b_is_placed` | `bool` | 节点B是否已放置 |

### 网络信息

| C++成员变量 | Python成员变量 | 类型 | 说明 |
|-------------|----------------|------|------|
| `net_id` | `_net_id` | `int` | 网络ID |
| `net_name` | `_net_name` | `string` | 网络名称 |
| `power_rail` | `_power_rail` | `int` | 电源轨信息 |

## 方法对应关系

### 构造函数

| C++方法 | Python方法 | 功能 |
|---------|------------|------|
| `edge(void)` | `__init__(self)` | 默认构造函数 |

**C++实现：**
```cpp
edge(void) {
    a_id = b_id = a_pad_id = b_pad_id = net_id = power_rail = -1;
    a_name = b_name = a_pad_name = b_pad_name = net_name = "";
    a_size_x = a_size_y = a_pos_x = a_pos_y = 0.0;
    b_size_x = b_size_y = b_pos_x = b_pos_y = 0.0;
    a_isPlaced = b_isPlaced = false;
}
```

**Python实现：**
```python
def __init__(self):
    self._a_id = -1
    self._a_name = ""
    # ... 其他初始化
```

### 字符串解析方法

| C++方法 | Python方法 | 功能 | 参数 | 返回值 |
|---------|------------|------|------|--------|
| `create_from_string_short()` | `create_from_string_short()` | 从短格式字符串创建 | `string` | `int8_t` |
| `create_from_string_long()` | `create_from_string_long()` | 从长格式字符串创建 | `string` | `int8_t` |

**C++实现：**
```cpp
int8_t create_from_string_short(std::string s) {
    std::vector<std::string> fields;
    get_fields(s, fields);
    
    if (fields.size() < 20) return -1;
    
    // 节点A信息
    a_id = std::stoi(fields[0]);
    a_name = fields[1];
    a_pad_id = std::stoi(fields[2]);
    a_size_x = std::stod(fields[3]);
    a_size_y = std::stod(fields[4]);
    a_pos_x = std::stod(fields[5]);
    a_pos_y = std::stod(fields[6]);
    a_isPlaced = (std::stoi(fields[7]) == 1);
    
    // 节点B信息
    b_id = std::stoi(fields[8]);
    b_name = fields[9];
    b_pad_id = std::stoi(fields[10]);
    b_size_x = std::stod(fields[11]);
    b_size_y = std::stod(fields[12]);
    b_pos_x = std::stod(fields[13]);
    b_pos_y = std::stod(fields[14]);
    b_isPlaced = (std::stoi(fields[15]) == 1);
    
    // 网络信息
    net_id = std::stoi(fields[16]);
    net_name = fields[17];
    power_rail = (fields.size() > 18) ? std::stoi(fields[18]) : 0;
    
    return 0;
}
```

**Python实现：**
```python
def create_from_string_short(self, s: str) -> int:
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
```

### 网络信息访问方法

| C++方法 | Python方法 | 功能 | 返回值 |
|---------|------------|------|--------|
| `get_net_id()` | `get_net_id()` | 获取网络ID | `int` |
| `get_net_name()` | `get_net_name()` | 获取网络名称 | `string` |
| `get_power_rail()` | `get_power_rail()` | 获取电源轨信息 | `int` |

**C++实现：**
```cpp
int get_net_id() { return net_id; }
std::string get_net_name() { return net_name; }
int get_power_rail() { return power_rail; }
```

**Python实现：**
```python
def get_net_id(self) -> int:
    return self._net_id

def get_net_name(self) -> str:
    return self._net_name

def get_power_rail(self) -> int:
    return self._power_rail
```

### 节点信息访问方法

| C++方法 | Python方法 | 功能 | 参数 | 返回值 |
|---------|------------|------|------|--------|
| `get_instance_id()` | `get_instance_id()` | 获取指定节点的实例ID | `int node` | `int` |
| `get_instance_isPlaced()` | `get_instance_is_placed()` | 获取指定节点的放置状态 | `int node` | `bool` |
| `get_pad_name()` | `get_pad_name()` | 获取指定节点的焊盘名称 | `int node` | `string` |
| `get_pad_id()` | `get_pad_id()` | 获取指定节点的焊盘ID | `int node` | `int` |

**C++实现：**
```cpp
int get_instance_id(int node) { return node ? b_id : a_id; }
int get_instance_isPlaced(int node) { return node ? b_isPlaced : a_isPlaced; }
std::string get_pad_name(int node) { return node ? b_pad_name : a_pad_name; }
int get_pad_id(int node) { return node ? b_pad_id : a_pad_id; }
```

**Python实现：**
```python
def get_instance_id(self, node: int) -> int:
    return self._b_id if node else self._a_id

def get_instance_is_placed(self, node: int) -> bool:
    return self._b_is_placed if node else self._a_is_placed

def get_pad_name(self, node: int) -> str:
    return self._b_pad_name if node else self._a_pad_name

def get_pad_id(self, node: int) -> int:
    return self._b_pad_id if node else self._a_pad_id
```

### 连接信息方法

| C++方法 | Python方法 | 功能 | 返回值 |
|---------|------------|------|--------|
| `get_edge_connectivity()` | `get_edge_connectivity()` | 获取边的连接信息 | `pair<int,int>` |

**C++实现：**
```cpp
std::pair<int,int> get_edge_connectivity() {
    std::pair<int,int> edge;
    edge.first = a_id;
    edge.second = b_id;
    return edge;
}
```

**Python实现：**
```python
def get_edge_connectivity(self) -> Tuple[int, int]:
    return (self._a_id, self._b_id)
```

### 几何信息方法

| C++方法 | Python方法 | 功能 | 参数 | 返回值 |
|---------|------------|------|------|--------|
| `get_size()` | `get_size()` | 获取指定节点的尺寸 | `int id` | `pair<double,double>` |
| `set_size()` | `set_size()` | 设置指定节点的尺寸 | `(int id, pair<double,double>)` | `int` |
| `get_pos()` | `get_pos()` | 获取指定节点的位置 | `int id` | `pair<double,double>` |
| `set_pos()` | `set_pos()` | 设置指定节点的位置 | `(int id, pair<double,double>)` | `int` |

**C++实现：**
```cpp
std::pair<double, double> get_size(int id) {
    if (id == a_id) return std::make_pair(a_size_x, a_size_y);
    else if (id == b_id) return std::make_pair(b_size_x, b_size_y);
    else return std::make_pair(0.0, 0.0);
}

int set_size(int id, std::pair<double, double> p) {
    if (id == a_id) { a_size_x = p.first; a_size_y = p.second; }
    else if (id == b_id) { b_size_x = p.first; b_size_y = p.second; }
    else return -1;
    return 0;
}
```

**Python实现：**
```python
def get_size(self, node_id: int) -> Tuple[float, float]:
    if node_id == self._a_id:
        return (self._a_size_x, self._a_size_y)
    elif node_id == self._b_id:
        return (self._b_size_x, self._b_size_y)
    else:
        return (0.0, 0.0)

def set_size(self, node_id: int, size: Tuple[float, float]) -> int:
    if node_id == self._a_id:
        self._a_size_x, self._a_size_y = size
    elif node_id == self._b_id:
        self._b_size_x, self._b_size_y = size
    else:
        return -1
    return 0
```

### 输出方法

| C++方法 | Python方法 | 功能 | 参数 |
|---------|------------|------|------|
| `print_to_console()` | `print_to_console()` | 打印到控制台 | `bool` |
| `print()` | `print()` | 打印边信息 | `bool` |
| `format_string_long()` | `format_string_long()` | 格式化长字符串 | `string&` |

**C++实现：**
```cpp
void print_to_console(bool format) {
    if (format) {
        std::cout << "Edge: " << a_name << "(" << a_id << ") -> " 
                  << b_name << "(" << b_id << "), "
                  << "Net: " << net_name << "(" << net_id << "), "
                  << "Power: " << power_rail << std::endl;
    } else {
        std::cout << a_id << "," << a_name << "," << a_pad_id << ","
                  << a_size_x << "," << a_size_y << "," << a_pos_x << ","
                  << a_pos_y << "," << (a_isPlaced ? 1 : 0) << ","
                  << b_id << "," << b_name << "," << b_pad_id << ","
                  << b_size_x << "," << b_size_y << "," << b_pos_x << ","
                  << b_pos_y << "," << (b_isPlaced ? 1 : 0) << ","
                  << net_id << ",\"" << net_name << "\"," << power_rail << std::endl;
    }
}
```

**Python实现：**
```python
def print_to_console(self, format_long: bool) -> None:
    if format_long:
        print(f"Edge: {self._a_name}({self._a_id}) -> {self._b_name}({self._b_id}), "
              f"Net: {self._net_name}({self._net_id}), Power: {self._power_rail}")
    else:
        print(f"{self._a_id},{self._a_name},{self._a_pad_id},{self._a_size_x:.6f},{self._a_size_y:.6f},"
              f"{self._a_pos_x:.6f},{self._a_pos_y:.6f},{1 if self._a_is_placed else 0},"
              f"{self._b_id},{self._b_name},{self._b_pad_id},{self._b_size_x:.6f},{self._b_size_y:.6f},"
              f"{self._b_pos_x:.6f},{self._b_pos_y:.6f},{1 if self._b_is_placed else 0},"
              f"{self._net_id},\"{self._net_name}\",{self._power_rail}")
```

### 设置器方法

| C++方法 | Python方法 | 功能 | 参数 |
|---------|------------|------|------|
| `set_id()` | `set_id()` | 设置指定节点的ID | `(int node, int id)` |
| `set_name()` | `set_name()` | 设置指定节点的名称 | `(int node, string name)` |
| `set_pad_id()` | `set_pad_id()` | 设置指定节点的焊盘ID | `(int node, int pid)` |
| `set_pad_name()` | `set_pad_name()` | 设置指定节点的焊盘名称 | `(int node, string pname)` |
| `set_isPlaced()` | `set_is_placed()` | 设置指定节点的放置状态 | `(int node, bool isPlaced)` |
| `set_net_id()` | `set_net_id()` | 设置网络ID | `int net_id` |
| `set_net_name()` | `set_net_name()` | 设置网络名称 | `string net_name` |
| `set_power_rail()` | `set_power_rail()` | 设置电源轨信息 | `int power_rail` |

**C++实现：**
```cpp
void set_id(int node, int id) { if(node) this->b_id = id; else this->a_id = id; }
void set_name(int node, std::string name) { if(node) this->b_name = name; else this->a_name = name; }
void set_pad_id(int node, int pid) { if(node) this->b_pad_id = pid; else this->a_pad_id = pid; }
void set_pad_name(int node, std::string pname) { if(node) this->b_pad_name = pname; else this->a_pad_name = pname; }
void set_isPlaced(int node, bool isPlaced) { if(node) this->b_isPlaced = isPlaced; else this->a_isPlaced = isPlaced; }
void set_net_id(int net_id) { this->net_id = net_id; }
void set_net_name(std::string &net_name) { this->net_name = net_name; }
void set_power_rail(int power_rail) { this->power_rail = power_rail; }
```

**Python实现：**
```python
def set_id(self, node: int, node_id: int) -> None:
    if node:
        self._b_id = node_id
    else:
        self._a_id = node_id

def set_name(self, node: int, name: str) -> None:
    if node:
        self._b_name = name
    else:
        self._a_name = name

def set_pad_id(self, node: int, pad_id: int) -> None:
    if node:
        self._b_pad_id = pad_id
    else:
        self._a_pad_id = pad_id

def set_pad_name(self, node: int, pad_name: str) -> None:
    if node:
        self._b_pad_name = pad_name
    else:
        self._a_pad_name = pad_name

def set_is_placed(self, node: int, is_placed: bool) -> None:
    if node:
        self._b_is_placed = is_placed
    else:
        self._a_is_placed = is_placed

def set_net_id(self, net_id: int) -> None:
    self._net_id = net_id

def set_net_name(self, net_name: str) -> None:
    self._net_name = net_name

def set_power_rail(self, power_rail: int) -> None:
    self._power_rail = power_rail
```

## 主要差异

### 1. 参数传递

**C++版本：**
- 使用引用传递避免拷贝
- 使用指针传递复杂对象
- 需要手动管理内存

**Python版本：**
- 使用值传递（Python自动优化）
- 无需手动管理内存
- 更简洁的参数传递

### 2. 条件判断

**C++版本：**
- 使用三元运算符 `node ? b_id : a_id`
- 简洁但可能不够直观

**Python版本：**
- 使用条件表达式 `self._b_id if node else self._a_id`
- 更直观易读

### 3. 错误处理

**C++版本：**
- 返回错误码（-1表示失败）
- 需要检查返回值

**Python版本：**
- 抛出异常
- 使用try-except处理
- 更友好的错误信息

## 性能对比

| 操作 | C++性能 | Python性能 | 说明 |
|------|---------|------------|------|
| 对象创建 | 快 | 中等 | Python对象创建开销 |
| 属性访问 | 快 | 快 | 都很快 |
| 字符串操作 | 快 | 快 | Python字符串优化良好 |
| 条件判断 | 快 | 快 | 都很快 |

## 使用建议

1. **选择C++版本**：当需要最高性能、大量边处理时
2. **选择Python版本**：当需要快速开发、原型设计时
3. **混合使用**：可以用C++实现核心算法，Python实现业务逻辑 
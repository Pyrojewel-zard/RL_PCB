# Node类 C++与Python对应关系

## 概述

Node类表示电路图中的节点（组件），包含组件的基本信息、电气特性和优化信息。

## 文件对应关系

| C++文件 | Python文件 | 说明 |
|---------|------------|------|
| `include/node.hpp` | `netlist_graph/node.py` | 节点类实现 |

## 类定义对比

### C++版本 (node.hpp)

```cpp
class node
{
private:
    int id;
    std::string name;
    double size_x;
    double size_y;
    double pos_x;
    double pos_y;
    double orientation;
    int layer;
    bool isPlaced;
    int pins;
    int pins_smd;
    int pins_th;
    int type;
    std::vector<std::pair<int,int>> neighbors;
    optimal opt;

public:
    node(void);
    // ... 方法声明
};
```

### Python版本 (node.py)

```python
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
        self._neighbors = []
        self._optimal = Optimal()
```

## 成员变量对应关系

| C++成员变量 | Python成员变量 | 类型 | 说明 |
|-------------|----------------|------|------|
| `id` | `_id` | `int` | 节点ID |
| `name` | `_name` | `string` | 节点名称 |
| `size_x, size_y` | `_size_x, _size_y` | `double` | 节点尺寸 |
| `pos_x, pos_y` | `_pos_x, _pos_y` | `double` | 节点位置 |
| `orientation` | `_orientation` | `double` | 节点方向 |
| `layer` | `_layer` | `int` | 层信息 |
| `isPlaced` | `_is_placed` | `bool` | 是否已放置 |
| `pins` | `_pins` | `int` | 引脚总数 |
| `pins_smd` | `_pins_smd` | `int` | SMD引脚数 |
| `pins_th` | `_pins_th` | `int` | 通孔引脚数 |
| `type` | `_type` | `int` | 节点类型 |
| `neighbors` | `_neighbors` | `vector<pair<int,int>>` | 邻居节点列表 |
| `opt` | `_optimal` | `optimal` | 优化信息 |

## 方法对应关系

### 构造函数

| C++方法 | Python方法 | 功能 |
|---------|------------|------|
| `node(void)` | `__init__(self)` | 默认构造函数 |

**C++实现：**
```cpp
node(void) {
    id = -1;
    name = "";
    size_x = size_y = pos_x = pos_y = orientation = 0.0;
    layer = pins = pins_smd = pins_th = type = 0;
    isPlaced = false;
}
```

**Python实现：**
```python
def __init__(self):
    self._id = -1
    self._name = ""
    self._size_x = 0.0
    self._size_y = 0.0
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
    
    if (fields.size() < 12) return -1;
    
    id = std::stoi(fields[0]);
    name = fields[1];
    size_x = std::stod(fields[2]);
    size_y = std::stod(fields[3]);
    pos_x = std::stod(fields[4]);
    pos_y = std::stod(fields[5]);
    orientation = std::stod(fields[6]);
    layer = std::stoi(fields[7]);
    isPlaced = (std::stoi(fields[8]) == 1);
    pins = std::stoi(fields[9]);
    pins_smd = std::stoi(fields[10]);
    pins_th = std::stoi(fields[11]);
    type = (fields.size() > 12) ? std::stoi(fields[12]) : 0;
    
    return 0;
}
```

**Python实现：**
```python
def create_from_string_short(self, s: str) -> int:
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
        
        return 0
    except Exception:
        return -1
```

### 访问器方法

| C++方法 | Python方法 | 功能 | 返回值 |
|---------|------------|------|--------|
| `get_id()` | `get_id()` | 获取节点ID | `int` |
| `get_name()` | `get_name()` | 获取节点名称 | `string` |
| `get_size()` | `get_size()` | 获取节点尺寸 | `pair<double,double>` |
| `get_pos()` | `get_pos()` | 获取节点位置 | `pair<double,double>` |
| `get_orientation()` | `get_orientation()` | 获取节点方向 | `double` |
| `get_layer()` | `get_layer()` | 获取层信息 | `int` |
| `get_pin_count()` | `get_pin_count()` | 获取引脚总数 | `int` |
| `get_isPlaced()` | `get_is_placed()` | 获取放置状态 | `bool` |

**C++实现：**
```cpp
int get_id() { return id; }
std::string get_name() { return name; }
std::pair<double,double> get_size() {
    std::pair<double, double> p;
    p.first = size_x; p.second=size_y;
    return p;
}
```

**Python实现：**
```python
def get_id(self) -> int:
    return self._id

def get_name(self) -> str:
    return self._name

def get_size(self) -> Tuple[float, float]:
    return (self._size_x, self._size_y)
```

### 设置器方法

| C++方法 | Python方法 | 功能 | 参数 |
|---------|------------|------|------|
| `set_id()` | `set_id()` | 设置节点ID | `int` |
| `set_name()` | `set_name()` | 设置节点名称 | `string` |
| `set_size()` | `set_size()` | 设置节点尺寸 | `pair<double,double>` |
| `set_pos()` | `set_pos()` | 设置节点位置 | `pair<double,double>` |
| `set_orientation()` | `set_orientation()` | 设置节点方向 | `double` |

**C++实现：**
```cpp
void set_id(int id) { this->id = id; opt.set_id(id); }
void set_name(std::string name) { this->name = name; opt.set_name(name); }
int set_size(std::pair<double, double> &size) { 
    size_x = size.first; size_y = size.second; 
    return 0; 
}
```

**Python实现：**
```python
def set_id(self, node_id: int) -> None:
    self._id = node_id
    self._optimal.set_id(node_id)

def set_name(self, name: str) -> None:
    self._name = name
    self._optimal.set_name(name)

def set_size(self, size: Tuple[float, float]) -> int:
    self._size_x, self._size_y = size
    return 0
```

### 几何计算方法

| C++方法 | Python方法 | 功能 | 参数 | 返回值 |
|---------|------------|------|------|--------|
| `get_inst_bb_coords()` | `get_inst_bb_coords()` | 获取边界框坐标 | `grid_resolution` | `(xmin,xmax,ymin,ymax)` |
| `get_inst_bb_centre_size()` | `get_inst_bb_centre_size()` | 获取边界框中心尺寸 | `grid_resolution` | `(xc,yc,x,y)` |
| `get_area()` | `get_area()` | 获取节点面积 | 无 | `double` |

**C++实现：**
```cpp
int get_inst_bb_coords(int &xmin, int &xmax, int &ymin, int &ymax, double grid_resolution) {
    xmin = (int)(pos_x / grid_resolution);
    ymin = (int)(pos_y / grid_resolution);
    xmax = (int)((pos_x + size_x) / grid_resolution);
    ymax = (int)((pos_y + size_y) / grid_resolution);
    return 0;
}

double get_area() {
    return size_x * size_y;
}
```

**Python实现：**
```python
def get_inst_bb_coords(self, grid_resolution: float) -> Tuple[int, int, int, int]:
    x_min = int(self._pos_x / grid_resolution)
    y_min = int(self._pos_y / grid_resolution)
    x_max = int((self._pos_x + self._size_x) / grid_resolution)
    y_max = int((self._pos_y + self._size_y) / grid_resolution)
    return (x_min, x_max, y_min, y_max)

def get_area(self) -> float:
    return self._size_x * self._size_y
```

### 输出方法

| C++方法 | Python方法 | 功能 | 参数 |
|---------|------------|------|------|
| `print_to_console()` | `print_to_console()` | 打印到控制台 | `bool` |
| `print()` | `print()` | 打印节点信息 | `bool` |
| `format_string_long()` | `format_string_long()` | 格式化长字符串 | `string&` |

**C++实现：**
```cpp
void print_to_console(bool format) {
    if (format) {
        std::cout << "Node(id=" << id << ", name='" << name << "', "
                  << "size=(" << size_x << ", " << size_y << "), "
                  << "pos=(" << pos_x << ", " << pos_y << "))" << std::endl;
    } else {
        std::cout << id << "," << name << "," << size_x << "," << size_y << ","
                  << pos_x << "," << pos_y << "," << orientation << ","
                  << layer << "," << (isPlaced ? 1 : 0) << "," << pins << ","
                  << pins_smd << "," << pins_th << "," << type << std::endl;
    }
}
```

**Python实现：**
```python
def print_to_console(self, format_long: bool) -> None:
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
```

## Optimal相关方法

| C++方法 | Python方法 | 功能 |
|---------|------------|------|
| `get_opt_id()` | `get_opt_id()` | 获取optimal的ID |
| `get_opt_name()` | `get_opt_name()` | 获取optimal的名称 |
| `get_opt_euclidean_distance()` | `get_opt_euclidean_distance()` | 获取欧几里得距离 |
| `get_opt_hpwl()` | `get_opt_hpwl()` | 获取HPWL |
| `set_opt_id()` | `set_opt_id()` | 设置optimal的ID |
| `set_opt_name()` | `set_opt_name()` | 设置optimal的名称 |
| `set_opt_euclidean_distance()` | `set_opt_euclidean_distance()` | 设置欧几里得距离 |
| `set_opt_hpwl()` | `set_opt_hpwl()` | 设置HPWL |

## 主要差异

### 1. 访问控制

**C++版本：**
- 使用private/public关键字
- 严格的访问控制
- 需要getter/setter方法

**Python版本：**
- 使用下划线前缀表示私有
- 约定俗成的访问控制
- 可以直接访问属性

### 2. 内存管理

**C++版本：**
- 需要手动管理内存
- 使用引用和指针
- 需要注意内存泄漏

**Python版本：**
- 自动垃圾回收
- 使用值传递
- 无需手动管理内存

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
| 对象创建 | 快 | 中等 | Python对象创建开销 |
| 属性访问 | 快 | 快 | 都很快 |
| 字符串操作 | 快 | 快 | Python字符串优化良好 |
| 数值计算 | 快 | 中等 | Python有GIL限制 |

## 使用建议

1. **选择C++版本**：当需要最高性能、大量数值计算时
2. **选择Python版本**：当需要快速开发、原型设计时
3. **混合使用**：可以用C++实现核心算法，Python实现业务逻辑 
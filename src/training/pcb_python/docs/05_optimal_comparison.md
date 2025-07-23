# Optimal类 C++与Python对应关系

## 概述

Optimal类存储节点的优化信息，包括ID、名称、欧几里得距离和HPWL等优化指标。

## 文件对应关系

| C++文件 | Python文件 | 说明 |
|---------|------------|------|
| `include/optimal.hpp` | `netlist_graph/optimal.py` | 优化信息类实现 |

## 类定义对比

### C++版本 (optimal.hpp)

```cpp
class optimal
{
private:
    int id;
    std::string name;
    double euclidean_distance;
    double hpwl;

public:
    optimal(void);
    // ... 方法声明
};
```

### Python版本 (optimal.py)

```python
class Optimal:
    """存储节点的优化信息"""
    
    def __init__(self):
        self._id = -1
        self._name = ""
        self._euclidean_distance = 0.0
        self._hpwl = 0.0
```

## 成员变量对应关系

| C++成员变量 | Python成员变量 | 类型 | 说明 |
|-------------|----------------|------|------|
| `id` | `_id` | `int` | 节点ID |
| `name` | `_name` | `string` | 节点名称 |
| `euclidean_distance` | `_euclidean_distance` | `double` | 欧几里得距离 |
| `hpwl` | `_hpwl` | `double` | 半周长线长 |

## 方法对应关系

### 构造函数

| C++方法 | Python方法 | 功能 |
|---------|------------|------|
| `optimal(void)` | `__init__(self)` | 默认构造函数 |

**C++实现：**
```cpp
optimal(void) {
    id = -1;
    name = "";
    euclidean_distance = 0.0;
    hpwl = 0.0;
}
```

**Python实现：**
```python
def __init__(self):
    self._id = -1
    self._name = ""
    self._euclidean_distance = 0.0
    self._hpwl = 0.0
```

### 访问器方法

| C++方法 | Python方法 | 功能 | 返回值 |
|---------|------------|------|--------|
| `get_id()` | `get_id()` | 获取节点ID | `int` |
| `get_name()` | `get_name()` | 获取节点名称 | `string` |
| `get_euclidean_distance()` | `get_euclidean_distance()` | 获取欧几里得距离 | `double` |
| `get_hpwl()` | `get_hpwl()` | 获取HPWL | `double` |

**C++实现：**
```cpp
int get_id() { return id; }
std::string get_name() { return name; }
double get_euclidean_distance() { return euclidean_distance; }
double get_hpwl() { return hpwl; }
```

**Python实现：**
```python
def get_id(self) -> int:
    return self._id

def get_name(self) -> str:
    return self._name

def get_euclidean_distance(self) -> float:
    return self._euclidean_distance

def get_hpwl(self) -> float:
    return self._hpwl
```

### 设置器方法

| C++方法 | Python方法 | 功能 | 参数 |
|---------|------------|------|------|
| `set_id()` | `set_id()` | 设置节点ID | `int id` |
| `set_name()` | `set_name()` | 设置节点名称 | `string name` |
| `set_euclidean_distance()` | `set_euclidean_distance()` | 设置欧几里得距离 | `double euclidean_distance` |
| `set_hpwl()` | `set_hpwl()` | 设置HPWL | `double hpwl` |

**C++实现：**
```cpp
void set_id(int id) { this->id = id; }
void set_name(std::string name) { this->name = name; }
void set_euclidean_distance(double euclidean_distance) { this->euclidean_distance = euclidean_distance; }
void set_hpwl(double hpwl) { this->hpwl = hpwl; }
```

**Python实现：**
```python
def set_id(self, node_id: int) -> None:
    self._id = node_id

def set_name(self, name: str) -> None:
    self._name = name

def set_euclidean_distance(self, euclidean_distance: float) -> None:
    self._euclidean_distance = euclidean_distance

def set_hpwl(self, hpwl: float) -> None:
    self._hpwl = hpwl
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
    
    if (fields.size() < 4) return -1;
    
    id = std::stoi(fields[0]);
    name = fields[1];
    euclidean_distance = std::stod(fields[2]);
    hpwl = std::stod(fields[3]);
    
    return 0;
}
```

**Python实现：**
```python
def create_from_string_short(self, s: str) -> int:
    try:
        fields = Utils.parse_csv_line(s)
        if len(fields) < 4:
            return -1
        
        self._id = Utils.safe_int(fields[0])
        self._name = fields[1]
        self._euclidean_distance = Utils.safe_float(fields[2])
        self._hpwl = Utils.safe_float(fields[3])
        
        return 0
    except Exception:
        return -1
```

### 输出方法

| C++方法 | Python方法 | 功能 | 参数 |
|---------|------------|------|------|
| `print_to_console()` | `print_to_console()` | 打印到控制台 | `bool` |
| `print()` | `print()` | 打印优化信息 | `bool` |
| `format_string_long()` | `format_string_long()` | 格式化长字符串 | `string&` |

**C++实现：**
```cpp
void print_to_console(bool format) {
    if (format) {
        std::cout << "Optimal(id=" << id << ", name='" << name << "', "
                  << "euclidean_distance=" << euclidean_distance << ", "
                  << "hpwl=" << hpwl << ")" << std::endl;
    } else {
        std::cout << id << "," << name << "," << euclidean_distance << "," << hpwl << std::endl;
    }
}
```

**Python实现：**
```python
def print_to_console(self, format_long: bool) -> None:
    if format_long:
        print(f"Optimal(id={self._id}, name='{self._name}', "
              f"euclidean_distance={self._euclidean_distance:.6f}, "
              f"hpwl={self._hpwl:.6f})")
    else:
        print(f"{self._id},{self._name},{self._euclidean_distance:.6f},{self._hpwl:.6f}")
```

### 比较方法

| C++方法 | Python方法 | 功能 | 参数 | 返回值 |
|---------|------------|------|------|--------|
| `operator<()` | `__lt__()` | 小于比较 | `const optimal& other` | `bool` |
| `operator==()` | `__eq__()` | 相等比较 | `const optimal& other` | `bool` |

**C++实现：**
```cpp
bool operator<(const optimal& other) const {
    if (hpwl != other.hpwl) {
        return hpwl < other.hpwl;
    }
    return euclidean_distance < other.euclidean_distance;
}

bool operator==(const optimal& other) const {
    return id == other.id && name == other.name &&
           euclidean_distance == other.euclidean_distance && hpwl == other.hpwl;
}
```

**Python实现：**
```python
def __lt__(self, other: 'Optimal') -> bool:
    if self._hpwl != other._hpwl:
        return self._hpwl < other._hpwl
    return self._euclidean_distance < other._euclidean_distance

def __eq__(self, other: 'Optimal') -> bool:
    return (self._id == other._id and 
            self._name == other._name and
            self._euclidean_distance == other._euclidean_distance and
            self._hpwl == other._hpwl)
```

### 计算和更新方法

| C++方法 | Python方法 | 功能 | 参数 | 返回值 |
|---------|------------|------|------|--------|
| `update_metrics()` | `update_metrics()` | 更新优化指标 | `(double euclidean_distance, double hpwl)` | 无 |
| `reset()` | `reset()` | 重置所有指标 | 无 | 无 |

**C++实现：**
```cpp
void update_metrics(double euclidean_distance, double hpwl) {
    this->euclidean_distance = euclidean_distance;
    this->hpwl = hpwl;
}

void reset() {
    id = -1;
    name = "";
    euclidean_distance = 0.0;
    hpwl = 0.0;
}
```

**Python实现：**
```python
def update_metrics(self, euclidean_distance: float, hpwl: float) -> None:
    self._euclidean_distance = euclidean_distance
    self._hpwl = hpwl

def reset(self) -> None:
    self._id = -1
    self._name = ""
    self._euclidean_distance = 0.0
    self._hpwl = 0.0
```

### 验证方法

| C++方法 | Python方法 | 功能 | 参数 | 返回值 |
|---------|------------|------|------|--------|
| `is_valid()` | `is_valid()` | 检查是否有效 | 无 | `bool` |
| `has_metrics()` | `has_metrics()` | 检查是否有指标 | 无 | `bool` |

**C++实现：**
```cpp
bool is_valid() const {
    return id >= 0 && !name.empty();
}

bool has_metrics() const {
    return euclidean_distance > 0.0 || hpwl > 0.0;
}
```

**Python实现：**
```python
def is_valid(self) -> bool:
    return self._id >= 0 and self._name != ""

def has_metrics(self) -> bool:
    return self._euclidean_distance > 0.0 or self._hpwl > 0.0
```

## 主要差异

### 1. 操作符重载

**C++版本：**
- 使用`operator<`和`operator==`重载
- 支持STL容器的自动排序
- 编译时类型检查

**Python版本：**
- 使用`__lt__`和`__eq__`特殊方法
- 支持Python内置排序
- 运行时类型检查

### 2. 字符串处理

**C++版本：**
- 使用`std::string`
- 需要手动处理字符串分割
- 使用`std::stoi`和`std::stod`转换

**Python版本：**
- 使用Python字符串
- 使用`split()`方法分割
- 使用`int()`和`float()`转换

### 3. 错误处理

**C++版本：**
- 返回错误码（-1表示失败）
- 使用异常处理
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
| 数值计算 | 快 | 中等 | Python有GIL限制 |
| 比较操作 | 快 | 快 | 都很快 |

## 使用建议

1. **选择C++版本**：当需要最高性能、大量优化计算时
2. **选择Python版本**：当需要快速开发、原型设计时
3. **混合使用**：可以用C++实现核心算法，Python实现业务逻辑

## 应用场景

### 1. 优化算法

**C++版本：**
```cpp
// 在优化算法中使用
std::vector<optimal> solutions;
// ... 生成多个解决方案
std::sort(solutions.begin(), solutions.end());  // 自动排序
```

**Python版本：**
```python
# 在优化算法中使用
solutions = []
# ... 生成多个解决方案
solutions.sort()  # 自动排序
```

### 2. 结果存储

**C++版本：**
```cpp
// 存储优化结果
optimal result;
result.set_id(node_id);
result.set_name(node_name);
result.update_metrics(euclidean_dist, hpwl_value);
```

**Python版本：**
```python
# 存储优化结果
result = Optimal()
result.set_id(node_id)
result.set_name(node_name)
result.update_metrics(euclidean_dist, hpwl_value)
```

### 3. 文件I/O

**C++版本：**
```cpp
// 从文件读取优化信息
std::string line;
std::getline(file, line);
optimal opt;
opt.create_from_string_short(line);
```

**Python版本：**
```python
# 从文件读取优化信息
line = file.readline().strip()
opt = Optimal()
opt.create_from_string_short(line)
``` 
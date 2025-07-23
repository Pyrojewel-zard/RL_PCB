# Utils类 C++与Python对应关系

## 概述

Utils类提供了通用的工具函数，用于距离计算、文件解析、数值转换等操作。

## 文件对应关系

| C++文件 | Python文件 | 说明 |
|---------|------------|------|
| `include/utils.hpp` | `netlist_graph/utils.py` | 工具类实现 |

## 类定义对比

### C++版本 (utils.hpp)

```cpp
// C++版本没有独立的Utils类，工具函数分散在各个文件中
// 主要使用标准库函数和自定义工具函数
```

### Python版本 (utils.py)

```python
class Utils:
    """工具类，提供各种辅助函数"""
    
    @staticmethod
    def euclidean_distance(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """计算两点间的欧几里得距离"""
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
```

## 函数对应关系

### 距离计算函数

| C++函数 | Python函数 | 功能 | 参数 | 返回值 |
|---------|------------|------|------|--------|
| 手动实现 | `euclidean_distance()` | 计算欧几里得距离 | `(pos1, pos2)` | `float` |
| 手动实现 | `manhattan_distance()` | 计算曼哈顿距离 | `(pos1, pos2)` | `float` |

**C++实现示例：**
```cpp
// 在需要的地方手动实现
double euclidean_distance(double x1, double y1, double x2, double y2) {
    return sqrt((x2-x1)*(x2-x1) + (y2-y1)*(y2-y1));
}
```

**Python实现：**
```python
@staticmethod
def euclidean_distance(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
```

### 文件解析函数

| C++函数 | Python函数 | 功能 | 参数 | 返回值 |
|---------|------------|------|------|--------|
| `get_fields()` | `parse_csv_line()` | 解析CSV行 | `string` | `List[str]` |

**C++实现：**
```cpp
int get_fields(std::string &s, std::vector<std::string> &v) {
    std::stringstream ss(s);
    std::string item;
    while (std::getline(ss, item, ',')) {
        v.push_back(item);
    }
    return 0;
}
```

**Python实现：**
```python
@staticmethod
def parse_csv_line(line: str) -> List[str]:
    return [field.strip() for field in line.split(',')]
```

### 数值转换函数

| C++函数 | Python函数 | 功能 | 参数 | 返回值 |
|---------|------------|------|------|--------|
| `std::stof()` | `safe_float()` | 安全浮点数转换 | `str` | `float` |
| `std::stoi()` | `safe_int()` | 安全整数转换 | `str` | `int` |

**C++实现：**
```cpp
// 使用try-catch处理转换错误
try {
    float value = std::stof(str);
} catch (const std::exception& e) {
    // 处理错误
}
```

**Python实现：**
```python
@staticmethod
def safe_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except (ValueError, TypeError):
        return default
```

### 几何计算函数

| C++函数 | Python函数 | 功能 | 参数 | 返回值 |
|---------|------------|------|------|--------|
| 手动实现 | `calculate_hpwl()` | 计算HPWL | `List[Tuple[float, float]]` | `float` |
| 手动实现 | `get_bounding_box()` | 计算边界框 | `List[Tuple[float, float]]` | `Tuple[float, float, float, float]` |

**C++实现示例：**
```cpp
double calculate_hpwl(const std::vector<std::pair<double, double>>& points) {
    if (points.empty()) return 0.0;
    
    double min_x = points[0].first, max_x = points[0].first;
    double min_y = points[0].second, max_y = points[0].second;
    
    for (const auto& point : points) {
        min_x = std::min(min_x, point.first);
        max_x = std::max(max_x, point.first);
        min_y = std::min(min_y, point.second);
        max_y = std::max(max_y, point.second);
    }
    
    return (max_x - min_x) + (max_y - min_y);
}
```

**Python实现：**
```python
@staticmethod
def calculate_hpwl(points: List[Tuple[float, float]]) -> float:
    if not points:
        return 0.0
    
    min_x = min(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_x = max(p[0] for p in points)
    max_y = max(p[1] for p in points)
    
    return (max_x - min_x) + (max_y - min_y)
```

## 主要差异

### 1. 错误处理

**C++版本：**
- 使用异常处理（try-catch）
- 返回错误码（-1表示失败）
- 需要手动检查返回值

**Python版本：**
- 使用try-except处理异常
- 提供默认值机制
- 更友好的错误信息

### 2. 内存管理

**C++版本：**
- 需要手动管理内存
- 使用引用和指针
- 需要注意内存泄漏

**Python版本：**
- 自动垃圾回收
- 使用值传递
- 无需手动管理内存

### 3. 类型安全

**C++版本：**
- 编译时类型检查
- 强类型系统
- 模板支持

**Python版本：**
- 运行时类型检查
- 动态类型系统
- 类型提示支持

## 性能对比

| 操作 | C++性能 | Python性能 | 说明 |
|------|---------|------------|------|
| 数值计算 | 快 | 中等 | Python有GIL限制 |
| 字符串处理 | 快 | 快 | Python字符串操作优化良好 |
| 内存分配 | 快 | 中等 | Python垃圾回收开销 |
| 文件I/O | 快 | 快 | 都使用系统调用 |

## 使用建议

1. **选择C++版本**：当需要最高性能、内存效率或系统级编程时
2. **选择Python版本**：当需要快速开发、原型设计或脚本处理时
3. **混合使用**：可以用C++实现核心算法，Python实现业务逻辑

## 迁移指南

从C++迁移到Python：

1. 将C++的异常处理改为Python的try-except
2. 将指针和引用改为值传递
3. 将手动内存管理改为自动管理
4. 添加类型提示以提高代码可读性
5. 使用Python的列表推导式简化循环操作 
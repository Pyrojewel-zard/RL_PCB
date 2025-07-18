# Board类 C++与Python对应关系

## 概述

Board类表示电路板，管理电路板的基本信息、尺寸、层数等属性，并提供电路板相关的操作方法。

## 文件对应关系

| C++文件 | Python文件 | 说明 |
|---------|------------|------|
| `include/board.hpp` | `netlist_graph/board.py` | 电路板类实现 |

## 类定义对比

### C++版本 (board.hpp)

```cpp
class board
{
private:
    int id;
    std::string name;
    double size_x;
    double size_y;
    int layers;
    double grid_resolution;
    std::string kicad_pcb_file;

public:
    board(void);
    // ... 方法声明
};
```

### Python版本 (board.py)

```python
class Board:
    """表示电路板，管理电路板的基本信息"""
    
    def __init__(self):
        self._id = -1
        self._name = ""
        self._size_x = 0.0
        self._size_y = 0.0
        self._layers = 0
        self._grid_resolution = 0.0
        self._kicad_pcb_file = ""
```

## 成员变量对应关系

| C++成员变量 | Python成员变量 | 类型 | 说明 |
|-------------|----------------|------|------|
| `id` | `_id` | `int` | 电路板ID |
| `name` | `_name` | `string` | 电路板名称 |
| `size_x, size_y` | `_size_x, _size_y` | `double` | 电路板尺寸 |
| `layers` | `_layers` | `int` | 层数 |
| `grid_resolution` | `_grid_resolution` | `double` | 网格分辨率 |
| `kicad_pcb_file` | `_kicad_pcb_file` | `string` | KiCad PCB文件名 |

## 方法对应关系

### 构造函数

| C++方法 | Python方法 | 功能 |
|---------|------------|------|
| `board(void)` | `__init__(self)` | 默认构造函数 |

**C++实现：**
```cpp
board(void) {
    id = -1;
    name = "";
    size_x = size_y = grid_resolution = 0.0;
    layers = 0;
    kicad_pcb_file = "";
}
```

**Python实现：**
```python
def __init__(self):
    self._id = -1
    self._name = ""
    self._size_x = 0.0
    self._size_y = 0.0
    self._layers = 0
    self._grid_resolution = 0.0
    self._kicad_pcb_file = ""
```

### 访问器方法

| C++方法 | Python方法 | 功能 | 返回值 |
|---------|------------|------|--------|
| `get_id()` | `get_id()` | 获取电路板ID | `int` |
| `get_name()` | `get_name()` | 获取电路板名称 | `string` |
| `get_size()` | `get_size()` | 获取电路板尺寸 | `pair<double,double>` |
| `get_layers()` | `get_layers()` | 获取层数 | `int` |
| `get_grid_resolution()` | `get_grid_resolution()` | 获取网格分辨率 | `double` |
| `get_kicad_pcb_file()` | `get_kicad_pcb_file()` | 获取KiCad PCB文件名 | `string` |

**C++实现：**
```cpp
int get_id() { return id; }
std::string get_name() { return name; }
std::pair<double,double> get_size() {
    std::pair<double, double> p;
    p.first = size_x; p.second = size_y;
    return p;
}
int get_layers() { return layers; }
double get_grid_resolution() { return grid_resolution; }
std::string get_kicad_pcb_file() { return kicad_pcb_file; }
```

**Python实现：**
```python
def get_id(self) -> int:
    return self._id

def get_name(self) -> str:
    return self._name

def get_size(self) -> Tuple[float, float]:
    return (self._size_x, self._size_y)

def get_layers(self) -> int:
    return self._layers

def get_grid_resolution(self) -> float:
    return self._grid_resolution

def get_kicad_pcb_file(self) -> str:
    return self._kicad_pcb_file
```

### 设置器方法

| C++方法 | Python方法 | 功能 | 参数 |
|---------|------------|------|------|
| `set_id()` | `set_id()` | 设置电路板ID | `int id` |
| `set_name()` | `set_name()` | 设置电路板名称 | `string name` |
| `set_size()` | `set_size()` | 设置电路板尺寸 | `pair<double,double>` |
| `set_layers()` | `set_layers()` | 设置层数 | `int layers` |
| `set_grid_resolution()` | `set_grid_resolution()` | 设置网格分辨率 | `double grid_resolution` |
| `set_kicad_pcb_file()` | `set_kicad_pcb_file()` | 设置KiCad PCB文件名 | `string filename` |

**C++实现：**
```cpp
void set_id(int id) { this->id = id; }
void set_name(std::string name) { this->name = name; }
int set_size(std::pair<double, double> &size) { 
    size_x = size.first; size_y = size.second; 
    return 0; 
}
void set_layers(int layers) { this->layers = layers; }
void set_grid_resolution(double grid_resolution) { this->grid_resolution = grid_resolution; }
void set_kicad_pcb_file(std::string filename) { this->kicad_pcb_file = filename; }
```

**Python实现：**
```python
def set_id(self, board_id: int) -> None:
    self._id = board_id

def set_name(self, name: str) -> None:
    self._name = name

def set_size(self, size: Tuple[float, float]) -> int:
    self._size_x, self._size_y = size
    return 0

def set_layers(self, layers: int) -> None:
    self._layers = layers

def set_grid_resolution(self, grid_resolution: float) -> None:
    self._grid_resolution = grid_resolution

def set_kicad_pcb_file(self, filename: str) -> None:
    self._kicad_pcb_file = filename
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
    
    if (fields.size() < 6) return -1;
    
    id = std::stoi(fields[0]);
    name = fields[1];
    size_x = std::stod(fields[2]);
    size_y = std::stod(fields[3]);
    layers = std::stoi(fields[4]);
    grid_resolution = std::stod(fields[5]);
    kicad_pcb_file = (fields.size() > 6) ? fields[6] : "";
    
    return 0;
}
```

**Python实现：**
```python
def create_from_string_short(self, s: str) -> int:
    try:
        fields = Utils.parse_csv_line(s)
        if len(fields) < 6:
            return -1
        
        self._id = Utils.safe_int(fields[0])
        self._name = fields[1]
        self._size_x = Utils.safe_float(fields[2])
        self._size_y = Utils.safe_float(fields[3])
        self._layers = Utils.safe_int(fields[4])
        self._grid_resolution = Utils.safe_float(fields[5])
        self._kicad_pcb_file = fields[6] if len(fields) > 6 else ""
        
        return 0
    except Exception:
        return -1
```

### 几何计算方法

| C++方法 | Python方法 | 功能 | 参数 | 返回值 |
|---------|------------|------|------|--------|
| `get_area()` | `get_area()` | 获取电路板面积 | 无 | `double` |
| `get_perimeter()` | `get_perimeter()` | 获取电路板周长 | 无 | `double` |
| `get_aspect_ratio()` | `get_aspect_ratio()` | 获取长宽比 | 无 | `double` |
| `is_point_inside()` | `is_point_inside()` | 检查点是否在电路板内 | `(double x, double y)` | `bool` |

**C++实现：**
```cpp
double get_area() {
    return size_x * size_y;
}

double get_perimeter() {
    return 2.0 * (size_x + size_y);
}

double get_aspect_ratio() {
    return size_x / size_y;
}

bool is_point_inside(double x, double y) {
    return x >= 0.0 && x <= size_x && y >= 0.0 && y <= size_y;
}
```

**Python实现：**
```python
def get_area(self) -> float:
    return self._size_x * self._size_y

def get_perimeter(self) -> float:
    return 2.0 * (self._size_x + self._size_y)

def get_aspect_ratio(self) -> float:
    return self._size_x / self._size_y if self._size_y != 0.0 else 0.0

def is_point_inside(self, x: float, y: float) -> bool:
    return 0.0 <= x <= self._size_x and 0.0 <= y <= self._size_y
```

### 网格相关方法

| C++方法 | Python方法 | 功能 | 参数 | 返回值 |
|---------|------------|------|------|--------|
| `get_grid_size()` | `get_grid_size()` | 获取网格尺寸 | 无 | `pair<int,int>` |
| `world_to_grid()` | `world_to_grid()` | 世界坐标转网格坐标 | `(double x, double y)` | `pair<int,int>` |
| `grid_to_world()` | `grid_to_world()` | 网格坐标转世界坐标 | `(int grid_x, int grid_y)` | `pair<double,double>` |

**C++实现：**
```cpp
std::pair<int,int> get_grid_size() {
    int grid_x = (int)(size_x / grid_resolution);
    int grid_y = (int)(size_y / grid_resolution);
    return std::make_pair(grid_x, grid_y);
}

std::pair<int,int> world_to_grid(double x, double y) {
    int grid_x = (int)(x / grid_resolution);
    int grid_y = (int)(y / grid_resolution);
    return std::make_pair(grid_x, grid_y);
}

std::pair<double,double> grid_to_world(int grid_x, int grid_y) {
    double world_x = grid_x * grid_resolution;
    double world_y = grid_y * grid_resolution;
    return std::make_pair(world_x, world_y);
}
```

**Python实现：**
```python
def get_grid_size(self) -> Tuple[int, int]:
    grid_x = int(self._size_x / self._grid_resolution)
    grid_y = int(self._size_y / self._grid_resolution)
    return (grid_x, grid_y)

def world_to_grid(self, x: float, y: float) -> Tuple[int, int]:
    grid_x = int(x / self._grid_resolution)
    grid_y = int(y / self._grid_resolution)
    return (grid_x, grid_y)

def grid_to_world(self, grid_x: int, grid_y: int) -> Tuple[float, float]:
    world_x = grid_x * self._grid_resolution
    world_y = grid_y * self._grid_resolution
    return (world_x, world_y)
```

### 验证方法

| C++方法 | Python方法 | 功能 | 参数 | 返回值 |
|---------|------------|------|------|--------|
| `is_valid()` | `is_valid()` | 检查电路板是否有效 | 无 | `bool` |
| `has_valid_size()` | `has_valid_size()` | 检查尺寸是否有效 | 无 | `bool` |
| `has_valid_layers()` | `has_valid_layers()` | 检查层数是否有效 | 无 | `bool` |

**C++实现：**
```cpp
bool is_valid() const {
    return id >= 0 && !name.empty() && size_x > 0.0 && size_y > 0.0 && layers > 0;
}

bool has_valid_size() const {
    return size_x > 0.0 && size_y > 0.0;
}

bool has_valid_layers() const {
    return layers > 0;
}
```

**Python实现：**
```python
def is_valid(self) -> bool:
    return (self._id >= 0 and 
            self._name != "" and 
            self._size_x > 0.0 and 
            self._size_y > 0.0 and 
            self._layers > 0)

def has_valid_size(self) -> bool:
    return self._size_x > 0.0 and self._size_y > 0.0

def has_valid_layers(self) -> bool:
    return self._layers > 0
```

### 输出方法

| C++方法 | Python方法 | 功能 | 参数 |
|---------|------------|------|------|
| `print_to_console()` | `print_to_console()` | 打印到控制台 | `bool` |
| `print()` | `print()` | 打印电路板信息 | `bool` |
| `format_string_long()` | `format_string_long()` | 格式化长字符串 | `string&` |

**C++实现：**
```cpp
void print_to_console(bool format) {
    if (format) {
        std::cout << "Board(id=" << id << ", name='" << name << "', "
                  << "size=(" << size_x << ", " << size_y << "), "
                  << "layers=" << layers << ", "
                  << "grid_resolution=" << grid_resolution << ")" << std::endl;
    } else {
        std::cout << id << "," << name << "," << size_x << "," << size_y << ","
                  << layers << "," << grid_resolution << "," << kicad_pcb_file << std::endl;
    }
}
```

**Python实现：**
```python
def print_to_console(self, format_long: bool) -> None:
    if format_long:
        print(f"Board(id={self._id}, name='{self._name}', "
              f"size=({self._size_x:.6f}, {self._size_y:.6f}), "
              f"layers={self._layers}, "
              f"grid_resolution={self._grid_resolution:.6f})")
    else:
        print(f"{self._id},{self._name},{self._size_x:.6f},{self._size_y:.6f},"
              f"{self._layers},{self._grid_resolution:.6f},{self._kicad_pcb_file}")
```

### 文件操作方法

| C++方法 | Python方法 | 功能 | 参数 | 返回值 |
|---------|------------|------|------|--------|
| `write_to_file()` | `write_to_file()` | 写入文件 | `string filename` | `int` |
| `read_from_file()` | `read_from_file()` | 从文件读取 | `string filename` | `int` |

**C++实现：**
```cpp
int write_to_file(std::string filename) {
    std::ofstream file(filename);
    if (!file.is_open()) return -1;
    
    file << id << "," << name << "," << size_x << "," << size_y << ","
         << layers << "," << grid_resolution << "," << kicad_pcb_file << std::endl;
    
    return 0;
}
```

**Python实现：**
```python
def write_to_file(self, filename: str) -> int:
    try:
        with open(filename, 'w') as f:
            f.write(f"{self._id},{self._name},{self._size_x:.6f},{self._size_y:.6f},"
                   f"{self._layers},{self._grid_resolution:.6f},{self._kicad_pcb_file}\n")
        return 0
    except Exception:
        return -1
```

## 主要差异

### 1. 坐标系统

**C++版本：**
- 使用`std::pair`表示坐标
- 需要手动创建pair对象
- 使用引用传递避免拷贝

**Python版本：**
- 使用`Tuple`表示坐标
- 直接返回元组
- Python自动优化内存使用

### 2. 数值计算

**C++版本：**
- 使用`std::min`、`std::max`等函数
- 需要包含相应头文件
- 编译时优化

**Python版本：**
- 使用Python内置函数
- 更简洁的语法
- 运行时优化

### 3. 文件操作

**C++版本：**
- 使用`std::ofstream`
- 需要手动检查文件状态
- 使用流操作符

**Python版本：**
- 使用`open()`和`with`语句
- 自动处理文件关闭
- 使用字符串格式化

## 性能对比

| 操作 | C++性能 | Python性能 | 说明 |
|------|---------|------------|------|
| 对象创建 | 快 | 中等 | Python对象创建开销 |
| 属性访问 | 快 | 快 | 都很快 |
| 数值计算 | 快 | 中等 | Python有GIL限制 |
| 坐标转换 | 快 | 中等 | Python数值计算开销 |
| 文件I/O | 快 | 快 | 都使用系统调用 |

## 使用建议

1. **选择C++版本**：当需要最高性能、大量几何计算时
2. **选择Python版本**：当需要快速开发、原型设计时
3. **混合使用**：可以用C++实现核心算法，Python实现业务逻辑

## 应用场景

### 1. PCB设计

**C++版本：**
```cpp
// 在PCB设计中使用
board pcb;
pcb.set_size(std::make_pair(100.0, 80.0));
pcb.set_layers(4);
pcb.set_grid_resolution(0.1);
```

**Python版本：**
```python
# 在PCB设计中使用
pcb = Board()
pcb.set_size((100.0, 80.0))
pcb.set_layers(4)
pcb.set_grid_resolution(0.1)
```

### 2. 坐标转换

**C++版本：**
```cpp
// 坐标转换
auto grid_pos = pcb.world_to_grid(50.0, 30.0);
auto world_pos = pcb.grid_to_world(grid_pos.first, grid_pos.second);
```

**Python版本：**
```python
# 坐标转换
grid_pos = pcb.world_to_grid(50.0, 30.0)
world_pos = pcb.grid_to_world(grid_pos[0], grid_pos[1])
```

### 3. 几何计算

**C++版本：**
```cpp
// 几何计算
double area = pcb.get_area();
double perimeter = pcb.get_perimeter();
double aspect_ratio = pcb.get_aspect_ratio();
```

**Python版本：**
```python
# 几何计算
area = pcb.get_area()
perimeter = pcb.get_perimeter()
aspect_ratio = pcb.get_aspect_ratio()
``` 
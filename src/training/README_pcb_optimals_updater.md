# PCB Optimals值更新工具

基于training文件夹中对PCB进行解析更新optimals值的逻辑，利用training文件夹中已有函数，创建了两个工具来对任意PCB进行当前node和edge对应的optimals值的更新。

## 工具说明

### 1. 单个PCB文件更新工具 (`pcb_optimals_updater.py`)

用于处理单个PCB文件，提供详细的更新信息和摘要。

**功能特点：**
- 加载单个PCB文件
- 计算每个节点的当前欧几里得距离和HPWL值
- 与原有optimals值比较，只更新更好的值
- 提供详细的更新日志和摘要
- 自动生成备份文件

**使用方法：**
```bash
# 基本用法
python pcb_optimals_updater.py <pcb_file_path>

# 指定输出文件
python pcb_optimals_updater.py <pcb_file_path> <output_path>
```

**示例：**
```bash
python pcb_optimals_updater.py example.kicad_pcb
python pcb_optimals_updater.py example.kicad_pcb updated_example.kicad_pcb
```

### 2. 批量PCB文件更新工具 (`batch_pcb_optimals_updater.py`)

用于批量处理多个PCB文件，适合处理大量PCB文件。

**功能特点：**
- 批量处理多个PCB文件
- 支持从目录中自动发现PCB文件
- 提供批量处理统计信息
- 支持指定输出目录
- 错误处理和失败文件报告

**使用方法：**
```bash
# 处理多个指定文件
python batch_pcb_optimals_updater.py file1.kicad_pcb file2.kicad_pcb file3.kicad_pcb

# 处理目录中的所有PCB文件
python batch_pcb_optimals_updater.py --dir /path/to/pcb/files

# 指定输出目录
python batch_pcb_optimals_updater.py --dir /path/to/pcb/files --output /path/to/output

# 处理指定文件并输出到指定目录
python batch_pcb_optimals_updater.py file1.kicad_pcb file2.kicad_pcb --output /path/to/output
```

**示例：**
```bash
# 处理当前目录下的所有PCB文件
python batch_pcb_optimals_updater.py --dir . --output ./updated_pcbs

# 处理指定目录下的PCB文件
python batch_pcb_optimals_updater.py --dir /home/user/pcb_files --output /home/user/updated_pcbs
```

## 核心算法

### Optimals值计算

1. **欧几里得距离计算：**
   - 使用 `compute_sum_of_euclidean_distances_between_pads()` 函数
   - 计算当前节点与所有邻居节点之间的最短pad-to-pad距离总和
   - 考虑组件的旋转和位置

2. **HPWL (Half-Perimeter Wire Length) 计算：**
   - 使用 `calc_hpwl_of_net()` 函数
   - 计算每个网络的最小边界框周长
   - 考虑所有相关网络的HPWL总和

3. **更新逻辑：**
   - 只有当新的欧几里得距离小于原有值时才更新
   - 只有当新的HPWL小于原有值时才更新
   - 使用 `update_original_nodes_with_current_optimals()` 更新原始节点列表

### 使用的Training文件夹函数

- `pcb_vector_utils.compute_sum_of_euclidean_distances_between_pads()`: 计算欧几里得距离
- `graph.calc_hpwl_of_net()`: 计算网络HPWL
- `graph.update_original_nodes_with_current_optimals()`: 更新原始节点optimals值
- `pcb.read_pcb_file()`: 读取PCB文件
- `pcb.write_pcb_file()`: 写入PCB文件

## 输出信息

### 单个文件处理输出示例：
```
=== PCB Optimals值更新工具 ===
成功加载PCB文件: example.kicad_pcb
节点数量: 15
边数量: 28
板子尺寸: 100.0 x 80.0

=== 节点Optimals值摘要 ===
节点ID   节点名称              欧几里得距离      HPWL      
------------------------------------------------------------
1        R1                   0.000000        0.000000   
2        C1                   0.000000        0.000000   
3        U1                   0.000000        0.000000   
...

开始更新 15 个节点的optimals值...
节点 1 (R1): 无需更新
节点 2 (C1): 无需更新
节点 3 (U1):
  欧几里得距离: 0.000000 -> 0.000000
  HPWL: 0.000000 -> 0.000000
...

更新完成:
  总节点数: 15
  更新节点数: 3
  更新率: 20.00%

PCB文件已保存到: example_backup.kicad_pcb
=== 更新完成 ===
```

### 批量处理输出示例：
```
=== 批量PCB Optimals值更新工具 ===
处理文件数量: 5
输出目录: ./updated_pcbs

[1/5] 处理文件: /path/to/file1.kicad_pcb
  节点数量: 12
  边数量: 20
  板子尺寸: 80.0 x 60.0
  更新完成: 2/12 个节点 (16.67%)
  保存到: ./updated_pcbs/file1.kicad_pcb

[2/5] 处理文件: /path/to/file2.kicad_pcb
  节点数量: 18
  边数量: 35
  板子尺寸: 120.0 x 90.0
  更新完成: 5/18 个节点 (27.78%)
  保存到: ./updated_pcbs/file2.kicad_pcb
...

=== 处理总结 ===
总文件数: 5
成功处理: 5
失败处理: 0
总节点数: 75
总更新节点数: 15
总体更新率: 20.00%
```

## 注意事项

1. **环境要求：**
   - 需要激活Python虚拟环境：`source setup.sh`
   - 确保training文件夹中的依赖模块可用

2. **文件格式：**
   - 支持 `.kicad_pcb` 和 `.pcb` 格式
   - 输入文件必须是有效的PCB文件

3. **备份策略：**
   - 单个文件工具会自动生成备份文件（添加 `_backup` 或 `_updated` 后缀）
   - 批量工具可以指定输出目录，避免覆盖原文件

4. **错误处理：**
   - 工具会检查文件是否存在和格式是否正确
   - 提供详细的错误信息和处理统计

5. **性能考虑：**
   - 对于大型PCB文件，处理时间可能较长
   - 批量处理时建议先在小数据集上测试

## 扩展功能

工具设计为模块化结构，可以轻松扩展：

1. **添加新的optimals计算函数**
2. **支持更多的PCB文件格式**
3. **添加并行处理能力**
4. **集成到更大的PCB处理流程中**

## 故障排除

### 常见问题：

1. **导入错误：**
   ```
   ModuleNotFoundError: No module named 'pcb'
   ```
   **解决方案：** 确保已激活正确的Python环境：`source setup.sh`

2. **文件不存在错误：**
   ```
   错误: PCB文件不存在: example.kicad_pcb
   ```
   **解决方案：** 检查文件路径是否正确

3. **PCB数据错误：**
   ```
   错误: PCB文件中没有找到有效的PCB数据
   ```
   **解决方案：** 检查PCB文件格式是否正确

4. **权限错误：**
   ```
   保存PCB文件时出错: Permission denied
   ```
   **解决方案：** 检查输出目录的写入权限 
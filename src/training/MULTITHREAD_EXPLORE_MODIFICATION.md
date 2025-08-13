# SAC多线程探索功能修改说明

## 概述

本次修改将SAC训练中的`explore_for_expert_targets`方法从单线程for循环改为多线程并行实现，以提高探索效率。

## 修改内容

### 1. 新增导入模块

```python
import threading
import queue
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import os
```

### 2. 新增ThreadSafeExplorer类

#### 2.1 类结构
```python
class ThreadSafeExplorer:
    def __init__(self, sac_model, num_workers=4, verbose=0):
        # 初始化线程安全探索器
```

#### 2.2 主要方法

##### `_explore_worker(self, worker_id, steps_per_worker, output_dir, save_pcb_every_n_steps)`
- **功能**: 单个工作线程的探索函数
- **线程安全**: 使用环境锁保护环境访问
- **PCB保存**: 线程安全的PCB文件保存机制

##### `_save_pcb_thread_safe(self, output_dir, step_id, worker_id)`
- **功能**: 线程安全的PCB文件保存
- **锁机制**: 使用PCB保存锁确保文件写入安全
- **错误处理**: 捕获并记录保存过程中的错误

##### `explore(self, total_steps, output_dir=None, save_pcb_every_n_steps=1000)`
- **功能**: 多线程探索主函数
- **任务分配**: 将总步数分配给多个工作线程
- **线程池**: 使用ThreadPoolExecutor管理线程
- **进度监控**: 实时监控探索进度

### 3. SAC类修改

#### 3.1 初始化修改
```python
# 在__init__方法中添加
self.explorer = ThreadSafeExplorer(self, num_workers=4, verbose=verbose)
self.env_lock = threading.Lock()
```

#### 3.2 explore_for_expert_targets方法重写
```python
def explore_for_expert_targets(self,
                               reward_target_exploration_steps=25_000,
                               output_dir=None,
                               save_pcb_every_n_steps=1000,
                               num_workers=4):
    # 使用多线程探索器执行探索
    self.explorer.explore(
        total_steps=reward_target_exploration_steps,
        output_dir=output_dir,
        save_pcb_every_n_steps=save_pcb_every_n_steps
    )
```

## 线程安全机制

### 1. 环境锁 (env_lock)
- **用途**: 保护训练环境的访问
- **作用范围**: 环境步进和重置操作
- **实现**: `threading.Lock()`

### 2. PCB保存锁 (pcb_save_lock)
- **用途**: 保护PCB文件写入操作
- **作用范围**: 所有PCB文件保存操作
- **实现**: `threading.Lock()`

### 3. 进度锁 (progress_lock)
- **用途**: 保护全局计数器更新
- **作用范围**: 步数计数器和完成计数器
- **实现**: `threading.Lock()`

## 性能优化

### 1. 并行执行
- **原实现**: 单线程顺序执行
- **新实现**: 多线程并行执行
- **性能提升**: 理论上可达到4倍性能提升（4个工作线程）

### 2. 任务分配
```python
steps_per_worker = total_steps // self.num_workers
remaining_steps = total_steps % self.num_workers
```

### 3. 负载均衡
- 平均分配步数给每个工作线程
- 剩余步数分配给前几个线程

## 错误处理和日志

### 1. 异常处理
- PCB保存异常捕获和记录
- 线程执行异常处理
- 环境访问异常处理

### 2. 日志系统
```python
if verbose > 0:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    self.logger = logging.getLogger(__name__)
```

### 3. 进度监控
- 实时记录每个线程的完成情况
- 统计总步数和完成次数
- 提供详细的执行日志

## 使用方法

### 1. 基本使用
```python
# 使用默认4个工作线程
sac_model.explore_for_expert_targets(
    reward_target_exploration_steps=25_000,
    output_dir="./output",
    save_pcb_every_n_steps=1000
)
```

### 2. 自定义线程数
```python
# 使用8个工作线程
sac_model.explore_for_expert_targets(
    reward_target_exploration_steps=25_000,
    output_dir="./output",
    save_pcb_every_n_steps=1000,
    num_workers=8
)
```

## 文件输出

### 1. PCB文件命名
- 普通步数: `explore_step_{step_id}_worker_{worker_id}.pcb`
- 重置步数: `explore_reset_{step_id}_worker_{worker_id}.pcb`

### 2. 输出目录结构
```
output/
└── explore_pcb/
    ├── explore_step_1000_worker_0.pcb
    ├── explore_step_1000_worker_1.pcb
    ├── explore_step_1000_worker_2.pcb
    ├── explore_step_1000_worker_3.pcb
    └── ...
```

## 兼容性

### 1. 向后兼容
- 保持原有的方法签名
- 添加新的可选参数
- 默认行为与原来一致

### 2. 环境要求
- Python 3.6+
- threading模块（标准库）
- concurrent.futures模块（标准库）

## 测试

### 1. 单元测试
运行测试脚本验证功能：
```bash
python test_multithread_explore.py
```

### 2. 功能测试
- 线程安全性测试
- PCB保存功能测试
- 进度监控测试

## 注意事项

### 1. 内存使用
- 多线程会增加内存使用
- 建议根据系统资源调整线程数

### 2. 文件系统
- 确保输出目录有写入权限
- 大量PCB文件可能占用较多磁盘空间

### 3. 调试
- 设置verbose=1启用详细日志
- 使用较少的线程数进行调试

## 性能对比

### 1. 理论性能
- **单线程**: 1x
- **4线程**: 4x（理想情况）
- **实际性能**: 取决于CPU核心数和I/O瓶颈

### 2. 实际测试
建议在实际环境中进行性能测试，考虑以下因素：
- CPU核心数
- 内存容量
- 磁盘I/O速度
- 网络带宽（如果有网络存储）

## 未来改进

### 1. 可能的优化
- 使用进程池替代线程池（绕过GIL限制）
- 实现异步I/O操作
- 添加更细粒度的锁机制

### 2. 功能扩展
- 支持动态调整线程数
- 添加更详细的性能监控
- 实现断点续传功能 
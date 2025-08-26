# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 环境设置

### Python环境激活
代码库使用Python虚拟环境，所有Python操作都必须在激活环境后进行：
```bash
source setup.sh
```

这个脚本会：
- 设置RL_PCB环境变量
- 配置CUDA路径（版本12.1）
- 激活venv虚拟环境

### 初始环境搭建
首次设置开发环境：
```bash
./setup_dev.sh                    # 完整安装（包含GPU支持）
./setup_dev.sh --cpu_only         # 仅CPU版本
```

## 核心架构

### 目录结构
- `src/training/` - 强化学习训练核心代码
  - `core/agent/` - 智能体实现（观察空间、动作空间、参数配置）
  - `core/environment/` - PCB布局环境实现
  - `train.py` - 主训练脚本
  - `SAC.py` / `TD3.py` - 强化学习算法实现
- `src/evaluation_scripts/` - 评估脚本
- `src/report_generation/` - 实验报告生成
- `dataset/` - PCB数据集
- `experiments/` - 参数实验配置
- `tests/` - 验证测试

### 强化学习架构
- **环境**: PCB组件布局问题建模为多智能体强化学习环境
- **智能体**: 每个PCB组件作为独立智能体，学习局部布局决策
- **观察空间**: 包含局部和全局信息（line-of-sight、overlap、域信息、欧氏距离等）
- **动作空间**: 组件位置和方向调整
- **算法**: 支持SAC和TD3两种深度强化学习算法

## 常用命令

### 运行测试
```bash
cd tests/01_training_td3_cpu
./run.sh
```

### 运行实验
```bash
cd experiments/00_parameter_exeperiments  
./run.sh
```

### 验证环境设置
```bash
python tests/00_verify_machine_setup/test_setup.py
```

### 清理实验结果
```bash
./clean.sh  # 在测试或实验目录中运行
```

## 开发工作流

### 训练流程
1. 配置超参数文件（hyperparameters/hp_sac.json 或 hp_td3.json）
2. 设置运行配置（run_config.txt）
3. 执行训练调度器（scheduler.sh）
4. 生成实验报告
5. 运行评估脚本

### 二进制工具依赖
项目依赖以下C++工具（位于bin/目录）：
- `kicadParser` - KiCad PCB文件解析
- `sa` - 模拟退火基线算法  
- `pcb_router` - PCB自动布线

### 数据流
1. KiCad PCB文件 (.kicad_pcb) → 解析为图结构
2. 图结构 → 强化学习环境状态
3. 智能体动作 → PCB组件位置更新
4. 评估指标：欧氏距离、半周长线长(HPWL)、重叠度

## 文件格式和约定

### PCB文件处理
- 输入：KiCad格式(.kicad_pcb)
- 中间格式：.board, .edges, .nodes文件
- 输出：优化后的PCB布局

### 实验配置
- 超参数：JSON格式存储
- 运行配置：文本格式，支持多实验并行
- 报告配置：Python脚本生成

### 禁止访问的目录
根据项目配置，以下目录被明确禁止检索：
- `venv/` - Python虚拟环境
- `bin/` - 编译后的二进制工具
- `ansible/` - 部署配置
- `lib/` - 库文件
- `c_plus_lib/` - C++库（禁止导入相关函数）

## 常见任务

### 添加新的强化学习算法
1. 在`src/training/`中创建新算法文件
2. 更新`model_setup.py`中的模型选择逻辑
3. 配置对应的超参数文件

### 修改观察空间或动作空间
1. 编辑`src/training/core/agent/observation.py`
2. 更新`src/training/core/agent/agent.py`中的空间定义
3. 确保环境和智能体的一致性

### 运行特定PCB文件的实验
1. 将PCB文件放入`dataset/`目录
2. 更新配置文件中的PCB路径
3. 执行对应的实验脚本

这个项目专注于使用强化学习解决PCB自动布局问题，通过多智能体学习实现组件的智能布局优化。
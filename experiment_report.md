# 强化学习实验报告

## 1. 概述

本文档旨在详细说明 `experiments_archive` 文件夹中所包含的一系列强化学习实验。这些实验围绕印刷电路板（PCB）自动布线问题，系统地评估了不同强化学习算法、奖励函数配置、数据集及关键超参数（如经验回放缓冲区大小）对模型性能的影响。

实验遵循了逻辑递进的研究流程：首先进行参数寻优，然后在不同质量的数据集上验证，接着通过消融研究分析模型组件的重要性，并最终对核心超参数进行专项测试。

---

## 2. 实验详情

以下是五个核心实验的详细说明：

### 2.1. `00_parameter_exeperiments` (参数实验)

*   **目的**: 此实验的核心目标是为 `TD3` 和 `SAC` 两种强化学习算法寻找最优的奖励函数配置。实验通过调整奖励函数中三个关键组件 (`-w`, `--hpwl`, `-o`) 的权重组合，来探索它们对最终布线性能的影响。
*   **数据集**: 使用 `base` 标准数据集进行训练和评估。
*   **核心变量**:
    *   **奖励函数权重**: 系统性地改变 `-w`, `--hpwl`, `-o` 的权重值。
    *   **强化学习算法**: 对比 `TD3` 和 `SAC` 两种算法。

### 2.2. `01_parameter_expert_experiments` (专家参数实验)

*   **目的**: 此实验与 `00` 号实验的目标一致，但测试环境切换到了一个更高质量的数据集上。其目的是验证在“专家”或“优化”过的数据上，`00` 号实验中得出的最优参数配置是否依然有效。
*   **数据集**: 使用 `base_opt` 数据集，该数据集可能经过了专家系统的预处理或包含了更优的布线示例。
*   **核心变量**: 实验变量与 `00` 号实验相同（奖励权重和算法），但作用于不同的数据集。

### 2.3. `02_ablation_experiments` (消融实验)

*   **目的**: 这是一组“消融研究”，旨在量化奖励函数中每个独立组件对模型性能的贡献。通过在实验中将某个组件的权重设置为零（即“消融”该组件），可以评估其对最终结果的正面或负面影响。
*   **数据集**: 使用 `base` 标准数据集。
*   **核心变量**: 将奖励函数中的 `-w` 或 `--hpwl` 组件的权重单独设置为零。

### 2.4. `03_ablation_expert_experiments` (专家消融实验)

*   **目的**: 此实验在“专家”数据集上重复 `02` 号消融研究。其目的是分析在高质量数据环境下，奖励函数各组件的重要性是否会发生变化，从而更深入地理解算法与数据质量之间的相互作用。
*   **数据集**: 使用 `base_opt` 数据集。
*   **核心变量**: 在 `base_opt` 数据集上对奖励函数的组件进行消融。

### 2.5. `04_replay_buffer_sizing_experiments` (回放缓冲区大小实验)

*   **目的**: 此实验专注于研究强化学习中的一个关键超参数——经验回放缓冲区（Replay Buffer）的大小——对模型性能的具体影响。
*   **数据集**: 使用 `base` 标准数据集。
*   **核心变量**: 回放缓冲区的大小。实验通过两种不同的方式进行配置：
    1.  **固定大小**: 测试了一系列固定的缓冲区大小（例如 300k, 600k, 1.2M, 2.4M, 4.8M）。
    2.  **动态大小**: 使用 `incremental_replay_buffer` 命令行参数（`double`, `triple`, `quadruple`）来动态地扩展缓冲区。

---

## 3. 总体研究策略

该系列实验的设计体现了严谨的科研方法：
1.  **参数寻优**: 从在标准数据集上寻找最优奖励函数配置开始 (`00`)。
2.  **泛化验证**: 将找到的配置在更高质量的数据集上进行验证 (`01`)。
3.  **组件分析**: 通过消融研究，在标准 (`02`) 和高质量 (`03`) 数据集上分析并理解奖励函数各组件的内在价值。
4.  **超参研究**: 最后，对影响学习过程稳定性和效率的关键超参数（缓冲区大小）进行专项、深入的测试 (`04`)。 
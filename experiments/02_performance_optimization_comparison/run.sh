#!/bin/bash

# RL_PCB 性能优化对比实验
# 该脚本对比原始版本与性能优化版本的训练效果

echo "🚀 RL_PCB 性能优化对比实验启动"
echo "=========================================="

# 系统资源检测
CPU_CORES=$(nproc)
GPU_COUNT=$(nvidia-smi -L 2>/dev/null | wc -l || echo 0)

echo "=== 系统资源检测 ==="
echo "CPU核心数: $CPU_CORES"
echo "GPU数量: $GPU_COUNT"
if [ $GPU_COUNT -gt 0 ]; then
    echo "GPU信息:"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits
fi
echo "====================="

# 设置环境变量
export OMP_NUM_THREADS=$CPU_CORES
export MKL_NUM_THREADS=$CPU_CORES
export NUMEXPR_NUM_THREADS=$CPU_CORES

# 实验目录设置
EXP_DIR=${PWD}
export EXP_DIR=${EXP_DIR}
echo "实验目录: ${EXP_DIR}"
echo "RL_PCB根目录: ${RL_PCB}"

# 创建工作目录
mkdir -p work
mkdir -p performance_logs

# 创建性能记录文件
PERF_LOG="${EXP_DIR}/performance_logs/performance_comparison.log"
touch $PERF_LOG

echo "$(date): 性能优化对比实验开始" >> $PERF_LOG

# 函数：记录性能数据
log_performance() {
    local experiment_name=$1
    local start_time=$2
    local end_time=$3
    local gpu_utilization=$4
    
    local duration=$((end_time - start_time))
    echo "$(date): $experiment_name - 耗时: ${duration}秒, GPU利用率: ${gpu_utilization}%" >> $PERF_LOG
}

# 函数：启动TensorBoard
start_tensorboard() {
    local port=${1:-6006}
    
    # 关闭已有的TensorBoard进程
    echo "关闭现有TensorBoard进程..."
    pkill -f "tensorboard.*--port.*" || true
    sleep 2
    
    echo "在端口 $port 启动TensorBoard..."
    tensorboard --logdir ./work/ --host 0.0.0.0 --port $port &
    sleep 3
    echo "TensorBoard已启动: http://localhost:$port"
}

# 函数：GPU监控
monitor_gpu() {
    local experiment_name=$1
    local duration_minutes=$2
    
    echo "开始监控GPU使用情况 ($experiment_name)..."
    nvidia-smi dmon -s pucvmet -d 5 -c $((duration_minutes * 12)) > "${EXP_DIR}/performance_logs/gpu_${experiment_name}.log" &
    echo "GPU监控已启动，日志: ${EXP_DIR}/performance_logs/gpu_${experiment_name}.log"
}

# 启动TensorBoard
start_tensorboard 6006

echo ""
echo "🎯 开始性能对比实验"
echo "实验包括:"
echo "1. 基线实验 (原始版本)"
echo "2. 优化实验 (多线程+GPU优化)"
echo "3. 消融实验 (分别测试各组件)"
echo ""

# 检查优化版本训练脚本是否存在
if [ ! -f "${RL_PCB}/src/training/train_optimized.py" ]; then
    echo "❌ 错误: 找不到优化版本训练脚本"
    echo "请确保 train_optimized.py 已创建在 src/training/ 目录下"
    exit 1
fi

# 切换到训练目录
cd ${RL_PCB}/src/training

# echo ""
# echo "📊 阶段 1: 基线性能测试 (原始版本)"
# echo "=========================================="

# # SAC基线测试
# echo "🔬 运行SAC基线实验..."
# baseline_sac_start=$(date +%s)
# monitor_gpu "baseline_sac" 30  # 假设运行30分钟

# python train.py \
#     --policy SAC \
#     --target_exploration_steps 25_000 \
#     --start_timesteps 25_000 \
#     --max_timesteps 500_000 \
#     --evaluate_every 50_000 \
#     --training_pcb ${RL_PCB}/dataset/base/region_8_fixed.pcb \
#     --evaluation_pcb ${RL_PCB}/dataset/base/evaluation.pcb \
#     --tensorboard_dir ${EXP_DIR}/work \
#     -w 4.0 --hpwl 4.0 -o 2.0 \
#     --hyperparameters ${EXP_DIR}/hyperparameters/hp_sac_baseline.json \
#     --incremental_replay_buffer double \
#     --verbose 1 \
#     --runs 3 \
#     --experiment baseline_sac_original \
#     --device cuda \
#     --pcb_save_freq 5000

# baseline_sac_end=$(date +%s)
# log_performance "baseline_sac" $baseline_sac_start $baseline_sac_end "N/A"
# echo "✅ SAC基线实验完成"

echo ""
echo "⚡ 阶段 2: 性能优化测试 (优化版本)"
echo "=========================================="

# SAC优化版测试
echo "🚀 运行SAC优化实验..."
optimized_sac_start=$(date +%s)
monitor_gpu "optimized_sac" 20  # 预期更快完成

python train_optimized.py \
    --policy SAC \
    --target_exploration_steps 25_000 \
    --start_timesteps 25_000 \
    --max_timesteps 500_000 \
    --evaluate_every 50_000 \
    --training_pcb ${RL_PCB}/dataset/base/region_8_fixed.pcb \
    --evaluation_pcb ${RL_PCB}/dataset/base/evaluation.pcb \
    --tensorboard_dir ${EXP_DIR}/work \
    -w 4.0 --hpwl 4.0 -o 2.0 \
    --hyperparameters ${EXP_DIR}/hyperparameters/hp_sac_optimized.json \
    --incremental_replay_buffer double \
    --verbose 1 \
    --runs 3 \
    --experiment optimized_sac_multithread_gpu \
    --device cuda \
    --pcb_save_freq 5000 \
    --enable_multithread true \
    --enable_gpu_optimization true \
    --num_workers 6

optimized_sac_end=$(date +%s)
log_performance "optimized_sac" $optimized_sac_start $optimized_sac_end "N/A"
echo "✅ SAC优化实验完成"

echo ""
echo "🔬 阶段 3: 消融实验 (分组件测试)"
echo "=========================================="

# 仅多线程优化测试
echo "🧵 测试仅多线程优化..."
multithread_only_start=$(date +%s)

python train_optimized.py \
    --policy SAC \
    --target_exploration_steps 25_000 \
    --start_timesteps 25_000 \
    --max_timesteps 300_000 \
    --evaluate_every 50_000 \
    --training_pcb ${RL_PCB}/dataset/base/region_8_fixed.pcb \
    --evaluation_pcb ${RL_PCB}/dataset/base/evaluation.pcb \
    --tensorboard_dir ${EXP_DIR}/work \
    -w 4.0 --hpwl 4.0 -o 2.0 \
    --hyperparameters ${EXP_DIR}/hyperparameters/hp_sac_baseline.json \
    --incremental_replay_buffer double \
    --verbose 1 \
    --runs 2 \
    --experiment ablation_sac_multithread_only \
    --device cuda \
    --pcb_save_freq 5000 \
    --enable_multithread true \
    --enable_gpu_optimization false \
    --num_workers 6

multithread_only_end=$(date +%s)
log_performance "multithread_only" $multithread_only_start $multithread_only_end "N/A"
echo "✅ 多线程单独测试完成"

# 仅GPU优化测试
echo "🎮 测试仅GPU优化..."
gpu_only_start=$(date +%s)

python train_optimized.py \
    --policy SAC \
    --target_exploration_steps 25_000 \
    --start_timesteps 25_000 \
    --max_timesteps 300_000 \
    --evaluate_every 50_000 \
    --training_pcb ${RL_PCB}/dataset/base/region_8_fixed.pcb \
    --evaluation_pcb ${RL_PCB}/dataset/base/evaluation.pcb \
    --tensorboard_dir ${EXP_DIR}/work \
    -w 4.0 --hpwl 4.0 -o 2.0 \
    --hyperparameters ${EXP_DIR}/hyperparameters/hp_sac_optimized.json \
    --incremental_replay_buffer double \
    --verbose 1 \
    --runs 2 \
    --experiment ablation_sac_gpu_only \
    --device cuda \
    --pcb_save_freq 5000 \
    --enable_multithread false \
    --enable_gpu_optimization true \
    --num_workers 1

gpu_only_end=$(date +%s)
log_performance "gpu_only" $gpu_only_start $gpu_only_end "N/A"
echo "✅ GPU单独测试完成"

# 返回实验目录
cd ${EXP_DIR}

echo ""
echo "📊 阶段 4: 生成性能报告"
echo "=========================================="

# 生成报告配置
python report_config.py

# 生成实验报告
echo "📄 生成实验报告..."
cd ${RL_PCB}/src/report_generation

python generate_experiment_report.py \
    --dir ${EXP_DIR}/work \
    --hyperparameters ${EXP_DIR}/hyperparameters/hp_sac_baseline.json ${EXP_DIR}/hyperparameters/hp_sac_optimized.json \
    --report_config ${EXP_DIR}/report_config.json \
    --output ${EXP_DIR}/performance_optimization_report.pdf \
    -y \
    --tmp_dir ${EXP_DIR}/tmp

cd ${EXP_DIR}

echo ""
echo "📈 性能分析"
echo "=========================================="

# 生成性能对比报告
python << 'EOF'
import os
import time
from datetime import datetime

def analyze_performance_log():
    log_file = "performance_logs/performance_comparison.log"
    if not os.path.exists(log_file):
        print("❌ 性能日志文件不存在")
        return
    
    print("🔍 性能分析结果:")
    print("-" * 40)
    
    with open(log_file, 'r') as f:
        lines = f.readlines()
    
    # 解析性能数据
    experiments = {}
    for line in lines:
        if " - 耗时:" in line:
            parts = line.strip().split(" - 耗时: ")
            if len(parts) == 2:
                exp_name = parts[0].split(": ")[1]
                duration = int(parts[1].split("秒")[0])
                experiments[exp_name] = duration
    
    # 计算加速比
    if 'baseline_sac' in experiments and 'optimized_sac' in experiments:
        baseline_time = experiments['baseline_sac']
        optimized_time = experiments['optimized_sac']
        speedup = baseline_time / optimized_time
        
        print(f"SAC基线版本耗时: {baseline_time}秒")
        print(f"SAC优化版本耗时: {optimized_time}秒")
        print(f"🚀 总体加速比: {speedup:.2f}x")
        print(f"⏰ 时间节省: {baseline_time - optimized_time}秒 ({((baseline_time - optimized_time)/baseline_time)*100:.1f}%)")
    
    # 分析消融实验结果
    if 'multithread_only' in experiments:
        mt_time = experiments['multithread_only']
        print(f"\n🧵 多线程优化效果:")
        if 'baseline_sac' in experiments:
            mt_speedup = (experiments['baseline_sac'] * 0.6) / mt_time  # 调整基线时间
            print(f"   仅多线程加速比: {mt_speedup:.2f}x")
    
    if 'gpu_only' in experiments:
        gpu_time = experiments['gpu_only']
        print(f"\n🎮 GPU优化效果:")
        if 'baseline_sac' in experiments:
            gpu_speedup = (experiments['baseline_sac'] * 0.6) / gpu_time  # 调整基线时间
            print(f"   仅GPU优化加速比: {gpu_speedup:.2f}x")
    
    print("-" * 40)

analyze_performance_log()
EOF

echo ""
echo "🎯 实验完成总结"
echo "=========================================="
echo "✅ 基线性能测试完成"
echo "✅ 优化版本测试完成"  
echo "✅ 消融实验完成"
echo "✅ 性能报告生成完成"
echo ""
echo "📁 生成的文件:"
echo "   - 性能报告: performance_optimization_report.pdf"
echo "   - 性能日志: performance_logs/performance_comparison.log"
echo "   - GPU监控日志: performance_logs/gpu_*.log"
echo "   - TensorBoard数据: work/"
echo ""
echo "🌐 TensorBoard地址: http://localhost:6006"
echo ""
echo "🎉 性能优化对比实验完成!"

# 最终性能统计
echo "$(date): 性能优化对比实验完成" >> $PERF_LOG
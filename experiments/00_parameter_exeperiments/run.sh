#!/bin/bash

# 系统资源检测和优化配置
CPU_CORES=$(nproc)                      # 获取CPU核心数
GPU_COUNT=$(nvidia-smi -L 2>/dev/null | wc -l || echo 0)  # 获取GPU数量

echo "=== 系统资源检测 ==="
echo "CPU核心数: $CPU_CORES"
echo "GPU数量: $GPU_COUNT"
if [ $GPU_COUNT -gt 0 ]; then
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits
fi
echo "====================="

# 设置环境变量以优化多线程性能
export OMP_NUM_THREADS=$CPU_CORES       # OpenMP线程数
export MKL_NUM_THREADS=$CPU_CORES       # Intel MKL线程数
export NUMEXPR_NUM_THREADS=$CPU_CORES   # NumExpr线程数
export CUDA_VISIBLE_DEVICES=0,1         # 显式设置可见的GPU

# 根据系统资源动态调整并行实例数
# 对于双GPU系统，建议使用较多的并行实例以充分利用资源
if [ $GPU_COUNT -ge 2 ]; then
    PARALLEL_INSTANCES=$((CPU_CORES / 2))  # 双GPU情况下可以更激进
else
    PARALLEL_INSTANCES=$((CPU_CORES / 4))  # 单GPU情况下保守一些
fi

# 确保至少有2个实例，最多不超过8个
PARALLEL_INSTANCES=$(( PARALLEL_INSTANCES < 2 ? 2 : PARALLEL_INSTANCES ))
PARALLEL_INSTANCES=$(( PARALLEL_INSTANCES > 8 ? 8 : PARALLEL_INSTANCES ))

echo "设置并行实例数: $PARALLEL_INSTANCES"

# 二进制工具路径定义
KICAD_PARSER=${RL_PCB}/bin/kicadParser  # KiCad解析器路径
SA_PCB=${RL_PCB}/bin/sa                 # 模拟退火工具路径
PCB_ROUTER=${RL_PCB}/bin/pcb_router     # PCB布线工具路径

# 实验目录设置
EXP_DIR=${PWD}                          # 获取当前目录作为实验目录
export EXP_DIR=${EXP_DIR}               # 导出为环境变量
echo "Script launched from ${EXP_DIR}"   # 打印启动路径
echo "RL_PCB repository root is ${RL_PCB}" # 显示项目根目录

# 创建工作目录
mkdir -p work                           # 创建work目录存放结果

# 关闭已有的TensorBoard进程
echo "Closing existing tensorboard processes ..."
pkill -f "tensorboard.*6001" || true   # 关闭端口6001上的TensorBoard进程，忽略错误
sleep 1                                 # 等待进程关闭

echo "Starting tensorboard ... "        # 启动TensorBoard监控
tensorboard --logdir ./work/ --host 0.0.0.0 --port 6001 &  # 后台运行TensorBoard
sleep 2                                 # 等待2秒确保启动

# 进入训练目录执行调度
cd ${RL_PCB}/src/training               # 切换到训练脚本目录
# 将scheduler.sh改为可执行

./scheduler.sh --run_config ${EXP_DIR}/run_config.txt --logfile $EXP_DIR/scheduler.log --instances $PARALLEL_INSTANCES --yes 
                                        # 启动训练调度器，使用动态计算的并行实例数
cd ${EXP_DIR}                           # 返回实验目录

# 生成报告配置
python report_config.py                 # 创建report_config.json配置文件

# 生成实验报告
cd ${RL_PCB}/src/report_generation      # 切换到报告生成目录
python generate_experiment_report.py --dir ${EXP_DIR}/work --hyperparameters ${EXP_DIR}/hyperparameters/hp_td3.json ${EXP_DIR}/hyperparameters/hp_sac.json --report_config ${EXP_DIR}/report_config.json --output ${EXP_DIR}/experiment_report.pdf -y --tmp_dir ${EXP_DIR}/tmp
                                        # 生成PDF格式实验报告
cd ${EXP_DIR}                           # 返回实验目录

# 检查二进制工具是否存在
if [ -e "$KICAD_PARSER" ] && [ -e "$SA_PCB" ] && [ -e "$PCB_ROUTER" ]; then
    echo "Starting evaluation ..."      # 如果工具齐全则开始评估
    cd ${RL_PCB}/src/evaluation_scripts # 切换到评估脚本目录

    # 设置评估输出目录
    TD3_EVAL_TESTING_DIR=${EXP_DIR}/work/eval_testing_set
    SAC_EVAL_TESTING_DIR=${EXP_DIR}/work/eval_testing_set

    # 执行评估脚本（注释掉的是简化版评估）
        #./eval_just_do_it.sh -p ${RL_PCB}/dataset/base/evaluation.pcb -b ${RL_PCB}/dataset/base_raw --bin_dir ${RL_PCB}/bin --path_prefix "" -d ${EXP_DIR}/work -e parameter_experiment_262,parameter_experiment_622 --report_type both,mean -o ${TD3_EVAL_TESTING_DIR} --runs 2 --max_steps 200 --report_type both,mean --skip_simulated_annealing 
        
    ./eval_just_do_it.sh -p ${RL_PCB}/dataset/base/evaluation.pcb -b ${RL_PCB}/dataset/base_raw --bin_dir ${RL_PCB}/bin --path_prefix "" -d ${EXP_DIR}/work -e parameter_experiment_262,parameter_experiment_622,parameter_experiment_226,parameter_experiment_442 --report_type both,mean -o ${TD3_EVAL_TESTING_DIR} --runs 4 --max_steps 600
                                        # 完整评估4种参数实验，每个跑600步

    cd ${EXP_DIR}                       # 返回实验目录
else
    echo "One or more place and route binaries expected at ${RL_PCB}/bin were not found."
                                        # 如果缺少工具则报错
fi
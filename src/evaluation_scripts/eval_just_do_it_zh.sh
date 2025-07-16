#!/bin/bash 

# 设置默认二进制文件目录
BIN=../../../../bin             

# 设置默认电路板目录             
BOARDS=../../../../boards       

# 设置默认PCB文件路径
PCB=/home/luke/Desktop/semi_autonomous/boards/05_3_multi_agent/no_power_components/05_3_multi_agent_no_power_0.pcb
# 备选PCB文件路径（被注释）
#PCB=/home/luke/Desktop/semi_autonomous/boards/05_3_multi_agent/no_power_components/05_3_multi_agent_no_power_eval_0.pcb

# 默认运行次数
RUNS=4

# 路径前缀（当前目录）
PATH_PREFIX="."

# 默认报告类型为"mean"
REPORT_TYPE="mean"

# 默认不跳过模拟退火
SKIP_SA=false

# 默认不随机打乱
SHUFFLE=false

# 最大步数限制
MAX_STEPS=600

# 默认使用CUDA设备
DEVICE="cuda"

# 帮助信息函数
print_help() {
    echo "-d, --dir                 包含实验运行的目录"
    echo "-e, --experiment          要评估的实验名称" 
    echo "-o, --output              输出目录"
    echo "--help                    打印帮助信息并退出"
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -b|--boards_dir)
            BOARDS="${2%/}"   # 移除路径末尾的斜杠
            shift
            shift
            ;;
        --bin_dir)
            BIN="${2%/}"      # 移除路径末尾的斜杠
            shift
            shift
            ;;
        -d|--dir)
            EXP_DIR="${2%/}"  # 实验目录
            shift
            shift
            ;;
        --device)
            DEVICE="$2"       # 设置计算设备
            shift
            shift
            ;;            
        -e|--experiment)       # 实验名称（多个用逗号分隔，无空格）
            ALL_EXP="$2"
            shift
            shift
            ;;      
        --max_steps)
            MAX_STEPS="$2"    # 设置最大步数
            shift
            shift
            ;;
        -o|--output)
            OUTPUT="${2%/}"   # 输出目录
            shift
            shift
            ;;      
        --path_prefix)
            PATH_PREFIX="${2%/}"  # 路径前缀
            shift
            shift
            ;;
        -p|--pcb)
            PCB="$2"          # PCB文件路径
            shift
            shift
            ;;            
        -r|--runs)
            RUNS="$2"         # 运行次数
            shift
            shift
            ;;
        --report_type)
            REPORT_TYPE="$2"  # 报告类型
            shift
            shift
            ;;
        --shuffle)
            SHUFFLE=true      # 启用随机打乱
            shift
            ;;
        --skip_simulated_annealing)
            SKIP_SA=true      # 跳过模拟退火
            shift
            ;;  
        --help)
            print_help        # 显示帮助
            exit 0
            ;;
        -*|--*)
            echo "未知选项 $1"
            exit 1
            ;;
        *)
            POSITIONAL_ARGS+=($1)  # 位置参数
            shift
            ;;
    esac
done

# 确保路径末尾没有斜杠
BIN="${BIN%/}"                  
BOARDS="${BOARDS%/}"            
PCB="${PCB%/}"            

# 构建完整路径
EXP_DIR=$PATH_PREFIX/$EXP_DIR
OUTPUT=$PATH_PREFIX/$OUTPUT

# 打印配置信息
echo ""
echo "二进制目录 (BIN)                  $BIN"
echo "电路板目录 (BOARD)                $BOARDS"
echo "实验目录 (EXP_DIR)                $EXP_DIR"
echo "实验名称 (EXP)                    $ALL_EXP"
echo "输出目录 (OUTPUT)                 $OUTPUT"
echo "PCB文件 (PCB)                     $PCB"
echo "跳过模拟退火 (SKIP_SA)            $SKIP_SA"
echo ""
sleep 1  # 暂停1秒

# 初始化数组
allRuns=()    # 存储所有运行路径
allExps=()    # 存储所有实验名称
allRewardParms=()  # 存储所有奖励参数

# 处理每个实验
IFS=','  # 设置分隔符为逗号
for EXP in ${ALL_EXP}; do
    # 遍历实验目录
    for dir in $EXP_DIR/*; do 
        echo "在目录 '$dir' 中搜索 '$EXP'"
        # 检查目录中的文件
        for file in $dir/*; do
            # 查找描述文件（以_desc.log结尾）
            if [[ ${file: -9} == "_desc.log" ]]; then
                # 读取描述文件内容
                while read -r line; do 
                    # 提取实验名称
                    tmp=$(echo "$line" | awk '{split($0,a," -> "); if(a[1] == "experiment") {print a[2];} }')
                    if [ ! -z "$tmp" ]; then
                        EXPERIMENT=$(echo $tmp | tr -d '\r\n')
                        # 如果实验不匹配则跳过
                        if [[ $EXPERIMENT != $EXP ]]; then
                            break;
                        fi
                    fi

                    # 提取运行名称
                    tmp=$(echo "$line" | awk '{split($0,a," -> "); if(a[1] == "run_name") {print a[2];} }')
                    if [ ! -z "$tmp" ]; then
                        RUN_NAME=$(echo $tmp | tr -d '\r\n')
                    fi

                    # 提取运行编号
                    tmp=$(echo "$line" | awk '{split($0,a," -> "); if(a[1] == "run") {print a[2];} }')
                    if [ ! -z "$tmp" ]; then
                        RUN=$(echo $tmp | tr -d '\r\n')
                    fi

                    # 提取RL模型类型
                    tmp=$(echo "$line" | awk '{split($0,a," -> "); if(a[1] == "rl_model_type") {print a[2];} }')
                    if [ ! -z "$tmp" ]; then
                        RL_MODEL_TYPE=$(echo $tmp | tr -d '\r\n')
                    fi

                    # 提取超参数路径
                    tmp=$(echo "$line" | awk '{split($0,a," -> "); if(a[1] == "hyperparameters") {print a[2];} }')
                    if [ ! -z "$tmp" ]; then
                        HYPERPARAMETERS=$(echo $tmp | tr -d '\r\n')
                    fi

                    # 提取欧式线长权重
                    tmp=$(echo "$line" | awk '{split($0,a," -> "); if(a[1] == "w") {print a[2];} }')
                    if [ ! -z "$tmp" ]; then
                        EUCLIDEAN_WIRELENGTH=$(echo $tmp | tr -d '\r\n')
                    fi

                    # 提取半周长线长权重
                    tmp=$(echo "$line" | awk '{split($0,a," -> "); if(a[1] == "hpwl") {print a[2];} }')
                    if [ ! -z "$tmp" ]; then
                        HPWL=$(echo $tmp | tr -d '\r\n')
                    fi

                    # 提取重叠权重
                    tmp=$(echo "$line" | awk '{split($0,a," -> "); if(a[1] == "o") {print a[2];} }')
                    if [ ! -z "$tmp" ]; then
                        OVERLAP=$(echo $tmp | tr -d '\r\n')
                    fi
                done < $file

                # 如果实验匹配则执行评估
                if [[ $EXPERIMENT == $EXP ]]; then
                    # 构建奖励参数
                    REWARD_PARAMS=${EUCLIDEAN_WIRELENGTH}:${HPWL}:${OVERLAP}

                    # 保存运行信息
                    allRuns+=( $OUTPUT/${RUN_NAME}_${RUN} )
                    allExps+=( $EXP )
                    allRewardParms+=( $REWARD_PARAMS ) 

                    # 根据是否随机打乱执行不同的评估命令
                    if [ "$SHUFFLE" = false ]; then
                        python eval_run_rl_policy.py --policy ${RL_MODEL_TYPE} --model="${EXP_DIR}/${RUN_NAME}_${RUN}_${RL_MODEL_TYPE}/models/best_mean" --pcb_file $PCB --hyperparameters $PATH_PREFIX/$HYPERPARAMETERS --max_steps $MAX_STEPS --runs $RUNS --reward_params $REWARD_PARAMS --output $OUTPUT/${RUN_NAME}_${RUN} --quick_eval --device $DEVICE
                    else
                        python eval_run_rl_policy.py --policy ${RL_MODEL_TYPE} --model="${EXP_DIR}/${RUN_NAME}_${RUN}_${RL_MODEL_TYPE}/models/best_mean" --pcb_file $PCB --hyperparameters $PATH_PREFIX/$HYPERPARAMETERS --max_steps $MAX_STEPS --runs $RUNS --reward_params $REWARD_PARAMS --output $OUTPUT/${RUN_NAME}_${RUN} --quick_eval --device $DEVICE --shuffle_idxs
                    fi

                    # 根据是否跳过模拟退火执行不同的布局布线命令
                    if [ "$SKIP_SA" = false ]; then
                        ./eval_place_and_route.sh -d $OUTPUT/${RUN_NAME}_${RUN} -b ${BOARDS} --bin_dir ${BIN} 
                    else
                        ./eval_place_and_route.sh -d $OUTPUT/${RUN_NAME}_${RUN} -b ${BOARDS} --bin_dir ${BIN} --skip_simulated_annealing
                    fi

                    # 生成结果文件
                    ./eval_generate_results_file.sh -d ${OUTPUT}/${RUN_NAME}_${RUN}
                fi
            fi
        done
    done
done

# 为每种报告类型生成报告
IFS=',' 
for RT in ${REPORT_TYPE}; do
    echo $RT
    # 根据是否跳过模拟退火执行不同的报告生成命令
    if [ "$SKIP_SA" = false ]; then
        python eval_report_generator.py --run_dirs ${allRuns[*]} --experiments ${allExps[*]} --reward_params ${allRewardParms[*]} --max_steps $MAX_STEPS --report_type=${RT} --output ${OUTPUT}/evaluation_report_${RT}.pdf &> /dev/null
    else
        python eval_report_generator.py --run_dirs ${allRuns[*]} --experiments ${allExps[*]} --reward_params ${allRewardParms[*]} --max_steps $MAX_STEPS --report_type=${RT} --output ${OUTPUT}/evaluation_report_${RT}.pdf --skip_simulated_annealing &> /dev/null
    fi
done
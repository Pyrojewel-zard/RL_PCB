#!/bin/bash

# PCB强化学习训练调试脚本
# 作者: PyroJewel
# 功能: 提供多种调试模式

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# 项目路径
PROJECT_ROOT="/home/pyrojewel/RL_PCB"
TRAINING_DIR="${PROJECT_ROOT}/src/training"

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}🐛 PCB强化学习训练调试器${NC}"
echo -e "${BLUE}=================================${NC}"

# 检查环境
check_environment() {
    echo -e "${YELLOW}🔍 检查环境...${NC}"
    
    # 检查虚拟环境
    if [ ! -d "${PROJECT_ROOT}/venv" ]; then
        echo -e "${RED}❌ 虚拟环境不存在: ${PROJECT_ROOT}/venv${NC}"
        echo -e "${YELLOW}请先运行: source setup.sh${NC}"
        exit 1
    fi
    
    # 检查训练脚本
    if [ ! -f "${TRAINING_DIR}/train.py" ]; then
        echo -e "${RED}❌ 训练脚本不存在: ${TRAINING_DIR}/train.py${NC}"
        exit 1
    fi
    
    # 检查配置文件
    CONFIG_FILE="${PROJECT_ROOT}/experiments/00_parameter_exeperiments/hyperparameters/hp_sac.json"
    if [ ! -f "${CONFIG_FILE}" ]; then
        echo -e "${RED}❌ 配置文件不存在: ${CONFIG_FILE}${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 环境检查通过${NC}"
}

# 激活环境
activate_environment() {
    echo -e "${YELLOW}🔧 激活环境...${NC}"
    
    # 设置环境变量
    export RL_PCB="${PROJECT_ROOT}"
    export PYTHONPATH="${TRAINING_DIR}:${PYTHONPATH}"
    
    # 激活虚拟环境
    source "${PROJECT_ROOT}/setup.sh"
    
    echo -e "${GREEN}✅ 环境激活成功${NC}"
    echo -e "RL_PCB=${RL_PCB}"
    echo -e "PYTHONPATH=${PYTHONPATH}"
}

# VS Code调试模式
vscode_debug() {
    echo -e "${PURPLE}🔍 启动VS Code调试模式...${NC}"
    echo -e "${YELLOW}说明:${NC}"
    echo -e "1. 确保VS Code已安装Python扩展"
    echo -e "2. 打开项目文件夹: ${PROJECT_ROOT}"
    echo -e "3. 按F5或使用调试面板选择配置:"
    echo -e "   - 'Python: Train PCB - Debug Mode' (完整调试)"
    echo -e "   - 'Python: Train PCB - Quick Debug (CPU)' (快速调试)"
    echo -e "4. 在代码中设置断点后开始调试"
    
    # 检查VS Code配置
    if [ -f "${PROJECT_ROOT}/.vscode/launch.json" ]; then
        echo -e "${GREEN}✅ VS Code调试配置已就绪${NC}"
    else
        echo -e "${RED}❌ VS Code调试配置文件不存在${NC}"
    fi
}

# 命令行交互式调试
interactive_debug() {
    echo -e "${PURPLE}🔍 启动命令行交互式调试...${NC}"
    
    cd "${TRAINING_DIR}"
    
    # 使用Python的pdb模块
    echo -e "${YELLOW}启动交互式调试器...${NC}"
    echo -e "${YELLOW}调试命令:${NC}"
    echo -e "  n (next) - 执行下一行"
    echo -e "  s (step) - 步入函数"
    echo -e "  c (continue) - 继续执行"
    echo -e "  l (list) - 显示当前代码"
    echo -e "  p <变量名> - 打印变量值"
    echo -e "  q (quit) - 退出调试"
    echo -e "${BLUE}=================================${NC}"
    
    python -m pdb train.py \
        --policy SAC \
        --target_exploration_steps 5 \
        --start_timesteps 10 \
        --max_timesteps 100 \
        --evaluate_every 50 \
        --training_pcb "${RL_PCB}/dataset/base/region_8_fixed.pcb" \
        --evaluation_pcb "${RL_PCB}/dataset/base/evaluation.pcb" \
        --tensorboard_dir "/tmp/debug_tensorboard" \
        -w 6.0 \
        --hpwl 2.0 \
        -o 2.0 \
        --hyperparameters "${RL_PCB}/experiments/00_parameter_exeperiments/hyperparameters/hp_sac.json" \
        --incremental_replay_buffer double \
        --verbose 2 \
        --runs 1 \
        --experiment debug_shell \
        --device cpu
}

# 自定义调试脚本
custom_debug() {
    echo -e "${PURPLE}🔍 启动自定义调试脚本...${NC}"
    
    cd "${TRAINING_DIR}"
    
    if [ -f "debug_train.py" ]; then
        python debug_train.py
    else
        echo -e "${RED}❌ 自定义调试脚本不存在: debug_train.py${NC}"
        echo -e "${YELLOW}请先创建调试脚本${NC}"
    fi
}

# 快速测试模式
quick_test() {
    echo -e "${PURPLE}⚡ 启动快速测试模式...${NC}"
    
    cd "${TRAINING_DIR}"
    
    # 创建临时目录
    TEMP_DIR="/tmp/pcb_debug_$(date +%s)"
    mkdir -p "${TEMP_DIR}"
    
    echo -e "${YELLOW}运行最小参数测试...${NC}"
    
    python train.py \
        --policy SAC \
        --target_exploration_steps 2 \
        --start_timesteps 5 \
        --max_timesteps 20 \
        --evaluate_every 10 \
        --training_pcb "${RL_PCB}/dataset/base/region_8_fixed.pcb" \
        --evaluation_pcb "${RL_PCB}/dataset/base/evaluation.pcb" \
        --tensorboard_dir "${TEMP_DIR}" \
        -w 6.0 \
        --hpwl 2.0 \
        -o 2.0 \
        --hyperparameters "${RL_PCB}/experiments/00_parameter_exeperiments/hyperparameters/hp_sac.json" \
        --incremental_replay_buffer double \
        --verbose 2 \
        --runs 1 \
        --experiment quick_test \
        --device cpu
    
    echo -e "${GREEN}✅ 快速测试完成${NC}"
    echo -e "${YELLOW}临时文件位置: ${TEMP_DIR}${NC}"
}

# 显示主菜单
show_menu() {
    echo -e "\n${BLUE}🔧 请选择调试模式:${NC}"
    echo -e "  ${GREEN}1${NC}. VS Code调试 (推荐)"
    echo -e "  ${GREEN}2${NC}. 命令行交互式调试"
    echo -e "  ${GREEN}3${NC}. 自定义调试脚本"
    echo -e "  ${GREEN}4${NC}. 快速测试模式"
    echo -e "  ${GREEN}5${NC}. 退出"
    echo -e "${BLUE}=================================${NC}"
}

# 主程序
main() {
    # 检查环境
    check_environment
    
    # 激活环境
    activate_environment
    
    # 如果有命令行参数，直接执行对应模式
    case "$1" in
        "vscode"|"1")
            vscode_debug
            ;;
        "interactive"|"2")
            interactive_debug
            ;;
        "custom"|"3")
            custom_debug
            ;;
        "quick"|"4")
            quick_test
            ;;
        *)
            # 显示菜单
            show_menu
            read -p "请输入选择 (1-5): " choice
            
            case $choice in
                1)
                    vscode_debug
                    ;;
                2)
                    interactive_debug
                    ;;
                3)
                    custom_debug
                    ;;
                4)
                    quick_test
                    ;;
                5)
                    echo -e "${GREEN}👋 退出调试器${NC}"
                    exit 0
                    ;;
                *)
                    echo -e "${RED}❌ 无效选择${NC}"
                    exit 1
                    ;;
            esac
            ;;
    esac
}

# 执行主程序
main "$@"

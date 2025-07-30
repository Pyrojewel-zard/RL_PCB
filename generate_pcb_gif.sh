#!/bin/bash

# PCB文件转GIF动图生成脚本
# 激活Python虚拟环境并运行PCB转GIF工具
# 使用方法: ./generate_pcb_gif.sh <WORK_NAME>
# 例如: ./generate_pcb_gif.sh 1753883227_0_SAC

echo "=== PCB文件转GIF动图生成器 ==="

# 检查参数
if [ $# -eq 0 ]; then
    echo "错误: 请提供WORK_NAME参数"
    echo "使用方法: $0 <WORK_NAME>"
    echo "例如: $0 1753883227_0_SAC"
    exit 1
fi

# 获取WORK_NAME参数
WORK_NAME="$1"

echo "使用WORK_NAME: $WORK_NAME"

# 激活虚拟环境
echo "激活Python虚拟环境..."
source setup.sh

# 检查是否需要安装Pillow库
echo "检查依赖项..."
python -c "import PIL" 2>/dev/null || {
    echo "正在安装Pillow库..."
    pip install Pillow
}

# 设置路径
PCB_DIR="/home/pyrojewel/RL_PCB/experiments/00_parameter_exeperiments/work/${WORK_NAME}/explore_pcb"
OUTPUT_GIF="/home/pyrojewel/RL_PCB/experiments/00_parameter_exeperiments/work/${WORK_NAME}/pcb_animation.gif"

echo "PCB文件目录: $PCB_DIR"
echo "输出GIF文件: $OUTPUT_GIF"

# 检查PCB目录是否存在
if [ ! -d "$PCB_DIR" ]; then
    echo "错误: PCB目录不存在: $PCB_DIR"
    exit 1
fi

# 设置循环间隔时间（秒）
INTERVAL=5

echo "开始循环生成GIF动图，每隔${INTERVAL}秒执行一次..."
echo "按 Ctrl+C 停止程序"

# 切换到src/evaluation_scripts目录
cd src/evaluation_scripts

# 循环执行转换脚本
while true; do
    echo ""
    echo "=== $(date '+%Y-%m-%d %H:%M:%S') 开始新一轮转换 ==="
    
    # 运行转换脚本
    python pcb_to_gif.py -d "$PCB_DIR" -o "$OUTPUT_GIF" --duration 300 --max-files 200
    
    # 检查转换是否成功
    if [ $? -eq 0 ]; then
        echo "GIF动图生成成功!"
        echo "输出文件: $OUTPUT_GIF"
    else
        echo "GIF动图生成失败，请检查错误信息"
    fi
    
    echo "等待${INTERVAL}秒后进行下一轮转换..."
    sleep $INTERVAL
done

echo "=== 程序已退出 ===" 
#!/bin/bash

# PCB文件转GIF动图生成脚本
# 激活Python虚拟环境并运行PCB转GIF工具

echo "=== PCB文件转GIF动图生成器 ==="

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
PCB_DIR="/home/pyrojewel/RL_PCB/experiments/00_parameter_exeperiments/work/1753863208_0_SAC/explore_pcb"
OUTPUT_GIF="/home/pyrojewel/RL_PCB/experiments/00_parameter_exeperiments/work/1753863208_0_SAC/pcb_animation.gif"

echo "PCB文件目录: $PCB_DIR"
echo "输出GIF文件: $OUTPUT_GIF"

# 运行转换脚本
echo "开始生成GIF动图..."
cd src/evaluation_scripts
python pcb_to_gif.py -d "$PCB_DIR" -o "$OUTPUT_GIF" --duration 300 --max-files 200

echo "=== 完成 ===" 
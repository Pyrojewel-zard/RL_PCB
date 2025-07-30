#!/bin/bash

# PCB转PNG脚本
# 使用方法: ./convert_pcb_to_png.sh <pcb文件名>
# 例如: ./convert_pcb_to_png.sh 1_merged.pcb

# 检查参数
if [ $# -eq 0 ]; then
    echo "错误: 请提供PCB文件名作为参数"
    echo "使用方法: $0 <pcb文件名>"
    echo "例如: $0 1_merged.pcb"
    exit 1
fi

# 获取PCB文件名（不包含路径）
PCB_FILENAME=$(basename "$1")

# 检查PCB文件是否存在
PCB_FULL_PATH="/home/pyrojewel/RL_PCB/dataset/base/$PCB_FILENAME"
if [ ! -f "$PCB_FULL_PATH" ]; then
    echo "错误: PCB文件不存在: $PCB_FULL_PATH"
    exit 1
fi

# 设置输出PNG文件路径（与PCB文件同路径，名称相同但扩展名为.png）
OUTPUT_PNG_PATH="/home/pyrojewel/RL_PCB/dataset/base/${PCB_FILENAME%.pcb}.png"

echo "开始转换PCB文件到PNG..."
echo "输入PCB文件: $PCB_FULL_PATH"
echo "输出PNG文件: $OUTPUT_PNG_PATH"

# 激活虚拟环境
echo "激活虚拟环境..."
source setup.sh

# 切换到src/training目录
echo "切换到src/training目录..."
cd src/training

# 运行pcb2png.py脚本
echo "运行PCB转PNG脚本..."
python /home/pyrojewel/RL_PCB/src/evaluation_scripts/pcb2png.py -p "$PCB_FULL_PATH" -o "$OUTPUT_PNG_PATH"

# 检查转换是否成功
if [ $? -eq 0 ]; then
    echo "转换成功完成!"
    echo "PNG文件已保存到: $OUTPUT_PNG_PATH"
else
    echo "转换失败，请检查错误信息"
    exit 1
fi 
#!/bin/bash

# PCB文件转MP4视频生成脚本
# 激活Python虚拟环境并运行PCB转MP4工具
# 使用方法: ./generate_pcb_gif.sh <PCB_DIR_PATH>
# 例如: ./generate_pcb_gif.sh /home/pyrojewel/RL_PCB/generated_pcb_100

echo "=== PCB文件转MP4视频生成器 ==="

# 检查参数
if [ $# -eq 0 ]; then
    echo "错误: 请提供PCB文件夹路径参数"
    echo "使用方法: $0 <PCB_DIR_PATH>"
    echo "例如: $0 /home/pyrojewel/RL_PCB/generated_pcb_100"
    exit 1
fi

# 获取PCB目录路径参数
PCB_DIR="$1"

# 激活虚拟环境
echo "激活Python虚拟环境..."
source setup.sh

# 检查是否需要安装Pillow库
echo "检查依赖项..."
python -c "import PIL" 2>/dev/null || {
    echo "正在安装Pillow库..."
    pip install Pillow
}

# 生成输出文件路径（在输入目录下生成MP4文件）
DIR_NAME=$(basename "$PCB_DIR")
OUTPUT_MP4="${PCB_DIR}/${DIR_NAME}.mp4"

echo "PCB文件目录: $PCB_DIR"
echo "输出MP4文件: $OUTPUT_MP4"

# 检查PCB目录是否存在
if [ ! -d "$PCB_DIR" ]; then
    echo "错误: PCB目录不存在: $PCB_DIR"
    exit 1
fi

# 设置循环间隔时间（秒）
INTERVAL=5

echo "开始循环生成MP4视频，每隔${INTERVAL}秒执行一次..."
echo "按 Ctrl+C 停止程序"

# 切换到src/evaluation_scripts目录
cd src/evaluation_scripts

# 循环执行转换脚本
while true; do
    echo ""
    echo "=== $(date '+%Y-%m-%d %H:%M:%S') 开始新一轮转换 ==="
    
    # 运行转换脚本，指定MP4格式
    python pcb_to_gif.py -d "$PCB_DIR" -o "$OUTPUT_MP4" --duration 100 --max-files 200 --format mp4
    
    # 检查转换是否成功
    if [ $? -eq 0 ]; then
        echo "MP4视频生成成功!"
        echo "输出文件: $OUTPUT_MP4"
    else
        echo "MP4视频生成失败，请检查错误信息"
    fi
    
    echo "等待${INTERVAL}秒后进行下一轮转换..."
    sleep $INTERVAL
done

echo "=== 程序已退出 ===" 
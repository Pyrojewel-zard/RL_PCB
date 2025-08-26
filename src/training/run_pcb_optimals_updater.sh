#!/bin/bash
# PCB Optimals更新工具启动脚本

# 设置脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 激活Python环境
echo "激活Python环境..."
source ../../setup.sh

# 检查环境
echo "检查环境..."
python3 -c "import pcb; import pcb_vector_utils; print('环境检查通过')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "错误: 环境检查失败，请确保已正确设置Python环境"
    exit 1
fi

# 显示帮助信息
show_help() {
    echo "PCB Optimals更新工具"
    echo ""
    echo "使用方法:"
    echo "  $0 single <pcb_file> [output_file]     # 单个PCB文件更新"
    echo "  $0 batch <pcb_file1> <pcb_file2> ...   # 批量PCB文件更新"
    echo "  $0 batch-dir <directory> [output_dir]   # 批量处理目录中的PCB文件"
    echo "  $0 test                                 # 运行测试"
    echo "  $0 example                              # 运行示例"
    echo "  $0 help                                 # 显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 single example.kicad_pcb"
    echo "  $0 single example.kicad_pcb updated.kicad_pcb"
    echo "  $0 batch file1.kicad_pcb file2.kicad_pcb"
    echo "  $0 batch-dir ./pcb_files ./updated_pcbs"
    echo ""
}

# 处理单个PCB文件
process_single() {
    if [ $# -lt 1 ]; then
        echo "错误: 请提供PCB文件路径"
        echo "使用方法: $0 single <pcb_file> [output_file]"
        exit 1
    fi
    
    pcb_file="$1"
    output_file="$2"
    
    if [ ! -f "$pcb_file" ]; then
        echo "错误: PCB文件不存在: $pcb_file"
        exit 1
    fi
    
    echo "处理单个PCB文件: $pcb_file"
    
    if [ -n "$output_file" ]; then
        python3 pcb_optimals_updater.py "$pcb_file" "$output_file"
    else
        python3 pcb_optimals_updater.py "$pcb_file"
    fi
}

# 处理批量PCB文件
process_batch() {
    if [ $# -lt 1 ]; then
        echo "错误: 请提供至少一个PCB文件路径"
        echo "使用方法: $0 batch <pcb_file1> <pcb_file2> ..."
        exit 1
    fi
    
    echo "批量处理PCB文件..."
    
    # 检查文件是否存在
    for file in "$@"; do
        if [ ! -f "$file" ]; then
            echo "警告: 文件不存在: $file"
        fi
    done
    
    python3 batch_pcb_optimals_updater.py "$@"
}

# 处理目录中的PCB文件
process_batch_dir() {
    if [ $# -lt 1 ]; then
        echo "错误: 请提供目录路径"
        echo "使用方法: $0 batch-dir <directory> [output_dir]"
        exit 1
    fi
    
    directory="$1"
    output_dir="$2"
    
    if [ ! -d "$directory" ]; then
        echo "错误: 目录不存在: $directory"
        exit 1
    fi
    
    echo "批量处理目录中的PCB文件: $directory"
    
    if [ -n "$output_dir" ]; then
        python3 batch_pcb_optimals_updater.py --dir "$directory" --output "$output_dir"
    else
        python3 batch_pcb_optimals_updater.py --dir "$directory"
    fi
}

# 运行测试
run_test() {
    echo "运行测试..."
    python3 test_pcb_optimals_updater.py
}

# 运行示例
run_example() {
    echo "运行示例..."
    python3 example_usage.py
}

# 主函数
main() {
    case "$1" in
        "single")
            shift
            process_single "$@"
            ;;
        "batch")
            shift
            process_batch "$@"
            ;;
        "batch-dir")
            shift
            process_batch_dir "$@"
            ;;
        "test")
            run_test
            ;;
        "example")
            run_example
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        "")
            show_help
            ;;
        *)
            echo "错误: 未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@" 
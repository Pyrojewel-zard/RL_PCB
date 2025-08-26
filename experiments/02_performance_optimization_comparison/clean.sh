#!/bin/bash

# 清理性能优化对比实验的所有生成文件

echo "🧹 清理性能优化对比实验文件..."

# 清理工作目录
if [ -d "work" ]; then
    echo "删除工作目录..."
    rm -rf work
fi

# 清理性能日志
if [ -d "performance_logs" ]; then
    echo "删除性能日志..."
    rm -rf performance_logs
fi

# 清理临时文件
if [ -d "tmp" ]; then
    echo "删除临时文件..."
    rm -rf tmp
fi

# 清理生成的报告
if [ -f "performance_optimization_report.pdf" ]; then
    echo "删除性能报告..."
    rm -f performance_optimization_report.pdf
fi

# 清理报告配置
if [ -f "report_config.json" ]; then
    echo "删除报告配置..."
    rm -f report_config.json
fi

# 清理日志文件
rm -f *.log
rm -f scheduler.log
rm -f train.log

echo "✅ 清理完成!"
echo "保留的文件:"
echo "  - hyperparameters/ (超参数配置)"
echo "  - run_config.txt (运行配置)"
echo "  - run.sh (执行脚本)"
echo "  - report_config.py (报告配置脚本)"
echo "  - clean.sh (本清理脚本)"
echo "  - README.md (说明文档)"
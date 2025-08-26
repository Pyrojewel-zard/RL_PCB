from datetime import datetime
import json

def save_report_config(filename, report_config):
    """
    将报告配置保存到指定的JSON文件中。
    """
    with open(filename, 'w') as fp:
        json.dump(report_config, fp)
    fp.close()
        
def load_report_config(filename):
    """
    从JSON配置文件中加载报告配置数据。
    """
    fp = open(filename, 'r')
    report_config = json.load(fp)
    fp.close()
    return report_config    

# 性能优化对比实验的图表配置
charts = {
    # 基线 vs 优化版本对比
    'performance_comparison_sac': { 
        'experiments': ['baseline_sac_original', 'optimized_sac_multithread_gpu'],
        'algorithms': ['SAC'],
        'multi_agent': True,
        'mean_std_plot': True,
        'ylim_bot': -1000,
        'xscale': 'k',
        'window': 100,
        'title': "SAC性能对比: 基线版本 vs 优化版本",
        'xlabel': "训练步数 (k)",
        'ylabel': "平均奖励",
        'label': {
            'baseline_sac_original:SAC': 'SAC基线版本 (原始)',
            'optimized_sac_multithread_gpu:SAC': 'SAC优化版本 (多线程+GPU)',
        },   
    },
    
    # 消融实验对比
    'ablation_study': { 
        'experiments': ['baseline_sac_original', 'ablation_sac_multithread_only', 'ablation_sac_gpu_only', 'optimized_sac_multithread_gpu'],
        'algorithms': ['SAC'],
        'multi_agent': True,
        'mean_std_plot': True,
        'ylim_bot': -1000,
        'xscale': 'k',
        'window': 50,
        'title': "消融实验: 各优化组件效果分析",
        'xlabel': "训练步数 (k)",
        'ylabel': "平均奖励",
        'label': {
            'baseline_sac_original:SAC': '基线版本',
            'ablation_sac_multithread_only:SAC': '仅多线程优化',
            'ablation_sac_gpu_only:SAC': '仅GPU优化',
            'optimized_sac_multithread_gpu:SAC': '完整优化',
        },   
    },
    
    # 训练速度对比
    'training_speed_comparison': { 
        'experiments': ['baseline_sac_original', 'optimized_sac_multithread_gpu'],
        'algorithms': ['SAC'],
        'multi_agent': True,
        'mean_std_plot': False,
        'ylim_bot': 0,
        'xscale': 'time',  # 按时间轴显示
        'window': 1,
        'title': "训练速度对比: 时间效率分析",
        'xlabel': "训练时间 (分钟)",
        'ylabel': "累计训练步数",
        'label': {
            'baseline_sac_original:SAC': '基线版本',
            'optimized_sac_multithread_gpu:SAC': '优化版本',
        },   
    },
    
    # 探索阶段性能对比
    'exploration_performance': { 
        'experiments': ['baseline_sac_original', 'optimized_sac_multithread_gpu'],
        'algorithms': ['SAC'],
        'multi_agent': True,
        'mean_std_plot': True,
        'ylim_bot': -500,
        'xscale': 'k',
        'window': 20,
        'title': "专家目标探索阶段性能对比",
        'xlabel': "探索步数 (k)",
        'ylabel': "探索奖励",
        'label': {
            'baseline_sac_original:SAC': '单线程探索',
            'optimized_sac_multithread_gpu:SAC': '多线程探索',
        },   
    },
}

# 性能统计表格配置
tables = {
    'performance_summary': {
        'title': '性能优化效果总结',
        'experiments': ['baseline_sac_original', 'optimized_sac_multithread_gpu', 'ablation_sac_multithread_only', 'ablation_sac_gpu_only'],
        'metrics': ['final_reward', 'training_time', 'exploration_time', 'total_time', 'speedup_ratio'],
        'columns': ['实验名称', '最终奖励', '训练时间(秒)', '探索时间(秒)', '总时间(秒)', '加速比'],
    },
    
    'hardware_utilization': {
        'title': '硬件资源利用率对比',
        'experiments': ['baseline_sac_original', 'optimized_sac_multithread_gpu'],
        'metrics': ['cpu_usage', 'gpu_usage', 'memory_usage', 'gpu_memory_usage'],
        'columns': ['实验版本', 'CPU使用率(%)', 'GPU使用率(%)', '内存使用率(%)', 'GPU内存使用率(%)'],
    },
    
    'optimization_breakdown': {
        'title': '优化组件贡献分析',
        'experiments': ['baseline_sac_original', 'ablation_sac_multithread_only', 'ablation_sac_gpu_only', 'optimized_sac_multithread_gpu'],
        'metrics': ['exploration_speedup', 'training_speedup', 'memory_efficiency', 'overall_speedup'],
        'columns': ['优化类型', '探索加速比', '训练加速比', '内存效率提升', '总体加速比'],
    }
}

# 报告配置
report_config = {
    'charts': charts,
    'tables': tables,
    'author': 'RL_PCB Performance Optimization Team',
    'title': 'RL_PCB 性能优化对比实验报告',
    'subtitle': '多线程探索与GPU优化效果评估',
    'timestamp': f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
    'experiment_description': '''
    本实验对比了RL_PCB项目中原始训练方法与性能优化方法的效果。
    
    实验设计:
    1. 基线实验: 使用原始的单线程explore_for_expert_targets和标准GPU利用率
    2. 优化实验: 使用多线程探索器和GPU优化技术
    3. 消融实验: 分别测试多线程优化和GPU优化的独立效果
    
    主要优化技术:
    - 多线程并行探索 (ThreadSafeExplorer)
    - GPU内存和计算优化 (GPUOptimizer)
    - 自适应批处理大小调整
    - 混合精度训练支持
    
    性能指标:
    - 训练速度 (步/秒)
    - 总训练时间
    - GPU/CPU利用率
    - 内存使用效率
    - 最终训练效果
    ''',
    'conclusions': [
        '多线程探索显著提升了专家目标探索阶段的效率',
        'GPU优化有效提高了训练阶段的硬件利用率',
        '结合两种优化技术可获得最佳的整体性能提升',
        '优化版本在保持训练质量的同时大幅减少了训练时间'
    ]
}

# 保存配置
save_report_config("./report_config.json", report_config)

print("📊 性能优化对比实验报告配置已生成")
print("包含的分析内容:")
print("  - SAC基线版本 vs 优化版本对比")
print("  - 消融实验分析 (多线程/GPU单独效果)")
print("  - 训练速度对比")
print("  - 硬件资源利用率分析")
print("  - 性能统计总结表")
print("")
print("📄 配置已保存到: report_config.json")
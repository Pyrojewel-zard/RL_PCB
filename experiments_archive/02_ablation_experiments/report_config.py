from datetime import datetime
import json

def save_report_config(filename, report_config):
    """
    将报告配置保存为JSON格式的文件。

    Args:
        filename (str): 要保存的JSON文件名
        report_config (dict): 包含报告配置的字典

    Returns:
        None
    """
    # Write default_hyperparameters dict to a json file
    with open(filename, 'w') as fp:
        json.dump(report_config, fp)  # ⭐ 将字典数据序列化为JSON格式并写入文件
    
    fp.close()
        
def load_report_config(filename):
    fp = open(filename, 'r')
    report_config = json.load(fp)
    fp.close()
    return report_config    
        
charts = {
    'ablation_test_055': {  'experiments':['ablation_experiment_055'],
                                            'algorithms': ['TD3', 'SAC'],
                                            'multi_agent': True,
                                            'mean_std_plot': True,
                                            'ylim_bot': -1000,
                                            'scale': 'k',
                                            'window': 100,
                                            'title': "Ablation test (W=0, H=5, O=5)",
                                            'xlabel': "Timesteps (unit)",
                                            'ylabel': "Average return (unit)",
                                            'label': {
                                                        # PARTIALLY SUPPORTED FOR MULTI AGENT
                                                     'ablation_experiment_055:TD3': 'TD3',
                                                     'ablation_experiment_055:SAC': 'SAC',
                                                     },   
                                            },        
    'ablation_test_082': {  'experiments':['ablation_experiment_082'],
                                            'algorithms': ['TD3', 'SAC'],
                                            'multi_agent': True,
                                            'mean_std_plot': True,
                                            'window': 100,
                                            'title': "Ablation test (W=0, H=8, O=2)",
                                            'xlabel': "Timesteps (unit)",
                                            'ylabel': "Average return (unit)",
                                            'label':    {
                                                        # PARTIALLY SUPPORTED FOR MULTI AGENT
                                                        'ablation_experiment_082:TD3': 'TD3',
                          				'ablation_experiment_082:SAC': 'SAC'                                                        
                                                        },   
                                            }, 
    'ablation_test_028': {  'experiments':['ablation_experiment_028'],
                                            'algorithms': ['TD3', 'SAC'],
                                            'multi_agent': True,
                                            'mean_std_plot': True,
                                            'window': 100,
                                            'title': "Ablation test (W=0, H=2, O=8)",
                                            'xlabel': "Timesteps (unit)",
                                            'ylabel': "Average return (unit)",
                                            'label':    {
                                                        # PARTIALLY SUPPORTED FOR MULTI AGENT
                                                        'ablation_experiment_028:TD3': 'TD3',
                                                        'ablation_experiment_028:SAC': 'SAC'                                                        
                                                        },   
                                            },     
    'ablation_test_505': {  'experiments':['ablation_experiment_505'],
                                            'algorithms': ['TD3', 'SAC'],
                                            'multi_agent': True,
                                            'mean_std_plot': True,
                                            'window': 100,
                                            'title': "Ablation test (W=5, H=0, O=5)",
                                            'xlabel': "Timesteps (unit)",
                                            'ylabel': "Average return (unit)",
                                            'label':    {
                                                        # PARTIALLY SUPPORTED FOR MULTI AGENT
                                                        'ablation_experiment_505:TD3': 'TD3',
                                                        'ablation_experiment_505:SAC': 'SAC'
                                                        },   
                                            },        
    'ablation_test_802': {  'experiments':['ablation_experiment_802'],
                                            'algorithms': ['TD3', 'SAC'],
                                            'multi_agent': True,
                                            'mean_std_plot': True,
                                            'window': 100,
                                            'title': "Ablation test (W=8, H=0, O=2)",
                                            'xlabel': "Timesteps (unit)",
                                            'ylabel': "Average return (unit)",
                                            'label':    {
                                                        # PARTIALLY SUPPORTED FOR MULTI AGENT
                                                        'ablation_experiment_802:TD3': 'TD3',
                          				'ablation_experiment_802:SAC': 'SAC'                                                        
                                                        },   
                                            }, 
    'ablation_test_208': {  'experiments':['ablation_experiment_208'],
                                            'algorithms': ['TD3', 'SAC'],
                                            'multi_agent': True,
                                            'mean_std_plot': True,
                                            'window': 100,
                                            'title': "Ablation test (W=2, H=0, O=8)",
                                            'xlabel': "Timesteps (unit)",
                                            'ylabel': "Average return (unit)",
                                            'label':    {
                                                        # PARTIALLY SUPPORTED FOR MULTI AGENT
                                                        'ablation_experiment_208:TD3': 'TD3',
                                                        'ablation_experiment_208:SAC': 'SAC'                                                        
                                                        },   
                                            },                                                                                                                                       
         }
    
tables = {
         }

# 报告配置文件字典，包含图表、表格、作者和时间戳信息
report_config = {'charts': charts,  # ⭐ 核心配置项：包含所有图表配置
                 'tables': tables,  # ⭐ 核心配置项：包含所有表格配置
                 'author': 'Luke Vassallo',
                 'timestamp': f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'  # ⭐ 自动生成当前时间戳
                }

# 将报告配置保存为JSON文件
save_report_config("./report_config.json", report_config)

# 以下是被注释掉的配置加载和打印示例
#rc = load_report_config("./report_config.json")
#for key,value in rc.items():
    #print(f'{key} : {value}')

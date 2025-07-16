from datetime import datetime
import json

def save_report_config(filename, report_config):
    """
    将报告配置字典保存为JSON文件

    Args:
        filename (str): 要保存的JSON文件路径
        report_config (dict): 包含报告配置的字典

    Returns:
        None
    """
    # Write default_hyperparameters dict to a json file
    with open(filename, 'w') as fp:
        json.dump(report_config, fp)  # ⭐ 将配置字典序列化为JSON并写入文件
    
    fp.close()
        
def load_report_config(filename):
    """
    加载并解析JSON格式的报告配置文件

    Args:
        filename (str): JSON配置文件的路径

    Returns:
        dict: 解析后的报告配置字典
    """
    fp = open(filename, 'r')
    report_config = json.load(fp)  # ⭐ 核心代码：解析JSON文件内容
    fp.close()
    return report_config    
        
charts = {
    'ablation_test_055': {  'experiments':['ablation_expert_experiment_055'],
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
                                                     'ablation_expert_experiment_055:TD3': 'TD3',
                                                     'ablation_expert_experiment_055:SAC': 'SAC',
                                                     },   
                                            },        
    'ablation_test_082': {  'experiments':['ablation_expert_experiment_082'],
                                            'algorithms': ['TD3', 'SAC'],
                                            'multi_agent': True,
                                            'mean_std_plot': True,
                                            'window': 100,
                                            'title': "Ablation test (W=0, H=8, O=2)",
                                            'xlabel': "Timesteps (unit)",
                                            'ylabel': "Average return (unit)",
                                            'label':    {
                                                        # PARTIALLY SUPPORTED FOR MULTI AGENT
                                                        'ablation_expert_experiment_082:TD3': 'TD3',
                          				'ablation_expert_experiment_082:SAC': 'SAC'                                                        
                                                        },   
                                            }, 
    'ablation_test_028': {  'experiments':['ablation_expert_experiment_028'],
                                            'algorithms': ['TD3', 'SAC'],
                                            'multi_agent': True,
                                            'mean_std_plot': True,
                                            'window': 100,
                                            'title': "Ablation test (W=0, H=2, O=8)",
                                            'xlabel': "Timesteps (unit)",
                                            'ylabel': "Average return (unit)",
                                            'label':    {
                                                        # PARTIALLY SUPPORTED FOR MULTI AGENT
                                                        'ablation_expert_experiment_028:TD3': 'TD3',
                                                        'ablation_expert_experiment_028:SAC': 'SAC'                                                        
                                                        },   
                                            },     
    'ablation_test_505': {  'experiments':['ablation_expert_experiment_505'],
                                            'algorithms': ['TD3', 'SAC'],
                                            'multi_agent': True,
                                            'mean_std_plot': True,
                                            'window': 100,
                                            'title': "Ablation test (W=5, H=0, O=5)",
                                            'xlabel': "Timesteps (unit)",
                                            'ylabel': "Average return (unit)",
                                            'label':    {
                                                        # PARTIALLY SUPPORTED FOR MULTI AGENT
                                                        'ablation_expert_experiment_505:TD3': 'TD3',
                                                        'ablation_expert_experiment_505:SAC': 'SAC'
                                                        },   
                                            },        
    'ablation_test_802': {  'experiments':['ablation_expert_experiment_802'],
                                            'algorithms': ['TD3', 'SAC'],
                                            'multi_agent': True,
                                            'mean_std_plot': True,
                                            'window': 100,
                                            'title': "Ablation test (W=8, H=0, O=2)",
                                            'xlabel': "Timesteps (unit)",
                                            'ylabel': "Average return (unit)",
                                            'label':    {
                                                        # PARTIALLY SUPPORTED FOR MULTI AGENT
                                                        'ablation_expert_experiment_802:TD3': 'TD3',
                          				'ablation_expert_experiment_802:SAC': 'SAC'                                                        
                                                        },   
                                            }, 
    'ablation_test_208': {  'experiments':['ablation_expert_experiment_208'],
                                            'algorithms': ['TD3', 'SAC'],
                                            'multi_agent': True,
                                            'mean_std_plot': True,
                                            'window': 100,
                                            'title': "Ablation test (W=2, H=0, O=8)",
                                            'xlabel': "Timesteps (unit)",
                                            'ylabel': "Average return (unit)",
                                            'label':    {
                                                        # PARTIALLY SUPPORTED FOR MULTI AGENT
                                                        'ablation_expert_experiment_208:TD3': 'TD3',
                                                        'ablation_expert_experiment_208:SAC': 'SAC'                                                        
                                                        },   
                                            },                                                                                                                                       
         }
    
tables = {
         }

# 报告配置字典，包含图表、表格、作者和时间戳等信息
report_config = {'charts': charts,  # ⭐ 定义报告中的图表配置
                 'tables': tables,  # ⭐ 定义报告中的表格配置
                 'author': 'Luke Vassallo',
                 'timestamp': f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'  # ⭐ 生成当前时间戳
                }

# 将报告配置保存为JSON文件
save_report_config("./report_config.json", report_config)

# 以下是被注释掉的加载和打印报告配置的代码
#rc = load_report_config("./report_config.json")
#for key,value in rc.items():
    #print(f'{key} : {value}')

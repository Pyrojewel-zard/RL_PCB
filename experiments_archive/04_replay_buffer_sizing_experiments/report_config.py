from datetime import datetime
import json

def save_report_config(filename, report_config):
    """
    将报告配置保存为JSON文件。

    Args:
        filename (str): 要保存的JSON文件路径。
        report_config (dict): 需要保存的报告配置字典。

    Returns:
        None
    """
    # Write default_hyperparameters dict to a json file
    with open(filename, 'w') as fp:
        json.dump(report_config, fp)  # ⭐ 将配置字典序列化为JSON并写入文件
    
    fp.close()
        
def load_report_config(filename):
    """
    加载并返回JSON格式的报告配置文件内容

    Args:
        filename (str): 要加载的JSON配置文件的路径

    Returns:
        dict: 解析后的JSON配置字典
    """
    fp = open(filename, 'r')
    report_config = json.load(fp)  # ⭐ 核心代码：解析JSON文件内容为Python字典
    fp.close()
    return report_config    
        
charts = {
        'buffer_tests_variable_double': {  'experiments':['buffer_experiment_262_double'],
                                            'algorithms': ['TD3', 'SAC'],
                                            'multi_agent': True,
                                            'mean_std_plot': True,
                                            'ylim_bot': -1000,
                                            'scale': 'k',
                                            'window': 100,
                                            'title': "Resizable buffer with a doubling strategy",
                                            'xlabel': "Timesteps (unit)",
                                            'ylabel': "Average return (unit)",
                                            'label': {
                                                        # PARTIALLY SUPPORTED FOR MULTI AGENT
                                                     'buffer_experiment_262_double:TD3': 'TD3',
                                                     'buffer_experiment_262_double:SAC': 'SAC',
                                                     },   
                                            },        
    'buffer_tests_variable_triple': {  'experiments':['buffer_experiment_262_triple'],
                                            'algorithms': ['TD3', 'SAC'],
                                            'multi_agent': True,
                                            'mean_std_plot': True,
                                            'window': 100,
                                            'title': "Resizable buffer with a tripling strategy",
                                            'xlabel': "Timesteps (unit)",
                                            'ylabel': "Average return (unit)",
                                            'label':    {
                                                        # PARTIALLY SUPPORTED FOR MULTI AGENT
                                                        'buffer_experiment_262_triple:TD3': 'TD3',
                          				'buffer_experiment_262_triple:SAC': 'SAC'                                                        
                                                        },   
                                            }, 
    'buffer_tests_variable_quadruple': {  'experiments':['buffer_experiment_262_quadruple'],
                                            'algorithms': ['TD3', 'SAC'],
                                            'multi_agent': True,
                                            'mean_std_plot': True,
                                            'window': 100,
                                            'title': "Resizable buffer with a quadrupling strategy",
                                            'xlabel': "Timesteps (unit)",
                                            'ylabel': "Average return (unit)",
                                            'label':    {
                                                        # PARTIALLY SUPPORTED FOR MULTI AGENT
                                                        'buffer_experiment_262_quadruple:TD3': 'TD3',
                                                        'buffer_experiment_262_quadruple:SAC': 'SAC'                                                        
                                                        },   
                                            },     
    'buffer_tests_fixed_300k': {  'experiments':['buffer_experiment_262_300_fixed'],
                                            'algorithms': ['TD3', 'SAC'],
                                            'multi_agent': True,
                                            'mean_std_plot': True,
                                            'window': 100,
                                            'title': "Fixed Replay Buffer of Size 300k",
                                            'xlabel': "Timesteps (unit)",
                                            'ylabel': "Average return (unit)",
                                            'label':    {
                                                        # PARTIALLY SUPPORTED FOR MULTI AGENT
                                                        'buffer_experiment_262_300_fixed:TD3': 'TD3',
                                                        'buffer_experiment_262_300_fixed:SAC': 'SAC'
                                                        },   
                                            },        
    'buffer_tests_fixed_600k': {  'experiments':['buffer_experiment_262_600_fixed'],
                                            'algorithms': ['TD3', 'SAC'],
                                            'multi_agent': True,
                                            'mean_std_plot': True,
                                            'window': 100,
                                            'title': "Fixed Replay Buffer of Size 600k",
                                            'xlabel': "Timesteps (unit)",
                                            'ylabel': "Average return (unit)",
                                            'label':    {
                                                        # PARTIALLY SUPPORTED FOR MULTI AGENT
                                                        'buffer_experiment_262_600_fixed:TD3': 'TD3',
                          				'buffer_experiment_262_600_fixed:SAC': 'SAC'                                                        
                                                        },   
                                            }, 
    'buffer_tests_fixed_1200k': {  'experiments':['buffer_experiment_262_1200_fixed'],
                                            'algorithms': ['TD3', 'SAC'],
                                            'multi_agent': True,
                                            'mean_std_plot': True,
                                            'window': 100,
                                            'title': "Fixed Replay Buffer of Size 1200k",
                                            'xlabel': "Timesteps (unit)",
                                            'ylabel': "Average return (unit)",
                                            'label':    {
                                                        # PARTIALLY SUPPORTED FOR MULTI AGENT
                                                        'buffer_experiment_262_1200_fixed:TD3': 'TD3',
                                                        'buffer_experiment_262_1200_fixed:SAC': 'SAC'                                                        
                                                        },   
                                            },
    'buffer_tests_fixed_2400k': {  'experiments':['buffer_experiment_262_2400_fixed'],
                                            'algorithms': ['TD3', 'SAC'],
                                            'multi_agent': True,
                                            'mean_std_plot': True,
                                            'window': 100,
                                            'title': "Fixed Replay Buffer of Size 2400k",
                                            'xlabel': "Timesteps (unit)",
                                            'ylabel': "Average return (unit)",
                                            'label':    {
                                                        # PARTIALLY SUPPORTED FOR MULTI AGENT
                                                        'buffer_experiment_262_2400_fixed:TD3': 'TD3',
                                                        'buffer_experiment_262_2400_fixed:SAC': 'SAC'
                                                        },
                                            },
    'buffer_tests_fixed_4800k': {  'experiments':['buffer_experiment_262_4800_fixed'],
                                            'algorithms': ['TD3', 'SAC'],
                                            'multi_agent': True,
                                            'mean_std_plot': True,
                                            'window': 100,
                                            'title': "Fixed Replay Buffer of Size 4800k",
                                            'xlabel': "Timesteps (unit)",
                                            'ylabel': "Average return (unit)",
                                            'label':    {
                                                        # PARTIALLY SUPPORTED FOR MULTI AGENT
                                                        'buffer_experiment_262_4800_fixed:TD3': 'TD3',
                                                        'buffer_experiment_262_4800_fixed:SAC': 'SAC'
                                                        },
                                            },
    
         }
    
tables = {
         }

report_config = {'charts': charts,
                 'tables': tables,
                 'author': 'Luke Vassallo',
                 'timestamp': f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'  # ⭐ 生成当前时间戳作为报告配置的创建时间
                }

save_report_config("./report_config.json", report_config)

#rc = load_report_config("./report_config.json")
#for key,value in rc.items():
    #print(f'{key} : {value}')

from datetime import datetime
import json

def save_report_config(filename, report_config):
    """
    将报告配置保存到指定的JSON文件中。

    Args:
        filename (str): 要保存的JSON文件路径
        report_config (dict): 包含报告配置的字典

    Returns:
        None
    """
    # Write default_hyperparameters dict to a json file
    with open(filename, 'w') as fp:
        json.dump(report_config, fp)  # ⭐ 将配置字典写入JSON文件
    
    fp.close()
        
def load_report_config(filename):
    """
    从JSON配置文件中加载报告配置数据。

    Args:
        filename (str): 要加载的JSON配置文件的路径。

    Returns:
        dict: 包含报告配置的字典对象。
    """
    fp = open(filename, 'r')
    report_config = json.load(fp)  # ⭐ 核心代码：从文件加载JSON数据并解析为字典
    fp.close()
    return report_config    
        
charts = {
    'parameter_test_622': { 'experiments':['parameter_experiment_622'],
                            'algorithms': ['TD3', 'SAC'],
                            'multi_agent': True,
                            'mean_std_plot': True,
                            'ylim_bot': -1000,
                            'xscale': 'k',
                            'window': 100,
                            'title': "Parameter test w/ emphasis on EW", #(W=6, H=2, O=2)
                            'xlabel': "Timesteps (unit)",
                            'ylabel': "Average return (unit)",
                            'label': {
                                         # PARTIALLY SUPPORTED FOR MULTI AGENT
                                         'parameter_experiment_622:TD3': 'TD3',
                                         'parameter_experiment_622:SAC': 'SAC',
                                     },   
                           }, 
    'parameter_test_262': { 'experiments':['parameter_experiment_262'],
                            'algorithms': ['TD3', 'SAC'],
                            'multi_agent': True,
                            'mean_std_plot': True,
                            'ylim_bot': -1000,
                            'xscale': 'k',
                            'window': 100,
                            'title': "Parameter test w/ emphasis on HPWL",
                            'xlabel': "Timesteps (unit)",
                            'ylabel': "Average return (unit)",
                            'label': {
                                         # PARTIALLY SUPPORTED FOR MULTI AGENT
                                         'parameter_experiment_262:TD3': 'TD3',
                                         'parameter_experiment_262:SAC': 'SAC',
                                     },   
                           },
    'parameter_test_226': { 'experiments':['parameter_experiment_226'],
                            'algorithms': ['TD3', 'SAC'],
                            'multi_agent': True,
                            'mean_std_plot': True,
                            'ylim_bot': -1000,
                            'xscale': 'k',
                            'window': 100,
                            'title': "Parameter test w/ emphasis on overlap",
                            'xlabel': "Timesteps (unit)",
                            'ylabel': "Average return (unit)",
                            'label': {
                                         # PARTIALLY SUPPORTED FOR MULTI AGENT
                                         'parameter_experiment_226:TD3': 'TD3',
                                         'parameter_experiment_226:SAC': 'SAC',
                                     },   
                           },
    'parameter_test_442': { 'experiments':['parameter_experiment_442'],
                            'algorithms': ['TD3', 'SAC'],
                            'multi_agent': True,
                            'mean_std_plot': True,
                            'ylim_bot': -1000,
                            'xscale': 'k',
                            'window': 100,
                            'title': "Parameter test w/ emphasis on wirelength", #(W=6, H=2, O=2)
                            'xlabel': "Timesteps (unit)",
                            'ylabel': "Average return (unit)",
                            'label': {
                                         # PARTIALLY SUPPORTED FOR MULTI AGENT
                                         'parameter_experiment_442:TD3': 'TD3',
                                         'parameter_experiment_442:SAC': 'SAC',
                                     },   
                           },                                                                                 
         }
    
tables = {
         }

report_config = {'charts': charts,
                 'tables': tables,
                 'author': 'Luke Vassallo',
                 'timestamp': f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'  # ⭐ 核心代码：自动生成当前时间戳
                }

save_report_config("./report_config.json", report_config)

#rc = load_report_config("./report_config.json")
#for key,value in rc.items():
    #print(f'{key} : {value}')

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
        json.dump(report_config, fp)  # ⭐ 核心操作：将字典序列化为JSON并写入文件
    
    fp.close()
        
def load_report_config(filename):
    """
    从JSON文件中加载报告配置

    Args:
        filename (str): 要加载的JSON配置文件的路径

    Returns:
        dict: 包含报告配置的字典对象
    """
    fp = open(filename, 'r')
    report_config = json.load(fp)  # ⭐ 核心代码：从文件加载JSON数据并转换为Python字典
    fp.close()
    return report_config    
        
charts = {
    '05_training_td3_cuda_fast_262': {  'experiments':['training_td3_cuda_262'],
                                            'algorithms': ['TD3'],
                                            'multi_agent': True,
                                            'window': 100,
                                            'title': "Parameter test w/ emphasis on wirelength (W=2, H=6, O=2)",
                                            'xlabel': "Timesteps (unit)",
                                            'ylabel': "Average return (unit)",
                                            'label':    {
                                                        # PARTIALLY SUPPORTED FOR MULTI AGENT
                                                        },   
                                            },                                                    
         }
    
tables = {
         }

report_config = {'charts': charts,
                 'tables': tables,
                 'author': 'Luke Vassallo',
                 'timestamp': f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
                }

save_report_config("./report_config.json", report_config)

#rc = load_report_config("./report_config.json")
#for key,value in rc.items():
    #print(f'{key} : {value}')

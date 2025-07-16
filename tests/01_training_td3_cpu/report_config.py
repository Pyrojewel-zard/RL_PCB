from datetime import datetime
import json

def save_report_config(filename, report_config):
    """
    将报告配置保存为JSON文件

    Args:
        filename (str): 要保存的目标文件名
        report_config (dict): 包含报告配置的字典

    Returns:
        None
    """
    # Write default_hyperparameters dict to a json file
    with open(filename, 'w') as fp:
        json.dump(report_config, fp)  # ⭐ 核心代码：将配置字典序列化为JSON并写入文件
    
    fp.close()
        
def load_report_config(filename):
    """
    从JSON文件加载报告配置数据

    Args:
        filename (str): 要加载的JSON配置文件的路径

    Returns:
        dict: 包含报告配置的字典对象
    """
    fp = open(filename, 'r')
    report_config = json.load(fp)  # ⭐ 核心代码：从文件读取并解析JSON数据
    fp.close()
    return report_config    
        
charts = {
    '01_training_td3_cpu_622': {  'experiments':['training_td3_cpu_622'],
                                            'algorithms': ['TD3'],
                                            'multi_agent': True,
                                            'window': 10,
                                            'title': "Parameter test w/ emphasis on wirelength (W=6, H=2, O=2)",
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

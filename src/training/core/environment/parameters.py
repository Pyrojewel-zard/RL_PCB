# 解析与环境相关的参数，不改变命令行参数解析
class parameters:
    """
    环境参数类，存储环境运行所需的所有配置参数
    """
    
    def __init__(self, params=None):
        """
        初始化环境参数
        
        Args:
            params: 参数字典，包含环境运行所需的所有配置
        """
        if params is None:
            print("params are needed to initialize the environment.\
                   Please provide a dictionary with PCB params when\
                   creating an agent object.")
            return -1
            
        # PCB文件相关参数
        self.training_pcb = params["training_pcb"]           # 训练用PCB文件
        self.evaluation_pcb = params["evaluation_pcb"]       # 评估用PCB文件
        self.pcb_file = params["pcb_file"]                   # PCB文件路径
        self.net = params["net"]                             # 神经网络模型路径
        
        # 数据增强相关参数
        self.use_dataAugmenter = params["use_dataAugmenter"] # 是否使用数据增强
        self.augment_position = params["augment_position"]   # 是否增强位置
        self.augment_orientation = params["augment_orientation"] # 是否增强方向
        
        # 智能体相关参数
        self.agent_max_action = params["agent_max_action"]   # 智能体最大动作值
        self.agent_expl_noise = params["agent_expl_noise"]   # 智能体探索噪声
        
        # 调试和训练参数
        self.debug = params["debug"]                         # 是否启用调试模式
        self.max_steps = params["max_steps"]                 # 最大步数
        
        # 奖励函数权重参数
        self.n = params["w"]                                 # 线长权重
        self.m = params["o"]                                 # 重叠度权重
        self.p = params["hpwl"]                              # HPWL权重
        
        # 其他参数
        self.seed = params["seed"]                           # 随机种子
        self.ignore_power = params["ignore_power"]           # 是否忽略电源网络
        self.log_dir = params["log_dir"]                     # 日志目录
        self.idx = params["idx"]                             # PCB索引
        self.shuffle_idxs = params["shuffle_idxs"]           # 是否随机打乱智能体执行顺序
        
    def write_to_file(self, fileName, append=True):
        """
        将参数写入文件（当前未实现）
        
        Args:
            fileName: 文件名
            append: 是否追加模式
        """
        return

    def write_to_tensoboard(self, tag):
        """
        将参数写入TensorBoard（当前未实现）
        
        Args:
            tag: TensorBoard标签
        """
        return

    def to_string(self):
        """
        将参数转换为HTML格式字符串
        
        Returns:
            s: 格式化的参数字符串
        """
        params = vars(self)
        s = ""
        s += "<strong>====== Environment parameters ======</strong><br>"
        for key, value in params.items():
            s += f"{key} -> {value}<br>"
        s += "<br>"

        return s

    def to_text_string(self, prefix=""):
        """
        将参数转换为纯文本格式字符串
        
        Args:
            prefix: 前缀字符串
            
        Returns:
            s: 格式化的参数字符串
        """
        params = vars(self)
        s = ""
        for key, value in params.items():
            s += f"{prefix}{key} -> {value}\r\n"

        return s

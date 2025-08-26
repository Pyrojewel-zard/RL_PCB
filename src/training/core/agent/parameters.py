# 解析与智能体相关的参数，不改变命令行参数解析
class parameters:
    """
    智能体参数类，存储智能体运行所需的所有配置参数
    """
    
    def __init__(self, pcb_params=None):
        """
        初始化智能体参数
        
        Args:
            pcb_params: PCB参数字典，包含智能体运行所需的所有配置
        """
        if pcb_params is None:
            print("PCB parameters are needed to initialize the agent.\
                   Please provide a dictionary with PCB parameters when\
                   creating an agent object.")
            return -1

        # PCB相关参数
        self.board = pcb_params["board"]                    # PCB板对象
        self.graph = pcb_params["graph"]                    # 网络图对象
        self.board_width = pcb_params["board_width"]        # 板宽度
        self.board_height = pcb_params["board_height"]      # 板高度
        
        # 节点相关参数
        self.node = pcb_params["node"]                      # 当前处理的节点句柄
        self.neighbors = pcb_params["neighbors"]            # 邻居节点句柄列表
        self.eoi = pcb_params["eoi"]                        # 相关边列表（Edges of Interest）

        # 网络相关参数
        self.net = pcb_params["net"]                        # 稳定基线3神经网络路径
        self.padding = 4                                    # 绘制时的填充值
        self.step_size = pcb_params["step_size"]            # 步长大小
        self.max_steps = pcb_params["max_steps"]            # 最大步数
        
        # 网络过滤参数
        self.ignore_power_nets = True                       # 是否忽略电源网络
        
        # 优化目标参数
        self.opt_euclidean_distance = pcb_params["opt_euclidean_distance"]  # 目标欧几里得距离
        self.opt_hpwl = pcb_params["opt_hpwl"]                             # 目标半周长线长
        
        # 随机性和网络参数
        self.seed = int(pcb_params["seed"])                 # 随机种子
        self.nets = pcb_params["nets"]                      # 网络集合
        self.graph = pcb_params["graph"]                    # 网络图对象
        
        # 强化学习参数
        self.max_action = pcb_params["max_action"]          # 最大动作值
        self.expl_noise = pcb_params["expl_noise"]          # 探索噪声
        
        # 奖励函数权重参数
        self.n = pcb_params["n"]                            # 线长权重
        self.m = pcb_params["m"]                            # 重叠度权重
        self.p = pcb_params["p"]                            # HPWL权重
        
        # 其他参数
        self.ignore_power = pcb_params["ignore_power"]      # 是否忽略电源
        self.log_file = pcb_params["log_file"]              # 日志文件路径

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
        s += f"<strong>====== Agent {self.node.get_name()} ({self.node.get_id()}) parameters ======</strong><br>"
        
        # 跳过复杂对象，只显示基本参数
        for key, value in params.items():
            if key in ("board", "graph", "node", "neighbors", "eoi", "edge"):
                continue
            s += f"{key} -> {value}<br>"
        s += "<br>"

        return s

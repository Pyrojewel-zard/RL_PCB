# parse parameters relevant to the environmnet only.
# do not alter cla in any way.
class parameters:
    def __init__(self, params=None):
        """
        初始化环境相关参数，用于PCB环境的训练和评估。

        Args:
            params (dict, optional): 包含所有必要参数的字典。如果为None，会提示错误信息并返回-1。

        Raises:
            ValueError: 如果params为None时会打印错误信息（但实际返回-1而不是抛出异常）

        Attributes:
            包含各种PCB环境配置参数，如训练/评估PCB文件、网络配置、数据增强设置、
            代理行为参数、优化权重等。
        """
        if params is None:
            print("params are needed to initialize the environment.\
                   Please provide a dictionary with PCB params when\
                   creating an agent object.")
            return -1
        self.training_pcb = params["training_pcb"]  # ⭐ 核心参数：训练用PCB文件
        self.evaluation_pcb = params["evaluation_pcb"]
        self.pcb_file = params["pcb_file"]
        self.net = params["net"]
        self.use_dataAugmenter = params["use_dataAugmenter"]
        self.augment_position = params["augment_position"]
        self.augment_orientation = params["augment_orientation"]
        self.agent_max_action = params["agent_max_action"]
        self.agent_expl_noise = params["agent_expl_noise"]
        self.debug = params["debug"]
        self.max_steps = params["max_steps"]
        # weight for euclidean distance based wirelength
        self.n = params["w"]
        # weight for overlap
        self.m = params["o"]
        # weight for hpwl
        self.p = params["hpwl"]
        self.seed = params["seed"]
        self.ignore_power = params["ignore_power"]
        self.log_dir = params["log_dir"]
        # TODO: Add error checking
        self.idx = params["idx"]
        self.shuffle_idxs = params["shuffle_idxs"]
    def write_to_file(self, fileName, append=True):
        return

    def write_to_tensoboard(self, tag):
        return

    def to_string(self):
        params = vars(self)
        s = ""
        s += "<strong>====== Environment parameters ======</strong><br>"
        for key,value in params.items():
            s += f"{key} -> {value}<br>"
        s += "<br>"

        return s

    def to_text_string(self, prefix = ""):
        params = vars(self)
        s = ""
        for key,value in params.items():
            s += f"{prefix}{key} -> {value}\r\n"

        return s

import os
import sys
from data_augmenter import dataAugmenter
from pcb import pcb
from graph import graph
from core.agent.agent import agent as agent
from core.agent.parameters import parameters as agent_parameters
from core.environment.tracker import tracker
from pcbDraw import draw_board_from_board_and_graph_with_debug, draw_ratsnest_with_board
import numpy as np
import random as random_package

class environment:
    """
    PCB布局优化环境类，管理整个PCB布局优化过程
    负责创建和管理多个智能体，协调它们之间的交互，并提供训练接口
    """
    
    def __init__(self, parameters):
        """
        初始化环境
        
        Args:
            parameters: 环境配置参数
        """
        self.parameters = parameters

        # 创建PCB对象列表
        self.pv = pcb.vptr_pcbs()
        # 读取PCB文件
        pcb.read_pcb_file(self.parameters.pcb_file, self.pv)

        # 检查PCB索引是否有效
        if (self.parameters.idx != -1) and (self.parameters.idx >= len(self.pv)):
            print("The supplied pcb index exceeds the number of layouts in the training set ... Program terminating")
            sys.exit()

        self.rng = np.random.default_rng(seed=self.parameters.seed)  # 随机数生成器
        
        # 初始化环境状态，从PCB文件加载
        self.initialize_environment_state_from_pcb(init=True, idx=self.parameters.idx)
        self.tracker = tracker()  # 环境跟踪器

        # 数据增强器配置
        if self.parameters.use_dataAugmenter is True:
            # 配置最大平移限制，需要满足以下约束：
            # 1. 必须只有一个LOCKED组件在网络表中
            # 2. LOCKED组件必须居中放置在板中央
            nn = self.g.get_nodes()
            c_sz = 0
            b_sz = np.minimum(self.b.get_width(), self.b.get_height())
            for i in range(len(nn)):
                if nn[i].get_isPlaced() == 1:
                    c_sz = np.maximum(nn[i].get_size()[0], nn[i].get_size()[1])
                    break

            sz = (b_sz - c_sz) / 2.0
            translation_limits = [0.66*sz, 0.66*sz]

            # 创建数据增强器
            self.dA = dataAugmenter(
                board_size=[self.b.get_width(), self.b.get_height()],
                max_translation=translation_limits,
                goal=[[-1,-1, 0]],
                augment_position=self.parameters.augment_position,
                augment_orientation=self.parameters.augment_orientation,
                rng=self.rng)

        self.padding = 4  # 绘制时的填充值

    def reset(self):
        """
        重置环境状态，开始新的训练回合
        """
        # 更新原始节点为当前最优值
        self.g.update_original_nodes_with_current_optimals()
        
        # 重新初始化环境状态
        self.initialize_environment_state_from_pcb(init=True, idx=self.parameters.idx)

        # 数据增强处理
        if self.parameters.use_dataAugmenter is True:
            # 重新配置数据增强器
            nn = self.g.get_nodes()
            c_sz = 0
            b_sz = np.minimum(self.b.get_width(), self.b.get_height())
            for i in range(len(nn)):
                if nn[i].get_isPlaced() == 1:
                    c_sz = np.maximum(nn[i].get_size()[0], nn[i].get_size()[1])
                    break

            sz = (b_sz - c_sz) / 2.0
            self.dA.board_size = [self.b.get_width(), self.b.get_height()]
            self.dA.set_translation_limits([0.66*sz, 0.66*sz])
            
            # 执行数据增强
            self.optimal_location = self.dA.augment_graph(grph=self.g, idx=0)

        # 随机初始化所有智能体
        for i in range(len(self.agents)):
            self.agents[i].init_random()

        # 重置所有智能体状态
        for i in range(len(self.agents)):
            self.agents[i].reset()

        # 调试模式下的可视化
        if self.parameters.debug:
            # 绘制组件网格
            comp_grids = draw_board_from_board_and_graph_with_debug(
                self.b, self.g, padding=self.padding)
            
            # 绘制飞线图
            for i in range(len(self.agents)):
                if i == 0:
                    ratsnest = draw_ratsnest_with_board(
                        self.agents[i].parameters.node,
                        self.agents[i].parameters.neighbors,
                        self.agents[i].parameters.eoi,
                        self.b,
                        line_thickness=1,
                        padding=self.padding,
                        ignore_power=True)
                else:
                    ratsnest = np.maximum(ratsnest, draw_ratsnest_with_board(
                        self.agents[i].parameters.node,
                        self.agents[i].parameters.neighbors,
                        self.agents[i].parameters.eoi,
                        self.b,
                        line_thickness=1,
                        padding=self.padding,
                        ignore_power=True))

            self.tracker.add(comp_grids=comp_grids, ratsnest=ratsnest)

    def step(self, model, random=False, deterministic:bool=False, rl_model_type:str="SAC"):
        """
        执行环境步进，让所有智能体执行动作
        
        该方法实现了多智能体强化学习环境的核心步进逻辑，支持两种工作模式：
        1. 随机探索模式 (random=True): 用于数据收集和环境验证
        2. 策略学习模式 (random=False): 用于强化学习训练
        
        Args:
            model: 强化学习模型对象，包含策略网络和值函数网络
            random: 是否强制使用随机动作，True表示随机探索，False表示策略学习
            deterministic: 是否确定性选择动作，仅在策略学习模式下有效
            rl_model_type: 强化学习算法类型，支持"TD3"和"SAC"两种算法
            
        Returns:
            observation_vec: 所有智能体的观察向量列表，每个元素包含：
                [_state, _next_state, reward, action, done, _next_state_info]
                
        Note:
            - 该方法采用"一票否决"机制，任何智能体终止都会结束当前步进
            - 支持智能体执行顺序的随机化，增加训练多样性
            - 提供完整的性能指标记录和可视化支持
        """
        # 初始化数据收集容器
        observation_vec = []    # 存储所有智能体的观察信息
        step_metrics = []       # 存储当前步进的性能指标

        # 智能体执行顺序控制（支持随机打乱）
        idxs = []
        for i in range(len(self.agents)):
            idxs.append(i)

        # 随机化智能体执行顺序，增加训练多样性
        # 这种随机化策略有助于避免智能体之间的顺序依赖
        if self.parameters.shuffle_idxs is True:
            random_package.shuffle(idxs)

        # 主循环：让每个智能体执行一步动作
        for i in idxs:
            # 调用智能体的step方法，执行动作并获取结果
            # 智能体内部会根据random参数选择动作策略：
            # - random=True: 使用随机动作
            # - random=False: 使用策略网络选择动作
            state, next_state, reward, action, done = self.agents[i].step(
                model=model,
                random=random,
                deterministic=deterministic,
                rl_model_type=rl_model_type)
            
            # 状态向量格式转换：将字典格式转换为向量格式
            # 原始状态格式：{"los": [...], "ol": [...], "dom": [...], ...}
            # 转换后格式：31维向量 [los[8], ol[8], dom[2], euc_dist[2], position[2], orientation[1], boardmask[8]]
            _state = list(state["los"]) + list(state["ol"]) + state["dom"] + state["euc_dist"] + state["position"] + state["ortientation"] + list(state["boardmask"])
            _next_state = list(next_state["los"]) + list(next_state["ol"]) + next_state["dom"] + next_state["euc_dist"] + next_state["position"] + next_state["ortientation"] + list(next_state["boardmask"])
            _next_state_info = next_state["info"]  # 提取附加信息
            
            # 构建观察向量：包含当前状态、下一状态、奖励、动作、终止标志和信息
            # 这个向量将用于强化学习算法的训练和更新
            observation_vec.append([_state, _next_state, reward, action, done, _next_state_info])

            # 记录详细的步进性能指标，用于训练监控和分析
            step_metrics.append({
                "id": self.agents[i].parameters.node.get_id(),        # 智能体ID
                "name": self.agents[i].parameters.node.get_name(),    # 智能体名称（组件名称）
                "reward": reward,                                     # 当前步的奖励值
                
                # 线长相关指标
                "W": self.agents[i].all_w[-1],                       # 归一化线长（当前值）
                "We": self.agents[i].We,                             # 目标线长（最优值）
                "Wi": self.agents[i].Wi,                             # 初始线长（起始值）
                "raw_W": self.agents[i].W[-1],                       # 原始线长（未归一化）
                
                # HPWL相关指标
                "HPWL": self.agents[i].all_hpwl[-1],                 # 归一化HPWL（当前值）
                "HPWLe": self.agents[i].HPWLe,                       # 目标HPWL（最优值）
                "HPWLi": self.agents[i].HPWLi,                       # 初始HPWL（起始值）
                "raw_HPWL": self.agents[i].HPWL[-1],                 # 原始HPWL（未归一化）
                
                # 重叠度和成本指标
                "ol": 1-self.agents[i].ol_term5[-1],                 # 重叠度（值越大表示重叠越严重）
                "weighted_cost": self.agents[i].all_weighted_cost[-1] # 加权成本（综合优化目标）
            })

            # 早期终止检查：如果任何智能体完成，则停止当前步进
            # 这种"一票否决"机制确保环境状态的一致性，避免无效计算
            if done is True:
                break

        # 调试模式下的可视化更新
        # 当debug=True时，实时更新组件网格和飞线图，便于训练过程监控
        if self.parameters.debug is True:
            # 绘制当前PCB布局的组件网格
            # 组件网格显示了所有电子组件在PCB上的位置和形状
            comp_grids = draw_board_from_board_and_graph_with_debug(
                self.b, self.g, padding=self.padding)
            
            # 更新飞线图：显示网络连接关系
            # 飞线图帮助理解组件之间的电气连接，是布局优化的重要参考
            for i in range(len(self.agents)):
                if i == 0:
                    # 第一个智能体：直接创建飞线图
                    ratsnest = draw_ratsnest_with_board(
                        self.agents[i].parameters.node,      # 当前智能体对应的组件节点
                        self.agents[i].parameters.neighbors, # 邻居组件列表
                        self.agents[i].parameters.eoi,       # 相关边列表（Edges of Interest）
                        self.b,                             # PCB板对象
                        line_thickness=1,                    # 飞线线条粗细
                        padding=self.padding,                # 绘制填充值
                        ignore_power=True)                   # 忽略电源网络
                else:
                    # 后续智能体：将飞线图叠加到现有图上
                    # 使用np.maximum确保重叠区域的飞线可见性
                    ratsnest = np.maximum(ratsnest, draw_ratsnest_with_board(
                        self.agents[i].parameters.node,
                        self.agents[i].parameters.neighbors,
                        self.agents[i].parameters.eoi,
                        self.b,
                        line_thickness=1,
                        padding=self.padding,
                        ignore_power=True))

            # 将组件网格和飞线图添加到跟踪器，用于后续的可视化和分析
            self.tracker.add(comp_grids=comp_grids, ratsnest=ratsnest)
            
        # 记录性能指标到跟踪器
        # 这些指标将用于训练过程监控、性能分析和可视化
        self.tracker.add_metrics(step_metrics)

        
        # 返回所有智能体的观察向量
        # 每个观察向量包含完整的状态转换信息，用于强化学习算法训练
        return observation_vec

    def initialize_environment_state_from_pcb(self, init=False, idx=-1):
        """
        从PCB文件初始化环境状态
        
        Args:
            init: 是否初始化智能体列表
            idx: PCB索引，-1表示随机选择
        """
        # 检查PCB数据是否存在
        if len(self.pv) == 0:
            raise ValueError(f"[ERROR] No PCB data found. Please check your training.pcb file.")
        
        # 选择PCB索引
        if idx == -1:
            self.idx = int(self.rng.integers(len(self.pv)))
        else:
            self.idx = idx
        self.p = self.pv[self.idx]

        # 初始化智能体列表
        if init:
            self.agents = []
        
        # 获取图和板对象
        self.g = self.p.get_graph()
        self.g.reset()
        self.b = self.p.get_board()
        
        # 重要：将组件原点设置为零
        self.g.set_component_origin_to_zero(self.b)

        # 遍历所有节点，为未放置的组件创建智能体
        nn = self.g.get_nodes()
        for i in range(len(nn)):
            if nn[i].get_isPlaced() == 0:  # 未放置的组件
                node_id = nn[i].get_id()
                nets = []

                # 获取邻居节点
                neighbor_ids = self.g.get_neighbor_node_ids(node_id)
                neighbors = []
                for n_id in neighbor_ids:
                    neighbors.append(self.g.get_node_by_id(n_id))

                # 获取相关边
                ee = self.g.get_edges()
                eoi = []
                for e in ee:
                    if e.get_instance_id(0) == node_id or e.get_instance_id(1) == node_id:
                        eoi.append(e)
                        nets.append(e.get_net_id())

                if init:
                    # 创建智能体参数
                    agent_params = agent_parameters({
                        "board": self.b,
                        "graph": self.g,
                        "board_width": self.b.get_width(),
                        "board_height": self.b.get_height(),
                        "node": nn[i],
                        "neighbors": neighbors,
                        "eoi": eoi,
                        "nets": set(nets),
                        "net": self.parameters.net,
                        "seed": self.rng.integers(0, 65535),
                        "step_size": min(self.b.get_width(), self.b.get_height()) * 0.05,
                        "max_steps": self.parameters.max_steps,
                        "expl_noise": self.parameters.agent_expl_noise,
                        "max_action": self.parameters.agent_max_action,
                        "opt_euclidean_distance": nn[i].get_opt_euclidean_distance(),
                        "opt_hpwl": nn[i].get_opt_hpwl(),
                        "n": self.parameters.n,           # 线长权重
                        "m": self.parameters.m,           # 重叠度权重
                        "p": self.parameters.p,           # HPWL权重
                        "ignore_power": self.parameters.ignore_power,
                        "log_file": None if self.parameters.log_dir is None else os.path.join(self.parameters.log_dir, self.p.get_kicad_pcb2().replace(".kicad_pcb", ".log")),
                    })

                    # 创建智能体并添加到列表
                    self.agents.append(agent(agent_params))
                else:
                    # 更新现有智能体的参数
                    self.agents[i].parameters.node = nn[i]
                    self.agents[i].parameters.neighbors = neighbors
                    self.agents[i].parameters.eoi = eoi

    def get_target_params(self):
        """
        获取所有智能体的目标参数
        
        Returns:
            target_params: 目标参数列表
        """
        target_params = []
        for agnt in self.agents:
            target_params.append({
                "id": agnt.parameters.node.get_id(),
                "We": agnt.We,        # 目标线长
                "HPWLe": agnt.HPWLe   # 目标HPWL
            })
        return target_params

    def get_all_target_params(self):
        """
        获取所有PCB的目标参数
        
        Returns:
            all_params: 所有PCB的目标参数列表
        """
        original_idx = self.idx
        all_params = []
        
        # 遍历所有PCB
        for i in range(len(self.pv)):
            self.initialize_environment_state_from_pcb(init=True, idx=i)
            all_params.append({
                "kicad_pcb": self.p.get_kicad_pcb2(),
                "expert_targets": self.get_target_params()
            })

        # 恢复原始索引
        self.initialize_environment_state_from_pcb(init=True, idx=original_idx)
        return all_params

    def info(self):
        """
        打印所有智能体的信息
        """
        for agnt in self.agents:
            agnt.print()

    def library_info(self):
        """
        打印库信息
        """
        graph.build_info()
        pcb.build_info()

    def library_info_as_string(self):
        """
        获取库信息字符串
        
        Returns:
            s: 格式化的库信息字符串
        """
        s = "<strong>====== Library information ======</strong><br>"
        s += pcb.build_info_as_string().replace("\n", "<br>")
        s += "pcb library dependency #1<br>"
        s += pcb.dependency_info_as_string().replace("\n", "<br>")[4:-4]
        s += graph.build_info_as_string().replace("\n", "<br>")
        return s

    def write_pcb_file(self, path=None, filename=None):
        """
        写入PCB文件
        
        Args:
            path: 文件路径
            filename: 文件名
        """
        if path is not None and filename is not None:
            save_loc = os.path.join(path, filename)
        else:
            save_loc = "./pcb_file.pcb"

        # 重置所有图
        for i in range(len(self.pv)):
            g = self.pv[i].get_graph()
            g.reset()
        
        pcb.write_pcb_file(save_loc, self.pv, False)

    def write_current_pcb_file(self, path=None, filename=None):
        """
        写入当前PCB文件
        
        Args:
            path: 文件路径
            filename: 文件名
        """
        if path is not None and filename is not None:
            save_loc = os.path.join(path, filename)
        else:
            save_loc = "./pcb_file.pcb"

        # 创建当前PCB的副本
        pv = pcb.vptr_pcbs()
        pv.append(self.pv[self.idx])
        g = pv[0].get_graph()
        g.update_hpwl(do_not_ignore_unplaced=True)
        
        # 重要：重置组件原点
        g.reset_component_origin(self.b)
        pcb.write_pcb_file(save_loc, pv, False)
        
        # 重要：将组件原点设置为零
        g.set_component_origin_to_zero(self.b)

    def calc_hpwl(self):
        """
        计算当前HPWL
        
        Returns:
            HPWL值
        """
        return self.g.calc_hpwl(True)

    def get_parameters(self):
        """
        获取环境参数
        
        Returns:
            环境参数对象
        """
        return self.parameters

    def get_current_pcb_name(self):
        """
        获取当前PCB名称（去掉.kicad_pcb扩展名）
        
        Returns:
            当前PCB名称
        """
        return self.pv[self.idx].get_kicad_pcb2().split(".")[0]

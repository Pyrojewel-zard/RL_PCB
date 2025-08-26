from pcb_vector_utils import compute_sum_of_euclidean_distances_between_pads
import numpy as np
import gym
from gym import spaces

from core.agent.observation import get_agent_observation
from core.agent.tracker import tracker

from pcbDraw import draw_board_from_board_and_graph_multi_agent

import datetime

class agent(gym.Env):
    """
    PCB布局优化智能体类，继承自gym.Env以实现强化学习环境接口
    负责单个电子组件的布局优化，通过强化学习算法学习最优位置和方向
    """
    
    def __init__(self, parameters):
        """
        初始化智能体
        
        Args:
            parameters: 包含PCB布局相关参数的配置对象
        """
        self.parameters = parameters

        # 定义观察空间，包含8个方向的视线、重叠度、距离向量等信息
        obs_space = {
            "los": spaces.Box(low=0.0, high=1.0, shape=(8,), dtype=np.float32),      # 8个方向的视线信息
            "ol": spaces.Box(low=0.0, high=1.0, shape=(8,), dtype=np.float32),       # 8个方向的重叠度
            "dom": spaces.Box(low=0.0, high=1.0, shape=(2,), dtype=np.float32),      # 距离向量
            "euc_dist": spaces.Box(low=0.0, high=1.0, shape=(2,), dtype=np.float32), # 欧几里得距离和角度
            "position": spaces.Box(low=0.0, high=1.0, shape=(2,), dtype=np.float32), # 当前位置坐标
            "ortientation": spaces.Box(low=0.0, high=1.0, shape=(1,), dtype=np.float32), # 当前方向
            "boardmask":spaces.Box( low=0.0, high=1.0,shape=(8,), dtype=np.float32)  # 板边界掩码
        }
        self.observation_space = spaces.Dict(obs_space)
        
        # 定义动作空间：步长、角度、方向
        self.action_space = spaces.Box(
            low=np.array([0,0,0], dtype=np.float32),
            high=np.array([1,2*np.pi,1], dtype=np.float32))

        self.tracker = tracker()  # 跟踪器，用于记录训练过程
        self.rng = np.random.default_rng(seed=self.parameters.seed)  # 随机数生成器
        self.action_space.seed(self.parameters.seed)  # 设置动作空间随机种子

        self.max_steps = self.parameters.max_steps  # 最大步数
        self.steps_done = 0  # 已完成的步数

        # 优化目标值
        self.HPWLe = self.parameters.opt_hpwl  # 目标半周长线长
        self.We = self.parameters.opt_euclidean_distance  # 目标欧几里得距离

        # 奖励函数权重参数
        self.n = self.parameters.n  # 线长权重
        self.m = self.parameters.m  # 重叠度权重
        self.p = self.parameters.p  # HPWL权重

        self.penalty_per_remaining_step = 15  # 每剩余步数的惩罚值

    def reset(self):
        """
        重置智能体状态，开始新的训练回合
        """
        self.tracker.reset()
        self.steps_done = 0

        # 重置历史记录列表
        self.W = []          # 线长历史
        self.HPWL = []       # HPWL历史
        self.ol_term5 = []   # 重叠度历史
        self.ol_board = []   # 板边界重叠历史
        self.current_We = self.We

        # 计算初始线长和HPWL
        self.Wi = compute_sum_of_euclidean_distances_between_pads(
            self.parameters.node,
            self.parameters.neighbors,
            self.parameters.eoi,
            ignore_power=self.parameters.ignore_power)
        self.HPWLi = 0
        for net_id in self.parameters.nets:
            self.HPWLi += self.parameters.graph.calc_hpwl_of_net(net_id, True)
        self.current_HPWL = self.HPWLe

        # 重置归一化指标列表
        self.all_w = []
        self.all_hpwl = []
        self.all_weighted_cost = []

    def step(self, model, random:bool=False, deterministic:bool=False, rl_model_type:str="TD3"):
        """
        执行一步动作，更新智能体状态
        
        Args:
            model: 强化学习模型
            random: 是否随机选择动作
            deterministic: 是否确定性选择动作
            rl_model_type: 强化学习算法类型（TD3或SAC）
            
        Returns:
            state: 当前状态
            next_state: 下一状态
            reward: 奖励值
            action: 执行的动作
            done: 是否结束
        """
        self.steps_done += 1
        
        # 获取当前状态观察
        state = get_agent_observation(parameters=self.parameters)
        # 将状态字典转换为向量形式
        _state = list(state["los"]) + list(state["ol"]) + state["dom"] + state["euc_dist"] + state["position"] + state["ortientation"] + list(state["boardmask"])

        if random is True:
            # 随机动作选择
            action = self.action_space.sample()
            if rl_model_type == "TD3":
                model_action = [0,0,0]
                model_action[0] = (action[0] - 0.5) * 2      # 步长归一化
                model_action[1] = (action[1] - np.pi) / np.pi # 角度归一化
                model_action[2] = (action[2] - 0.5) * 2      # 方向归一化
        else:
            if rl_model_type == "TD3":
                # TD3算法动作选择
                if deterministic is True:
                    model_action = model.select_action(np.array(_state))
                else:
                    # 添加探索噪声
                    model_action = (model.select_action(np.array(_state)) + 
                                  np.random.normal(0, self.parameters.max_action * self.parameters.expl_noise, size=3)).clip(-self.parameters.max_action, self.parameters.max_action)
                
                # 动作转换和归一化
                action = model_action
                action = (action + 1) / 2  # [-1, 1] => [0, 1]
                action[1] *= (2 * np.pi)   # 角度范围调整

            else:  # SAC算法
                action = model.select_action(np.array(_state), evaluate=deterministic)

        # 执行动作：更新组件位置和方向
        pos = self.parameters.node.get_pos()
        step_scale = (self.parameters.step_size * action[0])  # 计算步长
        x_offset = step_scale * np.cos(-action[1])           # X方向偏移
        y_offset = step_scale * np.sin(-action[1])           # Y方向偏移
        angle = (np.int0(action[2] * 4) % 4) * 90.0        # 方向角度（0°, 90°, 180°, 270°）

        # 设置新的位置和方向
        self.parameters.node.set_pos(tuple([pos[0] + x_offset, pos[1] + y_offset]))
        self.parameters.node.set_orientation(angle)

        # 获取下一状态并计算奖励
        next_state = get_agent_observation(parameters=self.parameters)
        reward, done = self.get_reward(next_state)

        # 根据算法类型返回不同的动作信息
        if rl_model_type == "TD3":
            return state, next_state, reward, model_action, done
        else:
            return state, next_state, reward, action, done

    def get_reward(self, observation):
        """
        计算奖励值和终止条件
        
        Args:
            observation: 当前观察状态
            
        Returns:
            reward: 奖励值
            done: 是否终止
        """
        done = False
        
        # 计算当前线长
        self.W.append(compute_sum_of_euclidean_distances_between_pads(
            self.parameters.node,
            self.parameters.neighbors,
            self.parameters.eoi,
            ignore_power=self.parameters.ignore_power))

        # 计算当前HPWL
        hpwl = 0
        for net_id in self.parameters.nets:
            hpwl += self.parameters.graph.calc_hpwl_of_net(net_id, True)
        self.HPWL.append(hpwl)

        # 计算重叠度惩罚项
        if np.sum(observation["ol"]) > 1E-6:
            self.ol_term5.append(np.clip((1-np.sum(observation["ol"])/8), 0.0, np.inf))
        else:
            self.ol_term5.append(1)
            
        # 计算板边界重叠惩罚项
        if np.sum(observation["boardmask"]) > 1E-6:
            self.ol_board.append(np.clip((1-np.sum(observation["boardmask"])/8), 0.0, np.inf))
        else:
            self.ol_board.append(1)  # 表示重叠值，重叠越小越接近1

        # 更新最优线长记录
        if self.W[-1] < self.We and self.ol_term5[-1] == 1 and self.ol_board[-1] == 1:
            if self.parameters.log_file is not None:
                f = open(self.parameters.log_file, "a", encoding="utf-8")
                f.write(f"{datetime.datetime.now().strftime('%Y%m%dT%H%M%S.%f')[:-3]} Agent {self.parameters.node.get_name()} ({self.parameters.node.get_id()}) found a better, legal, wirelength target of {np.round(self.W[-1],6)}, originally {np.round(self.We,6)}.\r\n")
                f.close()
            self.We = self.W[-1]
            self.parameters.node.set_opt_euclidean_distance(self.W[-1])

        # 更新最优HPWL记录
        if self.HPWL[-1] < self.HPWLe:
            # 绘制板布局并检查重叠
            stack = draw_board_from_board_and_graph_multi_agent(
                self.parameters.board,
                self.parameters.graph,
                node_id=self.parameters.node.get_id(),
                padding=4)

            # 计算重叠堆叠
            stack_sum = np.zeros((stack[0].shape[0],stack[0].shape[1]), dtype=np.int)
            for i in range(len(stack)):
                stack_sum += stack[i]

            # 检查重叠是否合法（最大堆叠值不超过128）
            if np.max(stack_sum) <= 128:
                if self.parameters.log_file is not None:
                    f = open(self.parameters.log_file, "a", encoding="utf-8")
                    f.write(f"{datetime.datetime.now().strftime('%Y%m%dT%H%M%S.%f')[:-3]} Agent {self.parameters.node.get_name()} ({self.parameters.node.get_id()}) found a better, legal, HPWL target of {np.round(self.HPWL[-1],6)}, originally {np.round(self.HPWLe,6)}.\r\n")
                    f.close()
                self.HPWLe = self.HPWL[-1]
                self.parameters.node.set_opt_hpwl(self.HPWL[-1])

        # 计算奖励值
        reward = 0

        # 安全处理除零情况，计算归一化指标
        denominator_w = self.Wi - self.current_We
        if abs(denominator_w) < 1e-10:
            x = 0.0
        else:
            x = np.clip((self.Wi - self.W[-1]) / denominator_w, -1, 1)
        
        denominator_hpwl = self.HPWLi - self.current_HPWL
        if abs(denominator_hpwl) < 1e-10:
            y = 0.0
        else:
            y = np.clip((self.HPWLi - self.HPWL[-1]) / denominator_hpwl, -1, 1)
        
        # 记录归一化指标
        self.all_w.append(x)
        self.all_hpwl.append(y)
        self.all_weighted_cost.append((self.n*x + self.m*self.ol_term5[-1] + self.p*y + self.m*self.ol_board[-1])/(self.n+2*self.m+self.p))

        # 使用正切函数计算最终奖励
        reward = np.tan((self.n*x + self.m*self.ol_term5[-1] + self.p*y + self.m*self.ol_board[-1])/(self.n+2*self.m+self.p) * np.pi/2.1)

        # 边界触碰惩罚
        if (((observation["position"][0] > 1) or
            (observation["position"][0] < 0) or
            (observation["position"][1] > 1) or
            (observation["position"][1] < 0)) and 
            ((np.sum(observation["ol"])/8) == 1) or (np.sum(observation["boardmask"])/8)==1):
            reward -= (self.max_steps-self.steps_done) * self.penalty_per_remaining_step
            done = True

        # 达到最大步数时终止
        if self.steps_done == self.max_steps:
            done = True

        return reward, done

    def init_random(self):
        """
        随机初始化组件位置和方向
        """
        # 随机位置（避开边界）
        r_pos = self.rng.uniform(low=0.05, high=0.95, size=(2))
        scaled_r_pos = tuple([r_pos[0]*self.parameters.board_width,
                              r_pos[1]*self.parameters.board_height])
        
        # 随机方向（0°, 90°, 180°, 270°）
        scaled_orientation = np.float64(self.rng.integers(4)*90)
        
        self.parameters.node.set_pos(scaled_r_pos)
        self.parameters.node.set_orientation(scaled_orientation)

    def get_observation_space_shape(self):
        """
        获取观察空间的总维度
        
        Returns:
            sz: 观察空间的总维度
        """
        sz = 0
        for _, value in self.observation_space.items():
            sz += value.shape[0]
        return sz

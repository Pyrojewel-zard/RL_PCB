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
    基于强化学习的PCB布局优化智能体环境类。
    
    该类通过调整元件位置和方向来优化PCB布局，最小化布线长度和元件重叠。
    继承自gym.Env类，定义了观察空间、动作空间以及相关参数。

    Attributes:
        parameters: 配置参数对象
        observation_space: 定义智能体的观察空间
        action_space: 定义智能体的动作空间
        tracker: 用于跟踪训练过程的对象
        rng: 随机数生成器
        max_steps: 最大步数限制
        steps_done: 已完成的步数计数器
        HPWLe: 优化目标中的布线长度权重
        We: 优化目标中的欧式距离权重
        n: PCB板参数
        m: PCB板参数
        p: PCB板参数
        penalty_per_remaining_step: 每剩余步数的惩罚系数
    """
    def __init__(self, parameters):
        """
        初始化智能体环境。

        Args:
            parameters: 包含各种配置参数的对象
        """
        self.parameters = parameters

        obs_space = {
            "los": spaces.Box(low=0.0, high=1.0, shape=(8,),
                              dtype=np.float32),
            "ol": spaces.Box(low=0.0, high=1.0, shape=(8,),
                             dtype=np.float32),
            "dom": spaces.Box(low=0.0, high=1.0, shape=(2,),
                              dtype=np.float32),
            "euc_dist": spaces.Box(low=0.0, high=1.0, shape=(2,),
                                   dtype=np.float32),
            "position": spaces.Box(low=0.0, high=1.0, shape=(2,),
                                   dtype=np.float32),
            "ortientation": spaces.Box(low=0.0, high=1.0, shape=(1,),
                                       dtype=np.float32),
            "boardmask": spaces.Box(low=0.0, high=1.0, shape=(8,),
                              dtype=np.float32)                           
            }
        self.observation_space = spaces.Dict(obs_space)  # ⭐ 定义观察空间的结构
        self.action_space = spaces.Box(
            low=np.array([0,0,0], dtype=np.float32),
            high=np.array([1,2*np.pi,1],
                          dtype=np.float32))

        self.tracker = tracker()
        self.rng = np.random.default_rng(seed=self.parameters.seed)
        # action spaces uses their own random number generator.
        self.action_space.seed(self.parameters.seed)

        # self.max_steps = 200
        self.max_steps = self.parameters.max_steps
        self.steps_done = 0

        self.HPWLe = self.parameters.opt_hpwl
        self.We = self.parameters.opt_euclidean_distance

        self.n = self.parameters.n
        self.m = self.parameters.m
        self.p = self.parameters.p

        self.penalty_per_remaining_step = 15

    def reset(self):
        self.tracker.reset()
        self.steps_done = 0

        self.W = []
        self.HPWL = []
        self.ol_term5 = []
        self.ol_board=[]
        self.current_We = self.We

        self.Wi = compute_sum_of_euclidean_distances_between_pads(
            self.parameters.node,
            self.parameters.neighbors,
            self.parameters.eoi,
            ignore_power=self.parameters.ignore_power)
        self.HPWLi = 0
        for net_id in self.parameters.nets:
            self.HPWLi += self.parameters.graph.calc_hpwl_of_net(net_id,
                                                                 True)
        self.current_HPWL = self.HPWLe

        self.all_w = []
        self.all_hpwl = []
        self.all_weighted_cost = []

    def step(self,
             model,
             random:bool=False,
             deterministic:bool =False,
             rl_model_type:str = "TD3"):
        self.steps_done += 1
        state = get_agent_observation(parameters=self.parameters)
        _state = list(state["los"]) + list(state["ol"]) + state["dom"] + state["euc_dist"] + state["position"] + state["ortientation"]+list(state["boardmask"])


        if random is True:
            action = self.action_space.sample()
            if rl_model_type == "TD3":
                model_action = [0,0,0]#action
                model_action[0] = (action[0] - 0.5) * 2
                model_action[1] = (action[1] - np.pi) / np.pi
                model_action[2] = (action[2] - 0.5) * 2
        else:
            if rl_model_type == "TD3":
                 # Action scaling done here, outside of policy.
                if deterministic is True:
                    model_action = model.select_action(np.array(_state))
                else:
                    model_action = (model.select_action(np.array(_state))
                            + np.random.normal(0, self.parameters.max_action * self.parameters.expl_noise, size=3)
                            ).clip(-self.parameters.max_action, self.parameters.max_action)
                # convert action
                action = model_action
                action = (action + 1) / 2  # [-1, 1] => [0, 1]
                action[1] *= (2 * np.pi)

            else: # SAC
                # Action scaling done inside policy
                action = model.select_action(
                    np.array(_state), evaluate=deterministic)

        pos = self.parameters.node.get_pos()
        step_scale = (self.parameters.step_size * action[0])
        x_offset = step_scale*np.cos(-action[1])
        y_offset = step_scale*np.sin(-action[1])
        angle = (np.int0(action[2] * 4) % 4) * 90.0

        self.parameters.node.set_pos(
            tuple([pos[0] + x_offset, pos[1] + y_offset]))
        self.parameters.node.set_orientation(angle)

        next_state = get_agent_observation(parameters=self.parameters)
        reward, done = self.get_reward(next_state)

        if rl_model_type == "TD3":
            return state, next_state, reward, model_action, done
        else:
            return state, next_state, reward, action, done

    def get_reward(self, observation):
        done = False
        self.W.append(compute_sum_of_euclidean_distances_between_pads(
            self.parameters.node,
            self.parameters.neighbors,
            self.parameters.eoi,
            ignore_power=self.parameters.ignore_power))

        hpwl = 0
        for net_id in self.parameters.nets:
            hpwl += self.parameters.graph.calc_hpwl_of_net(net_id, True)

        self.HPWL.append(hpwl)

        if np.sum(observation["ol"]) > 1E-6:
            self.ol_term5.append(
                np.clip((1-np.sum(observation["ol"])/8), 0.0, np.inf))
        else:
            self.ol_term5.append(1)
        if np.sum(observation["boardmask"]) > 1E-6:
            self.ol_board.append(
                np.clip((1-np.sum(observation["ol"])/8), 0.0, np.inf))
        else:
            self.ol_board.append(1)#表示重叠值，重叠越小越接近1    

        if self.W[-1] < self.We and self.ol_term5[-1] == 1:

            if self.parameters.log_file is not None:
                f = open(self.parameters.log_file, "a", encoding="utf-8")
                f.write(f"{datetime.datetime.now().strftime('%Y%m%dT%H%M%S.%f')[:-3]} Agent {self.parameters.node.get_name()} ({self.parameters.node.get_id()}) found a better, legal, wirelength target of {np.round(self.W[-1],6)}, originally {np.round(self.We,6)}.\r\n")
                f.close()

            self.We = self.W[-1]
            self.parameters.node.set_opt_euclidean_distance(self.W[-1])

        if self.HPWL[-1] < self.HPWLe:
            stack = draw_board_from_board_and_graph_multi_agent(
                self.parameters.board,
                self.parameters.graph,
                node_id=self.parameters.node.get_id(),
                padding=4)

            stack_sum = np.zeros((stack[0].shape[0],stack[0].shape[1]),
                                 dtype=np.int)
            for i in range(len(stack)):
                stack_sum += stack[i]

            if np.max(stack_sum) <= 64:
                if self.parameters.log_file is not None:
                    f = open(self.parameters.log_file, "a", encoding="utf-8")
                    f.write(f"{datetime.datetime.now().strftime('%Y%m%dT%H%M%S.%f')[:-3]} Agent {self.parameters.node.get_name()} ({self.parameters.node.get_id()}) found a better, legal, HPWL target of {np.round(self.HPWL[-1],6)}, originally {np.round(self.HPWLe,6)}.\r\n")
                    f.close()

                self.HPWLe = self.HPWL[-1]
                self.parameters.node.set_opt_hpwl(self.HPWL[-1])

        reward = 0

        numer = self.Wi - self.W[-1]
        denom = self.Wi - self.current_We
        if abs(denom) < 1e-8:
            x = -1.0 if numer < 0 else 1.0
        else:
            x = np.clip(numer / denom, -1.0, 1.0)
        y = np.clip(
            (self.HPWLi - self.HPWL[-1]) / (self.HPWLi - self.current_HPWL),
             -1, 1)
        self.all_w.append(x)
        self.all_hpwl.append(y)
        self.all_weighted_cost.append( (self.n*x + self.m*self.ol_term5[-1] + self.p*y+self.m*self.ol_board[-1])/(self.n+self.m+self.p) )

        reward = np.tan((self.n*x + self.m*self.ol_term5[-1] + self.p*y+self.m*self.ol_board[-1])/(self.n+2*self.m+self.p) * np.pi/2.1  )

        if ((observation["position"][0] > 1) or
            (observation["position"][0] < 0) or
            (observation["position"][1] > 1) or
            (observation["position"][1] < 0)) and ((np.sum(observation["ol"])/8) == 1)or (np.sum(observation["boardmask"])/8):
            reward -= (self.max_steps-self.steps_done) * self.penalty_per_remaining_step
            done = True

        if self.steps_done==self.max_steps:
            done = True

        return reward, done

    def init_random(self):
        r_pos = self.rng.uniform(low=0.05, high=0.95, size=(2))
        scaled_r_pos = tuple([r_pos[0]*self.parameters.board_width,
                              r_pos[1]*self.parameters.board_height])
        # 0, 90, 180, 270
        scaled_orientation = np.float64(self.rng.integers(4)*90)
        self.parameters.node.set_pos(scaled_r_pos)
        self.parameters.node.set_orientation(scaled_orientation)

    def get_observation_space_shape(self):
        sz = 0
        for _, value in self.observation_space.items():
            sz += value.shape[0]

        return sz

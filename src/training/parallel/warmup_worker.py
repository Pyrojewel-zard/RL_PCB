# -*- coding: utf-8 -*-
from __future__ import annotations
import random
import numpy as np
from typing import Dict, Any

def worker_loop_with_instance(task_q, result_q, env, wid: int, base_seed: int):
    """
    每个子进程的 worker 循环，直接用传进来的 env 实例。
    適配現有的 environment 類接口，而不是標準的 Gym 環境接口。
    """
    # 固定随机数种子，保证可复现
    np.random.seed(base_seed + wid * 7)
    random.seed(base_seed + wid * 11)

    while True:
        try:
            cmd, payload = task_q.get()
        except (EOFError, KeyboardInterrupt):
            break

        if cmd == "stop":
            break
        elif cmd == "rollout":
            n_steps = int(payload)
            batch: Dict[str, Any] = {"S": [], "A": [], "R": [], "S2": [], "D": []}
            
            # 適配現有的 environment 類接口
            env.reset()  # environment.reset() 沒有返回值
            
            # 獲取初始狀態（從第一個 agent 獲取）
            if hasattr(env, 'agents') and len(env.agents) > 0:
                obs = get_agent_observation(env.agents[0].parameters)
                # 轉換為向量格式，匹配訓練數據格式
                s = list(obs["los"]) + list(obs["ol"]) + obs["dom"] + obs["euc_dist"] + obs["position"] + obs["ortientation"] + list(obs["boardmask"])
            else:
                raise RuntimeError("Environment has no agents")

            for _ in range(n_steps):
                # 使用第一個 agent 的 action_space
                if hasattr(env.agents[0], 'action_space'):
                    a = env.agents[0].action_space.sample()
                else:
                    # 如果沒有 action_space，創建一個隨機動作
                    a = np.random.uniform(0, 1, 3)
                    a[1] *= 2 * np.pi  # 角度範圍
                
                # 使用 environment 的 step 方法
                # environment.step() 返回 observation_vec，包含每個 agent 的結果
                try:
                    # environment.step() 需要 model 參數，我們使用 None 表示隨機動作
                    observation_vec = env.step(model=None, random=True)
                    if observation_vec and len(observation_vec) > 0:
                        # 取第一個 agent 的結果
                        obs = observation_vec[0]
                        # obs[1] 是 next_state 字典，需要轉換為向量格式
                        next_state_dict = obs[1]
                        if isinstance(next_state_dict, dict):
                            s2 = list(next_state_dict["los"]) + list(next_state_dict["ol"]) + next_state_dict["dom"] + next_state_dict["euc_dist"] + next_state_dict["position"] + next_state_dict["ortientation"] + list(next_state_dict["boardmask"])
                        else:
                            s2 = obs[1]  # 如果已經是向量格式
                        r = obs[2]   # reward
                        done = obs[4]  # done
                        truncated = False
                        info = obs[5] if len(obs) > 5 else {}
                    else:
                        # 如果沒有結果，創建默認值
                        s2 = s
                        r = 0.0
                        done = True
                        truncated = False
                        info = {}
                except Exception as e:
                    # 如果調用失敗，創建默認值
                    print(f"Warning: environment.step() failed: {e}")
                    s2 = s
                    r = 0.0
                    done = True
                    truncated = False
                    info = {}
                
                batch["S"].append(s)
                batch["A"].append(a)
                batch["R"].append(r)
                batch["S2"].append(s2)
                batch["D"].append(done or truncated)
                s = s2
                
                if done or truncated:
                    env.reset()
                    if hasattr(env, 'agents') and len(env.agents) > 0:
                        obs = get_agent_observation(env.agents[0].parameters)
                        # 轉換為向量格式，匹配訓練數據格式
                        s = list(obs["los"]) + list(obs["ol"]) + obs["dom"] + obs["euc_dist"] + obs["position"] + obs["ortientation"] + list(obs["boardmask"])

            result_q.put((wid, batch))
        else:
            raise ValueError(f"Unknown cmd: {cmd}")

def get_agent_observation(parameters):
    """
    獲取 agent 的觀察狀態，適配現有的接口
    """
    from core.agent.observation import get_agent_observation as get_obs
    return get_obs(parameters)

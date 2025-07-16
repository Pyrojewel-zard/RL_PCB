#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 20 08:28:10 2022

@author: luke
"""

from collections import deque
import numpy as np

class tracker():
    def __init__(self, avg_size, rl_policy_type: str = "TD3"):
        """
        初始化强化学习训练指标跟踪器
        
        Args:
            avg_size (int): 滑动窗口的平均计算大小
            rl_policy_type (str): 强化学习算法类型，支持"TD3"或"SAC"
        """
        self.rl_policy_type=rl_policy_type  # ⭐ 设置强化学习算法类型

        self.avg_size = avg_size

        # 初始化各指标的滑动窗口队列
        self.actor_losses = deque(maxlen=self.avg_size)
        self.critic_losses = deque(maxlen=self.avg_size)
        self.episode_reward = deque(maxlen=self.avg_size)
        self.episode_length = deque(maxlen=self.avg_size)
        self.episode_fps = deque(maxlen=self.avg_size)

        # SAC算法特有的指标
        if self.rl_policy_type == "SAC":
            self.critic_1_loss = deque(maxlen=self.avg_size)
            self.critic_2_loss = deque(maxlen=self.avg_size)
            self.entropy_loss = deque(maxlen=self.avg_size)
            self.entropy = deque(maxlen=self.avg_size)

    def append(self,
               actor_loss,
               critic_loss,
               episode_reward,
               episode_length,
               episode_fps,
               critic_1_loss=None,
               critic_2_loss=None,
               entropy_loss=None,
               entropy=None):
        if actor_loss is not None:
            self.actor_losses.append(actor_loss)
        self.critic_losses.append(critic_loss)
        self.episode_reward.append(episode_reward)
        self.episode_length.append(episode_length)
        self.episode_fps.append(episode_fps)

        if self.rl_policy_type == "SAC" and critic_1_loss is not None:
            self.critic_1_loss.append(critic_1_loss)

        if self.rl_policy_type == "SAC" and critic_2_loss is not None:
            self.critic_2_loss.append(critic_2_loss)

        if self.rl_policy_type == "SAC" and entropy_loss is not None:
            self.entropy_loss.append(entropy_loss)

        if self.rl_policy_type == "SAC" and entropy is not None:
            self.entropy.append(entropy)

    def get_mean(self):
        if len(self.actor_losses) == 0:
            mean_actor_loss = 0
        else:
            mean_actor_loss = np.mean(self.actor_losses)
        return(mean_actor_loss,
               np.mean(self.critic_losses),
               np.mean(self.episode_reward),
               np.mean(self.episode_length),
               np.mean(self.episode_fps))

    def get_most_recent(self):
        if len(self.actor_losses) == 0:
            actor_loss = 0
        else:
            actor_loss = self.actor_losses[-1]
        return(actor_loss,
               self.critic_losses[-1],
               self.episode_reward[-1],
               self.episode_length[-1],
               self.episode_fps[-1])

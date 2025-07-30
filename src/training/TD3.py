import copy
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

import utils
import tracker
import time

# Implementation of Twin Delayed Deep Deterministic Policy Gradients (TD3)
# Paper: https://arxiv.org/abs/1802.09477


class Actor(nn.Module):
    def __init__(self,
                 state_dim,
                 action_dim,
                 max_action,
                 pi : list = [400, 300],
                 activation_fn: str = "relu",
                 device: str = "cuda"
                 ):

        super(Actor, self).__init__()
        self.device = device
        self.pi = nn.Sequential()
        in_size = state_dim
        for layer_sz in pi:
            self.pi.append(nn.Linear(in_size, layer_sz))
            in_size = layer_sz
        self.pi.append(nn.Linear(in_size, action_dim))
        self.max_action = max_action

        if activation_fn == "relu":
            self.activation_fn = F.relu
        elif activation_fn == "tanh":
            self.activation_fn == nn.Tanh

    def forward(self, state):
        x = state
        for i in range(len(self.pi)-1):
            x = self.activation_fn(self.pi[i](x))
        return self.max_action * torch.tanh(self.pi[-1](x))

    def select_action(self, state):
        state = torch.FloatTensor(state.reshape(1, -1)).to(self.device)
        return self.forward(state).cpu().data.numpy().flatten()

class Critic(nn.Module):
    def __init__(self,
                 state_dim,
                 action_dim,
                 qf : list = [400, 300],
                 activation_fn: str = "relu"
                 ):
        super(Critic, self).__init__()

        if activation_fn == "relu":
            self.activation_fn = F.relu
        elif activation_fn == "tanh":
            self.activation_fn == nn.Tanh

        # Q1 architecture
        self.qf1 = nn.Sequential()
        in_size = state_dim + action_dim
        for layer_sz in qf:
            self.qf1.append(nn.Linear(in_size, layer_sz))
            in_size = layer_sz
        self.qf1.append(nn.Linear(in_size, 1))

        # Q2 architecture
        self.qf2 = nn.Sequential()
        in_size = state_dim + action_dim
        for layer_sz in qf:
            self.qf2.append(nn.Linear(in_size, layer_sz))
            in_size = layer_sz
        self.qf2.append(nn.Linear(in_size, 1))

    def forward(self, state, action):
        sa = torch.cat([state, action], 1)

        q1 = sa
        for i in range(len(self.qf1)-1):
            q1 = self.activation_fn(self.qf1[i](q1))
        q1 = self.qf1[-1](q1)

        q2 = sa
        for i in range(len(self.qf2)-1):
            q2 = self.activation_fn(self.qf2[i](q2))
        q2 = self.qf2[-1](q2)

        return q1, q2


    def Q1(self, state, action):
        sa = torch.cat([state, action], 1)

        q1 = sa
        for i in range(len(self.qf1)-1):
            q1 = self.activation_fn(self.qf1[i](q1))
        q1 = self.qf1[-1](q1)
        return q1

class TD3(object):
    def __init__(
        self,
        max_action,
        hyperparameters,
        train_env,
        device:str = "cpu",
        early_stopping:int = 100_000,
        state_dim:int = 23,  # used when a training environment is not supplied
        action_dim:int = 3,  # used when a training environment is not supplied
        verbose: int = 0
    ):
        self.device=device
        if device == "cuda":
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device("cpu")

        if verbose == 1:
            print(f"Model TD3 is configured to device {self.device}")

        self.train_env = train_env
        self.verbose = verbose

        if self.train_env is not None:
            state_dim = self.train_env.agents[0].get_observation_space_shape()
            action_dim = self.train_env.agents[0].action_space.shape[0]

        self.actor = Actor(state_dim,
                           action_dim, max_action,
                           hyperparameters["net_arch"]["pi"],
                           hyperparameters["activation_fn"],
                           device=device).to(self.device)
        self.actor_target = copy.deepcopy(self.actor)
        self.actor_optimizer = torch.optim.Adam(self.actor.parameters(),
                                                lr=hyperparameters["learning_rate"])

        self.critic = Critic(state_dim,
                             action_dim,
                             hyperparameters["net_arch"]["qf"],
                             hyperparameters["activation_fn"]).to(self.device)
        self.critic_target = copy.deepcopy(self.critic)
        self.critic_optimizer = torch.optim.Adam(self.critic.parameters(),
                                                 lr=hyperparameters["learning_rate"])

        self.max_action = max_action
        self.buffer_size = hyperparameters["buffer_size"]
        self.discount = hyperparameters["gamma"]
        self.tau = hyperparameters["tau"]
        self.batch_size = hyperparameters["batch_size"]
        self.policy_noise = hyperparameters["policy_noise"] * self.max_action
        self.noise_clip = hyperparameters["noise_clip"] * self.max_action
        self.policy_freq = hyperparameters["policy_freq"]

        self.replay_buffer = utils.ReplayMemory(hyperparameters["buffer_size"],
                                                device=self.device)
        self.trackr = tracker.tracker(100)

        # Early stopping
        self.early_stopping = early_stopping
        self.exit = False

        self.total_it = 0

    def select_action(self, state):
        state = torch.FloatTensor(state.reshape(1, -1)).to(self.device)
        return self.actor(state).cpu().data.numpy().flatten()

    def train(self, replay_buffer):
        self.total_it += 1

        # Sample replay buffer
        state, action, next_state, reward, not_done = replay_buffer.sample(self.batch_size)

        with torch.no_grad():
            # Select action according to policy and add clipped noise
            noise = (
		    torch.randn_like(action) * self.policy_noise).clamp(
		    -self.noise_clip, self.noise_clip)

            next_action = (
		    self.actor_target(next_state) + noise
			).clamp(-self.max_action, self.max_action)

            # Compute the target Q value
            target_Q1, target_Q2 = self.critic_target(next_state, next_action)
            target_Q = torch.min(target_Q1, target_Q2)
            target_Q = reward + not_done * self.discount * target_Q

        # Get current Q estimates
        current_Q1, current_Q2 = self.critic.forward(state, action)

        # Compute critic loss
        critic_loss = F.mse_loss(current_Q1, target_Q) + F.mse_loss(current_Q2, target_Q)

        # Optimize the critic
        self.critic_optimizer.zero_grad()
        critic_loss.backward()
        self.critic_optimizer.step()

        # Delayed policy updates
        if self.total_it % self.policy_freq == 0:

            # Compute actor losse
            actor_loss = -self.critic.Q1(state, self.actor(state)).mean()

            # Optimize the actor
            self.actor_optimizer.zero_grad()
            actor_loss.backward()
            self.actor_optimizer.step()

            # Update the frozen target models
            for param, target_param in zip(self.critic.parameters(),
                                           self.critic_target.parameters()
                                           ):
                target_param.data.copy_(self.tau * param.data + (1 - self.tau) * target_param.data)

            for param, target_param in zip(self.actor.parameters(),
                                           self.actor_target.parameters()
                                           ):
                target_param.data.copy_(self.tau * param.data + (1 - self.tau) * target_param.data)

            return critic_loss.cpu().detach().numpy(), actor_loss.cpu().detach().numpy()

        return critic_loss.cpu().detach().numpy(), None

    def save(self, filename):
        torch.save(self.critic.state_dict(), filename + "_critic")
        torch.save(self.critic_optimizer.state_dict(),
                   filename + "_critic_optimizer")

        torch.save(self.actor.state_dict(), filename + "_actor")
        torch.save(self.actor_optimizer.state_dict(),
                   filename + "_actor_optimizer")

    def load(self, filename):
        self.critic.load_state_dict(torch.load(filename + "_critic"))
        self.critic_optimizer.load_state_dict(torch.load(filename + "_critic_optimizer"))
        self.critic_target = copy.deepcopy(self.critic)

        self.actor.load_state_dict(torch.load(filename + "_actor"))
        self.actor_optimizer.load_state_dict(torch.load(filename + "_actor_optimizer"))
        self.actor_target = copy.deepcopy(self.actor)

    def explore_for_expert_targets(self,
                                   reward_target_exploration_steps=25_000,
                                   output_dir=None,
                                   save_pcb_every_n_steps=1000):
        """
        在专家目标探索过程中，每隔一定步数保存当前PCB布局到work目录。
        
        Args:
            reward_target_exploration_steps: 探索步数
            output_dir: PCB文件输出目录，如果为None则不保存
            save_pcb_every_n_steps: 每隔多少步保存一次PCB文件
        """
        if self.train_env is None:
            print("Model cannot explore because training envrionment is missing. Please reload model and supply a training envrionment.")
            return

        # 创建PCB输出目录
        pcb_output_dir = None
        if output_dir is not None:
            import os
            from pathlib import Path
            pcb_output_dir = os.path.join(output_dir, "explore_pcb")
            Path(pcb_output_dir).mkdir(parents=True, exist_ok=True)
            if self.verbose > 0:
                print(f"PCB文件将保存到: {pcb_output_dir}")

        self.done = False
        step_count = 0
        
        for t in range(reward_target_exploration_steps):
            obs_vec = self.train_env.step(self.actor, random=True)

            step_count += 1

            # 每隔指定步数保存PCB文件
            if (pcb_output_dir is not None and 
                step_count % save_pcb_every_n_steps == 0):
                try:
                    filename = f"explore_step_{step_count}.pcb"
                    self.train_env.write_current_pcb_file(
                        path=pcb_output_dir,
                        filename=filename
                    )
                    if self.verbose > 0:
                        print(f"💾 已保存探索PCB文件: {filename} (步数: {step_count})")
                except Exception as e:
                    if self.verbose > 0:
                        print(f"保存PCB文件时出错: {e}")

            for indiv_obs in obs_vec:
                if indiv_obs[4] is True:
                    self.done = True

            if self.done:
                self.train_env.reset()
                self.done = False
                #env.tracker.create_video()
                self.train_env.tracker.reset()
                # 环境重置时也保存一次PCB文件
                if pcb_output_dir is not None:
                    try:
                        filename = f"explore_reset_{step_count}.pcb"
                        self.train_env.write_current_pcb_file(
                            path=pcb_output_dir,
                            filename=filename
                        )
                        if self.verbose > 0:
                            print(f"💾 环境重置时保存PCB文件: {filename}")
                    except Exception as e:
                        if self.verbose > 0:
                            print(f"重置时保存PCB文件出错: {e}")

        self.train_env.reset()
        self.done = False

    def learn(self,
              timesteps,
              callback,
              start_timesteps=25_000,
              incremental_replay_buffer = None):

        if self.train_env is None:
            print("Model cannot explore because training envrionment is\
                  missing. Please reload model and supply a training envrionment.")
            return

        next_update_at = self.buffer_size*2

        episode_reward = 0
        episode_timesteps = 0
        self.episode_num = 0

        callback.on_training_start()

        self.train_env.reset()
        self.done = False
        start_time = time.clock_gettime(time.CLOCK_REALTIME)

        episode_start_time = start_time

        for t in range(1,int(timesteps)+1):
            self.num_timesteps = t

            episode_timesteps += 1
            if t < start_timesteps:
                obs_vec = self.train_env.step(model=self.actor, random=True)
            else:
                obs_vec = self.train_env.step(model=self.actor, random=False)

            all_rewards = []
            for indiv_obs in obs_vec:
                if indiv_obs[4] is True:
                    self.done = True
                all_rewards.append(indiv_obs[2])
                transition = (indiv_obs[0], indiv_obs[3], indiv_obs[1], indiv_obs[2], 1. -indiv_obs[4])
                self.replay_buffer.add(*transition)

            episode_reward += float(np.mean(np.array(all_rewards)))

            if t >= start_timesteps:
                critic_loss, actor_loss = self.train(self.replay_buffer)

            if self.done:
                episode_finish_time = time.clock_gettime(time.CLOCK_REALTIME)
                if t < start_timesteps:
                    self.trackr.append(actor_loss=0,
                                       critic_loss=0,
                                       episode_reward=episode_reward,
                                       episode_length = episode_timesteps,
                                       episode_fps = episode_timesteps / (episode_finish_time - episode_start_time))
                else:
                    self.trackr.append(actor_loss=actor_loss,
                           critic_loss=critic_loss,
                           episode_reward=episode_reward,
                           episode_length = episode_timesteps,
                           episode_fps = episode_timesteps / (episode_finish_time - episode_start_time))

            callback.on_step()
            if self.done:
                self.train_env.reset()
                self.done = False
                episode_reward = 0
                episode_timesteps = 0
                self.episode_num += 1
                self.train_env.tracker.reset()
                episode_start_time = time.clock_gettime(time.CLOCK_REALTIME)

            # Early stopping
            if self.exit is True:
                print(f"Early stopping mechanism triggered at timestep=\
                      {self.num_timesteps} after {self.early_stopping} steps\
                       without improvement ... Learning terminated.")
                break

            if incremental_replay_buffer is not None:
                if t >= next_update_at:
                    if incremental_replay_buffer == "double":
                        self.buffer_size *= 2
                        next_update_at += self.buffer_size * 2
                    elif incremental_replay_buffer == "triple":
                        self.buffer_size *= 3
                        next_update_at += self.buffer_size# * 3
                    elif incremental_replay_buffer == "quadruple":
                        self.buffer_size *= 4
                        next_update_at += self.buffer_size# * 3

                    old_replay_buffer = self.replay_buffer
                    self.replay_buffer = utils.ReplayMemory(self.buffer_size,
                                                            device=self.device)
                    self.replay_buffer.add_content_of(old_replay_buffer)

                    print(f"Updated replay buffer at timestep {t};\
                           replay_buffer_size={self.buffer_size},\
                           len={self.replay_buffer.__len__()}\
                           next_update_at={next_update_at}")

        callback.on_training_end()

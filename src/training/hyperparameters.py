#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 31 18:47:01 2022

@author: luke
"""

import optuna
import json
from typing import Dict, Any
import sys

# 策略网络层数范围
hp_opt_pi_layers_min = 1
hp_opt_pi_layers_max = 3
# 价值函数网络层数范围
hp_opt_vf_layers_min = 1
hp_opt_vf_layers_max = 3
# Q函数网络层数范围
hp_opt_qf_layers_min = 1
hp_opt_qf_layers_max = 3

# 策略网络神经元数量范围
hp_opt_pi_neurons_min = 16
hp_opt_pi_neurons_max = 512
# 价值函数网络神经元数量范围
hp_opt_vf_neurons_min = 16
hp_opt_vf_neurons_max = 512
# Q函数网络神经元数量范围
hp_opt_qf_neurons_min = 16
hp_opt_qf_neurons_max = 512

def set_user_attributes(study: optuna.Study):
    '''
    将预定义的超参数范围设置为Optuna研究的用户属性，便于后续分析和报告生成。

    Args:
        study (optuna.Study): Optuna研究实例，用于存储超参数优化过程。

    Returns:
        None: 无返回值，直接修改输入的study对象。
    '''
    study.set_user_attr("hp_opt_pi_layers_min", hp_opt_pi_layers_min)  # ⭐ 设置策略网络最小层数属性
    study.set_user_attr("hp_opt_pi_layers_max", hp_opt_pi_layers_max)
    study.set_user_attr("hp_opt_vf_layers_min", hp_opt_vf_layers_min)
    study.set_user_attr("hp_opt_vf_layers_max", hp_opt_vf_layers_max)
    study.set_user_attr("hp_opt_qf_layers_min", hp_opt_qf_layers_min)
    study.set_user_attr("hp_opt_qf_layers_max", hp_opt_qf_layers_max)
    study.set_user_attr("hp_opt_pi_neurons_min", hp_opt_pi_neurons_min)
    study.set_user_attr("hp_opt_pi_neurons_max", hp_opt_pi_neurons_max)
    study.set_user_attr("hp_opt_vf_neurons_min", hp_opt_vf_neurons_min)
    study.set_user_attr("hp_opt_vf_neurons_max", hp_opt_vf_neurons_max)
    study.set_user_attr("hp_opt_qf_neurons_min", hp_opt_qf_neurons_min)
    study.set_user_attr("hp_opt_qf_neurons_max", hp_opt_qf_neurons_max)

def gen_default_hyperparameters(on_policy=False):
    """
    生成默认的强化学习超参数字典，根据策略类型(on_policy)调整网络架构和激活函数。

    Args:
        on_policy (bool): 是否为on-policy算法，默认为False（off-policy）

    Returns:
        dict: 包含完整超参数配置的字典，包括：
              - 学习率(learning_rate)
              - 经验回放缓冲区大小(buffer_size)
              - 采样步数(n_steps)
              - 批量大小(batch_size)
              - 折扣因子(gamma)
              - 网络架构(net_arch)
              - 激活函数类型(activation_fn)
              - 以及其他算法特定参数
    """
    default_hyperparameters = {
        "learning_rate": 0.001,
        "buffer_size": 1_000_000,
        "n_steps": 2048,
        "batch_size": 128,
        "gamma": 0.99,
        "net_arch": {},
        "activation_fn": "relu",
        # Added for contsistency between all hyperparameter generator functions
        "train_freq": 1,                   # trains at the end of the episode
        "gradient_steps": 1,               # trains at the end of the episode
        # Added for multi-agent
        "tau": 0.005,                      # Target network update rate
        # Noise added to target policy during critic update
        "policy_noise": 0.2,
        "noise_clip": 0.5,                 # Range to clip target policy noise
        "policy_freq": 2,                  # Frequency of delayed policy updates
        }

    if on_policy is True:
        default_hyperparameters["net_arch"] = [dict(pi=[32, 32, 128, 64, 64],  # ⭐ 设置on-policy算法的分层网络结构
                                                    vf=[64, 128, 64])]
        default_hyperparameters["activation_fn"] = "tanh"
    else:
        default_hyperparameters["net_arch"] = dict(pi=[400,300], qf=[400,300])  # ⭐ 设置off-policy算法的双网络结构

    return default_hyperparameters

def gen_default_sb3_hyperparameters(algo:str, max_steps:int):
    """
    为指定的强化学习算法生成默认的超参数配置。

    Args:
        algo (str): 算法名称，支持TRPO/PPO/TD3/SAC等
        max_steps (int): 最大训练步数，用于某些算法的特定参数设置

    Returns:
        dict: 包含完整超参数配置的字典

    Raises:
        SystemExit: 当输入不支持的算法名称时终止程序
    """
    if algo in ("TRPO", "PPO"):
        default_hyperparameters = gen_default_hyperparameters(on_policy=True)  # ⭐ 根据策略类型生成基础超参数
    else:
        default_hyperparameters = gen_default_hyperparameters(on_policy=False)

    if algo == "TRPO":
        default_hyperparameters["learning_rate"] = 0.001
        default_hyperparameters["n_steps"] = 2048
        default_hyperparameters["batch_size"] = 128

    elif algo == "PPO":
        default_hyperparameters["learning_rate"] = 0.0003
        default_hyperparameters["n_steps"] = 2048
        default_hyperparameters["batch_size"] = 64
    elif algo == "TD3":
        default_hyperparameters["learning_rate"] = 0.001
        default_hyperparameters["buffer_size"] = 1_000_000
        default_hyperparameters["batch_size"] = 100
        default_hyperparameters["train_freq"] = max_steps
        default_hyperparameters["gradient_steps"] = max_steps
        default_hyperparameters["tau"] = 0.005
        default_hyperparameters["policy_noise"] = 0.2
        default_hyperparameters["noise_clip"] = 0.5
        default_hyperparameters["policy_freq"] = 2

    elif algo == "SAC":
        default_hyperparameters["learning_rate"] = 0.0003
        default_hyperparameters["buffer_size"] = 1_000_000
        default_hyperparameters["batch_size"] = 256
        default_hyperparameters["train_freq"] = 1
        default_hyperparameters["gradient_steps"] = 1
    else:
        print(f"Algorithm {algo} is not supported. Progam terminating.")
        sys.exit()

    # common settings
    default_hyperparameters["gamma"] = 0.99  # ⭐ 设置所有算法共用的折扣因子

    if algo in ("TRPO", "PPO"):
        default_hyperparameters["net_arch"] = [dict(pi=[32, 32, 128, 64, 64],
                                                     vf=[64, 128, 64])]
        default_hyperparameters["activation_fn"] = "tanh"
    else:
        default_hyperparameters["net_arch"] = dict(pi=[400,300], qf=[400,300])
        default_hyperparameters["activation_fn"] = "relu"

    return default_hyperparameters

def sample_hyperparameters(trial: optuna.Trial,
                           on_policy=False) -> Dict[str, Any]:
    """
    通过Optuna试验对象采样强化学习模型的超参数配置。

    Args:
        trial (optuna.Trial): Optuna试验对象，用于超参数优化
        on_policy (bool): 是否为on-policy算法，默认为False

    Returns:
        Dict[str, Any]: 包含网络架构和激活函数的超参数字典
    """
    # 采样策略网络参数
    pi_layers = trial.suggest_int("pi_layers",
                                  hp_opt_pi_layers_min,
                                  hp_opt_pi_layers_max)
    pi_n_units_l = []
    for i in range(pi_layers):
        pi_n_units_l.append(trial.suggest_int("pi_n_units_l{}".format(i),
                                              hp_opt_pi_neurons_min,
                                              hp_opt_pi_neurons_max))  # ⭐ 采样每层神经元数量

    if on_policy is True:
        # on-policy算法采样价值函数网络
        vf_layers = trial.suggest_int("vf_layers",
                                      hp_opt_vf_layers_min,
                                      hp_opt_vf_layers_max)
        vf_n_units_l = []
        for i in range(vf_layers):
            vf_n_units_l.append(trial.suggest_int("vf_n_units_l{}".format(i),
                                                  hp_opt_vf_neurons_min,
                                                  hp_opt_vf_neurons_max))

        net_arch = [{"pi": pi_n_units_l, "vf": vf_n_units_l}]  # ⭐ 构建on-policy网络架构
    else: # off_policy
        # off-policy算法采样Q函数网络
        qf_layers = trial.suggest_int("qf_layers",
                                      hp_opt_qf_layers_min,
                                      hp_opt_qf_layers_max)
        qf_n_units_l = []
        for i in range(qf_layers):
            qf_n_units_l.append(trial.suggest_int("qf_n_units_l{}".format(i),
                                                  hp_opt_qf_neurons_min,
                                                  hp_opt_qf_neurons_max))

        net_arch = {"pi": pi_n_units_l, "qf": qf_n_units_l}  # ⭐ 构建off-policy网络架构

    # 采样激活函数类型
    activation_fn = trial.suggest_categorical("activation_fn",
                                              ["tanh", "relu"])

    hyperparameters = gen_default_hyperparameters()
    hyperparameters["net_arch"] = net_arch
    hyperparameters["activation_fn"] = activation_fn  # ⭐ 最终整合超参数配置

    return hyperparameters

def sample_hyperparameters_nas( trial: optuna.Trial,
                               algo:str,
                               max_steps:int ) -> Dict[str, Any]:
    """
    使用Optuna试验对象采样神经网络架构的超参数，适用于不同强化学习算法。

    Args:
        trial (optuna.Trial): Optuna试验对象，用于采样超参数
        algo (str): 强化学习算法名称（如"TRPO"/"PPO"/off-policy算法）
        max_steps (int): 最大训练步数

    Returns:
        Dict[str, Any]: 包含网络架构和超参数的字典，包括：
            - net_arch: 策略网络和价值函数网络的结构
            - activation_fn: 激活函数类型
            - 其他算法默认超参数
    """
    pi_layers = trial.suggest_int("pi_layers",
                                  hp_opt_pi_layers_min,
                                  hp_opt_pi_layers_max)
    pi_n_units_l = []
    for i in range(pi_layers):
        pi_n_units_l.append(trial.suggest_int("pi_n_units_l{}".format(i),
                                              hp_opt_pi_neurons_min,
                                              hp_opt_pi_neurons_max))  # ⭐ 采样策略网络每层的神经元数量

    if algo in ("TRPO", "PPO"):
        vf_layers = trial.suggest_int("vf_layers",
                                      hp_opt_vf_layers_min,
                                      hp_opt_vf_layers_max)
        vf_n_units_l = []
        for i in range(vf_layers):
            vf_n_units_l.append(trial.suggest_int("vf_n_units_l{}".format(i),
                                                  hp_opt_vf_neurons_min,
                                                  hp_opt_vf_neurons_max))

        net_arch = [{"pi": pi_n_units_l, "vf": vf_n_units_l}]  # ⭐ 构建on-policy算法的网络架构
    else: # off_policy
        qf_layers = trial.suggest_int("qf_layers",
                                      hp_opt_qf_layers_min,
                                      hp_opt_qf_layers_max)
        qf_n_units_l = []
        for i in range(qf_layers):
            qf_n_units_l.append(trial.suggest_int("qf_n_units_l{}".format(i),
                                                  hp_opt_qf_neurons_min,
                                                  hp_opt_qf_neurons_max))

        net_arch = {"pi": pi_n_units_l, "qf": qf_n_units_l}  # ⭐ 构建off-policy算法的网络架构

    activation_fn = trial.suggest_categorical("activation_fn", ["tanh", "relu"])  # ⭐ 采样激活函数类型

    hyperparameters = gen_default_sb3_hyperparameters(algo=algo,
                                                      max_steps=max_steps)
    hyperparameters["net_arch"] = net_arch
    hyperparameters["activation_fn"] = activation_fn

    return hyperparameters

def sample_hyperparameters_hp( trial: optuna.Trial,
                              algo:str,
                              max_steps:int,
                              base_hyperparameters:str=None) -> Dict[str, Any]:
    """
    使用Optuna试验对象采样强化学习算法的超参数。

    Args:
        trial (optuna.Trial): Optuna试验对象，用于超参数优化
        algo (str): 使用的强化学习算法名称（如"PPO"、"TRPO"等）
        max_steps (int): 训练的最大步数
        base_hyperparameters (str, optional): 基础超参数文件路径。默认为None。

    Returns:
        Dict[str, Any]: 包含所有优化后超参数的字典
    """
    if base_hyperparameters is None:
        hyperparameters = gen_default_sb3_hyperparameters(algo=algo,
                                                          max_steps=max_steps)
    else:
        hyperparameters = load_hyperparameters_from_file(base_hyperparameters)

    if algo in ("TRPO", "PPO"):
        learning_rate = trial.suggest_float("learning_rate",
                                            1e-5, 1e-2,
                                            log=True)  # ⭐ 采样学习率（对数尺度）
        batch_size = trial.suggest_categorical("batch_size",
                                               [32, 64, 128, 256, 512, 1024])
        n_steps = trial.suggest_int("n_steps",
                                    512, 4096,
                                    step=256) # 14 intervals

        hyperparameters["n_steps"] = n_steps

        pass
    else:
        learning_rate = trial.suggest_float("learning_rate",
                                            1e-5, 1e-2,
                                            log=True)
        buffer_size = trial.suggest_int("buffer_size",
                                        300_000, 3_000_000,
                                        step=300_000)
        batch_size = trial.suggest_categorical("batch_size",
                                               [32, 64, 128, 256, 512, 1024])
        # trains after every "train_freq" steps
        train_freq = trial.suggest_categorical("train_freq",
                                               [1, 2, 4, 8, 16, 32, 64, 128, 256])

        hyperparameters["learning_rate"] = learning_rate
        hyperparameters["buffer_size"] = buffer_size
        hyperparameters["train_freq"] = train_freq
        hyperparameters["gradient_steps"] = train_freq

    # common hyperparameters
    hyperparameters["learning_rate"] = learning_rate  # ⭐ 设置通用超参数：学习率
    hyperparameters["batch_size"] = batch_size

    return hyperparameters

def load_hyperparameters_from_file(filename):
    """
    从指定的JSON文件中加载超参数配置。

    Args:
        filename (str): 包含超参数配置的JSON文件路径。

    Returns:
        dict: 包含超参数配置的Python字典。
    """
    fp = open(filename, "r", encoding="utf-8")
    hyperparameters = json.load(fp)  # ⭐ 核心代码：将JSON文件内容解析为Python字典
    return hyperparameters

def save_hyperparameters_to_file(filename, hyperparameters):
    """
    将超参数字典保存为JSON格式的文件。

    Args:
        filename (str): 要保存的目标文件名（包含路径）
        hyperparameters (dict): 包含超参数的字典对象

    Returns:
        None
    """
    # Write default_hyperparameters dict to a json file
    with open(filename, "w", encoding="utf-8") as fp:
        json.dump(hyperparameters, fp)  # ⭐ 核心操作：将字典序列化为JSON格式写入文件

def save_best_hyperparameters(filename: str,
                              study:optuna.Study,
                              on_policy: bool = False):
    hyperparameters = gen_default_hyperparameters(on_policy=on_policy)

    best_params = study.best_params

    pi_n_units_l = []
    for i in range(best_params["pi_layers"]):
        pi_n_units_l.append(best_params[f"pi_n_units_l{i}"])

    if on_policy is True:
        vf_n_units_l = []
        for i in range(best_params["vf_layers"]):
            vf_n_units_l.append(best_params[f"vf_n_units_l{i}"])

        net_arch = [{"pi": pi_n_units_l, "vf": vf_n_units_l}]
    else:
        qf_n_units_l = []
        for i in range(best_params["qf_layers"]):
            qf_n_units_l.append(best_params[f"qf_n_units_l{i}"])

        net_arch = {"pi": pi_n_units_l, "qf": qf_n_units_l}

    hyperparameters["activation_fn"] = best_params["activation_fn"]
    hyperparameters["net_arch"] = net_arch

    save_hyperparameters_to_file(filename=filename,
                                 hyperparameters=hyperparameters)

    # Write default_hyperparameters dict to a json file
    with open(filename, "w", encoding="utf-8") as fp:
        json.dump(hyperparameters, fp)

def save_best_hyperparameters_hp(filename: str,
                                 study:optuna.Study,algo: str,
                                 max_steps: int):
    """
    保存Optuna优化后的最佳超参数到指定文件，根据算法类型自动适配不同参数结构。

    Args:
        filename (str): 要保存的目标文件名
        study (optuna.Study): 已完成超参数优化的Optuna study对象
        algo (str): 强化学习算法名称（如"PPO"、"TRPO"等）
        max_steps (int): 最大训练步数

    Returns:
        None: 结果直接保存到文件，无返回值
    """
    hyperparameters = gen_default_sb3_hyperparameters(algo=algo,
                                                      max_steps=max_steps)

    best_params = study.best_params
    hyperparameters["learning_rate"] = best_params["learning_rate"]  # ⭐ 更新学习率为最优值
    hyperparameters["batch_size"] = best_params["batch_size"]

    if algo in ("TRPO", "PPO"):
        hyperparameters["n_steps"] = best_params["n_steps"]  # ⭐ on-policy算法特有参数更新
    else:
        hyperparameters["buffer_size"] = best_params["buffer_size"]
        hyperparameters["train_freq"] = best_params["train_freq"]
        hyperparameters["gradient_steps"] = best_params["train_freq"]

    save_hyperparameters_to_file(filename=filename,
                                 hyperparameters=hyperparameters)

    # Write default_hyperparameters dict to a json file
    with open(filename, "w", encoding="utf-8") as fp:
        json.dump(hyperparameters, fp)  # ⭐ 将最终超参数写入json文件

def hyperparmeters_on_policy(hyperparameters):
    '''
    Method to test whether the given hyperparameters correspond to an on_policy
    or off_policy algorithm. The neural network architecture description of an
    on_policy algorithm is stored as a python list by stable baselines3

    :param hyperparameters: hyperparameters dictionary
    :type hyperparameters: dictionary
    :return: True if hyperparameters correspond to an on-policy algorithm,\
          false otherwise
    :rtype: bool

    '''
    if type(hyperparameters["net_arch"]) == list:  # ⭐ 核心判断逻辑：通过检查net_arch是否为列表类型来确定是否为on-policy算法
        return True
    else:
        return False

def hyperparmeters_off_policy(hyperparameters):
    '''
    判断给定的超参数是否对应off-policy算法（通过检查神经网络架构是否为字典类型）

    Args:
        hyperparameters (dict): 包含算法配置的超参数字典，其中"net_arch"键表示神经网络架构

    Returns:
        bool: 如果神经网络架构是字典类型（off-policy算法特征）返回True，否则返回False

    '''
    if type(hyperparameters["net_arch"]) == dict:  # ⭐ 核心判断：off-policy算法的神经网络架构以字典形式存储
        return True
    else:
        return False

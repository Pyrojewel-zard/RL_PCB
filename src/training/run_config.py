#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 10 11:57:27 2022

@author: luke
"""

import argparse
import numpy as np
from datetime import datetime
import torch
import pcb.pcb as pcb
import graph.graph as graph

def cmdline_args():
    parser = argparse.ArgumentParser(
        description="unified argument parser for pcb component training",
        usage="<script-name> -p <pcb_file> --rl_model_type [TD3 | SAC]",
        epilog="This text will be shown after the help")

    # Policy name (TD3 os SAC)
    parser.add_argument("--policy", default="TD3")
    # Sets Gym, PyTorch and Numpy seeds
    parser.add_argument("-s", "--seed", required=False, nargs="+",
                        type=np.uint32, default=None)
    # Time steps initial random policy is used
    parser.add_argument("--start_timesteps", default=25e3, type=int)
    # Max time steps to run environment (1e6)
    parser.add_argument("--max_timesteps", default=1e6, type=int)
    parser.add_argument("--target_exploration_steps", default=10e3, type=int)
    # Save model and optimizer parameters
    parser.add_argument("--save_model", action="store_true")
    # Model load file name, "" doesn't load, "default" uses file_name
    parser.add_argument("--load_model", default="")
    parser.add_argument(
        "--expert_model", default=None,
        help="path to expert model used in expert parameter exploration.")
    parser.add_argument("-w", required=False, type=np.float32, default=1.0)
    parser.add_argument("--hpwl", required=False, type=np.float32, default=1.0)
    parser.add_argument("-o", required=False, type=np.float32, default=1.0)
    parser.add_argument("--training_pcb", required=False, default=None)
    parser.add_argument("--evaluation_pcb", required=False, default=None)
    # log_dir is assigned to be equal to tensoboard_dir
    parser.add_argument("--tensorboard_dir", required=False,
                        default="./tensorboard")
    parser.add_argument("--incremental_replay_buffer",
                        choices=[None, "double", "triple", "quadruple"],
                        default=None, required=False)
    parser.add_argument("--device", default="cuda", choices=["cuda", "cpu"],
                        required=False)
    parser.add_argument("--experiment", required=False, type=str, default=None,
                        help="descriptive experiment name")
    parser.add_argument("--hyperparameters", required=False, type=str,
                        default=None, help="path to a hyperparameters file.")
    parser.add_argument("--runs", required=False, type=np.int32, default=1,
                        help="Number of times to run the experiment.")
    parser.add_argument(
        "--auto_seed", required=False, action="store_true", default=False,
        help="ignore seed value and generate one based of the current time\
              for everyrun")
    parser.add_argument("--workers", required=False, type=int, default=2,
                        help="number of workers on which 'runs' will execute.")
    parser.add_argument("--verbose", required=False, type=int, default=0,
                        help="Program verbosity")
    # How often (time steps) we evaluate
    parser.add_argument("--evaluate_every", required=False,
                        type=np.uint32, default=250000)
    parser.add_argument(
        "--early_stopping", required=False, type=int, default=None,
        help="If no improvement occurs after <early_stopping> steps, then\
              learning will terminate early. Mean episode reward computed\
                  over the last 100 episodes is used for comparision")
    parser.add_argument("--shuffle_training_idxs", required=False,
                        action="store_true", default=False,
                        help="shuffle agent idxs during training")
    parser.add_argument("--shuffle_evaluation_idxs", required=False,
                        action="store_true", default=False,
                        help="shuffle agent idxs during evaluation")
    parser.add_argument(
        "--pcb_idx", required=False, default=-1, type=int,
        help="When supplied the particular pcb is used for training")
    parser.add_argument("--redirect_stdout", required=False,
                        action="store_true", default=False,
                        help="redirect standard output to file")
    parser.add_argument("--redirect_stderr", required=False,
                        action="store_true", default=False,
                        help="redirect standard error to file")

    args = parser.parse_args()

    settings = {}
    settings["default_seed"] = args.seed

    configure_seed(args)

    settings["policy"] = args.policy
    # For backward compatibility.
    settings["rl_model_type"] = args.policy
    settings["seed"] = args.seed
    settings["start_timesteps"] = args.start_timesteps
    settings["max_timesteps"] = args.max_timesteps
    # For backward compatibility.
    settings["max_steps"] = args.max_timesteps
    settings["target_exploration_steps"] = args.target_exploration_steps
    settings["save_model"] = args.save_model
    settings["load_model"] = args.load_model
    settings["expert_model"] = args.expert_model
    settings["w"] = args.w
    settings["hpwl"] = args.hpwl
    settings["o"] = args.o
    settings["training_pcb"] = args.training_pcb
    settings["evaluation_pcb"] = args.evaluation_pcb
    settings["tensorboard_dir"] = args.tensorboard_dir
    settings["incremental_replay_buffer"] = args.incremental_replay_buffer

    if args.device == "cuda":
        settings["device"] = "cuda" if torch.cuda.is_available() else "cpu"
    else:
        print("Warning the command line argument specified a CUDA device,\
               but none were found. Using CPU.")
        settings["device"] = "cpu"

    settings["experiment"] = args.experiment
    settings["hyperparameters"] = args.hyperparameters
    settings["runs"] = args.runs
    settings["auto_seed"] = args.auto_seed
    settings["workers"] = args.workers
    settings["run_name"] = datetime.now().strftime("%s")
    settings["verbose"] = args.verbose

    settings["evaluate_every"] = args.evaluate_every
    if args.early_stopping is None:
        settings["early_stopping"] = args.max_timesteps
    else:
        settings["early_stopping"] = args.early_stopping
    settings["shuffle_training_idxs"] = args.shuffle_training_idxs
    settings["shuffle_evaluation_idxs"] = args.shuffle_evaluation_idxs
    settings["pcb_idx"] = args.pcb_idx
    settings["redirect_stdout"] = args.redirect_stdout
    settings["redirect_stderr"] = args.redirect_stderr

    return args, settings

def configure_seed(args):
    """
    配置随机种子，根据auto_seed参数决定使用自动生成种子还是用户提供的种子。

    Args:
        args (argparse.Namespace): 包含配置参数的对象，需要包含以下属性：
            - auto_seed (bool): 是否自动生成随机种子
            - seed (list[int]): 用户提供的种子列表
            - runs (int): 需要运行的次数

    功能说明：
        1. 当auto_seed为True时，会覆盖用户提供的种子值
        2. 当种子未提供或数量不匹配时，使用固定种子(99)生成随机种子
    """
    if (args.auto_seed is True) and (args.seed is not None):
        if len(args.seed) == args.runs:
            print("auto_seed is enabled while a valid seed configuration was\
                   provided. auto_seed takes precedence and will override the\
                   provided seed values.")

    # assign run seed values randomly based of an rng seed with current time.
    if args.auto_seed is True:
        args.seed = []
        rng = np.random.default_rng(seed=int(datetime.now().strftime("%s")))  # ⭐ 使用当前时间作为随机种子生成器的基础
        for _ in range(args.runs):
            args.seed.append(np.int0(rng.uniform(low=0,high=np.power(2,32)-1)))
    else:
        # seed value is not provided or not provided correctly
        if (args.seed is None) or (len(args.seed) != args.runs):
            # issue a warning
            rng = np.random.default_rng(seed=99)  # ⭐ 使用固定种子99作为后备方案
            args.seed = []
            for _ in range(args.runs):
                args.seed.append(
                    np.int0(rng.uniform(low=0,high=(np.power(2,32)-1)))
                    )

def write_desc_log(full_fn: str, settings: dict,
                   hyperparameters: dict = None,
                   model = None):
    """
    将训练配置信息写入日志文件，包括设置参数、超参数、模型架构和依赖信息。

    Args:
        full_fn (str): 日志文件的完整路径
        settings (dict): 训练配置参数字典
        hyperparameters (dict, optional): 训练超参数字典. Defaults to None.
        model (optional): 训练模型对象. Defaults to None.
    """
    f = open(full_fn, "w", encoding="utf-8")
    f.write("\n================== settings ==================\r\n")
    for key,value in settings.items():
        f.write(f"{key} -> {value}\r\n")  # ⭐ 写入所有设置参数到日志文件

    if hyperparameters is not None:
        f.write("\n================== hyperparameters ==================\r\n")
        for key,value in hyperparameters.items():
            f.write(f"{key} -> {value}\r\n")

    if model is not None:
        f.write(f"\n================== {settings['rl_model_type']} Model Architecture ==================\r\n")
        f.write("Actor\n")
        if settings["rl_model_type"] == "TD3":
            f.write(str(model.actor))  # ⭐ 写入TD3模型的Actor网络结构
        else: # SAC
            f.write(str(model.policy))  # ⭐ 写入SAC模型的策略网络结构
        f.write("\n\n")
        f.write("Critic\n")
        f.write(str(model.critic))
        f.write("\n\n")
        f.write("Critic target\n")
        f.write(str(model.critic_target))
        f.write("\n\n")
        f.write(f"Activation function : {str(model.critic.activation_fn)}")
        f.write("\n\n")

    f.write("\n================== Dependency Information ==================\r\n")
    # Strip leading and trailing newline ('\n') characters.
    f.write(pcb.build_info_as_string()[1:-1])  # ⭐ 写入PCB组件依赖信息
    f.write(graph.build_info_as_string())

    f.close()

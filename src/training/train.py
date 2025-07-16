"""
This module is the main script for running the training of an agent using a
policy on a PCB routing environment. It imports several modules such as
environment, parameters, numpy, torch, sys, and os.

It defines several functions such as setup_seed, program_info,
log_configuration, training_run, and main. The setup_seed function sets the
seed for numpy and torch random number generators, while program_info prints
the device being used. The log_configuration function logs the training
configuration to a tensorboard file, while training_run sets up the
environment and model, trains the model, and returns the best metrics.
Finally, main reads command line arguments, performs multiple training runs,
and prints the average of the best rewards and steps for each run.

To run this script, execute the main function.
"""

from core.environment.environment import environment
from core.environment.parameters import parameters

import numpy as np
import torch
import sys
import os 
import random

from run_config import cmdline_args, write_desc_log
from hyperparameters import load_hyperparameters_from_file
from model_setup import setup_model
from callbacks import log_and_eval_callback

best_reward = -np.inf          # New best model, you could save the agent here

def setup_seed(seed):
    # 确保seed是支持的类型 (None, int, float, str, bytes, bytearray)
    if seed is not None and not isinstance(seed, (int, float, str, bytes, bytearray)):
        seed = int(seed)  # 或者使用其他合适的转换方式

    # 设置随机种子
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)

        if torch.cuda.is_available():
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False

def program_info(device):
    """
    设置并显示程序运行的设备信息，自动选择可用的计算设备（CPU或CUDA）。
    """
    if device == "cuda":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # 添加CUDA可用性检查
        if torch.cuda.is_available():
            print("✅ CUDA is available and will be used")
            print(f"GPU Device: {torch.cuda.get_device_name(0)}")
        else:
            print("⚠️ CUDA is not available, falling back to CPU")
    else:
        device = torch.device("cpu")
        print("ℹ️ Using CPU as specified")

    print(f"using {device}")
    return device  # 建议添加返回值


def log_configuration(writer, args=None, cmdline_args=None, global_step=1):
    """
    将配置参数和命令行参数记录到TensorBoard的writer中。

    Args:
        writer (SummaryWriter): TensorBoard的SummaryWriter对象，用于记录数据。
        args (object, optional): 配置参数对象，通常包含训练相关的各种设置。默认为None。
        cmdline_args (object, optional): 命令行参数对象。默认为None。
        global_step (int, optional): 当前全局训练步数，用于标记记录的时间点。默认为1。
    """
    s = str("")

    if cmdline_args is not None:
        s += str(cmdline_args)
        s += "<br><br>"

    if args is not None:
        s += str(args).replace(",","<br>")[10:-2]

    writer.add_text(tag="params", text_string=s, global_step=global_step)  # ⭐ 核心操作：将参数文本写入TensorBoard
    writer.flush()

def training_run(settings):
    """
    执行完整的训练流程，包括环境初始化、模型训练和性能评估。

    Args:
        settings (dict): 包含所有训练配置参数的字典，包括随机种子、日志目录、策略类型等。

    Returns:
        list: 包含两个元素的列表，分别是callback.best_metrics和callback.best_mean_metrics，表示训练过程中的最佳指标和平均指标。
    """
    setup_seed(seed=settings["seed"][settings["run"]])

    settings["log_dir"] = os.path.join(settings["tensorboard_dir"],
                                       settings["run_name"] + f'_{settings["run"]}_{settings["policy"]}')

    # Create directory if it doesn't exsit.
    if not os.path.isdir(settings["tensorboard_dir"]):
        os.makedirs(settings["tensorboard_dir"])

    # Create directory if it doesn't exsit.
    if not os.path.isdir(settings["log_dir"]):
        os.makedirs(settings["log_dir"],exist_ok=True)

    hp = load_hyperparameters_from_file(settings["hyperparameters"])

    env_params=parameters({"pcb_file": settings["training_pcb"],
                           "training_pcb": settings["training_pcb"],
                           "evaluation_pcb": settings["evaluation_pcb"],
                           "net": "",
                           "use_dataAugmenter": True,
                           "augment_position": True,
                           "augment_orientation": True,
                           "agent_max_action": 1,
                           "agent_expl_noise": hp["expl_noise"],
                           "debug": False,
                           "max_steps": 200,
                           "w": settings["w"],
                           "o": settings["o"],
                           "hpwl": settings["hpwl"],
                           "seed": settings["seed"][settings["run"]],
                           "ignore_power": True,
                           "log_dir": settings["log_dir"],
                           "idx": settings["pcb_idx"],
                           "shuffle_idxs": settings["shuffle_training_idxs"],
                           })

    env = environment(env_params)  # ⭐ 初始化训练环境
    env.reset()

    model = setup_model(model_type=settings["policy"],
                        train_env=env,
                        hyperparameters=hp,
                        device=settings["device"],
                        early_stopping=settings["early_stopping"],
                        verbose=settings["verbose"])

    callback = log_and_eval_callback(log_dir=settings["log_dir"],
                                     settings=settings,
                                     hyperparameters=hp,
                                     model=model,
                                     eval_freq=settings["evaluate_every"],
                                     verbose=settings["verbose"],
                                     training_log="training.log",
                                     num_evaluations=16)

    write_desc_log( full_fn=os.path.join(settings["log_dir"],
                                         f'{settings["run_name"]}_desc.log'),
                                         settings=settings,
                                         hyperparameters=hp,
                                         model=model)

    model.explore_for_expert_targets(settings["target_exploration_steps"])  # ⭐ 执行探索阶段
    model.learn(timesteps=settings["max_timesteps"],  # ⭐ 执行主要训练过程
                callback=callback,
                start_timesteps=settings["start_timesteps"],
                incremental_replay_buffer=settings["incremental_replay_buffer"]
                )

    return [callback.best_metrics, callback.best_mean_metrics]

def main():
    """
    PCB布线策略训练主程序，负责初始化训练环境、执行多次训练运行并输出性能统计。

    功能流程：
    1. 解析命令行参数获取训练设置
    2. 可选重定向标准输出/错误到日志文件
    3. 进行多轮次训练运行
    4. 收集并计算平均性能指标
    """
    args,settings = cmdline_args()  # ⭐ 解析命令行参数获取配置

    if settings["redirect_stdout"] is True:
        redirection_file = os.path.join(settings["tensorboard_dir"],
                                        f"{settings['policy']}_{settings['experiment']}.stdout")
        sys.stdout = open(redirection_file, "w", encoding="utf-8")

    if settings["redirect_stderr"] is True:
        redirection_file = os.path.join(settings["tensorboard_dir"],
                                        f"{settings['policy']}_{settings['experiment']}.stderr")
        sys.stderr = open(redirection_file, "w", encoding="utf-8")

    program_info(args.device)

    mean_best_rewards = []
    mean_best_steps = []
    mean_best_mean_rewards = []
    mean_best_mean_steps = []

    for run in range(settings["runs"]):
        settings["run"] = run
        perf_metrics = training_run(settings=settings)  # ⭐ 执行单次训练运行

        mean_best_rewards.append(perf_metrics[0][0])
        mean_best_steps.append(perf_metrics[0][1])
        mean_best_mean_rewards.append(perf_metrics[1][0])
        mean_best_mean_steps.append(perf_metrics[1][1])

    print(f"mean best_reward = {np.mean(mean_best_rewards)}")
    print(f"mean best_step = {np.mean(mean_best_steps)}")
    print(f"mean best_mean_reward = {np.mean(mean_best_mean_rewards)}")
    print(f"mean best_mean_step = {np.mean(mean_best_mean_steps)}")

if __name__ == "__main__":
    main()


import os
import numpy as np
import pandas as pd
import seaborn as sns

def sort_key(e):
    """
    Define a sorting key function to sort elements by their 'run' value.

    Args:
        e (dict): A dictionary containing a 'run' key.

    Returns:
        Any: The value associated with the 'run' key for sorting purposes.
    """
    return e["run"]  # ⭐ Return the value of 'run' key as sorting criterion

def generate_table(data):
    """
    从强化学习训练数据中生成统计表格，包含各周期后20%阶段奖励的均值、标准差及汇总结果。

    Args:
        data (dict): 包含所有训练周期数据的字典，必须有"all_dfs"键。

    Returns:
        tuple: 包含三个列表：
            - all_means: 各周期后20%阶段奖励的均值列表，最后一项为总均值
            - all_stds: 各周期后20%阶段奖励的标准差列表，最后一项为总标准差
            - combined: 格式化后的均值±标准差字符串列表
    """
    all_means = []
    all_stds = []
    combined = []

    all_dfs = data["all_dfs"]  # ⭐ 获取所有训练周期的数据框架

    for i in range(len(all_dfs)):
        n_rows =  len(all_dfs[i]["accumulated_reward"])
        data = all_dfs[i]["accumulated_reward"][(int(n_rows*0.8)):]  # ⭐ 截取后20%阶段的奖励数据

        all_means.append(data.mean())
        all_stds.append(data.std())
        combined.append( "{:5.4f}".format(all_means[-1]) + " \u00B1 " + "{:3.4f}".format(all_stds[-1]) )

    all_means.append(np.mean(all_means))
    all_stds.append(np.mean(all_stds))
    combined.append( "{:5.4f}".format(np.mean(all_means)) + " \u00B1 " + "{:3.4f}".format(np.mean(all_stds)) )


    return all_means, all_stds, combined

def generate_plot(data,
                  plot: str = "reward",
                  max_steps: int = 200,
                  label=None, scale="M"):
    """
    生成并绘制强化学习训练数据的统计图表。

    Args:
        data (dict): 包含训练数据的字典，必须有'all_dfs'键
        plot (str): 图表类型，可选'reward'或'episode_length'
        max_steps (int): 每个回合的最大步数，用于计算x轴刻度
        label (str): 图例标签，默认为算法名称
        scale (str): x轴刻度单位，'M'表示百万，其他表示千

    Returns:
        None: 直接绘制图表，不返回具体值
    """
    all_dfs = data["all_dfs"]

    # 4. trim each dataset so that all dataset have an equal amount of episodes
    length = 1_000_000_000_000
    for df in all_dfs:
        if len(df) < length:
            length = len(df)

    for i in range(len(all_dfs)):
        all_dfs[i] = all_dfs[i].truncate(after=length-1)

    # 4. create a new data frame with all datasets appended
    for i in range(len(all_dfs)):
        if i == 0:
            df = all_dfs[i]
        else:
            df = df.append(all_dfs[i], ignore_index=True)  # ⭐ 合并所有数据帧

    df = df.assign(episode_timesteps=df["episode_number"]*max_steps)
    # 5. plot a line plot using seaborn and is should show a 95% ci.
    if label is None:
        label = f"{data['batch'][0]['algorithm']}"

    if plot == "reward":
        f = sns.lineplot(data=df, ci="sd",  # ⭐ 绘制奖励曲线图
                         x="episode_timesteps", y="accumulated_reward",
                         label=label)
    elif plot == "episode_length":
        f = sns.lineplot(data=df, ci="sd",
                         x="episode_timesteps", y="episode_length",
                         label=label)
    else:
        print(f"plot={plot} is not a supported option.")
    if scale == "M":
        xlabels = ["{:,.2f}".format(x) + "M" for x in f.get_xticks()/1000_000]
    else:
        xlabels = ["{:}".format(int(x)) + "k" for x in f.get_xticks()/1_000]

    f.set_xticklabels(xlabels)

def generate_multi_agent_plot(batch,
                              window: int = -1,
                              plot: str = "reward",
                              max_steps: int = 200,
                              label=None,
                              scale="k",
                              verbose=False):
    """
    生成多智能体训练数据的可视化图表（默认显示奖励曲线）

    Args:
        batch (list): 包含多个训练运行信息的字典列表，每个字典应包含"dir"和"run"字段
        window (int): 滑动窗口大小，用于数据平滑（<=0表示不进行平滑）
        plot (str): 要绘制的指标类型（当前仅支持"reward"）
        max_steps (int): 最大时间步数限制（未完全实现）
        label (str): 图例前缀标签
        scale (str): x轴刻度单位，"k"表示千，"M"表示百万
        verbose (bool): 是否打印调试信息

    Returns:
        None: 直接生成matplotlib图表
    """
    for b in batch:
        print(b)
        full_path = os.path.join(b["dir"], "training.log")

        f = open(full_path, "rb")   # 以二进制读模式打开文件

        episode_num = []
        timesteps = []
        timesteps_ax = []
        episode_length = []
        episode_reward = []
        read_data = False

        for line in f:
            l = str(line)[2:-5]
            if l == "data begin":
                if verbose is True:
                    print("Found tag: \"data begin\"")
                read_data = True
                continue

            if l == "data end":
                if verbose is True:
                    print("Found tag: \"data end\"")
                read_data = False
                continue

            if read_data:
                fields = l.split(",")
                if fields[0] == "episode_number":
                    hdr = l.split(",")
                    continue
                episode_num.append(int(fields[0]))
                timesteps.append(int(fields[1]))        # ⭐ 累计时间步数（关键指标）
                episode_length.append(int(fields[2]))
                episode_reward.append(np.float32(fields[3]))

        f.close()

        df = pd.DataFrame({"t": timesteps, "episode_return":episode_reward} )
        if window > 0:
            avg = df[["episode_return"]].rolling(center=False,
                                                 window=int(window),
                                                 min_periods=1).mean()
            # 将平滑后的数据替换原始数据
            df=df.assign(episode_return=avg["episode_return"])

        f = sns.lineplot(data=df,
                         x="t",
                         y="episode_return",
                         label=f'run_{b["run"]}' if label is None else label+f' - run_{b["run"]}')

    if scale == "M":
        xlabels = ["{:,.2f}".format(x) + "M" for x in f.get_xticks()/1000_000]
    else:
        xlabels = ["{:}".format(int(x)) + "k" for x in f.get_xticks()/1_000]

    f.set_xticklabels(xlabels)  # ⭐ 设置x轴刻度标签（关键可视化步骤）

def generate_multi_agent_plot_w_mean_std(batch,
                                         window: int = -1,
                                         plot: str = "reward",
                                         max_steps: int = 200,
                                         label=None,
                                         scale="k",
                                         verbose=False):
    """
    处理多个智能体的训练日志数据，生成带标准差的平均奖励曲线图。

    Args:
        batch (list): 包含各智能体训练目录信息的字典列表
        window (int): 滑动窗口大小（用于数据平滑），-1表示不使用平滑
        plot (str): 要绘制的指标类型（当前仅支持"reward"）
        max_steps (int): 单次episode最大步数（用于x轴缩放）
        label (str): 图例标签
        scale (str): 时间轴缩放单位（"k"表示千步，"M"表示百万步）
        verbose (bool): 是否打印调试信息

    Returns:
        None: 直接生成matplotlib绘图对象
    """
    all_dfs = []
    for b in batch:
        print(b)
        full_path = os.path.join(b["dir"], "training.log")

        f = open(full_path, "rb")   # 以二进制读模式打开文件

        episode_num = []
        timesteps = []
        episode_length = []
        episode_reward = []
        read_data = False

        for line in f:
            l = str(line)[2:-5]
            if l == "data begin":
                if verbose is True:
                    print("Found tag: \"data begin\"")
                read_data = True
                continue

            if l == "data end":
                if verbose is True:
                    print("Found tag: \"data end\"")
                read_data = False
                continue

            if read_data:
                fields = l.split(",")
                if fields[0] == "episode_number":
                    hdr = l.split(",")
                    continue
                episode_num.append(int(fields[0]))
                timesteps.append(int(fields[1]))        # 累计时间步数
                episode_length.append(int(fields[2]))
                episode_reward.append(np.float32(fields[3]))  # ⭐ 核心：提取每episode的奖励值

        f.close()

        df = pd.DataFrame({"t": timesteps,
                           "episode_return":episode_reward,
                           "episode_number":episode_num} )
        if window > 0:
            avg = df[["episode_return"]].rolling(center=False,
                                                 window=int(window),
                                                 min_periods=1).mean()
            # 将平滑后的数据添加回DataFrame
            df=df.assign(episode_return=avg["episode_return"])

        all_dfs.append(df)

    # 4. 截断所有数据集使它们具有相同的episode数量
    length = 1_000_000_000_000
    for df in all_dfs:
        if len(df) < length:
            length = len(df)

    for i in range(len(all_dfs)):
        all_dfs[i] = all_dfs[i].truncate(after=length-1)

    # 4. 合并所有数据集
    for i in range(len(all_dfs)):
        if i == 0:
            df = all_dfs[i]
        else:
            df = df.append(all_dfs[i], ignore_index=True)

    f = sns.lineplot(data=df, ci="sd",  # ⭐ 核心：绘制带标准差的曲线图
                     x="episode_number", y="episode_return",
                     label=label)

    if scale == "M":
        xlabels = ["{:,.2f}".format(x) + "M" for x in (f.get_xticks()*200)/1_000_000]
    else:
        xlabels = ["{:}".format(int(x)) + "k" for x in (f.get_xticks()*200)/1_000]

    f.set_xticklabels(xlabels)  # ⭐ 设置x轴刻度标签

def generate_dataset(batch, window: int = -1, verbose=False):
    """
    从批量训练日志中生成数据集，支持滑动平均处理。

    Args:
        batch (list): 包含多个训练运行信息的字典列表，每个字典应包含"dir"键指向日志目录
        window (int, optional): 滑动平均窗口大小，<=0表示不进行滑动平均。默认为-1
        verbose (bool, optional): 是否打印调试信息。默认为False

    Returns:
        dict: 包含两个键的字典：
            - "batch": 原始输入batch
            - "all_dfs": 包含所有训练日志数据的DataFrame列表
    """
    # 按运行编号升序排序，确保自动生成的表格行描述符与正确的运行编号对应
    batch.sort(key=sort_key)

    data = {"batch": batch}
    all_dfs = []
    for b in batch:
        full_path = os.path.join(b["dir"], "training.log")

        f = open(full_path, "rb")   # 以二进制读模式打开文件  # ⭐ 关键文件操作：打开训练日志文件

        episode_num = []
        timesteps = []
        episode_length = []
        episode_reward = []
        read_data = False
        hdr = ["episode_number", "timesteps", "episode_length", "accumulated_reward"]  # 设置默认列名

        for line in f:
            l = str(line)[2:-5]
            if l == "data begin":
                if verbose is True:
                    print("Found tag: \"data begin\"")
                read_data = True
                continue

            if l == "data end":
                if verbose is True:
                    print("Found tag: \"data end\"")
                read_data = False
                continue

            if read_data:
                fields = l.split(",")
                if fields[0] == "episode_number":
                    hdr = l.split(",")
                    continue
                episode_num.append(int(fields[0]))  # ⭐ 核心数据处理：解析并存储日志中的训练指标
                timesteps.append(int(fields[1]))
                episode_length.append(int(fields[2]))
                episode_reward.append(np.float32(fields[3]))

        f.close()

        episode_num = np.array(episode_num, dtype=np.int32)
        timesteps = np.array(timesteps, dtype=np.int32)
        episode_length = np.array(episode_length, dtype=np.int32)
        episode_reward = np.array(episode_reward, dtype=np.float32)

        df = pd.DataFrame(data = {hdr[0]: episode_num,
                                  hdr[1]: timesteps,
                                  hdr[2]: episode_length,
                                  hdr[3]: episode_reward})

            # 计算滑动平均值
            # 设置min_periods=1表示第一个值保持不变，第二个值为前两个值的平均值，依此类推
        if window > 0:
            avg = df[["episode_length",
                      "accumulated_reward"]].rolling(center=False,
                                                     window=int(window),
                                                     min_periods=1).mean()
            avg.rename({"episode_length": "episode_length_sma",
                        "accumulated_reward": "accumulated_reward_sma"},
                        inplace=True, axis=1)
            # 将列追加到DataFrame末尾
            df=df.assign(episode_length=avg["episode_length_sma"])  # ⭐ 关键数据处理：应用滑动平均
            df=df.assign(accumulated_reward=avg["accumulated_reward_sma"])

        all_dfs.append(df)

    data["all_dfs"] = all_dfs

    return data

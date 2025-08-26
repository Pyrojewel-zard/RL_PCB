import os

from core import video_utils
from collections import deque
import numpy as np

import matplotlib
import matplotlib.pyplot as plt
from datetime import datetime
matplotlib.use("Agg")

class tracker():
    """
    环境跟踪器类，用于记录和跟踪整个环境的训练过程
    包括组件网格、飞线图、奖励、指标等信息的存储、可视化和分析
    """
    
    def __init__(self, maxlen=1024):
        """
        初始化环境跟踪器
        
        Args:
            maxlen: 最大记录长度，防止内存溢出
        """
        self.maxlen = maxlen

        # 使用双端队列存储历史数据
        self.all_comp_grids = deque(maxlen=self.maxlen)  # 组件网格历史
        self.ratsnest = deque(maxlen=self.maxlen)        # 飞线图历史
        self.rewards = deque(maxlen=self.maxlen)          # 奖励历史
        self.metrics = deque(maxlen=self.maxlen)          # 指标历史
        self.frame_buffer = np.array([])                  # 帧缓冲区

    def add_comp_grids(self, comp_grids=None):
        """
        添加组件网格数据
        
        Args:
            comp_grids: 组件网格数据
        """
        if comp_grids is not None:
            self.all_comp_grids.append(comp_grids)

    def get_last_comp_grids(self):
        """
        获取最新的组件网格数据
        
        Returns:
            最新的组件网格数据
        """
        return self.all_comp_grids[-1]

    def add(self, comp_grids=None, ratsnest=None):
        """
        添加组件网格和飞线图数据
        
        Args:
            comp_grids: 组件网格数据
            ratsnest: 飞线图数据
        """
        if comp_grids is not None:
            self.all_comp_grids.append(comp_grids)

        if ratsnest is not None:
            self.ratsnest.append(ratsnest)

    def add_reward(self, reward):
        """
        添加奖励数据
        
        Args:
            reward: 奖励值
        """
        self.rewards.append(reward)

    def add_metrics(self, metrics):
        """
        添加指标数据
        
        Args:
            metrics: 指标数据列表
        """
        self.metrics.append(metrics)

    def reset(self):
        """
        重置跟踪器，清空所有历史数据
        """
        self.all_comp_grids.clear()
        self.ratsnest.clear()
        self.rewards.clear()
        self.metrics.clear()

    def create_video(self, fileName=None, v_id=None, display_metrics=True, fps=30):
        """
        创建训练过程视频
        
        Args:
            fileName: 输出文件名
            v_id: 视频ID
            display_metrics: 是否显示指标
            fps: 帧率
        """
        if display_metrics is True:
            video_utils.create_video(self.all_comp_grids,
                                     ratsnest=self.ratsnest,
                                     v_id=v_id,
                                     fileName=fileName,
                                     all_metrics=self.metrics,
                                     draw_debug=True,
                                     fps=fps)
        else:
            video_utils.create_video(self.all_comp_grids,
                                     ratsnest=self.ratsnest,
                                     v_id=v_id,
                                     fileName=fileName,
                                     all_metrics=None,
                                     draw_debug=True,
                                     fps=fps)

    def log_run_to_file(self, path=None, filename=None, kicad_pcb=None):
        """
        将运行日志写入文件
        
        Args:
            path: 文件路径
            filename: 文件名
            kicad_pcb: KiCad PCB文件名
        """
        f = open(os.path.join(path, filename), "w", encoding="utf-8")
        f.write(f"timestamp={datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')}\r\n")
        f.write(f"module={self.__class__.__name__}\r\n")
        if kicad_pcb is not None:
            f.write(f".kicad_pcb={kicad_pcb}\r\n")

        # 遍历所有组件
        for i in range(len(self.metrics[0])):
            f.write("component begin\r\n")
            f.write(f"\tid={self.metrics[0][i]['id']}\r\n")
            f.write(f"\tname={self.metrics[0][i]['name']}\r\n")
            f.write(f"\tinitial_wirelength={self.metrics[0][i]['Wi']}\r\n")
            f.write(f"\tinitial_hpwl={self.metrics[0][i]['HPWLi']}\r\n")
            f.write(f"\texpert_wirelength={self.metrics[0][i]['We']}\r\n")
            f.write(f"\texpert_hpwl={self.metrics[0][i]['HPWLe']}\r\n")

            f.write("\theader begin\r\n")
            f.write("\t\tstep,wirelength,raw_wirelength,hpwl,raw_hpwl,overlap,weighted_cost,reward\r\n")
            f.write("\theader end\r\n")

            f.write("\tdata begin\r\n")
            # -1是因为done会在第一次遇到时退出
            for j in range(len(self.metrics)-1):
                f.write(f"\t\t{j},{np.round(self.metrics[j][i]['W'],6)},{np.round(self.metrics[j][i]['raw_W'],6)},{np.round(self.metrics[j][i]['HPWL'],6)},{np.round(self.metrics[j][i]['raw_HPWL'],6)},{np.round(self.metrics[j][i]['ol'],6)},{np.round(self.metrics[j][i]['weighted_cost'],6)},{np.round(self.metrics[j][i]['reward'],6)},\r\n")
            f.write("data end\r\n")
        f.close()

    def create_plot(self, fileName=None):
        """
        创建训练过程的可视化图表
        
        Args:
            fileName: 输出文件名
        """
        _, ax = plt.subplots(nrows=2, ncols=3)
        
        # 为每个组件绘制指标曲线
        for i in range(len(self.metrics[0])):
            W = []              # 归一化线长
            raw_W = []          # 原始线长
            HPWL = []           # 归一化HPWL
            raw_HPWL = []       # 原始HPWL
            weighted_cost = []  # 加权成本
            
            # -1是因为done会在第一次遇到时退出
            for j in range(len(self.metrics)-1):
                W.append(self.metrics[j][i]["W"])
                raw_W.append(self.metrics[j][i]["raw_W"])
                HPWL.append(self.metrics[j][i]["HPWL"])
                raw_HPWL.append(self.metrics[j][i]["raw_HPWL"])
                weighted_cost.append(self.metrics[j][i]["weighted_cost"])

            # 绘制各种指标曲线
            ax[0,0].plot(W, label=f'{self.metrics[0][i]["name"]}')
            ax[1,0].plot(raw_W, label=f'{self.metrics[0][i]["name"]}, {np.round(self.metrics[0][i]["Wi"],2)}')
            ax[0,1].plot(HPWL, label=f'{self.metrics[0][i]["name"]}')
            ax[1,1].plot(raw_HPWL, label=f'{self.metrics[0][i]["name"]}, {np.round(self.metrics[0][i]["HPWLi"],2)}')
            ax[1,2].plot(weighted_cost, label=f'{self.metrics[0][i]["name"]}')

        # 设置图表标题和图例
        ax[0,0].set_title("W")
        ax[1,0].set_title("raw_W")
        ax[0,1].set_title("HPWL")
        ax[1,1].set_title("raw_HPWL")
        ax[1,2].set_title("Weighted cost")
        ax[0,0].legend()
        ax[1,0].legend()
        ax[0,1].legend()
        ax[1,1].legend()
        ax[1,2].legend()
        
        plt.tight_layout()
        plt.savefig(fileName)
        plt.close()

    def capture_snapshot(self, fileName):
        """
        捕获当前状态的快照图像
        
        Args:
            fileName: 输出文件名
        """
        video_utils.create_image(self.all_comp_grids,
                                 ratsnest=self.ratsnest,
                                 fileName=fileName,
                                 draw_debug=True)

    def video_tensor(self):
        """
        获取视频张量数据
        
        Returns:
            视频张量
        """
        return video_utils.get_video_tensor(self.all_comp_grids, self.ratsnest)

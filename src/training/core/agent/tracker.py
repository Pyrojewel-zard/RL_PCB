from core import video_utils

from collections import deque
import numpy as np

class tracker():
    """
    智能体跟踪器类，用于记录和跟踪智能体的训练过程
    包括观察历史、飞线图等信息的存储和视频生成
    """
    
    def __init__(self, maxlen=1024):
        """
        初始化跟踪器
        
        Args:
            maxlen: 最大记录长度，防止内存溢出
        """
        self.maxlen = maxlen

        # 使用双端队列存储历史数据
        self.all_comp_grids = deque(maxlen=self.maxlen)  # 组件网格历史
        self.ratsnest = deque(maxlen=self.maxlen)        # 飞线图历史

        self.frame_buffer = np.array([])  # 帧缓冲区

    def add_observation(self, comp_grids=None, los_grids=None, los=None, ol_grids=None, ol=None):
        """
        添加观察数据
        
        Args:
            comp_grids: 组件网格
            los_grids: 视线网格
            los: 视线值
            ol_grids: 重叠网格
            ol: 重叠值
        """
        if comp_grids is not None:
            self.all_comp_grids.append(comp_grids)

    def add_ratsnest(self, ratsnest):
        """
        添加飞线图数据
        
        Args:
            ratsnest: 飞线图数据
        """
        if ratsnest is not None:
            self.ratsnest.append(ratsnest)

    def reset(self):
        """
        重置跟踪器，清空所有历史数据
        """
        self.all_comp_grids.clear()
        self.ratsnest.clear()

    def create_video(self, fileName=None, v_id=None):
        """
        创建训练过程视频
        
        Args:
            fileName: 输出文件名
            v_id: 视频ID
        """
        video_utils.create_video(self.all_comp_grids, self.ratsnest, v_id=v_id)

    def update_frame_buffer(self, v_id=None):
        """
        更新帧缓冲区
        
        Args:
            v_id: 视频ID
        """
        if self.frame_buffer.size == 0:
            self.frame_buffer = video_utils.video_frames(self.all_comp_grids,
                                                         self.ratsnest,
                                                         v_id=v_id)
        else:
            # 连接新的帧到现有缓冲区
            self.frame_buffer = np.concatenate(
                (self.frame_buffer, video_utils.video_frames(self.all_comp_grids, self.ratsnest, v_id=v_id)),
                 axis=0)

    def write_frame_buffer(self, fileName=None, reset=False):
        """
        写入帧缓冲区到文件
        
        Args:
            fileName: 输出文件名
            reset: 是否重置缓冲区
        """
        video_utils.write_frame_buffer(self.frame_buffer)
        self.frame_buffer = np.array([])

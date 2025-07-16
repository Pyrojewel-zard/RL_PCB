from core import video_utils

from collections import deque
import numpy as np

class tracker():
    def __init__(self, maxlen=1024):
        """
        初始化跟踪器对象，设置最大记录长度并创建数据存储队列。

        Args:
            maxlen (int, optional): 队列的最大长度，默认为1024。
        """
        self.maxlen = maxlen

        self.all_comp_grids = deque(maxlen=self.maxlen)  # ⭐ 初始化组件网格存储队列
        self.ratsnest = deque(maxlen=self.maxlen)

        self.frame_buffer = np.array([])

    def add_observation(self, comp_grids=None,
                        los_grids=None,
                        los=None,
                        ol_grids=None,
                        ol=None):
        """
        添加观察数据到跟踪器中，目前仅支持组件网格数据的添加。

        Args:
            comp_grids: 组件网格数据
            los_grids: 鼠线网格数据（未实现）
            los: 鼠线数据（未实现）
            ol_grids: 重叠网格数据（未实现）
            ol: 重叠数据（未实现）
        """
        if comp_grids is not None:
            self.all_comp_grids.append(comp_grids)  # ⭐ 将组件网格数据添加到队列

    def add_ratsnest(self, ratsnest):
        if ratsnest is not None:
            self.ratsnest.append(ratsnest)

    def reset(self):
        self.all_comp_grids.clear()
        self.ratsnest.clear()

    def create_video(self, fileName=None, v_id=None):
        video_utils.create_video(self.all_comp_grids, self.ratsnest, v_id=v_id)

    def update_frame_buffer(self, v_id=None):
        if self.frame_buffer.size == 0:
            self.frame_buffer = video_utils.video_frames(self.all_comp_grids,
                                                         self.ratsnest,
                                                         v_id=v_id)
        else:
            self.frame_buffer = np.concatenate(
                (self.frame_buffer, video_utils.video_frames(self.all_comp_grids, self.ratsnest, v_id=v_id)),
                 axis=0)

    def write_frame_buffer(self, fileName=None, reset=False):
        video_utils.write_frame_buffer(self.frame_buffer)
        self.frame_buffer = np.array([])

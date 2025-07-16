import os
import pandas as pd
import numpy as np
import cv2
import ast
from pcb import pcb


def board_maskast(physical_width_mm, physical_height_mm, grid_step_mm):
    """
    生成矩形比例的二值掩码图。
    参数:
        physical_width_mm: 输出图像的物理宽度（mm）
        physical_height_mm: 输出图像的物理高度（mm）
        grid_step_mm: 每个像素代表的物理尺寸
    """
    # 获取项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(project_root, "board_csv", "mokuai.csv")

    grid_width = int(physical_width_mm / grid_step_mm)
    grid_height = int(physical_height_mm / grid_step_mm)
    row_index = 8

    # 读取并解析 CSV
    df = pd.read_csv(csv_path, header=None)
    raw_row = df.iloc[row_index].dropna()
    points = []
    for item in raw_row:
        try:
            pt = ast.literal_eval(item)
            if isinstance(pt, list) and len(pt) == 2:
                points.append(pt)
        except:
            continue
    points = np.array(points, dtype=np.float32)

    # 缩放处理
    min_xy = np.min(points, axis=0)
    size_xy = np.max(points, axis=0) - min_xy
    scale_x = physical_width_mm / size_xy[0]
    scale_y = physical_height_mm / size_xy[1]
    points_scaled = (points - min_xy) * np.array([scale_x, scale_y])

    # 居中处理
    delta_x = physical_width_mm - np.max(points_scaled[:, 0])
    delta_y = physical_height_mm - np.max(points_scaled[:, 1])
    points_scaled[:, 0] += delta_x / 2
    points_scaled[:, 1] += delta_y / 2

    # 转为像素坐标
    pixel_points = (points_scaled / grid_step_mm).astype(np.int32)
    pixel_points[:, 0] = np.clip(pixel_points[:, 0], 0, grid_width - 1)
    pixel_points[:, 1] = np.clip(pixel_points[:, 1], 0, grid_height - 1)

    # 生成图像
    board_mask = np.zeros((8,int(grid_width), int(grid_height)), dtype=np.uint8)
    for i in range(8):
       board_mask[i] = cv2.fillPoly(np.zeros((grid_width, grid_height), dtype=np.uint8),
                                 [pixel_points], 1)

    return board_mask




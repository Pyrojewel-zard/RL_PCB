import cv2
from datetime import datetime
import numpy as np
import torch

def create_video(all_comp_grids,
                 ratsnest,
                 fileName=None,
                 v_id=None,
                 all_metrics=None,
                 draw_debug=False,
                 fps=30):
    """
    创建包含组件布局、鼠线图和性能指标的视频文件。

    Args:
        all_comp_grids (list): 包含各帧组件网格数据的列表
        ratsnest (list): 鼠线图数据
        fileName (str, optional): 输出视频文件名，默认为时间戳命名
        v_id (str, optional): 视频ID水印文本
        all_metrics (list, optional): 性能指标数据
        draw_debug (bool, optional): 是否绘制调试信息
        fps (int, optional): 视频帧率，默认为30

    Returns:
        None: 函数直接生成视频文件，无返回值
    """
    width = all_comp_grids[0][0].shape[0]
    height = all_comp_grids[0][0].shape[1]
    channel = 1

    if all_metrics is not None:
        metrics_width = int(1*width)
        width = width + metrics_width

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # ⭐ 设置视频编码格式

    ts = datetime.now().strftime("%s_%f")

    if fileName is None:
        fileName = f"{ts}_video.mp4"

    video = cv2.VideoWriter(fileName, fourcc, float(
        fps), (width, height), False)

    if v_id is not None:
        for _ in range(fps):
            img = np.zeros(((width),height,1), np.uint8)
            (text_width, text_height) = cv2.getTextSize(text=f"{v_id}",
            fontFace = cv2.FONT_HERSHEY_SIMPLEX,
                fontScale = 5,
                thickness=2
                )[0]

            cv2.putText(img,
            f"{v_id}",
            (int(0.5*width - text_width/2), int(0.5*height + text_height/2)),
            cv2.FONT_HERSHEY_SIMPLEX,
            6,
            (128, 128, 0),
            3
            )
            video.write(img)

    for frame in range(len(all_comp_grids)):

        if all_metrics is not None:
            metrics_img = np.zeros((height, metrics_width, channel),
                                   dtype = np.uint8)

        img = all_comp_grids[frame][0] + \
            2*all_comp_grids[frame][1]  # ⭐ 合并基础组件网格

        if draw_debug is True:
            img = np.maximum(img,all_comp_grids[frame][2])

        if len(ratsnest) != 0:
            img = np.maximum(img, ratsnest[frame])

        cv2.putText(img, f"{frame}",
                    (int(0.075*width), int(0.1*height)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.85, # 0.85 is the font scale
                    (128, 128, 0),
                    2)

        accumulated_reward = 0
        if all_metrics is not None and frame > 0:
            height_mult = 0.04
            total_cost = 0
            total_reward = 0
            total_nodes = 0
            for item in all_metrics[frame-1]:
                # For five components
                cv2.putText(metrics_img,
                            f"id; cost    : {item['id']} ({item['name']}); {np.round(item['weighted_cost'],2)} ({np.round(item['reward'],2)})",
                            (int(0.02*width), int(height_mult*height)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.4,
                            (128, 128, 0),
                            1)
                height_mult += 0.04
                cv2.putText(metrics_img,
                            f"rW; rHPWL   : {np.round(item['W'],2)} ({np.round(item['We'],2)}); {np.round(item['HPWL'],2)} ({np.round(item['HPWLe'],2)})", (int(0.02*width), int(height_mult*height)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.4,
                            (128, 128, 0),
                            1)
                height_mult += 0.04
                cv2.putText(metrics_img,
                            f"ol           : {np.round(item['ol'],2)}", (int(0.02*width), int(height_mult*height)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.4,
                            (128, 128, 0),
                            1)

                total_cost += item["weighted_cost"]
                total_reward += item["reward"]
                total_nodes += 1
                height_mult += 0.075

            cv2.putText(metrics_img,
                        f"Average cost        : {np.round(total_cost/total_nodes,2)}",
                        (int(0.02*width), int(0.85*height)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.4,
                        (128, 128, 0),
                        1)  # ⭐ 在指标图像上绘制平均成本文本
            cv2.putText(metrics_img,
                        f"Average reward      : {np.round(total_reward/total_nodes,2)}",
                        (int(0.02*width), int(0.9*height)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.4,
                        (128, 128, 0),
                        1)  # ⭐ 在指标图像上绘制平均奖励文本
            accumulated_reward += total_reward/total_nodes
            cv2.putText(metrics_img,
                        f"Accumulated reward      : {np.round(accumulated_reward,2)}",
                        (int(0.02*width), int(0.95*height)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.4,
                        (128, 128, 0),
                        1)  # ⭐ 在指标图像上绘制累计奖励文本

        if all_metrics is not None:
            metrics_img = np.reshape(metrics_img,
                                    (metrics_img.shape[0],metrics_img.shape[1])
                                    )

        if all_metrics is not None:
            video.write(cv2.hconcat([img,metrics_img]))  # ⭐ 将原始图像和指标图像水平拼接后写入视频
        else:
            video.write(img)  # ⭐ 如果没有指标则直接写入原始图像

    video.release()  # ⭐ 释放视频写入资源

def video_frames(all_comp_grids, ratsnest, v_id=None):
    """
    生成视频帧缓冲区，合成组件网格和鼠线图，并添加文本标注。

    Args:
        all_comp_grids (list): 包含组件网格数据的列表，每个元素是(基础网格, 高亮网格)的元组
        ratsnest (list): 鼠线图数据列表
        v_id (str, optional): 视频ID标识文本，会显示在起始帧上

    Returns:
        numpy.ndarray: 包含所有合成帧的缓冲区数组，形状为(总帧数, 高度, 宽度, 通道数)
    """
    width = all_comp_grids[0][0].shape[0]
    height = all_comp_grids[0][0].shape[1]
    channels = 1

    fps = 30
    v_id_duration_in_frames = int(fps/2)

    total_frames = len(all_comp_grids) + v_id_duration_in_frames

    frame_buffer = np.zeros((total_frames, height, width, channels), np.uint8)

    if v_id is not None:
        for i in range(v_id_duration_in_frames):
            (text_width, text_height) = cv2.getTextSize(text=f"{v_id}",
            fontFace = cv2.FONT_HERSHEY_SIMPLEX,
                fontScale = 5,
                thickness=2
                )[0]

            cv2.putText(frame_buffer[i],
            f"{v_id}",
            (int(0.5*width - text_width/2), int(0.5*height + text_height/2)),
            cv2.FONT_HERSHEY_SIMPLEX,
            6,
            (128, 128, 0),
            3
            )

    for frame in range(len(all_comp_grids)):
        idx = frame+v_id_duration_in_frames
        frame_buffer[idx] = np.resize(
            np.maximum(all_comp_grids[frame][0] + 2*all_comp_grids[frame][1],
                       ratsnest[frame]),
            (width,height,channels)
            )  # ⭐ 核心合成逻辑：合并组件网格和鼠线图，取最大值合成

        cv2.putText(frame_buffer[idx], f"{frame}",
                    (int(0.075*width), int(0.1*height)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.85,
                    (128, 128, 0),
                    2)

    return frame_buffer

def write_frame_buffer(frame_buffer, fileName=None):
    """
    将帧缓冲区中的图像帧序列写入MP4视频文件。

    Args:
        frame_buffer (list): 包含视频帧的缓冲区列表，每帧应为numpy数组
        fileName (str, optional): 输出视频文件名。若为None则自动生成时间戳文件名

    Returns:
        None
    """
    width = frame_buffer[0].shape[-2]
    height = frame_buffer[0].shape[-3]
    fps = 30

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # ⭐ 设置MP4视频编码格式

    ts = datetime.now().strftime("%s_%f")

    if fileName is None:
        fileName = f"{ts}_video.mp4"

    video = cv2.VideoWriter(fileName,
                            fourcc,
                            float(fps),
                            (width, height),
                            False)

    for frame in frame_buffer:
        video.write(frame)  # ⭐ 将每帧图像写入视频文件

    video.release()

def create_image(all_comp_grids, ratsnest, fileName=None, draw_debug=False):
    """
    根据组件网格和鼠线数据生成合成图像，并可选择包含调试信息，最后保存图像到文件。

    Args:
        all_comp_grids (list): 包含多层组件网格数据的列表，每层包含多个网格
        ratsnest (list): 鼠线数据列表，用于在图像上绘制连接线
        fileName (str, optional): 要保存的图像文件名。默认为None
        draw_debug (bool, optional): 是否包含调试信息。默认为False

    Returns:
        None: 直接将图像保存到文件，不返回任何值
    """
    img = all_comp_grids[-1][0] + 2*all_comp_grids[-1][1]  # ⭐ 合成基础图像：第一层网格+第二层网格加权组合

    if draw_debug is True:
        img = np.maximum(img,all_comp_grids[-1][2])  # 添加调试层网格信息

    if len(ratsnest) != 0:
        img = np.maximum(img, ratsnest[-1])  # 添加鼠线层信息

    cv2.imwrite(fileName, img)  # ⭐ 将最终合成的图像写入文件

def get_video_tensor(all_comp_grids, ratsnest):
    """
    将组件网格和鼠线图数据组合成视频张量，包含帧合成、文本标注和格式转换。

    Args:
        all_comp_grids (list): 包含各帧组件网格数据的列表，每个元素是包含两个网格的元组
        ratsnest (list): 包含各帧鼠线图数据的列表

    Returns:
        torch.Tensor: 形状为[1,帧数,通道数,高度,宽度]的视频张量
    """
    width = all_comp_grids[0][0].shape[0]
    height = all_comp_grids[0][0].shape[1]
    channels = 3
    frame_buf = []
    frames = len(all_comp_grids)

    for frame_number in range(frames):
        frame = all_comp_grids[frame_number][0] + \
             2*all_comp_grids[frame_number][1]  # ⭐ 核心合成操作：将两个组件网格按权重相加
        frame = np.maximum(frame, ratsnest[frame_number])

        cv2.putText(frame, f"{frame_number}",
                    (int(0.075*width),int(0.1*height)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.85,    # 0.85 is the font scale
                    (128, 128, 0),
                    2)

        frame = np.tile(frame, (channels,1,1))
        np.reshape(frame, (channels, height, width))
        frame_buf.append(frame)

    video_tensor = torch.tensor(np.array(frame_buf))
    video_tensor = video_tensor.view([1,frames,channels,height,width])  # ⭐ 最终张量形状调整
    return video_tensor

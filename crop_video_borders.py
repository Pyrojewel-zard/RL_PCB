#!/usr/bin/env python3
"""
对MP4视频进行裁剪，去掉最外边一圈指定像素
"""

import cv2
import os
import numpy as np
from tqdm import tqdm


def crop_video_borders(input_video_path, output_video_path, border_pixels=20):
    """
    对视频进行裁剪，去掉最外边一圈指定像素
    
    Args:
        input_video_path: 输入视频路径
        output_video_path: 输出视频路径
        border_pixels: 要去掉的边框像素数
    """
    
    # 打开输入视频
    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        print(f"错误：无法打开输入视频 {input_video_path}")
        return
    
    # 获取原始视频信息
    original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"原始视频信息:")
    print(f"  尺寸: {original_width}x{original_height}")
    print(f"  总帧数: {total_frames}")
    print(f"  FPS: {fps}")
    
    # 计算裁剪后的尺寸
    new_width = original_width - 2 * border_pixels
    new_height = original_height - 2 * border_pixels
    
    if new_width <= 0 or new_height <= 0:
        print(f"错误：裁剪后的尺寸无效 ({new_width}x{new_height})")
        print(f"边框像素 {border_pixels} 太大，无法裁剪")
        cap.release()
        return
    
    print(f"裁剪参数:")
    print(f"  去除边框: {border_pixels} 像素")
    print(f"  裁剪后尺寸: {new_width}x{new_height}")
    
    # 设置输出视频编码器
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (new_width, new_height))
    
    if not out.isOpened():
        print(f"错误：无法创建输出视频文件 {output_video_path}")
        cap.release()
        return
    
    print(f"开始处理视频...")
    
    # 逐帧处理视频
    frame_count = 0
    with tqdm(total=total_frames, desc="裁剪进度") as pbar:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # 裁剪帧 - 去掉最外边一圈像素
            # frame[y1:y2, x1:x2] 格式
            cropped_frame = frame[border_pixels:original_height-border_pixels, 
                                border_pixels:original_width-border_pixels]
            
            # 写入输出视频
            out.write(cropped_frame)
            
            frame_count += 1
            pbar.update(1)
    
    # 释放资源
    cap.release()
    out.release()
    
    print(f"视频裁剪完成！")
    print(f"输出文件: {output_video_path}")
    
    # 显示输出文件信息
    if os.path.exists(output_video_path):
        file_size = os.path.getsize(output_video_path) / (1024 * 1024)  # MB
        print(f"文件大小: {file_size:.2f} MB")
        
        # 验证输出视频
        verify_cap = cv2.VideoCapture(output_video_path)
        if verify_cap.isOpened():
            verify_width = int(verify_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            verify_height = int(verify_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            verify_frames = int(verify_cap.get(cv2.CAP_PROP_FRAME_COUNT))
            print(f"验证结果:")
            print(f"  输出尺寸: {verify_width}x{verify_height}")
            print(f"  输出帧数: {verify_frames}")
            verify_cap.release()


def main():
    """主函数"""
    input_video = "14_with_pcb_mask.mp4"
    output_video = "14_with_pcb_mask_cropped.mp4"
    border_pixels = 20  # 去掉最外边一圈20像素
    
    print("开始裁剪视频边框...")
    print(f"输入视频: {input_video}")
    print(f"输出视频: {output_video}")
    print(f"裁剪边框: {border_pixels} 像素")
    
    crop_video_borders(input_video, output_video, border_pixels)


if __name__ == "__main__":
    main()
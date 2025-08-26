#!/usr/bin/env python3
"""
PCB文件转视频生成器
读取指定目录下的所有PCB文件，将它们转换为PNG图像，然后生成GIF动图或MP4视频
"""

import argparse
import os
import glob
import sys
import cv2
import numpy as np
from PIL import Image
import tempfile
import shutil
from pathlib import Path

# 添加PCB处理模块路径
sys.path.append('../training/')
from pcb import pcb
from pcbDraw import draw_board_from_board_and_graph_with_debug, draw_ratsnest_with_board

def convert_pcb_to_image(pcb_file_path):
    """
    将单个PCB文件转换为numpy图像数组
    
    Args:
        pcb_file_path (str): PCB文件路径
        
    Returns:
        numpy.ndarray: 转换后的图像数组，如果转换失败返回None
    """
    try:
        # 读取PCB文件
        pv = pcb.vptr_pcbs()
        pcb.read_pcb_file(pcb_file_path, pv)
        p = pv[0]

        # 获取图形和板信息
        g = p.get_graph()
        g.reset()
        b = p.get_board()
        g.set_component_origin_to_zero(b)

        # 绘制组件布局
        comp_grids = draw_board_from_board_and_graph_with_debug(b, g, padding=0.5)

        # 绘制飞线连接
        ratsnest = None
        nn = g.get_nodes()
        for i in range(len(nn)):
            node_id = nn[i].get_id()
            neighbor_ids = g.get_neighbor_node_ids(node_id)
            neighbors = []
            for n_id in neighbor_ids:
                neighbors.append(g.get_node_by_id(n_id))

            ee = g.get_edges()
            eoi = []
            for e in ee:
                if e.get_instance_id(0) == node_id or e.get_instance_id(1) == node_id:
                    eoi.append(e)

            if i == 0:
                ratsnest = draw_ratsnest_with_board(nn[i], neighbors, eoi, b,
                                              line_thickness=1, padding=0.5,
                                              ignore_power=True)
            else:
                ratsnest = np.maximum(ratsnest,
                                draw_ratsnest_with_board(nn[i], neighbors, eoi, b,
                                                         line_thickness=1,
                                                         padding=0.5,
                                                         ignore_power=True))

        # 合成最终图像
        img = comp_grids[0] + 2*comp_grids[1]
        if ratsnest is not None:
            img = np.maximum(img, ratsnest)
            
        return img
        
    except Exception as e:
        print(f"转换PCB文件 {pcb_file_path} 时出错: {e}")
        return None

def create_gif_from_pcb_directory(pcb_dir, output_file, duration=100, max_files=None, output_format='gif'):
    """
    从PCB目录创建GIF动图或MP4视频
    
    Args:
        pcb_dir (str): 包含PCB文件的目录路径
        output_file (str): 输出文件路径（GIF或MP4）
        duration (int): 每帧显示时间（毫秒）
        max_files (int): 最大处理文件数量，None表示处理所有文件
        output_format (str): 输出格式，'gif' 或 'mp4'
    """
    # 获取所有PCB文件并按文件名排序
    pcb_files = glob.glob(os.path.join(pcb_dir, "*.pcb"))
    pcb_files.sort()  # 按文件名排序，这样会按时间戳排序
    
    if max_files:
        pcb_files = pcb_files[:max_files]
    
    print(f"找到 {len(pcb_files)} 个PCB文件")
    
    if not pcb_files:
        print("未找到PCB文件！")
        return
    
    # 创建临时目录保存PNG文件
    temp_dir = tempfile.mkdtemp()
    png_files = []
    
    try:
        print("开始转换PCB文件...")
        
        for i, pcb_file in enumerate(pcb_files):
            print(f"正在处理 ({i+1}/{len(pcb_files)}): {os.path.basename(pcb_file)}")
            
            # 转换PCB为图像
            img = convert_pcb_to_image(pcb_file)
            
            if img is not None:
                # 在图像左上角添加序号
                img_with_number = img.copy()
                
                # 设置文字参数
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 2.0
                color = (255, 255, 255)  # 白色文字
                thickness = 3
                
                # 添加黑色背景以增强可读性
                text = f"{i+1:03d}"
                text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
                
                # 绘制黑色背景矩形
                padding = 10
                cv2.rectangle(img_with_number, 
                            (5, 5), 
                            (text_size[0] + padding + 5, text_size[1] + padding + 5), 
                            (0, 0, 0), 
                            -1)
                
                # 绘制白色文字
                cv2.putText(img_with_number, 
                          text, 
                          (padding, text_size[1] + padding), 
                          font, 
                          font_scale, 
                          color, 
                          thickness)
                
                # 保存为PNG文件
                png_file = os.path.join(temp_dir, f"frame_{i:04d}.png")
                cv2.imwrite(png_file, img_with_number)
                png_files.append(png_file)
            else:
                print(f"跳过文件: {pcb_file}")
        
        if not png_files:
            print("没有成功转换的图像文件！")
            return
        
        print(f"成功转换 {len(png_files)} 个图像文件")
        
        if output_format == 'gif':
            print("正在生成GIF动图...")
            
            # 读取第一张图像以确定尺寸
            first_img = Image.open(png_files[0])
            
            # 读取所有图像
            images = []
            for png_file in png_files:
                img = Image.open(png_file)
                # 确保所有图像尺寸一致
                if img.size != first_img.size:
                    img = img.resize(first_img.size, Image.Resampling.LANCZOS)
                images.append(img)
            
            # 创建GIF动图
            images[0].save(
                output_file,
                save_all=True,
                append_images=images[1:],
                duration=duration,
                loop=0  # 无限循环
            )
            
            print(f"GIF动图已保存至: {output_file}")
            print(f"包含 {len(images)} 帧，每帧持续 {duration}ms")
            
        elif output_format == 'mp4':
            print("正在生成MP4视频...")
            
            # 读取第一张图像以确定尺寸
            first_img = cv2.imread(png_files[0])
            height, width, _ = first_img.shape
            
            # 设置视频编码器和参数
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            fps = 1000 / duration  # 将毫秒转换为FPS
            
            # 创建视频写入器
            video_writer = cv2.VideoWriter(output_file, fourcc, fps, (width, height))
            
            # 逐帧写入视频
            for png_file in png_files:
                frame = cv2.imread(png_file)
                if frame is not None:
                    # 确保所有图像尺寸一致
                    if frame.shape[:2] != (height, width):
                        frame = cv2.resize(frame, (width, height))
                    video_writer.write(frame)
            
            # 释放视频写入器
            video_writer.release()
            
            print(f"MP4视频已保存至: {output_file}")
            print(f"包含 {len(png_files)} 帧，帧率 {fps:.2f} fps")
        
    finally:
        # 清理临时文件
        shutil.rmtree(temp_dir)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='将PCB文件目录转换为GIF动图或MP4视频',
        usage='python pcb_to_gif.py -d <pcb_directory> -o <output.gif/mp4> [--format gif/mp4]'
    )
    
    parser.add_argument('-d', '--directory', type=str, required=True, 
                       help='包含PCB文件的目录路径')
    parser.add_argument('-o', '--output', type=str, required=True,
                       help='输出文件路径（.gif 或 .mp4）')
    parser.add_argument('--duration', type=int, default=100,
                       help='每帧显示时间（毫秒），默认100ms')
    parser.add_argument('--max-files', type=int, default=None,
                       help='最大处理文件数量，默认处理所有文件')
    parser.add_argument('--format', type=str, choices=['gif', 'mp4'], default='gif',
                       help='输出格式：gif 或 mp4，默认为 gif')
    
    args = parser.parse_args()
    
    # 检查输入目录是否存在
    if not os.path.exists(args.directory):
        print(f"错误: 目录 {args.directory} 不存在")
        sys.exit(1)
    
    # 检查输出文件扩展名
    if args.format == 'gif' and not args.output.lower().endswith('.gif'):
        print(f"错误: 选择GIF格式时，输出文件必须以.gif结尾，当前为: {args.output}")
        sys.exit(1)
    elif args.format == 'mp4' and not args.output.lower().endswith('.mp4'):
        print(f"错误: 选择MP4格式时，输出文件必须以.mp4结尾，当前为: {args.output}")
        sys.exit(1)
    
    # 确保输出目录存在
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 生成视频文件
    create_gif_from_pcb_directory(
        args.directory, 
        args.output, 
        duration=args.duration,
        max_files=args.max_files,
        output_format=args.format
    )

if __name__ == '__main__':
    main() 
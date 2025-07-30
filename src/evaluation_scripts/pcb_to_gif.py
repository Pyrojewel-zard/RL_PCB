#!/usr/bin/env python3
"""
PCB文件转GIF动图生成器
读取指定目录下的所有PCB文件，将它们转换为PNG图像，然后生成GIF动图
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

def create_gif_from_pcb_directory(pcb_dir, output_gif, duration=500, max_files=None):
    """
    从PCB目录创建GIF动图
    
    Args:
        pcb_dir (str): 包含PCB文件的目录路径
        output_gif (str): 输出GIF文件路径
        duration (int): 每帧显示时间（毫秒）
        max_files (int): 最大处理文件数量，None表示处理所有文件
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
                # 保存为PNG文件
                png_file = os.path.join(temp_dir, f"frame_{i:04d}.png")
                cv2.imwrite(png_file, img)
                png_files.append(png_file)
            else:
                print(f"跳过文件: {pcb_file}")
        
        if not png_files:
            print("没有成功转换的图像文件！")
            return
        
        print(f"成功转换 {len(png_files)} 个图像文件")
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
            output_gif,
            save_all=True,
            append_images=images[1:],
            duration=duration,
            loop=0  # 无限循环
        )
        
        print(f"GIF动图已保存至: {output_gif}")
        print(f"包含 {len(images)} 帧，每帧持续 {duration}ms")
        
    finally:
        # 清理临时文件
        shutil.rmtree(temp_dir)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='将PCB文件目录转换为GIF动图',
        usage='python pcb_to_gif.py -d <pcb_directory> -o <output.gif>'
    )
    
    parser.add_argument('-d', '--directory', type=str, required=True, 
                       help='包含PCB文件的目录路径')
    parser.add_argument('-o', '--output', type=str, required=True,
                       help='输出GIF文件路径')
    parser.add_argument('--duration', type=int, default=500,
                       help='每帧显示时间（毫秒），默认500ms')
    parser.add_argument('--max-files', type=int, default=None,
                       help='最大处理文件数量，默认处理所有文件')
    
    args = parser.parse_args()
    
    # 检查输入目录是否存在
    if not os.path.exists(args.directory):
        print(f"错误: 目录 {args.directory} 不存在")
        sys.exit(1)
    
    # 确保输出目录存在
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 生成GIF
    create_gif_from_pcb_directory(
        args.directory, 
        args.output, 
        duration=args.duration,
        max_files=args.max_files
    )

if __name__ == '__main__':
    main() 
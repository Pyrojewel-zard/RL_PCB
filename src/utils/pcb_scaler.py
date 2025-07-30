#!/usr/bin/env python3
"""
PCB缩放工具
功能：将PCB文件中的所有坐标和尺寸按指定比例进行缩放
"""

import os
import sys
import re
import argparse
from typing import List, Tuple


class PCBScaler:
    """PCB缩放器"""
    
    def __init__(self, scale_factor: float = 5.0):
        self.scale_factor = scale_factor
        
    def scale_coordinate_value(self, value_str: str) -> str:
        """缩放单个坐标值"""
        try:
            value = float(value_str)
            scaled_value = value * self.scale_factor
            return f"{scaled_value:.3f}"
        except ValueError:
            return value_str
    
    def scale_node_line(self, line: str) -> str:
        """缩放节点行的坐标和尺寸"""
        # 节点格式: id,name,width,height,x,y,orientation,layer,is_placed,pins,pins_smd,pins_th,type
        fields = line.split(',')
        if len(fields) >= 6:
            # 缩放尺寸 (width, height)
            fields[2] = self.scale_coordinate_value(fields[2])  # width
            fields[3] = self.scale_coordinate_value(fields[3])  # height
            # 缩放位置 (x, y)
            fields[4] = self.scale_coordinate_value(fields[4])  # x
            fields[5] = self.scale_coordinate_value(fields[5])  # y
        return ','.join(fields)
    
    def scale_edge_line(self, line: str) -> str:
        """缩放边行的坐标"""
        # 边格式较复杂，包含两个节点的信息
        fields = line.split(',')
        if len(fields) >= 15:
            # 节点A的尺寸和位置 (索引3-6)
            fields[3] = self.scale_coordinate_value(fields[3])  # a_size_x
            fields[4] = self.scale_coordinate_value(fields[4])  # a_size_y
            fields[5] = self.scale_coordinate_value(fields[5])  # a_pos_x
            fields[6] = self.scale_coordinate_value(fields[6])  # a_pos_y
            
            # 节点B的尺寸和位置 (索引11-14)
            if len(fields) >= 15:
                fields[11] = self.scale_coordinate_value(fields[11])  # b_size_x
                fields[12] = self.scale_coordinate_value(fields[12])  # b_size_y
                fields[13] = self.scale_coordinate_value(fields[13])  # b_pos_x
                fields[14] = self.scale_coordinate_value(fields[14])  # b_pos_y
                
        return ','.join(fields)
    
    def scale_board_line(self, line: str) -> str:
        """缩放板子边界框坐标"""
        line = line.strip()
        if ',' in line:
            key, value = line.split(',', 1)
            if key.strip() in ['bb_min_x', 'bb_min_y', 'bb_max_x', 'bb_max_y']:
                scaled_value = self.scale_coordinate_value(value.strip())
                return f"{key},{scaled_value}"
        return line
    
    def scale_pcb_file(self, input_file: str, output_file: str) -> bool:
        """缩放PCB文件"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            scaled_lines = []
            current_section = None
            indent_level = 0
            
            for line in lines:
                # 计算缩进级别
                original_line = line
                stripped_line = line.lstrip('\t')
                indent_level = len(line) - len(stripped_line)
                
                # 去除行末的换行符进行处理
                line_content = stripped_line.strip()
                
                # 识别当前部分
                if line_content == "nodes begin":
                    current_section = "nodes"
                elif line_content == "nodes end":
                    current_section = None
                elif line_content == "edges begin":
                    current_section = "edges"
                elif line_content == "edges end":
                    current_section = None
                elif line_content == "board begin":
                    current_section = "board"
                elif line_content == "board end":
                    current_section = None
                elif line_content.startswith("hpwl="):
                    # 缩放HPWL值
                    hpwl_value = line_content.split('=')[1]
                    scaled_hpwl = self.scale_coordinate_value(hpwl_value)
                    line_content = f"hpwl={scaled_hpwl}"
                
                # 根据当前部分进行缩放处理
                if current_section == "nodes" and line_content and not line_content.endswith("begin") and not line_content.endswith("end"):
                    line_content = self.scale_node_line(line_content)
                elif current_section == "edges" and line_content and not line_content.endswith("begin") and not line_content.endswith("end"):
                    line_content = self.scale_edge_line(line_content)
                elif current_section == "board" and line_content and not line_content.endswith("begin") and not line_content.endswith("end"):
                    line_content = self.scale_board_line(line_content)
                
                # 重建带缩进的行
                if line_content:
                    rebuilt_line = '\t' * indent_level + line_content + '\n'
                else:
                    rebuilt_line = original_line
                
                scaled_lines.append(rebuilt_line)
            
            # 写入缩放后的文件
            with open(output_file, 'w', encoding='utf-8') as f:
                f.writelines(scaled_lines)
            
            print(f"PCB文件已成功缩放 {self.scale_factor} 倍")
            print(f"输入文件: {input_file}")
            print(f"输出文件: {output_file}")
            return True
            
        except Exception as e:
            print(f"缩放PCB文件时出错: {e}")
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='PCB文件缩放工具')
    parser.add_argument('input_file', help='输入PCB文件路径')
    parser.add_argument('-o', '--output', help='输出PCB文件路径（默认为输入文件名_scaled.pcb）')
    parser.add_argument('-s', '--scale', type=float, default=5.0, help='缩放倍数（默认为5.0）')
    
    args = parser.parse_args()
    
    # 检查输入文件是否存在
    if not os.path.exists(args.input_file):
        print(f"错误: 输入文件 '{args.input_file}' 不存在")
        return 1
    
    # 确定输出文件名
    if args.output:
        output_file = args.output
    else:
        # 自动生成输出文件名
        input_dir = os.path.dirname(args.input_file)
        input_name = os.path.basename(args.input_file)
        name_without_ext = os.path.splitext(input_name)[0]
        output_file = os.path.join(input_dir, f"{name_without_ext}_scaled_{args.scale}x.pcb")
    
    # 创建缩放器并执行缩放
    scaler = PCBScaler(scale_factor=args.scale)
    success = scaler.scale_pcb_file(args.input_file, output_file)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main()) 
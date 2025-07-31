"""Module for parsing command line arguments"""
import argparse
import cv2
import numpy as np
from pcb import pcb
import sys
sys.path.append('../training/')
from pcbDraw import draw_board_from_board_and_graph_with_debug, draw_ratsnest_with_board

def command_line_args():
    """
    解析用于将PCB文件转换为PNG图像的命令行参数。

    Returns:
        tuple: 包含两个元素的元组:
            - args (argparse.Namespace): 解析后的命令行参数对象
            - settings (dict): 包含脚本设置的字典，主要有:
                * 'pcb': 输入的PCB文件路径
                * 'output': 输出的PNG文件路径

    Raises:
        SystemExit: 如果缺少必需的参数会触发argparse自动退出程序

    Example:
        >>> args, settings = command_line_args()
        >>> print(settings['pcb'])  # 打印输入的PCB文件路径
        >>> print(settings['output'])  # 打印输出的PNG文件路径
    """
    parser = argparse.ArgumentParser(description='Python script for generating\
             a .png image from a .pcb file.', usage='python pcb2png.py -p \
            <pcb_file>')

    parser.add_argument('-p', '--pcb', type=str, required=True)  # ⭐ 定义必须的PCB文件输入参数
    parser.add_argument('-o', '--output', type=str, required=True)  # ⭐ 定义必须的PNG输出路径参数

    args = parser.parse_args()
    settings = {}

    settings['pcb'] = args.pcb
    settings['output'] = args.output

    return args, settings

def main():
    """
    主函数，负责将PCB文件转换为PNG图像。
    
    流程:
    1. 解析命令行参数获取设置
    2. 读取PCB文件并初始化PCB视图
    3. 绘制PCB板的组件布局网格
    4. 绘制所有节点的飞线连接关系
    5. 合成组件布局和飞线图像并输出PNG
    
    Returns:
        None
    """
    _, settings = command_line_args()
    pv = pcb.vptr_pcbs()
    pcb.read_pcb_file(settings['pcb'], pv)      # ⭐ 读取并解析PCB文件
    p = pv[0]

    g = p.get_graph()
    g.reset()
    b = p.get_board()
    g.set_component_origin_to_zero(b)

    comp_grids = draw_board_from_board_and_graph_with_debug(b, g, padding=0.5)

    ratsnest = None
    nn = g.get_nodes()
    for i in range(len(nn)):
        node_id = nn[i].get_id()
        nets = []

        neighbor_ids = g.get_neighbor_node_ids(node_id)
        neighbors = []
        for n_id in neighbor_ids:
            neighbors.append(g.get_node_by_id(n_id))

        ee = g.get_edges()
        eoi = []
        for e in ee:
            if e.get_instance_id(0) == node_id or e.get_instance_id(1) == node_id:
                eoi.append(e)
                nets.append(e.get_net_id)

        if i == 0:
            ratsnest = draw_ratsnest_with_board(nn[i], neighbors, eoi, b,
                                          line_thickness=1, padding=0.5,
                                          ignore_power=True)
        else:
            ratsnest = np.maximum(ratsnest,
                            draw_ratsnest_with_board(nn[i], neighbors, eoi, b,
                                                     line_thickness=1,
                                                     padding=0.5,
                                                     ignore_power=True)
                            )
    # 打印comp_grids[0]的shape
    print(comp_grids[0].shape)
    print(comp_grids[1].shape)
    img = comp_grids[0] + 2*comp_grids[1]       # ⭐ 合成组件布局图层
    img = np.maximum(img, ratsnest)             # ⭐ 叠加飞线图层
    cv2.imwrite(settings['output'], img)        # ⭐ 输出最终PNG图像

if __name__ == '__main__':
    main()

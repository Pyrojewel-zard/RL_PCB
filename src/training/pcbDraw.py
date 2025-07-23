#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  2 15:38:05 2022

@author: luke
"""

import numpy as np
import cv2
from graph_utils import kicad_rotate
from pcb_board import board_maskast#导入屏蔽罩二值数据
import sys
from pcb_python import pcb
from pcb_python import Graph
from pcb_python import Board
from pcb_python import Node
from pcb_python import Edge

r = 0.1    # resolution in mm

def draw_board_from_board_and_graph(b,
                                    g,
                                    draw_placed=True,
                                    draw_unplaced=True,
                                    padding=None,
                                    line_thickness=-1):
    """
    根据电路板和元件图生成包含已放置/未放置元件的灰度图像网格

    Args:
        b (board): 电路板对象，包含宽度和高度信息
        g (graph): 元件图对象，包含所有元件节点
        draw_placed (bool, optional): 是否绘制已放置元件. 默认为True
        draw_unplaced (bool, optional): 是否绘制未放置元件. 默认为True
        padding (float, optional): 图像边距填充值(mm). 默认为None
        line_thickness (int, optional): 轮廓线粗细. -1表示填充. 默认为-1

    Returns:
        list: 包含两个numpy数组的列表:
            - 位置0: 已放置元件的灰度图像
            - 位置1: 未放置元件的灰度图像
            如果指定padding，会添加边框并合并结果
    """
    nv = g.get_nodes()

    # Setup grid
    x = b.get_width() / r
    y = b.get_height() / r

    if padding is not None:
        grid_comps = np.zeros(
            (2,int(x)+2*int(padding/r),int(y)+2*int(padding/r),1),
            np.uint8)
    else:
        grid_comps = np.zeros((2,int(x),int(y),1), np.uint8)

    for n in nv:
        pos = n.get_pos()
        size = n.get_size()
        orientation = n.get_orientation()

        if padding is not None:
            xc = float(pos[0]) / r + int(padding/r)
            yc = float(pos[1]) / r + int(padding/r)
        else:
            xc = float(pos[0]) / r
            yc = float(pos[1]) / r

        sz_x = float(size[0]) / r
        sz_y = float(size[1]) / r
        # convert the center, size and orientation to rectange points
        box = cv2.boxPoints(((xc,yc), (sz_x,sz_y), -orientation))  # ⭐ 将元件转换为旋转矩形轮廓点
        box = np.int0(box)  # ensure that box point are integers
        if n.get_isPlaced() == 1:
            cv2.drawContours(grid_comps[0],[box],0,(64),line_thickness)
        else:
            cv2.drawContours(grid_comps[1],[box],0,(64),line_thickness)

    if padding is not None:
        border = np.zeros((int(x),int(y),1), np.uint8)
        border = cv2.copyMakeBorder(border,
                                    int(padding/r),
                                    int(padding/r),
                                    int(padding/r),
                                    int(padding/r),
                                    cv2.BORDER_CONSTANT,
                                    value=(64))

        return [cv2.copyMakeBorder(grid_comps[0],
                                   0, 0, 0, 0,
                                   cv2.BORDER_CONSTANT,
                                   value=(64)) + border,
              cv2.copyMakeBorder(grid_comps[1],
                                 0, 0, 0, 0,
                                 cv2.BORDER_CONSTANT,
                                 value=(0))]
    else:
        return grid_comps

def draw_board_from_board_and_graph_with_debug(b,
                                               g,
                                               draw_placed=True,
                                               draw_unplaced=True,
                                               padding=None,
                                               line_thickness=-1):
    """
    根据电路板布局和元件图生成带有调试信息的灰度图像，可分别绘制已放置和未放置的元件。

    Args:
        b: 电路板对象，包含宽度和高度信息
        g: 元件图对象，包含节点信息
        draw_placed (bool, optional): 是否绘制已放置元件，默认为True
        draw_unplaced (bool, optional): 是否绘制未放置元件，默认为True
        padding (int, optional): 图像边距大小，单位为像素
        line_thickness (int, optional): 绘制线条的粗细，-1表示填充

    Returns:
        list: 包含三个灰度图像的三维numpy数组:
            [0] 已放置元件的图像
            [1] 未放置元件的图像 
            [2] 元件名称标注图像
    """
    nv = g.get_nodes()

    # Setup grid
    x = b.get_width() / r
    y = b.get_height() / r

    if padding is not None:
        grid_comps = np.zeros(
            (3,int(x)+2*int(padding/r),int(y)+2*int(padding/r),1),
            np.uint8)
    else:
        grid_comps = np.zeros((3,int(x),int(y),1), np.uint8)

    for n in nv:
        pos = n.get_pos()
        size = n.get_size()
        orientation = n.get_orientation()

        if padding is not None:
            xc = float(pos[0]) / r + int(padding/r)
            yc = float(pos[1]) / r + int(padding/r)
        else:
            xc = float(pos[0]) / r
            yc = float(pos[1]) / r

        sz_x = float(size[0]) / r
        sz_y = float(size[1]) / r
        # convert the center, size and orientation to rectange points
        box = cv2.boxPoints(((xc,yc), (sz_x,sz_y), -orientation))  # ⭐ 将元件位置和尺寸转换为矩形顶点坐标
        box = np.int0(box)  # ensure that box point are integers
        if n.get_isPlaced() == 1:
            cv2.drawContours(grid_comps[0],[box],0,(64),line_thickness)
        else:
            cv2.drawContours(grid_comps[1],[box],0,(64),line_thickness)

        if padding is not None:
            tmp = draw_node_name(n,
                                 b.get_width(),
                                 b.get_height(),
                                 padding=padding)
            tmp = np.reshape(tmp,(tmp.shape[0],tmp.shape[1],1))
            grid_comps[2] = np.maximum(tmp, grid_comps[2])

    if padding is not None:
        border = np.zeros((int(x),int(y),1), np.uint8)
        border = cv2.copyMakeBorder(border,
                                    int(padding/r),
                                    int(padding/r),
                                    int(padding/r),
                                    int(padding/r),
                                    cv2.BORDER_CONSTANT,
                                    value=(64))

        return [cv2.copyMakeBorder(grid_comps[0],
                                   0, 0, 0, 0,
                                   cv2.BORDER_CONSTANT,
                                   value=(64)) + border,
                cv2.copyMakeBorder(grid_comps[1],
                                   0, 0, 0, 0,
                                   cv2.BORDER_CONSTANT,
                                   value=(0)),
                cv2.copyMakeBorder(grid_comps[2],
                                   0, 0, 0, 0,
                                   cv2.BORDER_CONSTANT,
                                   value=(0))
                                   ]
    else:
        return grid_comps

def draw_board_from_board_and_graph_multi_agent(b, g,
                                                node_id,
                                                draw_placed=True,
                                                draw_unplaced=True,
                                                padding=None,
                                                line_thickness=-1):
    """
    根据电路板布局和元件图生成多通道灰度图像，支持对特定元件的突出显示。

    Args:
        b: 电路板对象，包含宽度和高度信息
        g: 元件图对象，包含所有元件节点信息
        node_id: 需要突出显示的元件ID
        draw_placed: 是否绘制已放置元件，默认为True
        draw_unplaced: 是否绘制未放置元件，默认为True
        padding: 图像填充像素，可选参数
        line_thickness: 元件轮廓线粗细，-1表示填充

    Returns:
        list: 包含多个灰度图像层的堆栈，首层为电路板边框，后续层为各元件
    """
    nv = g.get_nodes()

    # Setup grid
    x = b.get_width() / r
    y = b.get_height() / r

    if padding is not None:
        grid_comps = np.zeros(
            (len(nv)+1,int(x)+2*int(padding/r),int(y)+2*int(padding/r),1),
            np.uint8)
    else:
        grid_comps = np.zeros((len(nv)+1,int(x),int(y),1), np.uint8)
    idx = 2
    for n in nv:
        pos = n.get_pos()
        size = n.get_size()
        orientation = n.get_orientation()

        if padding is not None:
            xc = float(pos[0]) / r + int(padding/r)
            yc = float(pos[1]) / r + int(padding/r)
        else:
            xc = float(pos[0]) / r
            yc = float(pos[1]) / r

        sz_x = float(size[0]) / r
        sz_y = float(size[1]) / r
        # convert the center, size and orientation to rectange points
        box = cv2.boxPoints(((xc,yc), (sz_x,sz_y), -orientation))  # ⭐ 将元件几何参数转换为绘制用的矩形框坐标
        box = np.int0(box)  # ensure that box point are integers
        if n.get_id() == node_id:
            cv2.drawContours(grid_comps[1],[box],0,(64),line_thickness)
        else:
            cv2.drawContours(grid_comps[idx],[box],0,(64),line_thickness)
            idx +=1

    if padding is not None:
        border = np.zeros((int(x),int(y),1), np.uint8)
        border = cv2.copyMakeBorder(border,
                                    int(padding/r),
                                    int(padding/r),
                                    int(padding/r),
                                    int(padding/r),
                                    cv2.BORDER_CONSTANT,
                                    value=(64))

        stack = []

        stack.append(cv2.copyMakeBorder(grid_comps[0],
                                        0, 0, 0, 0,
                                        cv2.BORDER_CONSTANT,
                                        value=(64)) + border)  # ⭐ 生成带边框的电路板基础层
        for i in range(1, idx, 1):
            stack.append(cv2.copyMakeBorder(grid_comps[i],
                                            0, 0, 0, 0,
                                            cv2.BORDER_CONSTANT,
                                            value=(0)))
        return stack
    else:
        print("draw_board_from_board_and_graph_multi_agent requires padding.")
        sys.exit()

def draw_comps_from_nodes_and_edges(n, nn, e, b, padding=None):
    """
    根据节点和边缘信息绘制PCB元件布局图，生成包含已放置和未放置元件的灰度图像网格。

    Args:
        n: 当前节点对象，包含位置、尺寸和方向信息
        nn: 邻居节点列表，每个节点包含位置、尺寸和方向信息
        e: 边缘信息（未在函数中使用）
        b: 板子对象，包含板子的宽度和高度信息
        padding: 可选参数，指定图像边界的填充大小

    Returns:
        list: 包含两个元素的列表，第一个元素是已放置元件的图像网格，
              第二个元素是未放置元件的图像网格
    """
    # Setup grid
    x = b.get_width() / r
    y = b.get_height() / r

    if padding is not None:
        grid_comps = np.zeros(
            (2,int(x)+2*int(padding/r),int(y)+2*int(padding/r),1), np.uint8)
    else:
        grid_comps = np.zeros((2,int(x),int(y),1), np.uint8)

    # draw current node
    pos = n.get_pos()
    size = n.get_size()
    orientation = n.get_orientation()

    if padding is not None:
        xc = float(pos[0]) / r + int(padding/r)
        yc = float(pos[1]) / r + int(padding/r)
    else:
        xc = float(pos[0]) / r
        yc = float(pos[1]) / r

    sz_x = float(size[0]) / r
    sz_y = float(size[1]) / r
    # convert the center, size and orientation to rectange points
    box = cv2.boxPoints(((xc,yc), (sz_x,sz_y), -orientation))  # ⭐ 将元件信息转换为矩形框坐标点
    box = np.int0(box)  # ensure that box point are integers
    if n.get_isPlaced() == 1: # should always return False!
        cv2.drawContours(grid_comps[0],[box],0,(64),-1)
    else:
        cv2.drawContours(grid_comps[1],[box],0,(64),-1)

    # draw neighbor nodes
    for v in nn:
        pos = v.get_pos()
        size = v.get_size()
        orientation = v.get_orientation()

        if padding is not None:
            xc = float(pos[0]) / r + int(padding/r)
            yc = float(pos[1]) / r + int(padding/r)
        else:
            xc = float(pos[0]) / r
            yc = float(pos[1]) / r

        sz_x = float(size[0]) / r
        sz_y = float(size[1]) / r
        # convert the center, size and orientation to rectange points
        box = cv2.boxPoints(((xc,yc), (sz_x,sz_y), -orientation))
        box = np.int0(box)  # ensure that box point are integers
        if v.get_isPlaced() == 1:  # should always return True!
            cv2.drawContours(grid_comps[0],[box],0,(64),-1)
        else:
            cv2.drawContours(grid_comps[1],[box],0,(64),-1)

    if padding is not None:
        border = np.zeros((int(x),int(y),1), np.uint8)
        border = cv2.copyMakeBorder(border,
                                    int(padding/r),
                                    int(padding/r),
                                    int(padding/r),
                                    int(padding/r),
                                    cv2.BORDER_CONSTANT,
                                    value=(64))

        return [cv2.copyMakeBorder(grid_comps[0],
                                   0, 0, 0, 0,
                                   cv2.BORDER_CONSTANT,
                                   value=(64)) + border,
                cv2.copyMakeBorder(grid_comps[1],
                                   0, 0, 0, 0,
                                   cv2.BORDER_CONSTANT,
                                   value=(0))]
    else:
        return grid_comps

# The following is the difference between this and the prior method
# neighbor nodes are always treated as 'locked'
# current node is always treated as 'unlocked'
def draw_board_from_nodes_and_edges_multi_agent(n,
                                                nn,
                                                e,
                                                bx,
                                                by,
                                                padding=None):
    """
    根据节点和边缘信息绘制PCB板布局图，生成包含当前节点、相邻节点和边界的灰度图像矩阵。

    Args:
        n: 当前节点对象，包含位置、尺寸和方向信息
        nn: 相邻节点对象列表
        e: 边缘信息（未使用）
        bx: 板子x方向尺寸
        by: 板子y方向尺寸
        padding: 可选参数，指定边界填充大小

    Returns:
        list/numpy.ndarray: 包含各组件图像的数组，索引0为边界，1为当前节点，2+为相邻节点
    """
    # Setup grid
    x = bx / r
    y = by / r

    if padding is not None:
        grid_comps = np.zeros(
            (len(nn)+2,int(x)+2*int(padding/r),int(y)+2*int(padding/r),1),
             np.uint8)
    else:
        grid_comps = np.zeros((len(nn)+2,int(x),int(y),1), np.uint8)

    # draw current node
    pos = n.get_pos()
    size = n.get_size()
    orientation = n.get_orientation()

    if padding is not None:
        xc = float(pos[0]) / r + int(padding/r)
        yc = float(pos[1]) / r + int(padding/r)
    else:
        xc = float(pos[0]) / r
        yc = float(pos[1]) / r

    sz_x = float(size[0]) / r
    sz_y = float(size[1]) / r
    # convert the center, size and orientation to rectange points
    box = cv2.boxPoints(((xc,yc), (sz_x,sz_y), -orientation))  # ⭐ 将节点转换为矩形轮廓点
    box = np.int0(box)  # ensure that box point are integers
    cv2.drawContours(grid_comps[1],[box],0,(64),-1)

    idx =2
    # draw neighbor nodes
    for v in nn:
        pos = v.get_pos()
        size = v.get_size()
        orientation = v.get_orientation()

        if padding is not None:
            xc = float(pos[0]) / r + int(padding/r)
            yc = float(pos[1]) / r + int(padding/r)
        else:
            xc = float(pos[0]) / r
            yc = float(pos[1]) / r

        sz_x = float(size[0]) / r
        sz_y = float(size[1]) / r
        # convert the center, size and orientation to rectange points
        box = cv2.boxPoints(((xc,yc), (sz_x,sz_y), -orientation))
        box = np.int0(box)  # ensure that box point are integers
        cv2.drawContours(grid_comps[idx],[box],0,(64),-1)
        idx += 1

    if padding is not None:
        border = np.zeros((int(x),int(y),1), np.uint8)
        border = cv2.copyMakeBorder(border,
                                    int(padding/r),
                                    int(padding/r),
                                    int(padding/r),
                                    int(padding/r),
                                    cv2.BORDER_CONSTANT,
                                    value=(64))

        tmp =[]
        for i in range(len(nn)+2):
            if i == 0:
                tmp.append(cv2.copyMakeBorder(
                    grid_comps[0],
                    0, 0, 0, 0,
                    cv2.BORDER_CONSTANT,
                    value=(64)) + border)  # ⭐ 合并边界和填充区域
            else:
                tmp.append(cv2.copyMakeBorder(
                    grid_comps[i],
                    0, 0, 0, 0,
                    cv2.BORDER_CONSTANT,
                    value=(0)))
        return tmp
    else:
        return grid_comps

# idx = 0 ( grid border )
# idx = 1 ( current node  )
# idx = 2 ... ( neighbors ... )
def draw_board_from_graph_multi_agent(g, node_id, bx, by, padding=None):
    """
    根据电路板布局图和多智能体信息生成元件位置的灰度图像网格。

    Args:
        g: 包含节点信息的图对象
        node_id: 当前需要特殊标记的节点ID
        bx: 电路板x方向尺寸
        by: 电路板y方向尺寸
        padding: 可选参数，图像填充边界大小

    Returns:
        list: 包含各元件位置信息的灰度图像网格列表
    """
    # Setup grid
    x = bx / r
    y = by / r

    all_nodes = g.get_nodes()

    if padding is not None:
        grid_comps = np.zeros(
            (len(all_nodes)+1,int(x)+2*int(padding/r),int(y)+2*int(padding/r),1),
            np.uint8)
    else:
        grid_comps = np.zeros((len(all_nodes)+1,int(x),int(y),1), np.uint8)

    idx =2
    # draw neighbor nodes
    for i in range(len(all_nodes)):
        pos = all_nodes[i].get_pos()
        size = all_nodes[i].get_size()
        orientation = all_nodes[i].get_orientation()
        current_node_id = all_nodes[i].get_id()

        if padding is not None:
            xc = float(pos[0]) / r + int(padding/r)
            yc = float(pos[1]) / r + int(padding/r)
        else:
            xc = float(pos[0]) / r
            yc = float(pos[1]) / r

        sz_x = float(size[0]) / r
        sz_y = float(size[1]) / r
        # convert the center, size and orientation to rectange points
        box = cv2.boxPoints(((xc,yc), (sz_x,sz_y), -orientation))  # ⭐ 将元件位置和方向转换为矩形顶点坐标
        box = np.int0(box)  # ensure that box point are integers
        if current_node_id == node_id:
            cv2.drawContours(grid_comps[1],[box],0,(64),-1)
        else:
            cv2.drawContours(grid_comps[idx],[box],0,(64),-1)
            idx += 1

    if padding is not None:
        border = np.zeros((int(x),int(y),1), np.uint8)
        border = cv2.copyMakeBorder(border,
                                    int(padding/r),
                                    int(padding/r),
                                    int(padding/r),
                                    int(padding/r),
                                    cv2.BORDER_CONSTANT,
                                    value=(64))

        tmp =[]
        for i in range(len(all_nodes)+1):
            if i == 0:
                tmp.append(cv2.copyMakeBorder(grid_comps[0],
                                              0, 0, 0, 0,
                                              cv2.BORDER_CONSTANT,
                                              value=(64)) + border)
            else:
                tmp.append(cv2.copyMakeBorder(grid_comps[i],
                                              0, 0, 0, 0,
                                              cv2.BORDER_CONSTANT,
                                              value=(0)))

        return tmp
    else:
        return grid_comps

# only comp_grids[0] is used.
def draw_board_from_nodes_multi_agent(n, bx, by, padding=None):
    """
    根据节点信息在PCB板上绘制多个元件，生成包含元件布局的图像数组。

    Args:
        n (list): 包含元件节点对象的列表，每个节点应包含位置、尺寸和方向信息
        bx (float): PCB板的x方向长度
        by (float): PCB板的y方向长度
        padding (float, optional): 要添加的边界填充大小，默认为None

    Returns:
        list: 包含两个通道的图像数组，第一个通道表示元件布局，第二个通道保留为空白
    """
    # Setup grid
    x = bx / r
    y = by / r

    if padding is not None:
        grid_comps = np.zeros(
            (2,int(x)+2*int(padding/r),int(y)+2*int(padding/r),1),
            np.uint8)
    else:
        grid_comps = np.zeros((2,int(x),int(y),1), np.uint8)

    # draw nodes
    for v in n:
        pos = v.get_pos()
        size = v.get_size()
        orientation = v.get_orientation()

        if padding is not None:
            xc = float(pos[0]) / r + int(padding/r)
            yc = float(pos[1]) / r + int(padding/r)
        else:
            xc = float(pos[0]) / r
            yc = float(pos[1]) / r

        sz_x = float(size[0]) / r
        sz_y = float(size[1]) / r
        # convert the center, size and orientation to rectange points
        box = cv2.boxPoints(((xc,yc), (sz_x,sz_y), -orientation))  # ⭐ 将元件信息转换为矩形顶点坐标
        box = np.int0(box)  # ensure that box point are integers
        cv2.drawContours(grid_comps[0],[box],0,(64),-1)

    if padding is not None:
        border = np.zeros((int(x),int(y),1), np.uint8)
        border = cv2.copyMakeBorder(border,
                                    int(padding/r),
                                    int(padding/r),
                                    int(padding/r),
                                    int(padding/r),
                                    cv2.BORDER_CONSTANT,
                                    value=(64))

        return [cv2.copyMakeBorder(grid_comps[0],
                                   0, 0, 0, 0,
                                   cv2.BORDER_CONSTANT,
                                   value=(64)) + border,
              cv2.copyMakeBorder(grid_comps[1],
                                 0, 0, 0, 0,
                                 cv2.BORDER_CONSTANT,
                                 value=(0))]
    else:
        return grid_comps

def draw_ratsnest_with_board(current_node,
                             neighbor_nodes,
                             e,
                             b,
                             line_thickness=1,
                             padding=None,
                             ignore_power=False):
    """
    在PCB板上绘制鼠线网络，通过获取电路板尺寸后调用核心绘制函数。

    Args:
        current_node: 当前需要绘制连接的中心节点
        neighbor_nodes: 与当前节点有连接关系的相邻节点列表
        e: 电路板布局信息对象
        b: 电路板对象，用于获取尺寸信息
        line_thickness (int): 鼠线线条的粗细，默认为1
        padding: 绘制时的边距参数
        ignore_power (bool): 是否忽略电源网络的连接，默认为False

    Returns:
        返回鼠线网络的绘制结果
    """
    # Setup grid
    bx = b.get_width()  # ⭐ 获取电路板宽度作为绘制区域尺寸
    by = b.get_height()  # ⭐ 获取电路板高度作为绘制区域尺寸

    return draw_ratsnest(current_node,
                         neighbor_nodes,
                         e,
                         bx,
                         by,
                         line_thickness=line_thickness,
                         padding=padding,
                         ignore_power=ignore_power)

def draw_ratsnest(current_node,
                  neighbor_nodes,
                  e,
                  bx,
                  by,
                  line_thickness=1,
                  padding=None,
                  ignore_power=False):
    """
    绘制PCB板上的飞线连接图。

    Args:
        current_node: 当前处理的节点对象
        neighbor_nodes: 相邻节点对象列表
        e: 边/连接关系列表
        bx: 画布宽度基准值
        by: 画布高度基准值
        line_thickness: 飞线宽度，默认为1
        padding: 画布边距，默认为None
        ignore_power: 是否忽略电源线，默认为False

    Returns:
        numpy.ndarray: 包含飞线连接的灰度图像数组
    """
    x = bx / r
    y = by / r

    if padding is not None:
        ratsnest = np.zeros(
            (int(x)+2*int(padding/r),int(y)+2*int(padding/r),1),
            np.uint8)
    else:
        ratsnest = np.zeros((int(x),int(y),1), np.uint8)

    # draw current node
    current_node_id = current_node.get_id()
    current_node_pos = current_node.get_pos()
    current_node_orientation = current_node.get_orientation()

    src = []
    dst = []
    for ee in e:
        if (ignore_power is True) and (ee.get_power_rail() > 0):
            continue
        # Get list of pos, size for all
        for i in range(2):
            if ee.get_instance_id(i) == current_node_id:
                pad_pos = ee.get_pos(i)
                # rotate pad positions so that they match the component's
                # orientation
                rotated_pad_pos = kicad_rotate(float(pad_pos[0]),
                                               float(pad_pos[1]),
                                               current_node_orientation)
                src.append([current_node_pos[0] + rotated_pad_pos[0],
                            current_node_pos[1] + rotated_pad_pos[1]
                            ])
            else:
                for n in neighbor_nodes:
                    if ee.get_instance_id(i) == n.get_id():
                        neighbor_node_pos = n.get_pos()
                        pad_pos = ee.get_pos(i)
                        # rotate pad positions so that they match the
                        # component's orientation
                        rotated_pad_pos = kicad_rotate(float(pad_pos[0]),
                                                       float(pad_pos[1]),
                                                       n.get_orientation())

                        dst.append([neighbor_node_pos[0] + rotated_pad_pos[0],
                                    neighbor_node_pos[1] + rotated_pad_pos[1]
                                    ])
                        break

    for i in range(min(len(src),len(dst))):
        if padding is not None:
            sx = int(src[i][0]/r) + int(padding/r)
            sy = int(src[i][1]/r) + int(padding/r)

            dx = int(dst[i][0]/r) + int(padding/r)
            dy = int(dst[i][1]/r) + int(padding/r)
        else:
            sx = int(src[i][0]/r)
            sy = int(src[i][1]/r)

            dx = int(dst[i][0]/r)
            dy = int(dst[i][1]/r)

        # image, pt1 (x,y), pt2, color (BGR), thickness
        cv2.line(ratsnest,
                 (sx,sy),
                 (dx,dy),
                 (255),
                 line_thickness)  # ⭐ 核心代码：在图像上绘制飞线连接

    if padding is not None:
        return cv2.copyMakeBorder(ratsnest,
                                  0, 0, 0, 0,
                                  cv2.BORDER_CONSTANT,
                                  value=(0))
    else:
        return ratsnest

def draw_los(pos_x,
             pos_y,
             radius,
             angle_offset,
             bx,
             by,
             padding=None):
    """
    绘制8个45度角间隔的椭圆扇形区域（LOS区域），用于PCB布局的可视区域分析。

    Args:
        pos_x (float): 节点x坐标（未转换为像素的原始坐标）
        pos_y (float): 节点y坐标（未转换为像素的原始坐标）
        radius (float): 椭圆半径
        angle_offset (float): 角度偏移量
        bx (float): 边界x尺寸
        by (float): 边界y尺寸
        padding (float, optional): 填充尺寸. 默认为None

    Returns:
        tuple: 包含两个元素的元组：
            - 8个LOS区域的图像数组（带填充或不带填充）
            - 每个LOS区域的像素值数组
    """
    x = bx / r
    y = by / r
    if padding is not None:
        los_segments = np.zeros(
            (8,int(x)+2*int(padding/r),int(y)+2*int(padding/r),1),
            np.uint8)
    else:
        los_segments = np.zeros((8,int(x),int(y),1), np.uint8)

    padded_los_segments = []
    segment_pixels = np.zeros(8)
    if padding is not None:
        scaled_x = np.int0(pos_x / r) + int(padding/r)
        scaled_y = np.int0(pos_y / r) + int(padding/r)
    else:
        scaled_x = np.int0(pos_x / r)
        scaled_y = np.int0(pos_y / r)
    scaled_radius = np.int0(radius / r)
    start = -22.5 - angle_offset
    stop = 22.5 - angle_offset
    for i in range(8):
        cv2.ellipse(los_segments[i],
                    (scaled_x,scaled_y),
                    (scaled_radius,scaled_radius),
                    0,
                    start,
                    stop,
                    (16),
                    -1)  # ⭐ 绘制椭圆扇形区域，核心绘图操作
        segment_pixels[i] = np.sum(los_segments[i]) / 16
        start -= 45
        stop -= 45

    # this is dumb, but needed so arrays are matching.
    # copyMakeBorder reshapes the output image.
    if padding is not None:
        for i in range(8):
            padded_los_segments.append(
                cv2.copyMakeBorder(los_segments[i],
                                   0, 0, 0, 0,
                                   cv2.BORDER_CONSTANT,
                                   value=(0))
                                   )

        return np.array(padded_los_segments), segment_pixels
    else:
        return los_segments, segment_pixels

def draw_node_name(n,
                   bx,
                   by,
                   padding=None,
                   loc="top_right",
                   designator_only=False):
    """
    在PCB板图像上绘制元件名称或标识符。

    Args:
        n (object): 元件节点对象，包含位置、尺寸等信息
        bx (float): 元件边界框的x方向尺寸
        by (float): 元件边界框的y方向尺寸
        padding (int, optional): 填充像素数，默认为None
        loc (str, optional): 文本位置，可选"top_left"或"top_right"，默认为"top_right"
        designator_only (bool, optional): 是否仅显示元件名称，默认为False(显示ID和名称)

    Returns:
        numpy.ndarray: 包含绘制文本的灰度图像矩阵
    """

    x = bx / r
    y = by / r
    if padding is not None:
        grid = np.zeros(
            (int(x)+2*int(padding/r),int(y)+2*int(padding/r),1),
            np.uint8)
    else:
        grid = np.zeros((int(x),int(y),1), np.uint8)

    if loc == "top_left":
        if padding is None:
            # - 1 since text moves from left to right
            text_origin = (
                int( (n.get_pos()[0] - n.get_size()[0]/2- 1)/r ),
                int( (n.get_pos()[1] - n.get_size()[1]/2 - 0.25 )/r ))
        else:
            # - 1 since text moves from left to right
            text_origin = (
                int((n.get_pos()[0] - n.get_size()[0]/2 - 1)/r) + int(padding/r),
                int((n.get_pos()[1] - n.get_size()[1]/2 - 0.25)/r) + int(padding/r))
    else:# loc == "top_right":
        # place orientation on the top right
        if padding is None:
            text_origin = (int((n.get_pos()[0] + n.get_size()[0]/2)/r),
                        int((n.get_pos()[1] - n.get_size()[1]/2)/r))
        else:
            text_origin = (
                int((n.get_pos()[0] + n.get_size()[0]/2)/r) + int(padding/r),
                int((n.get_pos()[1] - n.get_size()[1]/2)/r) + int(padding/r))

    if designator_only is True:
        cv2.putText(img=grid,
            text=f"{n.get_name()}",
            org=text_origin,
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=0.4,
            color=(127))  # ⭐ 核心代码：在图像上绘制元件名称文本
    else:
        cv2.putText(img=grid,
                    text=f"{n.get_id()} ({n.get_name()})",
                    org=text_origin,
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.4,
                    color=127)

    # this is dumb, but needed so arrays are matching.
    # copyMakeBorder reshapes the output image.
    if padding is not None:
        return cv2.copyMakeBorder(grid,
                                  0, 0, 0, 0,
                                  cv2.BORDER_CONSTANT,
                                  value=0)
    else:
        return grid

def pcbDraw_resolution():
    """
    获取PCB绘图的分辨率参数。

    Returns:
        int/float: 返回PCB绘图的分辨率值。
    """
    return r  # ⭐ 返回核心分辨率参数

def set_pcbDraw_resolution(resolution):
    """
    设置PCB绘制工具的分辨率参数。

    Args:
        resolution (int/float): 要设置的绘制分辨率值。
    
    Note:
        该函数会修改全局变量r，影响后续所有绘制操作的分辨率。
    """
    global r
    r = resolution  # ⭐ 更新全局分辨率参数

def setup_empty_grid(bx, by, resolution, padding=None):
    """
    根据给定的边界尺寸和分辨率创建一个空的网格数组，用于表示PCB板的布局空间。

    Args:
        bx (float): x轴方向的边界尺寸
        by (float): y轴方向的边界尺寸
        resolution (float): 网格的分辨率（每单位长度对应的像素数）
        padding (float, optional): 网格边缘的填充尺寸，默认为None

    Returns:
        numpy.ndarray: 一个三维的零数组，表示空的网格空间（高度×宽度×1通道）
    """
    # Setup grid
    x = bx / resolution
    y = by / resolution

    if padding is not None:
        grid = np.zeros((int(x)+2*int(padding/r),int(y)+2*int(padding/r),1),  # ⭐ 创建带填充的3D零数组
                        np.uint8)
    else:
        grid = np.zeros((int(x),int(y),1), np.uint8)  # ⭐ 创建基础3D零数组

    return grid

def get_los_and_ol_multi_agent(node,
                               board,
                               radius,
                               grid_comps,
                               padding,
                               los_type=0):
    """
    计算多智能体系统中节点的视线(LOS)和重叠区域(OL)信息。

    Args:
        node: 当前节点对象，包含位置和方向信息
        board: PCB板对象，包含宽度和高度信息
        radius: 视线检测半径
        grid_comps: 网格组件数组，包含不同层的掩码信息
        padding: 填充像素数，用于扩展检测区域
        los_type: 检测类型(0-传统方式,1-排除当前节点,3-显示重叠区域,4-显示重叠区域和当前节点)

    Returns:
        tuple: 包含四个元素的元组，分别是:
            - 各扇区的LOS像素比例
            - 各扇区的OL像素比例
            - LOS掩码数组
            - OL掩码数组
    """
    # type 0 - traditional case
    # type 1 - remove current node from the radius.
    # type 3 - cropped grid showing overlapping section
    # type 4 - cropped grid showing overlapping section and current node.

    angle_offset = node.get_orientation()
    res = pcbDraw_resolution()
    x = board.get_width() / res
    y = board.get_height() / res
    pos = node.get_pos()
    if padding is not None:
     board_mask_img=board_maskast(x*res+2*padding,y*res+2*padding,res)#异形边框程序导入，获取二值图像
    else:
     board_mask_img=board_maskast
     (x*res,y*res,res)#异形边框程序导入，获取二值图像

    if padding is not None:
        cx = int(pos[0]/res) + int(padding/res)
        cy = int(pos[1]/res) + int(padding/res)
    else:
        cx = int(pos[0]/res)
        cy = int(pos[1]/res)

    radius = int(radius / res)

    if los_type in (0, 1):
        if padding is not None:
            los_segments_mask = np.zeros(
                (8,int(x)+2*int(padding/res),int(y)+2*int(padding/res)),
                np.uint8)
            los_segments = np.zeros(
                (8,int(x)+2*int(padding/res),int(y)+2*int(padding/res)),
                np.uint8)
            overlap_segments_mask = np.zeros(
                (8,int(x)+2*int(padding/res),int(y)+2*int(padding/res)),
                np.uint8)
            overlap_segments = np.zeros(
                (8,int(x)+2*int(padding/res),int(y)+2*int(padding/res)),
                np.uint8)
            overlap_board_mask = np.zeros(
                (8,int(x)+2*int(padding/res),int(y)+2*int(padding/res)),
                np.uint8)#新增
        else:
            los_segments_mask = np.zeros((8,int(x),int(y)), np.uint8)
            los_segments = np.zeros((8,int(x),int(y)), np.uint8)
            overlap_segments_mask = np.zeros((8,int(x),int(y)), np.uint8)
            overlap_segments = np.zeros((8,int(x),int(y)), np.uint8)
            overlap_board_mask = np.zeros((8,int(x),int(y)), np.uint8)

        segment_mask_pixels = np.zeros(8)
        segment_pixels = np.zeros(8)
        overlap_mask_pixels = np.zeros(8)
        overlap_pixels = np.zeros(8)
        overlap_boardsum=np.zeros(8)#新增
        start = -22.5 - angle_offset
        stop = 22.5 - angle_offset
        for i in range(8):
            cv2.ellipse(los_segments_mask[i],
                        (cx,cy),
                        (radius,radius),
                        0,
                        start,
                        stop,
                        (64),
                        -1)  # ⭐ 绘制扇形区域作为LOS的基础掩码
            overlap_segments_mask[i] = cv2.bitwise_and(
                src1=los_segments_mask[i],
                src2=grid_comps[1])
           
           

            img1 = np.array(overlap_segments_mask[i], dtype=np.uint8, copy=True)
            img2 = np.array(board_mask_img[i], dtype=np.uint8, copy=True)
           
            guodu = cv2.bitwise_and(img1, img2)

            overlap_board_mask[i] = cv2.bitwise_or(guodu, overlap_board_mask[i])
 


            overlap_mask_pixels[i] = np.sum(overlap_segments_mask[i])
            if los_type == 1:
                los_segments_mask[i] -= overlap_segments_mask[i]

            segment_mask_pixels[i] = np.sum(los_segments_mask[i])

            for j in range(2, len(grid_comps),1):
                los_segments[i] = cv2.bitwise_or(
                    src1=cv2.bitwise_and(src1=los_segments_mask[i],
                                         src2=grid_comps[j]),
                    src2=los_segments[i])

                overlap_segments[i] = cv2.bitwise_or(
                    src1=cv2.bitwise_and(src1=overlap_segments_mask[i],
                                         src2=grid_comps[j]),
                    src2=overlap_segments[i])

            los_segments[i] = cv2.bitwise_or(
                src1=cv2.bitwise_and(src1=los_segments_mask[i],
                                     src2=grid_comps[0]),
                src2=los_segments[i])
            overlap_segments[i] = cv2.bitwise_or(
                src1=cv2.bitwise_and(src1=overlap_segments_mask[i],
                                     src2=grid_comps[0]),
                src2=overlap_segments[i])

            segment_pixels[i] = np.sum(los_segments[i])
            overlap_pixels[i] = np.sum(overlap_segments[i])
            overlap_boardsum[i]=np.sum(overlap_board_mask[i])#可以进行归一化

            start -= 45
            stop -= 45

        return segment_pixels/segment_mask_pixels, overlap_pixels/overlap_mask_pixels, los_segments_mask, overlap_segments_mask,overlap_boardsum/overlap_mask_pixels


    if los_type == 2:
        return

    if los_type in (3, 4):
        grid = setup_empty_grid(bx=board.get_width(),
                                by=board.get_height(),
                                resolution=pcbDraw_resolution(),
                                padding=padding)

        cv2.circle(img=grid,
                    center=(cx,cy),
                    color=(64),
                    radius=radius,
                    thickness = -1 )

        grid = grid.reshape(grid.shape[0], grid.shape[1])
        grid = cv2.bitwise_and(src1=grid, src2=grid_comps[0])
        if los_type == 3:
            return grid[int(cy-radius/2-1):int(cy+radius/2+1),
                        int(cx-radius/2-1):int(cx+radius/2+1)]
        else:
            grid += grid_comps[1]
            return grid[int(cy-radius/2-1):int(cy+radius/2+1),
                        int(cx-radius/2-1):int(cx+radius/2+1)]


def compute_hpwl(current_node, neighbor_nodes, e, ignore_power=False):
    """
    直接复刻 draw_ratsnest() 的坐标逻辑，计算当前元件相关连接的 HPWL（半周线长）

    Args:
        current_node: 当前处理的元件节点对象
        neighbor_nodes: 与当前元件相连的节点列表
        e: 边（连线）集合
        ignore_power: 是否忽略电源线

    Returns:
        float: HPWL 总和
    """
    current_node_id = current_node.get_id()
    current_node_pos = current_node.get_pos()
    current_node_ori = current_node.get_orientation()

    src = []
    dst = []

    for ee in e:
        if ignore_power and ee.get_power_rail() > 0:
            continue

        for i in range(2):
            if ee.get_instance_id(i) == current_node_id:
                pad_pos = ee.get_pos(i)
                rotated_pad = kicad_rotate(float(pad_pos[0]), float(pad_pos[1]), current_node_ori)
                src.append([current_node_pos[0] + rotated_pad[0],
                            current_node_pos[1] + rotated_pad[1]])
            else:
                for n in neighbor_nodes:
                    if ee.get_instance_id(i) == n.get_id():
                        neigh_pos = n.get_pos()
                        neigh_ori = n.get_orientation()
                        pad_pos = ee.get_pos(i)
                        rotated_pad = kicad_rotate(float(pad_pos[0]), float(pad_pos[1]), neigh_ori)
                        dst.append([neigh_pos[0] + rotated_pad[0],
                                    neigh_pos[1] + rotated_pad[1]])
                        break

    # 计算 HPWL
    hpwl = 0.0
    all_points = src + dst

    if not all_points:
     return 0.0

    xs = [p[0] for p in all_points]
    ys = [p[1] for p in all_points]
    hpwl = (max(xs) - min(xs)) + (max(ys) - min(ys))
    return hpwl


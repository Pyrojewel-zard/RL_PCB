#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  6 21:33:31 2022

@author: luke
"""
import numpy as np
from graph_utils import kicad_rotate
from pcbDraw import draw_los, draw_comps_from_nodes_and_edges, pcbDraw_resolution

def polar_to_rectangular(r, theta):
    """
    将极坐标转换为直角坐标（复数形式表示）

    Args:
        r (float): 极坐标半径
        theta (float): 极坐标角度（弧度制）

    Returns:
        complex: 以复数形式表示的直角坐标
    """
    return r * np.exp( 1j * theta )  # ⭐ 核心计算：通过欧拉公式将极坐标转换为复数形式的直角坐标

def rectangular_to_polar(z):
    """
    将直角坐标系的复数转换为极坐标表示（模和幅角）

    Args:
        z (complex): 需要转换的复数

    Returns:
        tuple: 包含两个元素的元组，第一个元素是模(r)，第二个元素是幅角(theta)
    """
    r = np.abs(z)  # ⭐ 计算复数的模（绝对值）
    theta = np.angle(z)  # ⭐ 计算复数的幅角（相位角）
    return (r, theta)

def compute_pad_referenced_distance_vectors_v2(n, nn, e, ignore_power=False):
    """
    计算基于焊盘参考的距离向量（v2版本），用于PCB元件布局优化。

    Args:
        n: 当前元件对象
        nn: 邻居元件对象列表
        e: 网络连接对象列表
        ignore_power: 是否忽略电源网络（默认False）

    Returns:
        tuple: 包含三个返回值：
            - dom: 主导方向向量
            - resultant_vecs: 合力向量列表，每个元素格式为[网络ID,当前节点ID,目标节点ID,当前焊盘ID,目标焊盘ID](r,θ)
            - all_vecs: 所有向量列表，每个元素包含完整的向量信息

    实现步骤：
        1. 计算当前焊盘到邻居焊盘的连接向量（自动选择最短距离）
        2. 对同网络的向量进行求和得到合力向量
        3. 汇总所有合力向量确定移动方向
        注：合力向量的大小会除以该网络的向量数量进行归一化
    """
    current_node_id = n.get_id()
    current_node_pos = n.get_pos()
    net_ids = []

    # 1 为每个网络创建数据点对列表
    for ee in e:
        if (ignore_power is True) and (ee.get_power_rail() > 0):
            continue
        if ee.get_net_id() not in net_ids:
            net_ids.append(ee.get_net_id())

    pts = []
    for net_id in net_ids:
        for ee in e:
            if ee.get_net_id() == net_id:
                for i in range(2):
                    if ee.get_instance_id(i) == current_node_id:
                        current_pad_pos = ee.get_pos(i)
                        # 旋转焊盘位置以匹配元件方向
                        rotated_current_pad_pos = kicad_rotate(
                            float(current_pad_pos[0]),
                            float(current_pad_pos[1]),
                            n.get_orientation())  # ⭐ 关键旋转操作：校正焊盘位置

                        neighbor_pad_pos = ee.get_pos(1-i)
                        for v in nn:
                            if v.get_id() == ee.get_instance_id(1-i):
                                # 旋转邻居焊盘位置以匹配其元件方向
                                rotated_neighbor_pad_pos = kicad_rotate(
                                    float(neighbor_pad_pos[0]),
                                    float(neighbor_pad_pos[1]),
                                    v.get_orientation())

                                neighbor_node_pos = v.get_pos()

                                header = [net_id,
                                            current_node_id,
                                            v.get_id(),
                                            ee.get_pad_id(i),      # 当前节点焊盘ID
                                            ee.get_pad_id(1-i)]    # 目标节点焊盘ID
                                break

                        sx = current_node_pos[0] + rotated_current_pad_pos[0]
                        sy = current_node_pos[1] + rotated_current_pad_pos[1]
                        dx = neighbor_node_pos[0] + rotated_neighbor_pad_pos[0]
                        dy = neighbor_node_pos[1] + rotated_neighbor_pad_pos[1]

                        delta_y = (sy-dy)
                        delta_x = (dx-sx)

                        euclidean_dist = np.sqrt(
                            np.square(delta_x) + np.square(delta_y))  # ⭐ 计算欧式距离
                        angle = np.arctan(delta_y/delta_x)
                        if delta_x < 0: angle += np.pi

                        # 2 Remove duplicates by taking the shorter ones
                        found = False
                        for j in range(len(pts)):
                            if pts[j][0:4] == header[0:4]:
                                found = True
                                if pts[j][-2] > euclidean_dist:
                                    pts[j] = header + [
                                                sx,
                                                sy,
                                                dx,
                                                dy,
                                                euclidean_dist,
                                                angle
                                                ]
                                    break

                        if not found:
                            pts.append(
                                header + [sx, sy, dx, dy, euclidean_dist, angle])

    # 3 Compute vectors
    # p[2:3] -> current_node_id, current_pad_id
    vec_sc = []
    for p in pts:
        if [p[1], p[3]] not in vec_sc:
            vec_sc.append([p[1], p[3]])

    all_vecs = []
    for i in vec_sc:
        tmp = []
        for p in pts:
            if [p[1], p[3]] == i:
                tmp.append(p)
        all_vecs.append(tmp)
    resultant_vecs = []
    # The simplest way to add two polar vectors is by converting them to
    # rectangular form, summing them up and converting them back to polar.
    for vecs in all_vecs:
        v_pts = []
        for v in vecs:
            # Divide the magnitude of a vector the sum of vectors in the list.
            v_pts.append(polar_to_rectangular(v[-2]/len(pts),v[-1]))

        z = rectangular_to_polar(np.sum(v_pts))
        resultant_vecs.append([v[0:5], z])

    v_pts = []
    for v in resultant_vecs:
        v_pts.append(polar_to_rectangular(v[-1][0], v[-1][1]))

    dom = rectangular_to_polar(np.sum(v_pts))
    return dom, resultant_vecs, all_vecs

def sort_resultant_vectors( resultant_vecs ):
    """
    对结果向量列表按照特定规则进行排序（默认升序）

    Args:
        resultant_vecs (list): 需要排序的向量列表，每个向量应包含子列表结构

    Returns:
        list: 排序后的向量列表，按照每个子向量第4个元素(x[0][3])的值升序排列
    """
    # reverse = None (Sorts in Ascending order)
    # key is set to sort using second element of
    # sublist lambda has been used
    resultant_vecs.sort(key = lambda x: x[0][3])  # ⭐ 核心排序操作：按子列表第4个元素的值进行排序
    return resultant_vecs

def compute_vector_to_group_midpoint(n, nn):
    all_pos_x = []
    all_pos_y = []

    current_node_pos = n.get_pos()
    all_pos_x.append(current_node_pos[0])
    all_pos_y.append(current_node_pos[1])

    for v in nn:
        pos = v.get_pos()
        all_pos_x.append(pos[0])
        all_pos_y.append(pos[1])

    cx = np.sum(np.array(all_pos_x))/len(all_pos_x)
    cy = np.sum(np.array(all_pos_y))/len(all_pos_y)

    delta_y = (current_node_pos[1]-cy)
    delta_x = (cx-current_node_pos[0])

    euclidean_dist = np.sqrt(np.square(delta_x) + np.square(delta_y))
    angle = np.arctan(delta_y/delta_x)
    if delta_x < 0: angle += np.pi

    return tuple([cx,cy]), euclidean_dist, angle

# computes the sum of shortest distances between the current node and
# it's neighbors
def compute_sum_of_euclidean_distances(n, nn, eoi):
    current_node_id = n.get_id()
    current_node_pos = n.get_pos()
    current_node_orientation = n.get_orientation()
    all_lengths = []
    for v in nn:
        neighbor_node_id = v.get_id()
        lengths = []
        for e in eoi:
            if (e.get_instance_id(0) == current_node_id or e.get_instance_id(0) == neighbor_node_id) and (e.get_instance_id(1) == current_node_id or e.get_instance_id(1) == neighbor_node_id):
                for i in range(2):
                    if e.get_instance_id(i) == current_node_id:
                        current_pad_pos = e.get_pos(i)
                        rotated_current_pad_pos = kicad_rotate(
                            float(current_pad_pos[0]),
                            float(current_pad_pos[1]),
                            current_node_orientation)

                        neighbor_pad_pos = e.get_pos(1-i)
                        # rotate pad positions so that they match the
                        # component's orientation
                        rotated_neighbor_pad_pos = kicad_rotate(
                            float(neighbor_pad_pos[0]),
                            float(neighbor_pad_pos[1]),
                            v.get_orientation())
                        neighbor_node_pos = v.get_pos()

                        p1 = [current_node_pos[0] + rotated_current_pad_pos[0], current_node_pos[1] + rotated_current_pad_pos[1]]
                        p2 = [neighbor_node_pos[0] + rotated_neighbor_pad_pos[0], neighbor_node_pos[1] + rotated_neighbor_pad_pos[1]]

                        lengths.append(np.sqrt(np.square(p1[0]-p1[1])+np.square(p2[0]-p2[1])))

        all_lengths.append(np.min(np.array(lengths)))
        print(f" Length array between current_node {current_node_id},{n.get_name()} and neighbor node  {v.get_id()},{v.get_name()} is : {lengths}")
        print(f"The smallest value being {all_lengths[-1]}")

    print(np.sum(all_lengths))

# computes the sum of shortest distances between the current node's pads and
# it's neighbors. This is achieved by first computing the euclidean distance
# of all edges. These represent a pad to pad connection. For each pad of the
# current node the shortest pad-pad distance to any of its neighbors is noted.
# The sum is returned.
def compute_sum_of_euclidean_distances_between_pads(n,
                                                    nn,
                                                    eoi,
                                                    ignore_power=False):
    """
    计算当前元件所有焊盘到相邻元件对应焊盘的欧式距离之和。

    Args:
        n: 当前元件对象，需包含位置、旋转角度和焊盘信息
        nn: 相邻元件对象列表
        eoi: 元件间连接关系对象列表
        ignore_power (bool): 是否忽略电源轨焊盘

    Returns:
        float: 所有焊盘到对应相邻焊盘的最小距离之和
    """
    current_node_id = n.get_id()
    current_node_pos = n.get_pos()
    current_node_orientation = n.get_orientation()
    current_node_pins = n.get_pin_count()

    all_lengths = []
    for i in range(current_node_pins):
        lengths = []
        for e in eoi:
            if ignore_power is True and e.get_power_rail() > 0:
                continue

            for j in range(2):
                if (e.get_instance_id(j) == current_node_id) and (e.get_pad_id(j) == i):
                    for k in range(2):
                        if (e.get_instance_id(k) == current_node_id) and (e.get_pad_id(k) == i):
                            current_pad_pos = e.get_pos(k)
                            rotated_current_pad_pos = kicad_rotate(
                                float(current_pad_pos[0]),
                                float(current_pad_pos[1]),
                                current_node_orientation)  # ⭐ 旋转当前焊盘坐标以匹配元件方向

                            for v in nn:
                                if v.get_id() == e.get_instance_id(1-k):
                                    neighbor_pad_pos = e.get_pos(1-k)
                                    # rotate pad positions so that they match
                                    # the component's orientation
                                    rotated_neighbor_pad_pos = kicad_rotate(
                                        float(neighbor_pad_pos[0]),
                                        float(neighbor_pad_pos[1]),
                                        v.get_orientation())
                                    neighbor_node_pos = v.get_pos()
                                    break

                            p1 = [current_node_pos[0] + rotated_current_pad_pos[0], current_node_pos[1] + rotated_current_pad_pos[1]]
                            p2 = [neighbor_node_pos[0] + rotated_neighbor_pad_pos[0], neighbor_node_pos[1] + rotated_neighbor_pad_pos[1]]

                            lengths.append(np.sqrt(np.square(p1[0]-p2[0])+np.square(p1[1]-p2[1])))

        if len(lengths) != 0: all_lengths.append(np.min(np.array(lengths)))

    return np.sum(all_lengths)

def distance_between_two_points(p1,p2):
    """
    计算两个二维点之间的欧几里得距离。

    Args:
        p1 (tuple/list): 第一个点的坐标，格式为(x1, y1)
        p2 (tuple/list): 第二个点的坐标，格式为(x2, y2)

    Returns:
        float: 两点之间的直线距离。如果两点重合则返回0。
    """
    if p1[0] == p2[0] and p1[1] == p2[1]:
        return 0
    else:
        return np.sqrt(np.square(p1[0]-p2[0])+np.square(p1[1]-p2[1]))  # ⭐ 使用欧几里得公式计算两点距离

# img and los_segment should be layers containing drawings with a single value.
def shortest_distance_to_object_within_segment(img,
                                               los_segment,
                                               centre,
                                               radius,
                                               normalize=True,
                                               padding=(0,0)):
    """
    计算线段区域内图像对象到中心点的最短距离。

    Args:
        img (ndarray): 输入的二值图像矩阵
        los_segment (ndarray): 线段区域的掩模矩阵
        centre (tuple): 中心点坐标(x,y)
        radius (float): 归一化半径基准值
        normalize (bool): 是否对距离进行归一化处理
        padding (tuple): 中心点坐标的填充偏移量(x,y)

    Returns:
        tuple: (最短距离, 最近点坐标)。若normalize=True则返回归一化后的距离
    """
    tmp = los_segment/16 * img/64  # ⭐ 通过矩阵运算得到有效区域掩模

    dist = radius
    coords = (-1,-1)

    for i in range(tmp.shape[1]):
        for j in range(tmp.shape[0]):
            if tmp[i][j] == 1:
                d = distance_between_two_points(
                    (centre[0]+padding[0],centre[1]+padding[1]),
                    (j,i))
                if d < dist:
                    dist = d
                    coords = tuple([j,i])

    if normalize:
        dist /= radius  # ⭐ 执行距离归一化计算

    return dist, coords

def get_coords_from_polar_vector(r, theta, p0, angle_degrees=False):
    """
    根据极坐标向量计算对应的笛卡尔坐标。

    Args:
        r (float): 极坐标半径/向量长度
        theta (float): 极坐标角度（弧度制或角度制）
        p0 (tuple): 原始点坐标(x,y)
        angle_degrees (bool): 是否为角度制，默认为False（弧度制）

    Returns:
        tuple: 包含两个元组的新坐标点和原始点坐标 ((新x,新y), (原x,原y))
    """
    if angle_degrees is  True:
        if theta > 180: theta -= 360
        theta = (theta / 180.0) * np.pi  # ⭐ 角度制转弧度制的核心计算

    p = [0,0]

    p[0] = p0[0] + r*np.cos(theta)  # ⭐ 计算x坐标的核心公式
    p[1] = p0[1] - r*np.sin(theta)  # ⭐ 计算y坐标的核心公式

    return (p[0],p[1]), (p0[0], p0[1])

# orientation invariant
# theta= -theta
def distance_from_rectangle_center_to_edge( size, theta, degrees=True ):
    """
    计算从矩形中心到边缘的距离，基于给定的角度和矩形尺寸。

    Args:
        size (tuple): 矩形的尺寸，格式为(宽度, 高度)。
        theta (float): 从矩形中心出发的角度。
        degrees (bool, optional): 角度是否为度数而非弧度。默认为True。

    Returns:
        float: 从矩形中心到边缘的距离。
    """
    if degrees is True:
        theta = deg2rad(theta)  # ⭐ 将角度转换为弧度（如果需要）

    if np.abs(np.tan(theta)) <= (size[1]/size[0]):
        m = 0.5 * (size[0] / np.abs(np.cos(theta)))  # ⭐ 计算水平方向的距离
    else:
        m = 0.5 * (size[1] / np.abs(np.sin(theta)))  # ⭐ 计算垂直方向的距离

    return m

def deg2rad(theta):
    """
    将角度值从度转换为弧度。

    Args:
        theta (float): 以度为单位的输入角度值。

    Returns:
        float: 转换后的弧度值。
    """
    return (theta / 360) * 2 * np.pi  # ⭐ 执行角度到弧度的转换计算

def rad2deg(theta):
    """
    将弧度值转换为角度值。

    Args:
        theta (float): 需要转换的弧度值。

    Returns:
        float: 转换后的角度值。
    """
    return (theta * 360) / (2 * np.pi)  # ⭐ 执行弧度到角度的转换计算

def get_los_feature_vector(n, nn, eoi, b, clamp_at_zero=True, padding=None):
    """
    计算PCB元件间的视线(LOS)特征向量，用于布局优化分析。

    Args:
        n: 当前元件节点对象
        nn: 相邻元件节点列表
        eoi: 边对象列表
        b: 板边界对象
        clamp_at_zero (bool): 是否将负距离值钳制为0
        padding: 填充参数

    Returns:
        tuple: 包含四个元素的元组：
            - los_feature: 归一化的LOS特征向量(8个方向)
            - box_edge_coords: 元件边缘坐标列表
            - intersection_point_coords: 交点坐标列表
            - dict: 包含LOS线段信息的字典
    """
    current_node_size = n.get_size()
    current_node_position = n.get_pos()
    current_node_orientation = n.get_orientation()

    los_segments, _ =  draw_los(current_node_position[0],
                                         current_node_position[1],
                                         np.max(current_node_size)*2,
                                         current_node_orientation,
                                         bx=b.get_width(),
                                         by=b.get_height(),
                                         padding=padding)  # ⭐ 生成8个方向的LOS线段

    grid_comps = draw_comps_from_nodes_and_edges(n,
                                                 nn,
                                                 eoi,
                                                 b,
                                                 padding=padding)

    scaled_current_node_pos = [0,0]
    scaled_current_node_pos[0] = int(current_node_position[0]/pcbDraw_resolution()) + int(3/pcbDraw_resolution())  # centre is offset for padding
    scaled_current_node_pos[1] = int(current_node_position[1]/pcbDraw_resolution()) + int(3/pcbDraw_resolution())  # centre is offset for padding

    los_feature = []
    box_edge_coords = []
    intersection_point_coords = []
    los_radius = int( (np.max(current_node_size)*2) / pcbDraw_resolution())
    for i in range(8):
        # The center point of the current node must factor in the padding of
        # the grid!
        d, c = shortest_distance_to_object_within_segment(  # ⭐ 计算线段到最近障碍物的距离和交点
            grid_comps[0],
            los_segments[i],
            tuple([scaled_current_node_pos[0],scaled_current_node_pos[1]]),
            los_radius,
            normalize=False)

        intersection_point_coords.append(c)
        # if distance is less than the radius of the los signal
        if d < los_radius:
            if d == 0:
                angle = current_node_orientation
                d = 1E-3
                m = np.sqrt(np.square(current_node_size[0]/2)+np.square(current_node_size[1]/2)) / pcbDraw_resolution()
                # component center as edge coord
                box_edge_coords.append(
                    (scaled_current_node_pos[0], scaled_current_node_pos[1]))
            else:
                dx = c[0] - scaled_current_node_pos[0]
                dy = c[1] - scaled_current_node_pos[1]
                angle = np.arctan2( (dy+1E-15)  , (dx+1E-15) )

                if angle < 0: angle += 2 * np.pi

                angle = 2 * np.pi - angle

                x = np.int0(
                    np.ceil(current_node_size[0] / pcbDraw_resolution()))
                y = np.int0(
                    np.ceil(current_node_size[1] / pcbDraw_resolution()))
                m = distance_from_rectangle_center_to_edge(
                    (x,y),
                    angle-deg2rad(current_node_orientation),
                    degrees=False )

                box_edge_coords.append(
                    (np.int0(scaled_current_node_pos[0] + m*np.cos(angle)),
                    np.int0(scaled_current_node_pos[1] - m*np.sin(angle)))
                    )

            edge_to_intersection_dist = d - m
        else:
            m=0
            edge_to_intersection_dist = d - 0
            angle = 0
            box_edge_coords.append(
                (scaled_current_node_pos[0], scaled_current_node_pos[1]))

        if clamp_at_zero is True:
            max(edge_to_intersection_dist, 0)

        los_feature.append(edge_to_intersection_dist/los_radius)
    return los_feature, box_edge_coords, intersection_point_coords, {"los_segments":los_segments}

# wraps theta between -pi and pi. Angle always returned in radians
def wrap_angle(theta, degrees=True):
    """
    将角度值规范到[-π, π]区间（弧度制）或对应的角度区间。

    Args:
        theta (float): 输入的角度值
        degrees (bool): 标志位，True表示输入为角度制，False表示输入为弧度制

    Returns:
        float: 规范化后的角度值（与输入保持相同的单位制）
    """
    if degrees is True:
        theta = deg2rad(theta)  # ⭐ 将角度转换为弧度（如果需要）

    if theta > np.pi:
        return theta - np.pi  # ⭐ 核心处理逻辑：将大于π的角度减去π进行规范化
    else:
        return theta

def cosine_distance_for_two_terminal_component(resultant, degrees=False):
    """
    计算两个终端元件向量间的余弦距离（方向相似性）。

    Args:
        resultant (list): 包含元件向量信息的列表，每个元素格式为(标签, (x,y,角度))。
        degrees (bool): 角度单位标志，True表示角度制，False表示弧度制（默认）。

    Returns:
        float: 两个向量夹角的余弦值（仅当输入为2个向量时有效），否则返回0。

    Note:
        当输入向量数≠2时会打印错误提示。
    """
    if len(resultant) == 2:
        return np.cos(resultant[0][1][-1] - resultant[1][1][-1])  # ⭐ 计算两个向量最后角度值的余弦差
    else:
        if len(resultant) > 2:
            print("Function 'cosine_distance_for_two_terminal_component' can only work with two resultant vectors. Returning 0.")
        return 0

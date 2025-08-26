from pcbDraw import draw_los, draw_board_from_graph_multi_agent, draw_ratsnest, get_los_and_ol_multi_agent
from pcb_vector_utils import compute_pad_referenced_distance_vectors_v2, compute_vector_to_group_midpoint
from pcb_vector_utils import wrap_angle
import numpy as np

def line_of_sight_and_overlap_v0(parameters, comp_grids):
    """
    计算视线和重叠度的早期版本函数
    
    Args:
        parameters: 智能体参数
        comp_grids: 组件网格
        
    Returns:
        los_grids: 视线网格
        los: 视线值
        ol_grids: 重叠网格
        ol: 重叠值
    """
    los_grids = []
    los = []

    ol_grids = []
    ol = []

    # 获取当前节点位置、尺寸和方向
    current_node_pos = parameters.node.get_pos()
    current_node_size = parameters.node.get_size()
    current_orientation = parameters.node.get_orientation()

    # 绘制视线段，计算8个方向的视线
    los_segments, segment_pixels = draw_los(current_node_pos[0],
                                    current_node_pos[1],
                                    np.max(current_node_size)*1.5,  # 视线半径
                                        angle_offset=current_orientation,
                                        bx=parameters.board_width,
                                        by=parameters.board_height,
                                        padding=parameters.padding)

    # 计算8个方向的视线值
    for i in range(8):
        los_grids.append(comp_grids[0] * (los_segments[i]/16))
        los.append(((np.sum(los_grids[-1])/64) + 1E-3) / segment_pixels[i])

    # 计算当前组件与已放置组件之间的重叠
    for i in range(8):
        ol_grids.append(
            (comp_grids[0]/64) * (comp_grids[1]/64) * (los_segments[i]/16))
        ol.append((np.sum(ol_grids[-1]) + 1E-6) / np.sum(comp_grids[1]/64))

    return los_grids, los, ol_grids, ol

def get_agent_observation(parameters, tracker=None):
    """
    获取智能体的观察状态
    
    Args:
        parameters: 智能体参数
        tracker: 跟踪器对象（可选）
        
    Returns:
        包含各种观察信息的字典
    """
    node_id = parameters.node.get_id()
    
    # 从节点绘制组件网格
    comp_grids = draw_board_from_graph_multi_agent(g=parameters.graph,
                                                   node_id=node_id,
                                                   bx=parameters.board_width,
                                                   by=parameters.board_height,
                                                   padding=parameters.padding)

    # 获取视线、重叠度和板边界掩码
    los, ol, _, ol_grids, boardmask = get_los_and_ol_multi_agent(
        node=parameters.node,
        board=parameters.board,
        radius=np.max(parameters.node.get_size())*1.5,  # 视线半径
        grid_comps=comp_grids,
        padding=parameters.padding)  # 新增异形边界二值获取

    # 计算重叠比例
    ol_ratios = []
    total = np.sum(ol_grids)/64
    
    # 添加安全检查以避免除0错误
    if total == 0:
        # 当total为0时，所有ol_ratios设为0（表示没有重叠）
        ol_ratios = [0.0] * len(ol_grids)
    else:
        for grid in ol_grids:
            ol_ratios.append((np.sum(grid) / 64) / total)

    # 计算距离向量（DOM - Direction of Movement）
    dom, _, _ = compute_pad_referenced_distance_vectors_v2(
        parameters.node,
        parameters.neighbors,
        parameters.eoi,
        ignore_power=parameters.ignore_power_nets
        )

    # 计算到组中心的向量
    _, eucledian_dist, angle = compute_vector_to_group_midpoint(
        parameters.node,
        parameters.neighbors
    )

    # 如果提供了跟踪器，记录观察信息
    if tracker is not None:
        tracker.add_observation(comp_grids=comp_grids)
        tracker.add_ratsnest(
            draw_ratsnest(parameters.node,
                          parameters.neighbors,
                          parameters.eoi,
                          parameters.board_width,
                          parameters.board_height,
                          padding=parameters.padding,
                          ignore_power=parameters.ignore_power_nets)
                          )

    # 构建信息字典
    info = {"ol_ratios": ol_ratios}

    # 返回完整的观察字典
    return {"los": los[-8:],                    # 8个方向的视线信息
            "ol": ol[-8:],                      # 8个方向的重叠度
            "dom": [dom[0], dom[1]],            # 距离向量
            "euc_dist": [eucledian_dist, angle], # 欧几里得距离和角度
            "position": [parameters.node.get_pos()[0] / parameters.board_width,
                         parameters.node.get_pos()[1] / parameters.board_height],  # 归一化位置
            "ortientation": [wrap_angle(parameters.node.get_orientation())],      # 方向角度
            "boardmask": boardmask[-8:],        # 板边界掩码
            "info": info                        # 附加信息
        }

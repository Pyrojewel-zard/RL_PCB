from pcbDraw import draw_los, draw_board_from_graph_multi_agent, draw_ratsnest, get_los_and_ol_multi_agent
from pcb_vector_utils import compute_pad_referenced_distance_vectors_v2, compute_vector_to_group_midpoint
from pcb_vector_utils import wrap_angle
import numpy as np

def line_of_sight_and_overlap_v0(parameters, comp_grids):
    """
    计算当前组件与其他组件之间的视线检测和重叠区域情况。

    Args:
        parameters: 包含PCB板参数和当前节点信息的对象
            - node: 当前组件节点对象
            - board_width: PCB板宽度
            - board_height: PCB板高度
            - padding: 边缘填充值
        comp_grids: 包含组件网格信息的列表
            - [0]: 当前组件网格
            - [1]: 已放置组件网格

    Returns:
        tuple: 包含四个元素的元组
            - los_grids: 8个方向的视线网格列表
            - los: 8个方向的视线值列表(归一化)
            - ol_grids: 8个方向的重叠网格列表
            - ol: 8个方向的重叠值列表(归一化)
    """
    los_grids = []
    los = []

    ol_grids = []
    ol = []
    boardmask=[]
    boardmasknum=[]

    current_node_pos = parameters.node.get_pos()
    current_node_size = parameters.node.get_size()
    current_orientation = parameters.node.get_orientation()

    # ⭐ 计算8个方向的视线线段和像素数(核心视线检测)
    los_segments, segment_pixels = draw_los(current_node_pos[0],
                                    current_node_pos[1],
                                    np.max(current_node_size)*1.5,
                                        angle_offset=current_orientation,
                                        bx=parameters.board_width,
                                        by=parameters.board_height,
                                        padding=parameters.padding)

    for i in range(8):      # Calculate line-of-sight
        los_grids.append(comp_grids[0] * (los_segments[i]/16))
        los.append(((np.sum(los_grids[-1])/64) + 1E-3) / segment_pixels[i])

    # Calculate overlap between current component and placed components
    for i in range(8):
        ol_grids.append(
            (comp_grids[0]/64) * (comp_grids[1]/64) * (los_segments[i]/16))
        ol.append((np.sum(ol_grids[-1]) + 1E-6) / np.sum(comp_grids[1]/64))

    return los_grids, los, ol_grids, ol

def get_agent_observation(parameters, tracker=None):
    """
    获取PCB布局智能体的观测数据，包括空间关系特征和位置信息。

    Args:
        parameters (object): 包含节点、图形、板尺寸等参数的对象
        tracker (object, optional): 用于跟踪观测数据的对象，默认为None

    Returns:
        dict: 包含以下键的字典：
            - los: 最后8个视线检测结果
            - ol: 最后8个重叠区域检测结果
            - dom: 支配向量[x,y]
            - euc_dist: [欧式距离, 角度]
            - position: 节点位置归一化坐标[x,y]
            - ortientation: 节点方向角度
            - info: 包含重叠比例等附加信息
    """
    node_id = parameters.node.get_id()
    # 从节点绘制组件网格
    comp_grids = draw_board_from_graph_multi_agent(g=parameters.graph,
                                                   node_id=node_id,
                                                   bx=parameters.board_width,
                                                   by=parameters.board_height,
                                                   padding=parameters.padding)  # ⭐ 生成组件网格表示

    los, ol, _, ol_grids,boardmask = get_los_and_ol_multi_agent(
        node=parameters.node,
        board=parameters.board,
        radius=np.max(parameters.node.get_size())*1.5,
        grid_comps=comp_grids,
        padding=parameters.padding)  # ⭐ 计算视线和重叠区域

    # 计算重叠比例
    ol_ratios = []
    total = np.sum(ol_grids)/64
    for grid in ol_grids:
        ol_ratios.append((np.sum(grid) / 64) / total)

    dom, _, _ = compute_pad_referenced_distance_vectors_v2(
        parameters.node,
        parameters.neighbors,
        parameters.eoi,
        ignore_power=parameters.ignore_power_nets
        )  # ⭐ 计算支配向量

    # 计算到组中点的距离和角度
    _, eucledian_dist, angle = compute_vector_to_group_midpoint(
        parameters.node,
        parameters.neighbors
    )

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

    info = { "ol_ratios": ol_ratios, }

    return {"los":  los[-8:],
            "ol": ol[-8:],
            "dom": [dom[0], dom[1]],
            "euc_dist": [ eucledian_dist, angle ],
            "position": [parameters.node.get_pos()[0] / parameters.board_width,
                         parameters.node.get_pos()[1] / parameters.board_height],
            "ortientation": [wrap_angle(parameters.node.get_orientation())],
            "boardmask":boardmask[-8:],
            "info": info
        }

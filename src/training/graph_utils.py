"""
This module provides utility functions for performing rotation operations
using the Kicad rotation formula.

Module Dependencies:
    - numpy

Functions:
    - kicad_rotate: Rotate a point (x, y) by an angle (a) using the Kicad
    rotation formula.
    - kicad_rotate_around_point: Rotate a point (x, y) around a center point
    (cx, cy) by an angle (a) using the Kicad rotation formula.

Example Usage:
    import numpy as np
    from graph_utils import kicad_rotate, kicad_rotate_around_point

    point = [1.0, 2.0]
    angle = 45.0
    rotated_point = kicad_rotate(point[0], point[1], angle)

    center = [0.0, 0.0]
    rotated_around_point = kicad_rotate_around_point(point[0], point[1],
    center[0], center[1], angle)

"""
import numpy as np

def kicad_rotate( x, y, a):
    """
    使用Kicad旋转公式计算点(x,y)绕原点旋转后的坐标

    Args:
        x (float): 点的x坐标
        y (float): 点的y坐标
        a (float): 旋转角度(度)

    Returns:
        list: 旋转后的新坐标[rx, ry]
    """
 	# --             --     -- --
 	# |  cos()   sin() | \/  | x |
 	# | -sin()   cos() | /\  | y |
 	# --             --     -- --

    theta =  np.pi * (a / 180.0)  # ⭐ 将角度转换为弧度

    rx = x * np.cos( theta ) + y * np.sin( theta )  # ⭐ 计算旋转后的x坐标
    ry = - x * np.sin( theta ) + y * np.cos( theta )  # ⭐ 计算旋转后的y坐标

    return [rx,ry]

def kicad_rotate_around_point( x, y, cx, cy, a):
    """
    Rotate a point (x, y) around a center point (cx, cy) by an angle
    a (in degrees)
    using the Kicad rotation formula.

    Args:
        x (float): x-coordinate of the point.
        y (float): y-coordinate of the point.
        cx (float): x-coordinate of the center point.
        cy (float): y-coordinate of the center point.
        a (float): Angle of rotation in degrees.

    Returns:
        list: The rotated point [rx, ry].
    """
 	# --             --     -- --
 	# |  cos()   sin() | \/  | x |
 	# | -sin()   cos() | /\  | y |
  	# --             --     -- --

    theta =  np.pi * (a / 180.0)  # ⭐ 将角度转换为弧度，为后续三角函数计算做准备

    rx = ((x - cx) * np.cos( theta ) + ( y - cy ) * np.sin( theta )) + cx
    ry = (-(x - cx) * np.sin( theta ) + ( y - cy ) * np.cos( theta )) + cy

    return [rx,ry]

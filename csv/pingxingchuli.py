
import pandas as pd
import matplotlib.pyplot as plt
import ast
import numpy as np

def load_csv(filepath):
    df = pd.read_csv(filepath, header=None)
    return df

def parse_points(row):
    points = []
    for item in row.dropna():
        try:
            pt = ast.literal_eval(item)
            if isinstance(pt, list) and len(pt) == 2:
                points.append(pt)
        except:
            continue
    return points

def update_region(df, row_index, inner_range):
    points = parse_points(df.iloc[row_index])
    inner_points = points[inner_range[0]:inner_range[1] + 1]
    new_row = [''] * df.shape[1]
    for i, pt in enumerate(inner_points):
        new_row[i] = str(pt)
    df.iloc[row_index] = new_row
    return df

def visualize_all_regions(df, title="所有区域轮廓（红字为行号）"):
    fig, ax = plt.subplots(figsize=(12, 12))
    for idx, row in df.iloc[1:].iterrows():
        points = parse_points(row)
        if len(points) >= 2:
            points.append(points[0])
            x, y = zip(*points)
            ax.plot(x, y, linewidth=1)
            ax.text(x[0], y[0], f"{idx}", fontsize=8, color='red')
    ax.set_aspect('equal')
    ax.set_title(title)
    plt.grid(True)
    plt.show()

def save_csv(df, output_path):
    df.to_csv(output_path, index=False, header=False)

if __name__ == "__main__":
    # ==== 修改以下部分 ====
    input_csv = "你的输入文件.csv"
    output_csv = "处理后的输出文件.csv"

    # 格式: (行号（从0开始）: (起始编号, 结束编号))
    inner_regions = {
        5: (1, 226),     # 区域 5（第6行）
        8: (120, 614),   # 区域 8（第9行）
        9: (280, 430),   # 区域 9（第10行）
    }

    df = load_csv(input_csv)

    for row_index, inner_range in inner_regions.items():
        df = update_region(df, row_index, inner_range)

    save_csv(df, output_csv)
    visualize_all_regions(df)

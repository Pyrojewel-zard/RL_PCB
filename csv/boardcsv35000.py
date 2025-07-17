import numpy as np
import pandas as pd
import cv2

# === 1. 读取 Excel 文件 ===
df = pd.read_excel("filtered_outline_only.xlsx")  # 替换为你的路径

# === 2. 提取 LINE 和 ARC ===
lines = df[df["GRAPHIC_DATA_NAME"] == "LINE"]
arcs = df[df["GRAPHIC_DATA_NAME"] == "ARC"]

contours = []

for _, row in lines.iterrows():
    x1, y1 = row["GRAPHIC_DATA_1"], row["GRAPHIC_DATA_2"]
    x2, y2 = row["GRAPHIC_DATA_3"], row["GRAPHIC_DATA_4"]
    contours.append([(x1, y1), (x2, y2)])

def arc_to_lines(x1, y1, x2, y2, cx, cy, direction, segments=15):
    start_angle = np.arctan2(y1 - cy, x1 - cx)
    end_angle = np.arctan2(y2 - cy, x2 - cx)
    if direction == "COUNTERCLOCKWISE":
        if end_angle <= start_angle:
            end_angle += 2 * np.pi
    else:
        if end_angle >= start_angle:
            end_angle -= 2 * np.pi
    angles = np.linspace(start_angle, end_angle, segments)
    radius = np.linalg.norm([x1 - cx, y1 - cy])
    points = [(cx + radius * np.cos(a), cy + radius * np.sin(a)) for a in angles]
    return list(zip(points[:-1], points[1:]))

for _, row in arcs.iterrows():
    x1, y1 = row["GRAPHIC_DATA_1"], row["GRAPHIC_DATA_2"]
    x2, y2 = row["GRAPHIC_DATA_3"], row["GRAPHIC_DATA_4"]
    cx, cy = row["GRAPHIC_DATA_5"], row["GRAPHIC_DATA_6"]
    direction = str(row["GRAPHIC_DATA_9"]).strip()
    if np.isnan(cx) or np.isnan(cy):
        continue
    arc_lines = arc_to_lines(x1, y1, x2, y2, cx, cy, direction, segments=15)
    contours.extend(arc_lines)

# === 3. 绘制所有轮廓线到图像 ===
scale = 100
border = 20
all_points = [pt for seg in contours for pt in seg]
xs, ys = zip(*all_points)
min_x, max_x = min(xs), max(xs)
min_y, max_y = min(ys), max(ys)
w = int((max_x - min_x) * scale) + 2 * border
h = int((max_y - min_y) * scale) + 2 * border
img = np.zeros((h, w), dtype=np.uint8)

def to_img_coords(x, y):
    return int((x - min_x) * scale) + border, int((max_y - y) * scale) + border

for pt1, pt2 in contours:
    p1 = to_img_coords(*pt1)
    p2 = to_img_coords(*pt2)
    cv2.line(img, p1, p2, 255, 1)

# === 4. 查找轮廓并筛选面积 > 35000 ===
contour_list, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
selected_contours = [cnt for cnt in contour_list if cv2.contourArea(cnt) > 35000]

# === 5. 还原原始坐标 ===
def to_original_coords(px, py):
    x = (px - border) / scale + min_x
    y = max_y - (py - border) / scale
    return [round(x, 4), round(y, 4)]

contour_point_sets = []
for cnt in selected_contours:
    cnt = cnt.squeeze()
    if len(cnt.shape) != 2:
        continue
    points = [to_original_coords(x, y) for x, y in cnt]
    if points[0] != points[-1]:  # 保证闭合
        points.append(points[0])
    contour_point_sets.append(points)

# === 6. 导出为 DataFrame 格式（可导出为 CSV/JSON） ===
export_df = pd.DataFrame({
    f"point_{i}": [pts[i] if i < len(pts) else None for pts in contour_point_sets]
    for i in range(max(len(pts) for pts in contour_point_sets))
})

# 保存为 CSV
export_df.to_csv("closed_contours_gt_35000.csv", index=False)

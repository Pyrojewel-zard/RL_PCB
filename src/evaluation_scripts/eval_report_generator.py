#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 15 08:56:26 2022

@author: luke
"""
import argparse
from datetime import datetime

import sys
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, Frame, PageTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import (ParagraphStyle, getSampleStyleSheet)
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from setup_info import machine_info_in_paragraphs, lib_info_in_paragraphs
import numpy as np

class PageNumCanvas(canvas.Canvas):
    """
    http://code.activestate.com/recipes/546511-page-x-of-y-with-reportlab/
    http://code.activestate.com/recipes/576832/
    """
    def __init__(self, *args, **kwargs):
        """Constructor"""
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []

    def showPage(self):
        """
        On a page break, add information to the list
        """
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """
        Add the page number to each page (page x of y)
        """
        page_count = len(self.pages)

        for page in self.pages:
            self.__dict__.update(page)
            self.draw_page_number(page_count, page["_pagesize"])
            canvas.Canvas.showPage(self)

        canvas.Canvas.save(self)

    def draw_page_number(self, page_count, page_size):
        """
        Add the page number
        """
        page = "Page %s of %s" % (self._pageNumber, page_count)
        date = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.setFont("Helvetica", 9)
        self.drawRightString(int(0.17*page_size[0]),
                             int(0.95*page_size[1]),
                             date)
        self.drawRightString(int(0.93*page_size[0]),
                             int(0.95*page_size[1]),
                             page)

def cmdline_args():
    """
    解析命令行参数并构建实验设置字典。

    该函数定义了程序运行所需的各种参数，包括实验目录、奖励参数权重、最大步数等，
    并将这些参数组织成结构化数据返回。

    Returns:
        tuple: 包含两个元素的元组：
            - args: 解析后的命令行参数对象
            - settings: 包含所有实验设置的字典
    """
    parser = argparse.ArgumentParser(
        description="Multi-agent pcb component placement evaluation",
        usage="<script-name> -p <pcb_file> --rl_model_type [TD3 | SAC]",
        epilog="This text will be shown after the help")

    parser.add_argument("-e", "--experiments", nargs="+", type=str, default=None, required=False)
    parser.add_argument("--run_dirs", nargs="+", type=str, required=True)
    parser.add_argument("--reward_params", nargs="+", type=str, required=True, help="Colon seperated weights for euclidean wirelength, hpwl and overlap.")
    parser.add_argument("--max_steps", type=int, required=True, help="Number of steps carried out in each trial.")
    parser.add_argument("-o", "--output", required=False, type=str, help="Output file location. NO CHECKS PERFORMED. PLEASE BE CAREFUL!", default="./evaluation_report.pdf")
    parser.add_argument("-r", "--report_type", required=False, type=str, choices=["raw", "mean", "both"], default="mean", help="Generates tables containing raw information, mean information or both")
    parser.add_argument("--skip_simulated_annealing", required=False, action="store_true", default=False)

    args = parser.parse_args()
    settings = {}

    settings["experiments"] = args.experiments
    settings["run_dirs"] = args.run_dirs
    settings["output"] = args.output
    settings["report_type"] = args.report_type

    settings["reward_params"] = []
    for rp in args.reward_params:
        settings["reward_params"].append({"w": 0.0, "hpwl": 0.0, "o": 0.0})
        rp_split = rp.split(":")  # ⭐ 将冒号分隔的奖励参数拆分成单独权重
        settings["reward_params"][-1]["w"] = rp[0]
        settings["reward_params"][-1]["hpwl"] = rp_split[1]
        settings["reward_params"][-1]["o"] = rp_split[2]

    settings["max_steps"] = args.max_steps
    return args, settings

def main():
    """
    生成PCB元件布局评估报告的主函数。

    该函数执行以下操作：
    1. 解析命令行参数和设置
    2. 配置PDF文档模板和样式
    3. 收集机器和库信息
    4. 处理实验数据并生成报告内容
    5. 将结果输出为PDF文档

    Returns:
        None: 但会生成PDF报告文件
    """
    args, settings = cmdline_args()  # ⭐ 获取命令行参数和设置
    for key, value in settings.items():
        print(f"{key} -> {value}")

    doc = SimpleDocTemplate(args.output,
                                leftMargin = 0.75*inch,
                                rightMargin = 0.75*inch,
                                topMargin = 1*inch,
                                bottomMargin = 1*inch, pagesize=A4)

    # TrueType fonts work in Unicode/UTF8 and aren't limited to 256 characters.
    pdfmetrics.registerFont(TTFont("Verdana", "verdana.ttf"))  # ⭐ 注册字体
    pdfmetrics.registerFont(TTFont("Vera", "Vera.ttf"))

    styles = getSampleStyleSheet()
    style_s = ParagraphStyle("yourtitle",
                        fontName="Verdana",
                        fontSize=8,
                        spaceAfter=6
                    )
    style = ParagraphStyle("yourtitle",
                            fontName="Verdana",
                            fontSize=12,
                            spaceAfter=6
                        )
    style_h1 = styles["Heading1"]
    style_h2 = styles["Heading2"]

    p_frame = Frame(0.5 * inch, 0.5 * inch, 7.5 * inch, 10 * inch,
                leftPadding=0, rightPadding=0,
                topPadding=0, bottomPadding=0,
                id="portrait_frame")

    l_frame = Frame(0.5 * inch, 0.5 * inch, 10 * inch, 7.5 * inch,
                    leftPadding=0, rightPadding=0,
                    topPadding=0, bottomPadding=0,
                    id="landscape_frame")

    portrait_tmpl = PageTemplate(id="portrait_tmpl",
                                 frames=[p_frame],
                                 pagesize=A4)
    landscape_tmpl = PageTemplate(id="landscape_tmpl",
                                  frames=[l_frame],
                                  pagesize=landscape(A4))

    doc.addPageTemplates([portrait_tmpl, landscape_tmpl])  # ⭐ 添加页面模板

    report_data = []
    report_data.append(Paragraph("Experiment Report",style_h1))
    report_data.append(Paragraph(f"Start of automated test report {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",style))

    try:
        report_data.append(Paragraph(f'Author={os.environ["USERNAME"]}@{os.uname()[1]} obo {rc["author"]}',style))
    except:
        print("Could not get 'USERNAME'. This may happen in an RDP session.")
        report_data.append(Paragraph(
            f"Author=UNKNOWN@{os.uname()[1]} obo Luke Vassallo",style))

    report_data.append(Paragraph("Machine Information",style_h1))
    report_data += machine_info_in_paragraphs(style)
    report_data.append(Paragraph("Library Information",style_h1))
    report_data += lib_info_in_paragraphs(style)

    for j in range(len(settings["run_dirs"])):
        report_data.append(PageBreak())
        report_data.append(Paragraph(f'{settings["experiments"][j]}:{settings["run_dirs"][j].split("/")[-1]}',style_h1))
        report_data.append(Paragraph(f'\tSteps per trial                   = {settings["max_steps"]}',style))
        report_data.append(Paragraph(f'\tEuclidean wirelength (w)          = {settings["reward_params"][j]["w"]}',style))
        report_data.append(Paragraph(f'\tHalf perimeter wirelength (hpwl)  = {settings["reward_params"][j]["hpwl"]}',style))
        report_data.append(Paragraph(f'\tOverlap (o)                       = {settings["reward_params"][j]["o"]}',style))
        file = open(os.path.join(settings["run_dirs"][j],"results.txt"), encoding="utf-8")
        pcbs=[]
        data={}
        while True:
            line = file.readline().strip("\n")
            if not line:
                break
            else:
                fields = line.split(",")
                if fields[0] not in pcbs:
                    pcbs.append(fields[0])
                    data[f"{fields[0]}"] = {}

                if f"{fields[1]}" not in data[f"{fields[0]}"]:
                    data[f"{fields[0]}"][f"{fields[1]}"] = {}

                if f"{fields[2]}" in data[f"{fields[0]}"][f"{fields[1]}"]:
                    data[f"{fields[0]}"][f"{fields[1]}"][f"{fields[2]}"] += fields[3:]
                else:
                    data[f"{fields[0]}"][f"{fields[1]}"][f"{fields[2]}"] = fields[3:]

        file.close()

        for wl_idx in [0, 2]:
            pcb_col = ["pcb name"]
            trial_col = ["trial"]
            best_hpwl_00 = ["0% overlap"]
            best_hpwl_10 = ["10% overlap"]
            best_hpwl_20 = ["20% overlap"]
            sa_pcb = ["sa_pcb"]

            mean_pcb_col = ["pcb name"]
            mean_trial_col = ["run"]
            mean_best_hpwl_00 = ["0% overlap (#)¹"]
            mean_best_hpwl_10 = ["10% overlap (#)¹"]
            mean_best_hpwl_20 = ["20% overlap (#)¹"]
            mean_sa_pcb = ["simulated\nannealing"]

            for pcb_key, pcb_value in data.items():
                n_trials = 0
                for trial_key, trial_value in pcb_value.items():
                    """
                    处理每个PCB板的每次试验数据，收集不同重叠率下的HPWL结果和模拟退火结果。
                    
                    Args:
                        pcb_key: PCB板的标识符
                        pcb_value: 该PCB板的所有试验数据
                        trial_key: 试验标识符
                        trial_value: 单次试验的具体数据
                    """
                    if pcb_key == "bistable_oscillator_with_555_timer_and_ldo_2lyr_setup_00":
                        pcb_col.append("555_timer")
                    else:
                        pcb_col.append(pcb_key)
                    trial_col.append(trial_key)
                    if "best_hpwl_00_overlap" in trial_value:
                        best_hpwl_00.append(np.round(
                            float(trial_value["best_hpwl_00_overlap"][wl_idx]),
                            2))  # ⭐ 处理0%重叠率下的最佳HPWL数据
                    else:
                        best_hpwl_00.append("-")

                    if "best_hpwl_10_overlap" in trial_value:
                        best_hpwl_10.append(np.round(
                            float(trial_value["best_hpwl_10_overlap"][wl_idx]),
                            2))  # ⭐ 处理10%重叠率下的最佳HPWL数据
                    else:
                        best_hpwl_10.append("-")

                    if "best_hpwl_20_overlap" in trial_value:
                        best_hpwl_20.append(np.round(
                            float(trial_value["best_hpwl_20_overlap"][wl_idx]),
                            2))  # ⭐ 处理20%重叠率下的最佳HPWL数据
                    else:
                        best_hpwl_20.append("-")

                    if ("SA_PCB" in trial_value) and (args.skip_simulated_annealing is False):
                        sa_pcb.append(np.round(
                            float(trial_value["SA_PCB"][wl_idx]),
                            2))  # ⭐ 处理模拟退火结果数据
                    else:
                        sa_pcb.append("-")

                    n_trials += 1

                """
                计算每个PCB板的各项指标统计值(均值±标准差)
                """
                if pcb_key == "bistable_oscillator_with_555_timer_and_ldo_2lyr_setup_00":
                    mean_pcb_col.append("555_timer")
                else:
                    mean_pcb_col.append(pcb_key)

                mean_trial_col.append(f"{settings['run_dirs'][j].split('/')[-1]}")

                mean_best_hpwl_00.append(f"{np.round(np.mean( [ x for x in best_hpwl_00[-n_trials:] if isinstance(x, np.float64) ] ),2)} \u00B1 {np.round(np.std( [ x for x in best_hpwl_00[-n_trials:] if isinstance(x, np.float64) ] ),2)} ({len([ x for x in best_hpwl_00[-n_trials:] if isinstance(x, np.float64) ])})")  # ⭐ 计算0%重叠率HPWL的统计值

                mean_best_hpwl_10.append(f"{np.round(np.mean( [ x for x in best_hpwl_10[-n_trials:] if isinstance(x, np.float64) ] ),2)} \u00B1 {np.round(np.std( [ x for x in best_hpwl_10[-n_trials:] if isinstance(x, np.float64) ] ),2)} ({len([ x for x in best_hpwl_10[-n_trials:] if isinstance(x, np.float64) ])})")  # ⭐ 计算10%重叠率HPWL的统计值

                mean_best_hpwl_20.append(f"{np.round(np.mean( [ x for x in best_hpwl_20[-n_trials:] if isinstance(x, np.float64) ] ),2)} \u00B1 {np.round(np.std( [ x for x in best_hpwl_20[-n_trials:] if isinstance(x, np.float64) ] ),2)} ({len([ x for x in best_hpwl_20[-n_trials:] if isinstance(x, np.float64) ])})")  # ⭐ 计算20%重叠率HPWL的统计值

                if args.skip_simulated_annealing is False:
                    mean_sa_pcb.append(f"{np.round(np.mean( [ x for x in sa_pcb[-n_trials:] if isinstance(x, np.float64) ] ),2)} \u00B1 {np.round(np.std( [ x for x in sa_pcb[-n_trials:] if isinstance(x, np.float64) ] ),2)} ({len([ x for x in sa_pcb[-n_trials:] if isinstance(x, np.float64) ])})")  # ⭐ 计算模拟退火结果的统计值

            colwidths =[]

            """
            根据是否包含模拟退火结果，准备不同的列配置和列宽设置
            """
            if args.skip_simulated_annealing is False:
                cols = (pcb_col,
                        trial_col,
                        best_hpwl_00,
                        best_hpwl_10,
                        best_hpwl_20,
                        sa_pcb)
                mean_cols = (mean_pcb_col,
                             mean_trial_col,
                             mean_best_hpwl_00,
                             mean_best_hpwl_10,
                             mean_best_hpwl_20,
                             mean_sa_pcb)

                for i in range(len(cols)):     # data is not transposed ...
                    if i == 0:
                        colwidths.append(1.7*inch)  # ⭐ 设置第一列(PCB名称)的宽度
                    else:
                        colwidths.append(1.15*inch)  # 设置其他列的宽度

            else:
                cols = (pcb_col,
                        trial_col,
                        best_hpwl_00,
                        best_hpwl_10,
                        best_hpwl_20)

                mean_cols = (mean_pcb_col,
                             mean_trial_col,
                             mean_best_hpwl_00,
                             mean_best_hpwl_10,
                             mean_best_hpwl_20)

                for i in range(len(cols)):     # data is not transposed ...
                    if i == 0:
                        colwidths.append(2.0*inch)  # ⭐ 设置第一列的宽度为2英寸（比其他列宽）
                    else:
                        colwidths.append(1.43*inch)  # 设置其他列的宽度为1.43英寸

            cols = list(zip(*cols))
            t_cols=Table(cols, rowHeights=25, colWidths=colwidths)
            t_cols.setStyle(TableStyle([
                    ("ALIGN", (0, 0), (-1, -1), "CENTRE"),  # ⭐ 设置表格内容居中对齐
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
                    ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
                    # from first col of last row to last col of last row
                    #("TEXTCOLOR",(0,-1),(-1,-1),colors.red),
                    ]))

            mean_cols = list(zip(*mean_cols))
            t_mean_cols=Table(mean_cols, rowHeights=25, colWidths=colwidths)
            t_mean_cols.setStyle(TableStyle([
                    ("ALIGN", (0, 0), (-1, -1), "CENTRE"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
                    ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
                    # from first col of last row to last col of last row
                    #("TEXTCOLOR",(0,-1),(-1,-1),colors.red),
                    ]))

            if wl_idx == 0:
                report_data.append(
                    Paragraph("Estimated Wirelength (HPWL)",style_h2))  # ⭐ 添加估计线长标题
            else:
                report_data.append(Paragraph("Routed Wirelength",style_h2))  # 添加实际布线长度标题

            if (settings["report_type"] == "raw") or (settings["report_type"] == "both"):
                report_data.append(Paragraph(f'<br />Raw trial data for run {settings["run_dirs"][j]}<br />',style))
                report_data.append(t_cols)  # ⭐ 添加原始数据表格

            if (settings["report_type"] == "mean") or (settings["report_type"] == "both"):
                report_data.append(Paragraph(f'<br />Mean over all trials in run {settings["run_dirs"][j]}',style))
                report_data.append(t_mean_cols)  # ⭐ 添加平均值表格
                report_data.append(Paragraph("¹ # indicates the number of layouts over which the mean \u00B1 std was computed", style_s))
            report_data.append(Paragraph("<br />",style))

    doc.build(report_data, canvasmaker=PageNumCanvas)  # ⭐ 构建最终的PDF文档

    sys.exit()

if __name__ == "__main__":
    main()

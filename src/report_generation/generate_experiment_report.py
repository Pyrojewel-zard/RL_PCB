import argparse
from datetime import datetime
import json
import os
import sys

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Image, Paragraph, PageBreak, Frame, PageTemplate, NextPageTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import (ParagraphStyle, getSampleStyleSheet)
from reportlab.lib.units import inch, cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from reportlab.lib import utils
from setup_info import machine_info_in_paragraphs, lib_info_in_paragraphs
from gen_utils import generate_dataset, generate_plot, generate_multi_agent_plot, generate_multi_agent_plot_w_mean_std, generate_table
import matplotlib.pyplot as plt
from pathlib import Path

plt.rc("axes", titlesize=16)
plt.rc("axes", labelsize=14)    # fontsize of the x and y labels
plt.rc("xtick", labelsize=14)# Set the font size for x tick labels
plt.rc("ytick", labelsize=14)# Set the font size for y tick labels
plt.rc("legend",fontsize=12) # using a size in points

def load_hyperparameters_from_file(filename):
    """
    从JSON格式的文件中加载超参数配置。

    Args:
        filename (str): 包含超参数配置的JSON文件路径。

    Returns:
        dict: 包含所有超参数的字典对象。
    """
    fp = open(filename, "r", encoding="utf-8")
    hyperparameters = json.load(fp)  # ⭐ 核心代码：读取并解析JSON文件内容

    return hyperparameters

def get_image(path, width=1*cm):
    """
    从指定路径加载图片并创建按比例缩放的图像对象

    Args:
        path (str): 图片文件路径
        width (float): 图片宽度（默认为1厘米）

    Returns:
        Image: 按比例缩放的图像对象
    """
    img = utils.ImageReader(path)
    iw, ih = img.getSize()
    aspect = ih / float(iw)  # ⭐ 计算图片宽高比以保持比例
    return Image(path, width=width, height=(width * aspect))

class PageNumCanvas(canvas.Canvas):
    """
    自定义画布类，用于在PDF报告中添加页码显示功能（如"Page X of Y"）
    参考实现：
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
        self.drawRightString(
            int(0.17*page_size[0]), int(0.95*page_size[1]), date)
        self.drawRightString(
            int(0.93*page_size[0]), int(0.95*page_size[1]), page)

def save_report_config(filename, report_config):
    """
    将实验报告配置信息保存为JSON格式的文件。

    Args:
        filename (str): 要保存的JSON文件路径
        report_config (dict): 包含实验报告配置信息的字典

    Returns:
        None
    """
    # Write default_hyperparameters dict to a json file
    with open(filename, "w", encoding="utf-8") as fp:
        json.dump(report_config, fp)  # ⭐ 将配置字典序列化为JSON并写入文件

    fp.close()

def load_report_config(filename):
    """
    从JSON格式的配置文件中加载实验报告配置信息

    Args:
        filename (str): 配置文件的路径

    Returns:
        dict: 解析后的JSON配置字典对象
    """
    fp = open(filename, "r", encoding="utf-8")
    report_config = json.load(fp)  # ⭐ 核心操作：解析JSON配置文件内容
    fp.close()

    return report_config

def prompt_yn(prompt: str = "Do you want to continue?", yes:bool =False):
    """
    提示用户进行是/否选择，支持自动默认选择功能。

    Args:
        prompt (str): 提示信息文本，默认为"Do you want to continue?"
        yes (bool): 是否自动返回True（默认选择"是"），默认为False

    Returns:
        bool: 用户选择的结果，True表示"是"，False表示"否"
    """
    if yes is True:
        print(prompt + "[y|n] Y")  # ⭐ 自动返回True时显示默认选择
        return True
    else:
        while True:
            resp = input(prompt + "[y|n]" )
            if resp.lower() == "y":  # ⭐ 处理用户输入并返回对应布尔值
                return True
            elif resp.lower() == "n":
                return False
            else:
                continue

def rmdir(directory):
    """
    递归删除指定目录及其所有内容（包括子目录和文件）

    Args:
        directory (str/Path): 需要删除的目录路径
    """
    directory = Path(directory)
    for item in directory.iterdir():
        if item.is_dir():
            rmdir(item)
        else:
            item.unlink()  # ⭐ 删除目录中的单个文件
    directory.rmdir()

if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="Automated plotting experimnet plotting",
        usage="<script-name> --report_config <report_config>.json",
        epilog="This text will be shown after the help")
    ap.add_argument("--dirs", required=True, nargs="+",
                    help="list of directories containing experiment data")
    ap.add_argument("--report_config", required=True, type=str,
                    help="JSON report configuration file.")
    ap.add_argument("-o", "--output", required=False, type=str,
                    help="Output file location. NO CHECKS PERFORMED",
                    default="./experiment_report.pdf")
    ap.add_argument("-y", "--yes", required=False, action="store_true",
                    default=False, help="Respond with yes to all prompts")
    ap.add_argument(
        "--hyperparameters", required=False, nargs="+", type=str, default=None,
        help="Optional one or more hyperparameters files to be logged in the report.")
    ap.add_argument(
        "--tmp_dir", required=False, default=None,
        help="optional lcoation to store temporary files used for report generation.")
    args = ap.parse_args()

    if args.tmp_dir is not None:
        tmp_dir = args.tmp_dir
    else:
        tmp_dir = "./tmp"

    if os.path.isdir(tmp_dir) is True:
        if prompt_yn(f"{tmp_dir} exists. Do you want to continue?", yes=args.yes) is True:
            rmdir(tmp_dir)
        else:
            sys.exit()
    else:
        os.makedirs(tmp_dir)  # ⭐ 创建临时目录用于报告生成

    rc = load_report_config(args.report_config)

    # setup document
    doc = SimpleDocTemplate(args.output,
                                leftMargin = 0.75*inch,
                                rightMargin = 0.75*inch,
                                topMargin = 1*inch,
                                bottomMargin = 1*inch, pagesize=A4)

    # TrueType fonts work in Unicode/UTF8 and are not limited to 256 characters.
    pdfmetrics.registerFont(TTFont("Verdana", "verdana.ttf"))
    pdfmetrics.registerFont(TTFont("Vera", "Vera.ttf"))

    styles = getSampleStyleSheet()
    style = ParagraphStyle("yourtitle",
                            fontName="Verdana",
                            fontSize=12,
                            spaceAfter=6
                        )
    style_h1 = styles["Heading1"]

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

    doc.addPageTemplates([portrait_tmpl, landscape_tmpl])  # ⭐ 添加PDF页面模板

    report_data = []
    report_data.append(Paragraph("Experiment Report",style_h1))
    report_data.append(Paragraph(f'Start of automated test report {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',style))
    try:
        report_data.append(Paragraph(f'Author={os.environ["USERNAME"]}@{os.uname()[1]} obo {rc["author"]}',style))
    except:
        print("Could not get 'USERNAME'. This may happen in an RDP session.")
        report_data.append(Paragraph(f'Author=UNKNOWN@{os.uname()[1]} obo {rc["author"]}',style))

    report_data.append(Paragraph("Machine Information",style_h1))
    report_data += machine_info_in_paragraphs(style)
    report_data.append(Paragraph("Library Information",style_h1))
    report_data += lib_info_in_paragraphs(style)

    report_data.append(PageBreak())
    if args.hyperparameters is not None:
        report_data.append(Paragraph("Hpyerparameters",style_h1))
        for hpf in args.hyperparameters:
            try:
                hp = load_hyperparameters_from_file(hpf)
                report_data.append(Paragraph(f"{hpf}",style))
                for key,value in hp.items():
                    report_data.append(Paragraph(f"{key}:{value}",style))

            except Exception as e:
                print(e)
                print(f"Failed to write hyperparameters from file {hpf}")

            report_data.append(Paragraph("<br />",style))

    for key,value in rc.items():
        print(key)
        if key == "charts":
            for k,v in value.items():
                work_dir = os.path.join(tmp_dir,k)
                os.makedirs(work_dir)

                all_recs = []
                for directory in args.dirs:
                    for fd in os.listdir(directory):
                        path = os.path.join(directory,fd)
                        if os.path.isdir(path):
                            name_fields = fd.split("_")
                            if len(name_fields) == 3:
                                rec = {"dir":path,
                                    "run_name": name_fields[0],
                                    "run": name_fields[1],
                                    "algorithm": name_fields[2] }
                                all_recs.append(rec)

                err_idx = []
                for i in range(len(all_recs)):
                    file_to_open = os.path.join(
                        all_recs[i]["dir"],
                        all_recs[i]["run_name"] + "_desc.log")
                    try:
                        with open(file_to_open, "r", encoding="utf-8") as file:
                            for line in file:
                                line = line.rstrip("\r\n")
                                line_fields = line.split(" ")
                                if line_fields[0] == "experiment":
                                    all_recs[i]["experiment"] = line_fields[2]
                                if line_fields[0] == "max_steps":
                                    all_recs[i]["max_steps"] = int(line_fields[2])
                        file.close()

                    except:
                        err_idx.append(i)
                        print("Something went wrong when opening the file {file_to_open}... Noting index to remove from list.")
                # err_idx is sorted in ascending order by default.
                # Therefore we always have to subtract n from the next idx.
                # n = iters-1
                for i in range(len(err_idx)):
                    print(f"Removing original idx {err_idx[i]}, modified to {err_idx[i]-i} -> {all_recs[err_idx[i]-i]}")
                    all_recs.pop(err_idx[i]-i)

                exp_algos = []
                for e in v["experiments"]:
                    for a in v["algorithms"]:
                        t = []
                        print(e, a)
                        for r in all_recs:
                            if e == str(r["experiment"]) and a == str(r["algorithm"]):
                                t.append(r)

                        if len(t) == 0:
                            print(f"[WARNING] Did not find any experiments for \"{e}\" using algorithm \"{a}\"")
                        else:
                            exp_algos.append(t)

                cols_combined = []
                for ea in exp_algos:
                    if "window" in v:
                        window = v["window"]
                    else:
                        window = 10
                    data = generate_dataset(ea, window=window)

                    label=None
                    if "label" in v:        # Do we have a label dictionary?
                        if f"{ea[0]['experiment']}:{ea[0]['algorithm']}" in v["label"]:         # Yes we do! but do we have a label for this specific experiment ?
                            label = v["label"][f"{ea[0]['experiment']}:{ea[0]['algorithm']}"]   # Yes we do!

                    xscale="M"
                    if "xscale" in v:
                        xscale = v["xscale"]


                    if "multi_agent" in v and v["multi_agent"] is True:
                        if "mean_std_plot" in v:
                            mean_std_plot = v["mean_std_plot"]
                        else:
                            mean_std_plot = False

                        if mean_std_plot is True:
                            generate_multi_agent_plot_w_mean_std(
                                ea,
                                window=window,
                                plot="reward",
                                max_steps=200,
                                label=label,
                                scale=xscale)
                        else:
                            generate_multi_agent_plot(
                                ea,
                                window=window,
                                plot="reward",
                                max_steps=ea[0]["max_steps"],
                                label=label,
                                scale=xscale)
                    else:
                        # all runs in an "ea" should have the same number of max_steps
                        generate_plot(data,
                                      plot="reward",
                                      max_steps= ea[0]["max_steps"],
                                      label=label,
                                      scale=xscale)

                    data = generate_dataset(ea)
                    all_means, all_stds, combined = generate_table(data)
                    cols_combined.append([f"{ea[0]['experiment'].split('_',1)[-1]}:{ea[0]['algorithm']}"] + combined)

                plt.legend()
                # which=["major"|"minor"|"both] axis=["x"|"y"|"both]
                plt.grid(which="both", axis="both")

                if "title" in v: # Test for key "title" existance
                    plt.title(v["title"])
                else:
                    plt.title(k)

                if "xlabel" in v:
                    plt.xlabel(v["xlabel"])

                if "ylabel" in v:
                    plt.ylabel(v["ylabel"])

                if "ylim_bot" in v:
                    plt.ylim(bottom=int(v["ylim_bot"]))

                if "xlim_right" in v:
                    plt.xlim(right=int(v["xlim_right"]))

                chart_loc = os.path.join(work_dir, f"{k}_reward.png")
                plt.savefig(chart_loc,bbox_inches="tight")
                plt.close()

                report_data.append(PageBreak())
                report_data.append(Paragraph(f"experiment={k}",style))
                report_data.append(
                    Paragraph(f'experiments={v["experiments"]}',style))
                report_data.append(
                    Paragraph(f'algorithms={v["algorithms"]}',style))
                if "window" in v:
                    report_data.append(Paragraph(
                        f"averaging window={v['window']} (user assigned)",
                        style))
                else:
                    report_data.append(Paragraph(
                        f"averaging window=10 (default)",style))

                report_data.append(get_image(chart_loc, width=int(0.9*A4[0])))

                colwidths =[]
                # data is not transposed ...
                # +1 to account for the titles column appending next.
                for i in range(len(cols_combined)+1):
                    if i == 0:
                        colwidths.append(0.5*inch)
                    else:
                        colwidths.append(1.8*inch)

                td = list(zip(*cols_combined))

                for i in range(len(td)):
                    if i==0:
                        td[0] = ("title", *td[i])
                    elif i == len(td)-1:
                        td[i] = ("mean", *td[i])
                    else:
                        td[i] = (f"run #{i-1}", *td[i])

                t=Table(td, rowHeights=25, colWidths=colwidths)
                t.setStyle(TableStyle([
                        ("ALIGN", (0, 0), (-1, -1), "CENTRE"),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
                        ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
                        # from first col of last row to last col of last row
                        ("TEXTCOLOR",(0,-1),(-1,-1),colors.red)]))

                if len(cols_combined) > 4:
                    report_data.append(NextPageTemplate("landscape_tmpl"))
                    report_data.append(PageBreak())

                report_data.append(Paragraph("<br /><br />",style))
                report_data.append(t)
                report_data.append(Paragraph("<br /><br />",style))

                runs_involved = []
                for ea in exp_algos:
                    for item in ea:
                        runs_involved.append(
                            f"{item['run_name']}_{item['run']}")
                report_data.append(Paragraph(
                    f"runs_involved={runs_involved}",style))

        if key == "tables":
            for k,v in value.items():
                all_recs = []
                for directory in args.dirs:
                    for fd in os.listdir(directory):
                        path = os.path.join(directory,fd)
                        if os.path.isdir(path):
                            name_fields = fd.split("_")
                            if len(name_fields) == 3:
                                rec = {"dir":path,
                                    "run_name": name_fields[0],
                                    "run": name_fields[1],
                                    "algorithm": name_fields[2] }
                                all_recs.append(rec)

                err_idx = []
                for i in range(len(all_recs)):
                    file_to_open = os.path.join(
                        all_recs[i]["dir"],
                        all_recs[i]["run_name"] + "_desc.log")
                    try:
                        with open(file_to_open, "r", encoding="utf-8") as file:
                            for line in file:
                                line = line.rstrip("\r\n")
                                line_fields = line.split(" ")
                                if line_fields[0] == "experiment":
                                    all_recs[i]["experiment"] = line_fields[2]

                                if line_fields[0] == "max_steps":
                                    all_recs[i]["max_steps"] = int(line_fields[2])
                        file.close()

                    except:
                        err_idx.append(i)
                        print(f"Something went wrong when opening the file {file_to_open}... Noting index to remove from list.")
                # err_idx is sorted in ascending order by default.
                # Therefore we always have to subtract n from the next idx.
                # n = iters-1
                for i in range(len(err_idx)):
                    print(f"Removing original idx {err_idx[i]}, modified to {err_idx[i]-i} -> {all_recs[err_idx[i]-i]}")
                    all_recs.pop(err_idx[i]-i)

                exp_algos = []
                for e in v["experiments"]:
                    for a in v["algorithms"]:
                        t = []
                        print(e, a)
                        for r in all_recs:
                            if e == str(r["experiment"]) and a == str(r["algorithm"]):
                                t.append(r)

                        if len(t) == 0:
                            print(f"[WARNING] Did not find any experiments for \"{e}\" using algorithm \"{a}\"")
                        else:
                            exp_algos.append(t)

                for ea in exp_algos:
                    data = generate_dataset(ea)
                    generate_table(data)

                cols_combined = []
                for ea in exp_algos:
                    data = generate_dataset(ea)
                    all_means, all_stds, combined = generate_table(data)
                    cols_combined.append([f"{ea[0]['experiment'].split('_',1)[-1]}:{ea[0]['algorithm']}"] + combined)

                colwidths =[]
                # data is not transposed ...
                for i in range(len(cols_combined)):
                    if i == 0:
                        colwidths.append(0.5*inch)
                    else:
                        colwidths.append(1.8*inch)

                td = list(zip(*cols_combined))

                for i in range(len(td)):
                    if i==0:
                        td[0] = ("title", *td[i])
                    elif i == len(td)-1:
                        td[i] = ("mean", *td[i])
                    else:
                        td[i] = (f"run #{i-1}", *td[i])

                t=Table(td, rowHeights=25, colWidths=colwidths)
                t.setStyle(TableStyle([
                        ("ALIGN", (0, 0), (-1, -1), "CENTRE"),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
                        ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
                        # from first col of last row to last col of last row
                        ("TEXTCOLOR",(0,-1),(-1,-1),colors.red)]))

                if len(cols_combined) > 4:
                    report_data.append(NextPageTemplate("landscape_tmpl"))
                report_data.append(PageBreak())

                report_data.append(Paragraph(f"experiment={k}",style))
                report_data.append(Paragraph("<br /><br />",style))
                report_data.append(t)
                report_data.append(Paragraph("<br /><br />",style))

                runs_involved = []
                for ea in exp_algos:
                    for item in ea:
                        runs_involved.append(
                            f"{item['run_name']}_{item['run']}")
                report_data.append(Paragraph(
                    f"runs_involved={runs_involved}",style))

        print()
    report_data.append(PageBreak())
    report_data.append(Paragraph(f"End of automated test report {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",style))

    doc.build(report_data, canvasmaker=PageNumCanvas)

import platform
import sys
import os
import torch
import psutil
import pkg_resources
from reportlab.platypus import Paragraph

def machine_info_in_paragraphs(style=None):
    info = []
    info.append(Paragraph("<strong>系统信息:</strong>", style))
    info.append(Paragraph(f"操作系统: {platform.system()} {platform.release()} ({platform.version()})", style))
    info.append(Paragraph(f"架构: {platform.machine()}", style))
    info.append(Paragraph(f"处理器: {platform.processor()}", style))
    info.append(Paragraph(f"CPU核心数: {os.cpu_count()}", style))
    
    if torch.cuda.is_available():
        info.append(Paragraph(f"GPU数量: {torch.cuda.device_count()}", style))
        for i in range(torch.cuda.device_count()):
            info.append(Paragraph(f"GPU {i}: {torch.cuda.get_device_name(i)}", style))
    else:
        info.append(Paragraph("GPU: 未检测到CUDA设备", style))
    
    mem = psutil.virtual_memory()
    info.append(Paragraph(f"总内存: {mem.total / (1024**3):.2f} GB", style))
    info.append(Paragraph(f"可用内存: {mem.available / (1024**3):.2f} GB", style))
    
    return info

def lib_info_in_paragraphs(style=None):
    info = []
    info.append(Paragraph("<strong>库信息:</strong>", style))
    info.append(Paragraph(f"Python版本: {sys.version}", style))
    
    installed_packages = {p.project_name: p.version for p in pkg_resources.working_set}
    
    relevant_packages = ["torch", "numpy", "psutil"] # Add other relevant packages used in your project
    
    for pkg_name in relevant_packages:
        if pkg_name in installed_packages:
            info.append(Paragraph(f"{pkg_name}版本: {installed_packages[pkg_name]}", style))
        else:
            info.append(Paragraph(f"{pkg_name}版本: 未安装", style))
            
    return info

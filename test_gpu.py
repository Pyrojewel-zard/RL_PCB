import torch
print(torch.cuda.device_count())  # 应输出 2
print(torch.cuda.get_device_name(0), torch.cuda.get_device_name(1))  # 确认两块 4090
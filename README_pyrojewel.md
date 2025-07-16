# RL_PCB 开发流程

本文档描述了如何设置和开发 `RL_PCB` 项目。

## 1. 克隆代码库

首先，从 Git 仓库克隆代码。

```bash
git clone git@github.com:Pyrojewel-zard/RL_PCB.git
```

## 2. 进入项目目录

克隆完成后，进入项目根目录。

```bash
cd RL_PCB
```

## 3. 初始化开发环境

运行 `setup_dev.sh` 脚本来安装所有系统依赖、编译第三方工具和设置 Python 虚拟环境。

```bash
./setup_dev.sh
```

**提示**:
*   此脚本会使用 `sudo` 来安装系统级别的软件包 (如 `build-essential`, `python3.10-venv` 等)，因此在执行过程中可能会提示您输入管理员密码。
*   如果您没有 NVIDIA GPU 或不想安装 GPU 版本的 PyTorch，可以添加 `--cpu_only` 标志来仅安装 CPU 版本：
    ```bash
    ./setup_dev.sh --cpu_only
    ```

## 4. 激活虚拟环境

脚本成功执行后，您需要手动激活已创建的 Python 虚拟环境。之后所有与 Python 相关的开发和运行任务都应在此环境中进行。

```bash
source venv/bin/activate
```

激活成功后，您的命令行提示符左侧应该会显示 `(venv)` 字样。

## 5. 开始开发

现在，开发环境已经准备就绪。您可以开始修改源代码了。项目的主要 Python 源代码位于 `src/` 目录下。

## 6. 运行验证脚本

为了确保所有依赖都已正确安装，您可以运行项目自带的验证脚本。

```bash
python tests/00_verify_machine_setup/test_setup.py
```

*(请注意：根据 `setup_dev.sh` 的逻辑，此脚本在环境安装的最后一步会自动运行一次，您也可以手动再次运行以进行验证。)*

## 7. 退出虚拟环境

当您完成当天的开发工作后，可以运行以下命令退出 Python 虚拟环境：

```bash
deactivate
``` 
# CUDA 启用问题排查指南（PyTorch版）

## 快速诊断流程
当 `torch.cuda.is_available()` 返回 `False` 时，按顺序执行以下命令：

### 第一步：基础诊断
```bash
# 检查PyTorch的CUDA支持
python -c "import torch; print(f'PyTorch版本: {torch.__version__}'); print(f'CUDA可用: {torch.cuda.is_available()}')"

# 检查GPU驱动状态（所有系统通用）
nvidia-smi
```

### 第二步：环境验证
```bash
# 检查CUDA编译器版本
nvcc --version 2>/dev/null || echo "未找到nvcc，请安装CUDA Toolkit"

# 查看CUDA环境变量（不同系统命令）
echo "Linux/Mac CUDA路径: $CUDA_HOME"  # 若为空需设置环境变量
echo "Windows CUDA路径: %CUDA_PATH%"   # 在CMD/PowerShell中执行
```

---

## 分步解决方案

### 1. 验证PyTorch版本兼容性
```bash
# 查看当前安装的PyTorch版本
pip show torch | grep -E "Version|Location"

# 安装指定CUDA版本的PyTorch（以CUDA12.1为例）
pip uninstall -y torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### 2. 创建纯净环境（推荐）
```bash
# 使用conda创建新环境
conda create -n pytorch_cuda python=3.9 -y
conda activate pytorch_cuda

# 使用venv创建（系统自带）
python -m venv cuda_env
source cuda_env/bin/activate  # Linux/Mac
# cuda_env\Scripts\activate   # Windows
```

### 3. 快速诊断脚本
将以下内容保存为 `cuda_check.py`：
```python
import torch
print(f"PyTorch版本: {torch.__version__}")
print(f"CUDA可用: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"设备数量: {torch.cuda.device_count()}")
    print(f"当前设备: {torch.cuda.get_device_name(0)}")
else:
    print("可能原因：1. 驱动未安装 2. PyTorch版本不匹配 3. 虚拟环境问题")
```

执行命令：
```bash
python cuda_check.py
```

---

## 常见问题处理

### 问题1：驱动正常但PyTorch不识别GPU
```bash
# 安装精简版CUDA工具包（conda方案）
conda install cudatoolkit=12.1 -c nvidia

# 验证驱动兼容性（驱动版本需>=CUDA版本要求）
nvidia-smi | grep "Driver Version"
```

### 问题2：多CUDA版本冲突
```bash
# Linux切换默认CUDA版本
sudo update-alternatives --config cuda

# Windows检查环境变量优先级
echo %PATH% | grep -i "cuda"
```

---

## 一键验证命令
```bash
# 综合诊断命令（复制到终端直接运行）
echo "=== 基础检查 ===" && \
python -c "import torch; print(f'PyTorch版本: {torch.__version__}'); print(f'CUDA可用: {torch.cuda.is_available()}')" && \
echo "\n=== GPU状态 ===" && \
nvidia-smi && \
echo "\n=== CUDA工具链 ===" && \
nvcc --version 2>/dev/null || echo "未找到nvcc" && \
echo "\n=== 环境变量 ===" && \
echo "CUDA_HOME: $CUDA_HOME"
```

---

## 技术支持
- PyTorch官方安装：[pytorch.org/get-started](https://pytorch.org/get-started)
- NVIDIA驱动下载：[nvidia.com/drivers](https://www.nvidia.com/Download/index.aspx)
- CUDA兼容性查询：[NVIDIA文档](https://docs.nvidia.com/cuda/)

#!/bin/bash
# 修复 diffusers 依赖问题的脚本

echo "🔧 修复 diffusers 依赖问题..."
echo ""

# 检查 Python 版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python 版本: $python_version"

# 方案1: 降级 huggingface_hub 到兼容版本
echo ""
echo "方案1: 降级 huggingface_hub 到 0.25.2 (推荐)"
echo "执行: pip3 install --user 'huggingface_hub==0.25.2'"
echo ""

# 方案2: 升级 diffusers 到最新版本
echo "方案2: 升级 diffusers 到最新版本"
echo "执行: pip3 install --user --upgrade diffusers transformers"
echo ""

# 方案3: 使用虚拟环境（推荐用于生产环境）
echo "方案3: 使用虚拟环境重新安装所有依赖"
echo "执行步骤:"
echo "  1. python3 -m venv venv"
echo "  2. source venv/bin/activate"
echo "  3. pip install -r requirements.txt"
echo ""

echo "请选择其中一个方案执行。"
echo "如果网络有问题，可以尝试使用国内镜像:"
echo "  pip3 install --user -i https://pypi.tuna.tsinghua.edu.cn/simple huggingface_hub==0.25.2"

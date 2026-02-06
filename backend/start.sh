#!/bin/bash

# AI Meme Generator - 启动脚本
# 支持 Clipdrop / 本地 WebUI / Hugging Face / Mock 等模式

echo "🎭 AI Meme Generator 启动脚本"
echo "================================"

# 检查 Clipdrop Key
if [ -n "$CLIPDROP_API_KEY" ]; then
    echo "🟦 Clipdrop API: 已配置"
    USE_CLIPDROP=true
else
    echo "🟦 Clipdrop API: 未配置"
    USE_CLIPDROP=false
fi

# 检查 WebUI
if [ -n "$SD_WEBUI_URL" ]; then
    echo "🧪 SD WebUI: 已配置 ($SD_WEBUI_URL)"
    USE_WEBUI=true
else
    echo "🧪 SD WebUI: 未配置"
    USE_WEBUI=false
fi

# 检查 Hugging Face API Token
if [ -n "$HUGGINGFACE_API_TOKEN" ]; then
    echo "🔑 Hugging Face API: 已配置"
    USE_HF=true
else
    echo "🔑 Hugging Face API: 未配置"
    USE_HF=false
fi

echo ""
echo "请选择运行模式:"
echo "1. 使用 Clipdrop（优先推荐）"
echo "2. 使用本地 WebUI（需要 A1111）"
echo "3. 使用 Hugging Face API（需要 Token）"
echo "4. 使用 Mock 模式（开发测试用）"
echo ""

read -p "请输入选择 (1/2/3/4): " choice

case $choice in
    1)
        if [ "$USE_CLIPDROP" = false ]; then
            echo ""
            echo "❌ 错误: 未设置 CLIPDROP_API_KEY"
            echo ""
            echo "请设置环境变量:"
            echo "  export CLIPDROP_API_KEY='your_key_here'"
            echo ""
            echo "或直接运行:"
            echo "  CLIPDROP_API_KEY='your_key_here' python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
            exit 1
        fi
        echo "🚀 启动 Clipdrop 模式..."
        python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
        ;;
    2)
        if [ "$USE_WEBUI" = false ]; then
            echo ""
            echo "❌ 错误: 未设置 SD_WEBUI_URL"
            echo ""
            echo "请设置环境变量:"
            echo "  export SD_WEBUI_URL='http://127.0.0.1:7860'"
            echo ""
            echo "或直接运行:"
            echo "  SD_WEBUI_URL='http://127.0.0.1:7860' python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
            exit 1
        fi
        echo "🚀 启动本地 WebUI 模式..."
        python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
        ;;
    3)
        if [ "$USE_HF" = false ]; then
            echo ""
            echo "❌ 错误: 未设置 HUGGINGFACE_API_TOKEN"
            echo ""
            echo "请设置环境变量:"
            echo "  export HUGGINGFACE_API_TOKEN='your_token_here'"
            echo ""
            echo "或直接运行:"
            echo "  HUGGINGFACE_API_TOKEN='your_token' python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
            exit 1
        fi
        echo "🚀 启动 Hugging Face API 模式..."
        python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
        ;;
    4)
        echo "🚀 启动 Mock 模式..."
        echo "⚠️  注意: Mock 模式会生成简单的占位图"
        python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

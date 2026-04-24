#!/bin/bash

# Oasis 后端启动脚本

echo "🚀 启动 Oasis 后端服务器..."

# 检查虚拟环境
if [ ! -d "../.venv" ]; then
    echo "❌ 虚拟环境不存在，请先创建: python -m venv ../.venv"
    exit 1
fi

# 激活虚拟环境
source ../.venv/bin/activate

# 检查依赖
echo "📦 检查依赖..."
pip list | grep -q "fastapi" || pip install -r requirements.txt

# 启动服务器
echo "✅ 启动 FastAPI 服务器 (http://localhost:8000)"
echo "📚 API 文档: http://localhost:8000/docs"
echo "📖 ReDoc: http://localhost:8000/redoc"
echo "🔧 OpenAPI JSON: http://localhost:8000/openapi.json"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000

#!/bin/bash

# Oasis 启动脚本

cd "$(dirname "$0")"

echo "🚀 启动 Oasis 后端..."

source venv/bin/activate
cd backend

# 如果.env不存在则创建
if [ ! -f .env ]; then
    echo "创建 .env 文件..."
    cat > .env << EOF
DATABASE_URL=sqlite:///./oasis.db
HOST=0.0.0.0
PORT=8000
DEBUG=True
EOF
fi

# 启动服务器
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

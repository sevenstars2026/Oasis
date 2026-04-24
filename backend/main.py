"""
Oasis - 主程序
世界操作系统 v0.1
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from utils.database import init_db
from api.routes.players import router as players_router
from api.routes.tasks import router as tasks_router
from api.routes.trades import router as trades_router
from api.routes.map import router as map_router
from api.routes.jobs import router as jobs_router
from api.routes.properties import router as properties_router
from api.routes.websocket import router as websocket_router

# 初始化FastAPI应用
app = FastAPI(
    title="Oasis",
    description="持久的社会模拟游戏",
    version="0.1.0"
)

# CORS配置（允许前端访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    init_db()
    print("🚀 Oasis server started")


@app.get("/health")
async def health():
    """健康检查端点"""
    return {
        "status": "ok",
        "message": "Oasis is running"
    }


@app.get("/")
async def root():
    """根端点"""
    return {
        "name": "Oasis",
        "version": "0.1.0",
        "docs": "/docs"
    }


# 注册路由
app.include_router(players_router)
app.include_router(tasks_router)
app.include_router(trades_router)
app.include_router(map_router)
app.include_router(jobs_router)
app.include_router(properties_router)
app.include_router(websocket_router)


if __name__ == "__main__":
    # 获取配置
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    # 运行服务器
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=True
    )

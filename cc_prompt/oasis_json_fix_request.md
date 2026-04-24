# Oasis 前后端JSON乱码问题修复请求

## 问题描述
用户打开前后端网址看到JSON乱码。实际诊断发现：
- `/openapi.json` 返回空内容
- 某些API可能有序列化问题
- 后端启动有deprecation警告

## 代码现状

### requirements.txt
```
FastAPI==0.104.1
uvicorn==0.24.0
pydantic==2.5.0  ← 高版本，需要检查兼容性
```

### main.py（简化版）
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(...)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ← 可能有问题
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")  # ← ❌ 已弃用，FastAPI 0.104需要用lifespan
async def startup_event():
    init_db()

@app.get("/")
async def root():
    return {"name": "Oasis", ...}

# 注册6个路由器
app.include_router(players_router)
app.include_router(tasks_router)
app.include_router(trades_router)
app.include_router(map_router)
app.include_router(jobs_router)
app.include_router(properties_router)
app.include_router(websocket_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)  # ← ❌ reload=True在直接python运行时无效
```

### schemas.py 关键模型
- PlayerResponse: ✅ 简单字段，应无问题
- TaskResponse: ⚠️ 有 `datetime` 字段，需检查序列化
- TradeResponse: ⚠️ 有 `datetime` 字段和自定义 `from_orm()`
- MarketStatsResponse: ⚠️ 有 Dict 嵌套类型

## 需要修复

### 修复1: main.py 中的 on_event deprecation
```python
# 旧方式（已弃用）
@app.on_event("startup")
async def startup_event():
    init_db()

# 新方式 (FastAPI 0.93+)
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    print("🚀 Oasis server started")
    yield
    # Shutdown
    print("🛑 Oasis server shutting down")

app = FastAPI(
    title="Oasis",
    description="持久的社会模拟游戏",
    version="0.1.0",
    lifespan=lifespan
)
```

### 修复2: 检查所有 schemas 的 JSON 序列化能力
特别注意：
- datetime 字段是否能正确序列化？
- Dict 嵌套结构是否正确？
- 自定义 from_orm() 是否完整？

### 修复3: CORS 配置优化
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # ← 具体指定
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)
```

### 修复4: 启动方式修复
不要在 if __name__ == "__main__" 中使用 reload=True，
改为用命令行：`uvicorn main:app --reload --host 0.0.0.0 --port 8000`

## 你需要做的

1. 📋 **检查诊断**
   - 所有 datetime 字段是否能序列化？
   - 是否有循环引用？
   - 所有枚举值是否正确定义？

2. 🔧 **生成修复文件**
   - 新的 main.py （使用 lifespan）
   - 更新 schemas.py（如有需要）
   - 更新 requirements.txt（如有版本冲突）

3. ✅ **提供执行步骤**
   - 如何更新代码
   - 如何启动后端
   - 如何验证 /openapi.json 能正常返回

4. 📝 **给出诊断结论**
   - 根本原因是什么？
   - 为什么会导致JSON乱码/为空？
   - 如何从根本上避免此问题？

## 背景信息
- 项目: Oasis（持久社会模拟游戏）
- Python虚拟环境：/home/sevenstars/CLionProjects/Oasis/.venv
- 后端路径：/home/sevenstars/CLionProjects/Oasis/backend
- 前端运行在 5173，后端应运行在 8000
- 已有 6 个路由器集成

## 优先级
**🔴 紧急** - 用户无法使用系统，JSON返回乱码阻塞所有功能


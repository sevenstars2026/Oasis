# Oasis - 世界操作系统 v0.1

## 🎯 目标

一个持久的、自组织的、异步协作的社会模拟世界。

## 🏗️ 项目结构

```
Oasis/
├── backend/
│   ├── main.py              ← FastAPI 主程序
│   ├── models/              ← 数据模型
│   ├── services/            ← 业务逻辑
│   ├── utils/
│   │   └── database.py      ← 数据库连接
│   ├── requirements.txt      ← 依赖
│   └── .env                 ← 配置
├── frontend/                ← React 前端（待开发）
└── run.sh                   ← 启动脚本
```

## 🚀 快速开始

### 1. 启动后端

```bash
chmod +x run.sh
./run.sh
```

访问 http://localhost:8000/docs 查看API文档

### 2. 启动前端（待开发）

```bash
cd frontend
npm install
npm run dev
```

## 📋 核心数据模型

- **Player** - 玩家
- **Task** - 任务
- **Trade** - 交易
- **CityEvent** - 城市事件（历史）
- **CityState** - 城市状态
- **Inventory** - 背包
- **NPC** - NPC角色

## 🎮 核心特性

✅ 持久的世界状态
✅ 异步任务系统
✅ 交易市场
✅ 历史记录
✅ 自动化NPC
✅ 城市政策系统（待开发）

## 📝 开发进度

- [x] 项目初始化
- [x] 数据模型设计
- [x] FastAPI 框架搭建
- [ ] 玩家认证系统
- [ ] 任务系统实现
- [ ] 交易系统实现
- [ ] WebSocket 实时通信
- [ ] 前端 React UI
- [ ] AI 自动化系统

## 🔧 开发命令

```bash
# 启动后端（自动重加载）
./run.sh

# 运行测试
cd backend
source ../venv/bin/activate
pytest

# 生成 API 文档
# 自动生成在 http://localhost:8000/docs
```

## 📚 核心概念

### 异步任务去人绑定

任务不绑定具体的玩家，而是绑定"能力需求"：
- 任务需要 "战士" 能力
- 任何战士都可以接手
- 若无玩家，AI可自动完成

这保证了：
✅ 玩家离线不会卡住任务
✅ 新加入的玩家能立即参与
✅ 没有人因为"摆烂"而被惩罚

### 持久世界

- 城市 24/7 自动演进
- NPC 自动行动
- 交易市场自动撮合
- 历史永久记录

---

**Oasis - 让每个人都能成为世界的共同创造者** 🌍

# Oasis - 第二国度 v0.2

## 🎯 项目愿景

Oasis 不是传统游戏，也不是元宇宙，而是一个**基于 AI 和互联网的第二国度** - 一个人类可以自由探索、工作、交易、建立真实社会关系的平行世界。

### 三大核心驱动力

1. **真实的"第二人生"机会** - 提供现实世界无法提供的社会流动性
2. **时间主权 + 异步协作** - 不受固定时间约束，每份劳动公平计量
3. **AI 时代的"人类价值证明"** - 人类独有价值：信任、情感、创造性协作

## 🏗️ 项目结构

```
Oasis/
├── backend/
│   ├── main.py              ← FastAPI 主程序
│   ├── models/              ← 数据模型
│   │   └── __init__.py      ← Player, Task, Trade, Location, Job, Property 等
│   ├── services/            ← 业务逻辑层
│   │   ├── player_service.py
│   │   ├── task_service.py
│   │   ├── trade_service.py
│   │   ├── map_service.py      ← 新增
│   │   ├── job_service.py      ← 新增
│   │   └── property_service.py ← 新增
│   ├── api/routes/          ← API 路由
│   │   ├── players.py
│   │   ├── tasks.py
│   │   ├── trades.py
│   │   ├── map.py              ← 新增
│   │   ├── jobs.py             ← 新增
│   │   └── properties.py       ← 新增
│   ├── utils/
│   │   └── database.py      ← 数据库连接
│   ├── seed_data.py         ← 种子数据初始化 ← 新增
│   ├── requirements.txt     ← 依赖
│   └── .env                 ← 配置
├── frontend/                ← React 前端（待开发）
├── TECHNICAL_DESIGN.md      ← 技术设计文档 ← 新增
└── run.sh                   ← 启动脚本
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
pip install -r backend/requirements.txt
```

### 2. 初始化数据库和种子数据

```bash
cd backend
python3 seed_data.py
```

### 3. 启动后端

```bash
# 方式1：使用 uvicorn
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 方式2：使用启动脚本
./run.sh
```

访问 http://localhost:8000/docs 查看 API 文档

### 4. 启动前端（待开发）

```bash
cd frontend
npm install
npm run dev
```

## 📋 核心数据模型

### 已实现
- **Player** - 玩家（认证、职业、金币）
- **Task** - 任务（异步协作）
- **Trade** - 交易（市场撮合）
- **Location** - 地图位置 ⭐ 新增
- **Job** - 工作系统 ⭐ 新增
- **WorkSession** - 工作记录 ⭐ 新增
- **Property** - 房产系统 ⭐ 新增
- **Resource** - 资源点 ⭐ 新增
- **PlayerState** - 玩家实时状态 ⭐ 新增
- **MarketPrice** - 市场价格历史 ⭐ 新增
- **Inventory** - 背包
- **NPC** - NPC 角色
- **CityEvent** - 城市事件
- **CityState** - 城市状态

## 🎮 核心系统

### ✅ 已实现
- 玩家认证系统
- 异步任务系统
- 交易市场（自动撮合）
- **地图与探索系统** ⭐ 新增
  - 7 个初始位置（广场、住宅区、工业区、市场街、森林、矿山、港口）
  - 玩家移动和位置管理
  - 资源采集系统
- **工作系统** ⭐ 新增
  - 6 种初始工作（木材加工、矿石冶炼、市场摊贩、伐木工、矿工、图书管理员）
  - 基于时间的收益计算
  - 离线工作支持（最多 8 小时）
- **房产系统** ⭐ 新增
  - 9 个初始房产（公寓、房屋、商铺、仓库）
  - 购买、租赁、升级机制
  - 房产估值动态调整

### 🚧 待开发
- WebSocket 实时通信
- 前端 React UI
- AI 调控系统（Claude API 集成）
- 社交系统（聊天、好友）
- 声誉系统

## 📝 开发进度

- [x] 项目初始化
- [x] 数据模型设计
- [x] FastAPI 框架搭建
- [x] 玩家认证系统
- [x] 任务系统实现
- [x] 交易系统实现
- [x] **地图与探索系统** ⭐
- [x] **工作系统** ⭐
- [x] **房产系统** ⭐
- [x] **种子数据初始化** ⭐
- [x] **技术设计文档** ⭐
- [ ] WebSocket 实时通信
- [ ] 前端 React UI
- [ ] AI 自动化系统

## 🔧 开发命令

```bash
# 启动后端（自动重加载）
cd backend
uvicorn main:app --reload

# 初始化种子数据
cd backend
python3 seed_data.py

# 运行测试
cd backend
source ../.venv/bin/activate
pytest

# 查看 API 文档
# 访问 http://localhost:8000/docs
```

## 📚 API 端点

### 玩家系统
- `POST /players/register` - 注册
- `POST /players/login` - 登录
- `GET /players/me` - 获取当前玩家信息

### 任务系统
- `GET /tasks` - 获取任务列表
- `POST /tasks/create` - 创建任务
- `POST /tasks/{task_id}/accept` - 接受任务

### 交易系统
- `GET /trades/market` - 获取市场挂单
- `POST /trades/create` - 创建交易
- `POST /trades/{trade_id}/accept` - 接受交易

### 地图系统 ⭐ 新增
- `GET /map/locations` - 获取所有位置
- `GET /map/locations/{location_id}` - 获取位置详情
- `POST /map/move` - 移动玩家
- `POST /map/harvest` - 采集资源

### 工作系统 ⭐ 新增
- `GET /jobs/available` - 获取可用工作
- `POST /jobs/start` - 开始工作
- `POST /jobs/end` - 结束工作
- `GET /jobs/history` - 工作历史

### 房产系统 ⭐ 新增
- `GET /properties/for-sale` - 可售房产
- `GET /properties/my-properties` - 我的房产
- `POST /properties/buy` - 购买房产
- `POST /properties/rent` - 租赁房产
- `POST /properties/upgrade` - 升级房产

## 📖 技术文档

详细的技术设计文档请查看：[TECHNICAL_DESIGN.md](./TECHNICAL_DESIGN.md)

包含：
- 完整系统架构
- 数据模型设计
- API 设计规范
- MVP 实现路线图
- 性能优化方案

## 🛡️ 技术保障

### 内存管理
- ✅ SQLAlchemy session 自动管理
- ✅ 数据库连接池
- ✅ 查询分页防止内存溢出

### 性能优化
- ✅ 数据库索引优化
- ✅ 外键约束保证数据一致性
- ✅ 事务管理

### 安全性
- ✅ JWT 认证
- ✅ 密码加密存储
- ✅ SQL 注入防护（ORM）
- ✅ 输入验证

## 📊 当前数据统计

初始化后的数据：
- 位置：7 个
- 资源点：4 个
- 工作：6 个
- 房产：9 个

## 🎯 下一步计划

1. **WebSocket 实时通信**（Week 1-2）
   - 玩家位置同步
   - 聊天系统
   - 实时事件推送

2. **前端开发**（Week 3-4）
   - React + Canvas 2.5D 渲染
   - 地图显示和玩家移动
   - UI 界面

3. **AI 集成**（Week 5-6）
   - Claude API 集成
   - 经济调控
   - 事件生成

---

**Oasis - 探索更好的现实** 🌍

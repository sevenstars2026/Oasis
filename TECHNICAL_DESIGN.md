# Oasis - 技术设计文档 v1.0

## 📋 文档概述

**项目名称**: Oasis - 第二国度  
**版本**: v1.0  
**更新日期**: 2026-04-24  
**文档目标**: 定义 Oasis MVP 的完整技术架构和实现路线

---

## 🎯 项目愿景

### 核心定位
Oasis 不是传统游戏，也不是元宇宙，而是一个**基于 AI 和互联网的第二国度** - 一个人类可以自由探索、工作、交易、建立真实社会关系的平行世界。

### 三大核心驱动力

**1. 真实的"第二人生"机会**
- 提供现实世界无法提供的社会流动性
- 经济系统真实（供需、通胀、竞争）
- 社交关系真实（真人互动，非 NPC）
- 努力有复利效应（房产增值、声誉积累）

**2. 时间主权 + 异步协作**
- 异步工作：不受固定时间约束
- 任务不绑定人：可随时接手他人任务
- 贡献被记录：每份劳动公平计量
- 时间灵活：每天 10 分钟或 10 小时都能参与

**3. AI 时代的"人类价值证明"**
- 人类独有价值：信任、情感、创造性协作
- AI 是工具不是替代：AI 处理重复劳动，人做决策和创造
- 社会性动物本质：需要被真人认可，不是 AI

### 核心差异化
- **自由度优先**：不是任务驱动，而是开放世界
- **经济驱动**：真实的供需关系，不是打怪升级
- **社交自然发生**：在工作、交易、探索中自然相遇
- **AI 调控者**：维持世界运转，但不主导玩家体验

---

## 🏗️ 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   React UI   │  │ Canvas 2.5D  │  │  WebSocket   │      │
│  │   (Zustand)  │  │   Renderer   │  │    Client    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                         API Gateway                          │
│                    FastAPI + WebSocket                       │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                       Backend Services                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │  Player  │ │   Map    │ │  Trade   │ │   Job    │      │
│  │ Service  │ │ Service  │ │ Service  │ │ Service  │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │ Property │ │   Task   │ │   NPC    │ │    AI    │      │
│  │ Service  │ │ Service  │ │ Service  │ │Controller│      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                        Data Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  PostgreSQL  │  │    Redis     │  │   Claude API │      │
│  │  (主数据库)  │  │   (缓存)     │  │  (AI 服务)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### 技术栈选择

**Backend**
- **框架**: FastAPI (已有)
- **数据库**: PostgreSQL + SQLAlchemy (已有)
- **缓存**: Redis (用于实时数据、WebSocket 状态)
- **AI**: Claude API (Opus 4.7)
- **实时通信**: WebSocket (FastAPI 原生支持)

**Frontend**
- **框架**: React 18 + TypeScript
- **状态管理**: Zustand (轻量级)
- **渲染引擎**: Canvas 2D + 自定义渲染器 (2.5D 效果)
- **备选**: Phaser.js (如果需要更复杂的游戏逻辑)
- **通信**: WebSocket + Axios

**DevOps**
- **容器化**: Docker + Docker Compose
- **CI/CD**: GitHub Actions
- **监控**: Prometheus + Grafana (后期)

---

## 📊 数据模型设计

### 核心模型扩展

#### 1. Location (地图位置)

```python
class Location(Base):
    """地图位置模型"""
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(100))  # 显示名称
    
    # 位置信息
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    zone_type = Column(String(50))  # residential, commercial, industrial, wilderness
    
    # 属性
    description = Column(Text)
    capacity = Column(Integer, default=50)  # 最大容纳人数
    current_players = Column(Integer, default=0)
    
    # 资源点
    resources = Column(Text)  # JSON: [{"type": "wood", "amount": 100}, ...]
    
    # 建筑/设施
    buildings = Column(Text)  # JSON: [{"type": "shop", "owner_id": 1}, ...]
    
    # 状态
    is_unlocked = Column(Boolean, default=True)
    unlock_requirement = Column(Text)  # JSON: {"gold": 1000, "reputation": 50}
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
```

#### 2. Property (房产)

```python
class Property(Base):
    """房产模型"""
    __tablename__ = "properties"
    
    id = Column(Integer, primary_key=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    
    # 基本信息
    property_type = Column(String(50))  # apartment, house, shop, warehouse
    size = Column(Integer)  # 面积（平方米）
    
    # 所有权
    owner_id = Column(Integer, ForeignKey("players.id"), nullable=True)
    purchase_price = Column(Float)
    current_value = Column(Float)  # 当前估值
    
    # 租赁
    is_rented = Column(Boolean, default=False)
    tenant_id = Column(Integer, ForeignKey("players.id"), nullable=True)
    rent_price = Column(Float, default=0)
    rent_due_date = Column(DateTime, nullable=True)
    
    # 状态
    condition = Column(Float, default=100.0)  # 0-100，影响价值
    upgrade_level = Column(Integer, default=1)
    
    # 功能
    features = Column(Text)  # JSON: ["storage_+50", "crafting_bench", ...]
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
```

#### 3. Job (工作系统)

```python
class Job(Base):
    """工作模型（持续性工作，不是一次性任务）"""
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True)
    
    # 工作信息
    title = Column(String(100), nullable=False)
    description = Column(Text)
    job_type = Column(String(50))  # mining, crafting, trading, guarding, researching
    
    # 需求
    required_job_class = Column(String(50))  # warrior, merchant, crafter, scholar
    required_level = Column(Integer, default=1)
    location_id = Column(Integer, ForeignKey("locations.id"))
    
    # 报酬
    base_pay = Column(Float)  # 基础工资（每小时）
    bonus_conditions = Column(Text)  # JSON: {"efficiency": 1.5, "quality": 1.2}
    
    # 状态
    is_available = Column(Boolean, default=True)
    max_workers = Column(Integer, default=1)
    current_workers = Column(Integer, default=0)
    
    # 雇主
    employer_id = Column(Integer, ForeignKey("players.id"), nullable=True)  # null = NPC/系统
    employer_type = Column(String(20), default="system")  # system, player, npc
    
    created_at = Column(DateTime, default=datetime.now)
```

#### 4. WorkSession (工作记录)

```python
class WorkSession(Base):
    """工作会话记录"""
    __tablename__ = "work_sessions"
    
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    
    # 时间
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, default=0)
    
    # 产出
    output = Column(Text)  # JSON: {"items": [...], "quality": 0.85}
    earnings = Column(Float, default=0)
    
    # 状态
    status = Column(String(20), default="active")  # active, completed, interrupted
    
    created_at = Column(DateTime, default=datetime.now)
```

#### 5. Resource (资源点)

```python
class Resource(Base):
    """资源点模型"""
    __tablename__ = "resources"
    
    id = Column(Integer, primary_key=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    
    # 资源信息
    resource_type = Column(String(50))  # wood, stone, ore, herbs
    amount = Column(Float)  # 当前数量
    max_amount = Column(Float)  # 最大容量
    
    # 采集
    regeneration_rate = Column(Float)  # 每小时恢复量
    difficulty = Column(Float, default=1.0)  # 采集难度系数
    
    # 状态
    is_depleted = Column(Boolean, default=False)
    last_harvested = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
```

#### 6. PlayerState (玩家实时状态)

```python
class PlayerState(Base):
    """玩家实时状态（用于 WebSocket 同步）"""
    __tablename__ = "player_states"
    
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"), unique=True, nullable=False)
    
    # 位置
    location_id = Column(Integer, ForeignKey("locations.id"))
    x = Column(Float, default=0)
    y = Column(Float, default=0)
    
    # 状态
    is_online = Column(Boolean, default=False)
    current_activity = Column(String(50))  # idle, working, trading, moving
    
    # 工作状态
    current_job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    work_session_id = Column(Integer, ForeignKey("work_sessions.id"), nullable=True)
    
    # 社交
    current_chat_room = Column(String(100), nullable=True)
    
    last_active = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
```

#### 7. MarketPrice (市场价格历史)

```python
class MarketPrice(Base):
    """市场价格历史（用于经济分析）"""
    __tablename__ = "market_prices"
    
    id = Column(Integer, primary_key=True)
    item_name = Column(String(100), nullable=False)
    
    # 价格
    average_price = Column(Float)
    min_price = Column(Float)
    max_price = Column(Float)
    
    # 交易量
    volume = Column(Integer)  # 交易数量
    trade_count = Column(Integer)  # 交易次数
    
    # 时间
    date = Column(DateTime, nullable=False)
    
    created_at = Column(DateTime, default=datetime.now)
```

---

## 🎮 核心系统设计

### 1. 地图与探索系统

#### 功能需求
- 玩家可以在地图上自由移动
- 不同区域有不同的资源、NPC、任务
- 某些区域需要解锁（金币、声誉、任务完成）
- 实时显示其他在线玩家位置

#### API 设计

```python
# 获取地图信息
GET /api/map/locations
Response: [
    {
        "id": 1,
        "name": "plaza",
        "display_name": "中央广场",
        "x": 0,
        "y": 0,
        "zone_type": "commercial",
        "current_players": 15,
        "is_unlocked": true,
        "resources": [],
        "buildings": [...]
    },
    ...
]

# 移动到新位置
POST /api/map/move
Request: {"location_id": 2, "x": 100, "y": 50}
Response: {"success": true, "new_location": {...}}

# 获取位置详情
GET /api/map/locations/{location_id}
Response: {
    "location": {...},
    "players_here": [...],
    "available_jobs": [...],
    "resources": [...],
    "properties": [...]
}

# 采集资源
POST /api/map/harvest
Request: {"resource_id": 1, "duration_minutes": 10}
Response: {"items_gained": [...], "experience": 10}
```

#### 前端实现
- Canvas 2D 渲染地图
- 瓦片地图（Tilemap）或矢量绘制
- 玩家精灵（Sprite）+ 平滑移动动画
- 小地图（Minimap）显示全局位置

### 2. 工作系统

#### 核心机制
- **持续性工作**：不是一次性任务，而是可以持续做的工作
- **时间灵活**：可以工作 10 分钟或 10 小时
- **产出计算**：基于时间、技能、效率
- **异步结算**：离线也可以继续工作（有上限）

#### 工作流程

```
1. 玩家找到工作 (Job)
2. 开始工作 (创建 WorkSession)
3. 工作中... (实时或离线)
4. 结束工作 (结算产出和报酬)
5. 获得金币 + 物品 + 经验
```

#### API 设计

```python
# 获取可用工作列表
GET /api/jobs/available
Query: ?location_id=1&job_class=crafter
Response: [
    {
        "id": 1,
        "title": "木材加工",
        "job_type": "crafting",
        "base_pay": 50,  # 每小时
        "location": "工业区",
        "current_workers": 2,
        "max_workers": 5
    },
    ...
]

# 开始工作
POST /api/jobs/start
Request: {"job_id": 1}
Response: {
    "work_session_id": 123,
    "started_at": "2026-04-24T10:00:00",
    "estimated_pay_per_hour": 50
}

# 结束工作
POST /api/jobs/end
Request: {"work_session_id": 123}
Response: {
    "duration_minutes": 30,
    "earnings": 25,
    "items_produced": [{"name": "木板", "quantity": 5}],
    "experience_gained": 15
}

# 获取工作历史
GET /api/jobs/history
Response: [...]
```

#### 离线工作机制
- 玩家可以设置"离线工作"（最多 8 小时）
- 离线期间按基础效率计算产出（无加成）
- 上线时自动结算

### 3. 房产系统

#### 核心机制
- **购买房产**：花费金币购买
- **房产增值**：基于区域发展、供需关系
- **租赁收入**：出租给其他玩家或 NPC
- **功能升级**：增加存储、工作台等功能

#### 房产类型

| 类型 | 基础价格 | 功能 | 租金收入 |
|------|---------|------|---------|
| 公寓 | 5,000 | 基础居住 | 50/天 |
| 房屋 | 20,000 | 存储+50 | 200/天 |
| 商铺 | 50,000 | 可开店 | 500/天 |
| 仓库 | 100,000 | 存储+500 | 1000/天 |

#### API 设计

```python
# 获取可售房产
GET /api/properties/for-sale
Query: ?location_id=1&property_type=house
Response: [...]

# 购买房产
POST /api/properties/buy
Request: {"property_id": 1}
Response: {"success": true, "property": {...}}

# 出租房产
POST /api/properties/rent-out
Request: {"property_id": 1, "rent_price": 200}
Response: {"success": true}

# 升级房产
POST /api/properties/upgrade
Request: {"property_id": 1, "upgrade_type": "storage"}
Response: {"success": true, "new_features": [...]}

# 获取我的房产
GET /api/properties/my-properties
Response: [...]
```

### 4. 经济系统

#### 核心机制
- **供需驱动**：价格由市场决定
- **通货膨胀控制**：AI 监测并调控
- **生产链**：原材料 → 加工 → 成品
- **税收系统**：交易税、房产税

#### 生产链示例

```
木材 (采集) → 木板 (加工) → 家具 (制作) → 出售
矿石 (采集) → 金属锭 (冶炼) → 工具 (锻造) → 出售
```

#### AI 经济调控

```python
class EconomyController:
    """AI 经济调控器"""
    
    def monitor_inflation(self):
        """监测通货膨胀"""
        # 计算物价指数
        # 如果通胀过高，增加 NPC 供给
        # 如果通缩，减少 NPC 供给
        
    def adjust_npc_behavior(self):
        """调整 NPC 行为"""
        # NPC 根据市场价格决定买卖
        # 但不会破坏玩家主导的市场
        
    def generate_economic_events(self):
        """生成经济事件"""
        # 资源短缺、新区域开放、政策变化
```

### 5. 社交系统

#### 核心机制
- **实时聊天**：全局、区域、私聊
- **好友系统**：添加好友、查看在线状态
- **公会/组织**：玩家可以创建组织
- **声誉系统**：基于交易、协作的信用评分

#### WebSocket 实时通信

```python
# WebSocket 事件类型
{
    "player_move": {"player_id": 1, "x": 100, "y": 50},
    "chat_message": {"from": "Alice", "message": "Hello!", "room": "plaza"},
    "trade_notification": {"trade_id": 123, "status": "completed"},
    "job_update": {"job_id": 1, "current_workers": 3},
    "economic_event": {"type": "resource_shortage", "item": "wood"}
}
```

### 6. AI 调控系统

#### AI 的职责

**1. 经济调控**
- 监测物价、供需
- 调整 NPC 行为
- 生成经济事件

**2. 内容生成**
- 生成随机事件
- 生成 NPC 对话
- 生成任务描述

**3. 社交匹配（非强制）**
- 推荐可能合作的玩家
- 推荐适合的工作/任务
- 但玩家可以忽略

**4. 反作弊**
- 检测异常交易
- 检测刷金行为
- 维护公平性

#### Claude API 集成

```python
from anthropic import Anthropic

class AIController:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    async def generate_event(self, city_state: dict) -> dict:
        """根据城市状态生成事件"""
        prompt = f"""
        当前城市状态：
        - 人口：{city_state['population']}
        - 经济指数：{city_state['economy_index']}
        - 安全指数：{city_state['security_level']}
        
        生成一个合理的城市事件（JSON格式）：
        {{
            "title": "事件标题",
            "description": "事件描述",
            "type": "economic/social/security",
            "effects": {{"economy_index": -5}}
        }}
        """
        
        response = self.client.messages.create(
            model="claude-opus-4-7",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return json.loads(response.content[0].text)
```

---

## 🚀 MVP 实现路线图

### Phase 1: 基础设施（Week 1-2）

**Backend**
- [ ] 扩展数据模型（Location, Property, Job, WorkSession, Resource）
- [ ] 实现 WebSocket 服务
- [ ] Redis 集成（缓存、实时状态）
- [ ] 基础 API 实现

**Frontend**
- [ ] React 项目初始化
- [ ] Canvas 渲染引擎搭建
- [ ] WebSocket 客户端
- [ ] 基础 UI 组件

**DevOps**
- [ ] Docker Compose 配置
- [ ] 开发环境搭建

### Phase 2: 地图与探索（Week 3）

**Backend**
- [ ] 地图 API 实现
- [ ] 位置管理服务
- [ ] 资源点系统
- [ ] 玩家移动逻辑

**Frontend**
- [ ] 地图渲染
- [ ] 玩家移动
- [ ] 其他玩家显示
- [ ] 小地图

### Phase 3: 工作与经济（Week 4-5）

**Backend**
- [ ] 工作系统 API
- [ ] 工作会话管理
- [ ] 离线工作机制
- [ ] 生产链逻辑

**Frontend**
- [ ] 工作界面
- [ ] 背包系统
- [ ] 交易市场 UI
- [ ] 经济数据可视化

### Phase 4: 房产系统（Week 6）

**Backend**
- [ ] 房产 API
- [ ] 购买/租赁逻辑
- [ ] 房产估值算法
- [ ] 租金自动结算

**Frontend**
- [ ] 房产列表
- [ ] 房产详情
- [ ] 购买/租赁界面

### Phase 5: AI 集成（Week 7）

**Backend**
- [ ] Claude API 集成
- [ ] 经济调控器
- [ ] 事件生成器
- [ ] NPC 行为 AI

**Frontend**
- [ ] 事件通知
- [ ] AI 推荐界面

### Phase 6: 社交与优化（Week 8）

**Backend**
- [ ] 聊天系统
- [ ] 好友系统
- [ ] 声誉系统
- [ ] 性能优化

**Frontend**
- [ ] 聊天 UI
- [ ] 好友列表
- [ ] 性能优化
- [ ] 移动端适配

---

## 📈 成功指标

### MVP 验证指标

**用户留存**
- 次日留存率 > 40%
- 7 日留存率 > 20%

**经济活跃度**
- 日均交易量 > 100 笔
- 玩家间交易占比 > 60%

**社交互动**
- 日均聊天消息 > 500 条
- 好友添加率 > 30%

**时间投入**
- 日均在线时长 > 30 分钟
- 周活跃用户 > 100 人

---

## 🔒 安全与性能

### 安全考虑
- JWT 认证
- API 限流
- 交易验证（防止刷金）
- WebSocket 认证
- 敏感数据加密

### 性能优化
- Redis 缓存热数据
- 数据库索引优化
- WebSocket 消息批处理
- 前端资源懒加载
- CDN 静态资源

---

## 📝 后续规划

### Phase 2 功能（3-6 个月）
- 3D 渲染（Three.js）
- 移动端 App
- 更复杂的生产链
- 公会系统
- PvP 竞技

### Phase 3 功能（6-12 个月）
- Unity 客户端
- VR 支持
- 用户生成内容（UGC）
- 跨服交易
- 区块链集成（可选）

### 长期愿景（1-3 年）
- 脑机接口适配
- AI Agent 深度集成
- 去中心化治理
- 真实经济价值转换

---

## 🤝 开发协作

### 分工建议
- **Backend**: Python/FastAPI 开发
- **Frontend**: React/Canvas 开发
- **AI**: Claude API 集成与提示工程
- **DevOps**: 部署与监控

### 技术债务管理
- 每周 Code Review
- 单元测试覆盖率 > 60%
- 文档同步更新

---

**文档版本**: v1.0  
**最后更新**: 2026-04-24  
**维护者**: Oasis 开发团队

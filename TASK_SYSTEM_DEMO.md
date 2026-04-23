# 🎮 任务系统演示 (Week 1 Day 4-5)

## ✅ 实现完成

任务系统 (Task System) 已完整实现，实现了Oasis的核心功能：**能力绑定** (Capability Binding)。

### 🏗️ 实现范围

#### 1️⃣ **数据模型** (`backend/models/__init__.py`)
```python
class Task(Base):
    # 任务描述
    title: String
    description: String
    
    # 能力要求
    required_job: String  # warrior/merchant/crafter/scholar
    required_count: Integer  # 需要的人数
    
    # 奖励
    reward_gold: Float
    
    # 多人协作追踪
    accepted_by: Text(JSON)    # 格式: [{"player_id": 1, "accepted_at": "..."}]
    completed_by: Text(JSON)   # 格式: [{"player_id": 1, "completed_at": "..."}]
    
    # 状态管理
    status: String  # pending/in_progress/completed/cancelled
    progress: Float  # 0-1
    deadline: DateTime
```

#### 2️⃣ **Pydantic Schemas** (`backend/schemas.py`)
- `TaskCreate`: 创建任务请求
- `TaskResponse`: 任务响应 (自动将 `reward_gold` → `reward`, `required_count` → `required_players`)
- `TaskProgressResponse`: 任务进度信息
- `TaskUpdate`: 更新任务状态

#### 3️⃣ **业务逻辑服务层** (`backend/services/task_service.py`)

**核心方法 (6个):**

1. **`create_task()`** - 创建新任务
   - 验证创建者存在
   - 初始化空的 `accepted_by` 和 `completed_by` 列表

2. **`accept_task()`** - 玩家接受任务
   - ✅ 验证职业匹配
   - ✅ 防止重复接受
   - ✅ 满员检查
   - ⭐ **自动晋升**: 当接受人数达到 `required_count` 时，状态自动变为 `in_progress`

3. **`complete_task()`** - 玩家完成任务
   - ✅ 验证已接受
   - ✅ 防止重复完成
   - ⭐ **自动完成**: 当所有接受者都完成时，自动标记为 `completed` 并分配奖励
   - ⭐ **平均分配**: `奖励 = task.reward_gold / completed_count`

4. **`get_task_by_id()`** - 获取任务
5. **`get_tasks()`** - 列表查询 (支持按职业/状态筛选)
6. **`get_task_progress()`** - 获取任务进度
7. **`cancel_task()`** - 取消任务 (仅创建者)

#### 4️⃣ **HTTP API 路由** (`backend/api/routes/tasks.py`)

| 端点 | 方法 | 身份 | 功能 |
|------|------|------|------|
| `/tasks/create` | POST | ✅ 需登陆 | 创建任务 |
| `/tasks` | GET | 无需 | 列表查询 (支持filter) |
| `/tasks/{id}/accept` | POST | ✅ 需登陆 | 接受任务 |
| `/tasks/{id}/complete` | POST | ✅ 需登陆 | 完成任务 |
| `/tasks/{id}/progress` | GET | 无需 | 查询进度 |
| `/tasks/{id}/cancel` | DELETE | ✅ 需登陆 | 取消任务 |

---

## 🎯 核心创新：能力绑定 (Capability Binding)

### 问题
传统多人游戏中，任务绑定到特定玩家。当玩家离线时，任务停滞，其他玩家无法进行。

### 方案
**任务绑定到"能力"而非"玩家"**:
- 任务要求职业类型 (`required_job`)，而非特定玩家ID
- 任何该职业的玩家都可以接受和完成
- 当玩家离线时，其他玩家可以继续进行

### 实现细节

```
任务: "击败地下城恶龙"
需要: 2个warrior

时刻1 (t=0):
  ├─ warrior_A 接受任务
  └─ 状态: pending (需要再1人)

时刻2 (t=30min):
  ├─ warrior_A 离线
  ├─ warrior_B 接受任务 ← warrior_A离线不影响
  └─ 状态: in_progress (满员)

时刻3 (t=60min):
  ├─ warrior_A 重新上线，完成任务
  ├─ warrior_B 也完成了任务
  └─ 状态: completed (分配奖励给A和B)
```

---

## 📊 工作流示例

### 场景：两个warrior合作击败恶龙

**Step 1: warrior1 创建任务**
```
POST /tasks/create
{
  "title": "击败地下城恶龙",
  "description": "...",
  "required_job": "warrior",
  "reward": 600.0,
  "required_players": 2
}

Response:
{
  "id": 1,
  "status": "pending",
  "accepted_count": 0,  (未计算此字段，但内部已追踪)
  ...
}
```

**Step 2: warrior1 接受任务**
```
POST /tasks/1/accept
状态变化: pending → pending (需要2人)
```

**Step 3: warrior2 接受任务**
```
POST /tasks/1/accept
状态变化: pending → in_progress (满员！)
```

**Step 4: warrior1 完成任务**
```
POST /tasks/1/complete
completed_count = 1/2
状态保持: in_progress
```

**Step 5: warrior2 完成任务**
```
POST /tasks/1/complete
completed_count = 2/2
状态变化: in_progress → completed ✅

奖励分配:
- warrior1: +300 gold (600/2)
- warrior2: +300 gold (600/2)
```

---

## 🔧 技术实现细节

### 多人协作追踪

**accepted_by 字段 (JSON)**
```json
[
  {"player_id": 1, "accepted_at": "2026-04-23T20:00:00"},
  {"player_id": 2, "accepted_at": "2026-04-23T20:05:00"}
]
```

**completed_by 字段 (JSON)**
```json
[
  {"player_id": 1, "completed_at": "2026-04-23T20:10:00"},
  {"player_id": 2, "completed_at": "2026-04-23T20:15:00"}
]
```

### 防护机制

✅ **防止重复操作**
- 同一玩家无法接受同一任务两次
- 同一玩家无法完成同一任务两次

✅ **职业验证**
- 玩家职业必须与 `required_job` 匹配

✅ **权限控制**
- 只有创建者才能取消任务
- 登陆玩家才能接受/完成任务

✅ **自动状态管理**
- 任务人满 → 自动 `in_progress`
- 全部完成 → 自动 `completed` + 分配奖励

---

## 📈 数据库设计

### players 表更新
- 新增: `gold` 字段存储玩家货币

### tasks 表创建
```sql
CREATE TABLE tasks (
  id INTEGER PRIMARY KEY,
  title VARCHAR(200),
  description TEXT,
  required_job VARCHAR(50),    -- 能力要求
  required_count INTEGER,      -- 需要的人数
  reward_gold FLOAT,
  accepted_by TEXT,            -- JSON array
  completed_by TEXT,           -- JSON array
  status VARCHAR(20),
  progress FLOAT,
  creator_id INTEGER,          -- 创建者
  created_at DATETIME,
  completed_at DATETIME,
  ...
);
```

---

## 🧪 测试场景

### ✅ 通过的场景
1. ✅ 创建任务 (任何职业都能创建)
2. ✅ 职业匹配接受 (warrior接受warrior任务)
3. ✅ 职业不匹配拒绝 (merchant无法接受warrior任务)
4. ✅ 多人协作完成 (需要2人的任务需要2人全部完成)
5. ✅ 奖励平均分配 (3人完成的600金币 = 每人200)
6. ✅ 自动状态晋升 (满员自动in_progress)
7. ✅ 取消权限验证 (仅创建者可取消)

### ⚠️ 已处理的错误情况
- 404: 任务/玩家不存在
- 400: 职业不匹配、已接受、已完成、满员、无权取消
- 401: 无效token
- 403: 缺少认证

---

## 🚀 集成

### 已集成到主应用
- ✅ `main.py` 注册了 `tasks_router`
- ✅ 自动生成 Swagger 文档 (`/docs`)
- ✅ 支持 ReDoc 文档 (`/redoc`)

### 如何使用

```bash
# 启动服务器
cd backend
python -m uvicorn main:app --reload

# 访问API文档
# Swagger: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

---

## 📝 代码质量

- ✅ 清晰的服务层架构 (model → service → route)
- ✅ 完整的错误处理 (GameException 异常体系)
- ✅ 自动状态管理 (防止手动错误)
- ✅ JSON追踪 (accepted_by/completed_by)
- ✅ 单一职责原则 (TaskService独立处理业务逻辑)

---

## 🎯 下一步 (Week 1 Day 6-7)

### 交易系统 (Trade System)
- Trade 模型 (seller, buyer, item, price)
- 自动价格计算算法
- 市场匹配逻辑
- 交易历史追踪

---

## 📚 相关文件

- `backend/models/__init__.py` - Task 数据模型
- `backend/schemas.py` - TaskCreate, TaskResponse 等 schemas
- `backend/services/task_service.py` - 业务逻辑 (240行代码)
- `backend/api/routes/tasks.py` - HTTP 端点 (6个)
- `backend/main.py` - 主应用 (已注册tasks_router)

---

✅ **Week 1 Day 4-5 任务系统实现完成！**

下一步: Week 1 Day 6-7 实现交易系统 (Trade System)

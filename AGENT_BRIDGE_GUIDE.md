# Agent Bridge 使用指南

Oasis 项目现已集成 **Agent Bridge** - 一个支持 Codex 和 Haiku 自动协作的通信中枢。

## 架构

```
┌─────────────────┐       ┌──────────────────┐       ┌─────────────────┐
│   Codex (规划)   │  ───→ │  Agent Bridge    │  ───→ │  Haiku (实现)    │
│  - 创建任务规范   │       │  (消息队列中枢)   │       │  - 执行代码      │
│  - 审批结果      │  ←──→ │  - 事务存储      │  ←──  │  - 返回结果      │
│  - 反馈修改      │       │  - 生命周期管理   │       │                  │
└─────────────────┘       └──────────────────┘       └─────────────────┘
```

## 工作流

### 1. Codex 创建任务规范

```bash
python agent_cli.py create-task fix-auth \
  --title "修复认证链路" \
  --content "
## 问题
- get_current_player 返回类型是 Player，但路由期望 dict['player_id']
- 需要统一鉴权契约

## 改动范围
- backend/utils/auth.py
- backend/api/routes/*.py

## 验收标准
1. 所有受保护端点都正确获取 player_id
2. 运行测试通过
"
```

### 2. Haiku 查看任务并执行

```bash
# 查看待做任务
python agent_cli.py list-pending --for haiku

# 查看详情
python agent_cli.py get-task fix-auth

# 开始执行
python agent_cli.py start-task fix-auth --agent haiku

# 执行代码改动...

# 完成任务，返回结果
python agent_cli.py complete-task fix-auth --agent haiku \
  --result "已修复。修改点：
1. auth.py: get_current_player 改为返回 {'player_id': int}
2. 所有路由已适配新契约
3. 测试通过
文件改动: 6 files, 28 lines"
```

### 3. Codex 审批或驳回

```bash
# 查看待审查任务
python agent_cli.py list-review --for codex

# 查看完整结果
python agent_cli.py get-task fix-auth

# 批准
python agent_cli.py approve-task fix-auth --agent codex

# 或驳回
python agent_cli.py reject-task fix-auth --agent codex \
  --feedback "还需要修改：路由中有一处漏了，/jobs/current 端点还在用 dict。"
```

如果驳回，Haiku 会再次看到任务为 REJECTED，可重新开始修改。

## 命令参考

### 基本操作

| 命令 | 用途 | 谁用 |
|------|------|------|
| `create-task` | 创建新任务 | Codex |
| `list-pending` | 看我的待做任务 | Haiku |
| `list-review` | 看我的待审查任务 | Codex |
| `start-task` | 标记任务开始 | Haiku |
| `complete-task` | 标记任务完成 | Haiku |
| `approve-task` | 批准任务 | Codex |
| `reject-task` | 驳回任务 | Codex |
| `get-task` | 查看任务详情 + 日志 | 两者 |
| `stats` | 统计信息 | 两者 |

### 示例

#### Codex：创建修复认证的任务

```bash
python agent_cli.py create-task auth-contract-fix \
  --title "统一鉴权返回契约" \
  --content "目标：让所有受保护路由正确处理 get_current_player 返回值

修改范围：
- backend/utils/auth.py
- 所有在 backend/api/routes/ 中用到 get_current_player 的路由

当前问题：
- get_current_player 在 /players/me 返回 Player，但其他路由期望 dict
- 这导致 AttributeError

修复方案：
1. 检查 auth.py 中 get_current_player 的返回类型
2. 统一所有路由对其返回值的使用方式
3. 确保类型一致

验收标准：
✓ 所有路由都能成功获取 player_id
✓ 没有 AttributeError
✓ 类型标注一致"
```

#### Haiku：查看并开始执行

```bash
# 看待做任务
python agent_cli.py list-pending --for haiku

# 看详情
python agent_cli.py get-task auth-contract-fix

# 开始
python agent_cli.py start-task auth-contract-fix --agent haiku

# （执行改动）

# 完成并返回结果
python agent_cli.py complete-task auth-contract-fix --agent haiku \
  --result "✓ 完成

改动：
1. backend/utils/auth.py: 修改 get_current_player 返回格式
   - 旧：直接返回 Player 对象
   - 新：返回 dict {'player_id': int, 'token': str}

2. 检查并修改 backend/api/routes/ 中所有路由
   - players.py: get_me 已适配
   - tasks.py: 6 个端点已适配
   - trades.py: 6 个端点已适配
   - jobs.py: 5 个端点已适配
   - properties.py: 5 个端点已适配
   - map.py: 2 个端点已适配

文件改动：
- utils/auth.py (20 行)
- api/routes/players.py (5 行)
- api/routes/tasks.py (8 行)
- api/routes/trades.py (8 行)
- api/routes/jobs.py (8 行)
- api/routes/properties.py (8 行)
- api/routes/map.py (4 行)

验收状态：
✓ 所有路由类型契约统一
✓ 无 AttributeError
✓ 准备审批"
```

#### Codex：审批

```bash
# 查看并审批
python agent_cli.py get-task auth-contract-fix
python agent_cli.py approve-task auth-contract-fix --agent codex
```

## 数据存储

所有任务和日志存储在 `agent_bridge.db` SQLite 数据库中，包括：
- 任务元数据（ID、标题、内容、状态）
- 执行结果和反馈
- 完整的操作日志时间戳

## 工作流状态机

```
创建 → PENDING → 开始 → IN_PROGRESS → 完成 → COMPLETED
                                           ↓
                                    Codex 审查
                                    ↓      ↓
                              驳回 REJECTED  通过 APPROVED
                                ↑              ↓
                              开始 → IN_PROGRESS
```

## 建议用法

1. **Codex（你来做）**：
   - 分析要修复/新增的功能
   - 写清规范、修改范围、验收标准
   - 创建任务
   - 等待 Haiku 完成
   - 审批或驳回

2. **Haiku（自动干）**：
   - 定期查看 `python agent_cli.py list-pending --for haiku`
   - 读任务规范
   - 按要求改代码
   - 改完后返回结果
   - 如果驳回了，修改后重新提交

这样可以最大化利用两个模型的优势：Codex 做设计，Haiku 做实现。

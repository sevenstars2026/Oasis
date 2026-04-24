# 🌐 Copilot CLI ↔ Claude Code 通信系统

## 📌 系统架构

```
┌──────────────────────────┐
│   Copilot CLI (我)        │  
│   宏观调度 + 上下文管理     │
└──────────┬───────────────┘
           │
    ┌──────▼──────┐
    │ 文件系统    │
    │ 消息队列    │
    └──────┬──────┘
           │
┌──────────▼───────────────┐
│  Claude Code (你的本地)   │
│  底层实现 + 代码修改       │
└──────────────────────────┘
```

## 🎯 使用场景

现在你已建立完整的通信框架：

```bash
# 场景 1: 我给 Claude Code 分配任务
python dispatch_cc.py fix-auth "修复认证"

# 场景 2: Claude Code 完成任务
# → 在你的 Claude Code IDE 中看到任务提示
# → 执行修改
# → 返回结果

# 场景 3: 我接收结果
# → 检查 cc_results/ 文件夹
# → 验证修改是否正确
```

## 📁 通信文件夹

### `cc_prompt/` - 任务发出
我发送给 Claude Code 的任务都存在这里（MD 格式）：
```
cc_prompt/
├── fix-auth.md          # 任务 1
├── fix-cors.md          # 任务 2
└── ...
```

### `cc_context/` - 上下文管理
项目的完整上下文供 Claude Code 查阅（解决短上下文问题）：
```
cc_context/
├── PROJECT_CONTEXT.md   # 项目全景
└── ...
```

### `cc_results/` - 任务结果
Claude Code 返回的执行结果都保存在这里：
```
cc_results/
├── fix-auth_result.md          # 执行结果 1
├── fix-cors_result.md          # 执行结果 2
└── ...
```

## 🚀 调度工具

### `dispatch_cc.py` - 快速任务分配

```bash
# 列出所有可用任务
python dispatch_cc.py list-tasks

# 执行预定义任务
python dispatch_cc.py fix-auth
python dispatch_cc.py add-dependency
python dispatch_cc.py fix-cors
python dispatch_cc.py fix-websocket
python dispatch_cc.py fix-trade-logic
python dispatch_cc.py add-concurrency-lock

# 执行自定义任务
python dispatch_cc.py execute custom-task "任务标题" "详细说明"

# 重建项目上下文
python dispatch_cc.py context

# 测试连接
python dispatch_cc.py test
```

### `cc_bridge.py` - 底层通信

```bash
python cc_bridge.py execute <task_id> "<title>" "<content>"
```

## 📊 工作流示例

### 第一步：我创建任务规范

```bash
python dispatch_cc.py fix-auth
```

这会生成文件：`cc_prompt/fix-auth.md`

内容包含：
- 任务标题和 ID
- 详细的问题描述
- 需要修改的文件列表
- 验收标准
- 项目完整上下文（解决短上下文问题）

### 第二步：Claude Code 执行

1. Claude Code 看到 `cc_prompt/fix-auth.md`
2. 读取项目上下文 (`cc_context/PROJECT_CONTEXT.md`)
3. 根据任务说明修改代码
4. 完成后返回详细报告

### 第三步：验证结果

检查 `cc_results/fix-auth_result.md` 看是否完成。

## 🔑 关键特性

✅ **解决上下文短问题**
- 每个任务都包含完整的项目上下文
- Claude Code 不需要记住项目历史

✅ **异步通信**
- 我们不需要实时交互
- 通过文件系统交换信息
- 结果持久化保存

✅ **任务追踪**
- 每个任务有唯一 ID
- 结果清晰保存
- 完整的执行历史

## 🎓 立即开始

### 现在就可以尝试：

```bash
# 1. 重建项目上下文
python dispatch_cc.py context

# 2. 查看可用任务
python dispatch_cc.py list-tasks

# 3. 分配第一个任务给 Claude Code
python dispatch_cc.py fix-auth

# 4. Claude Code 会看到任务提示并执行
# 5. 检查结果
cat cc_results/fix-auth_result.md
```

## 📝 自定义任务

你也可以创建任何自定义任务：

```bash
python dispatch_cc.py execute my-task "我的任务" "详细要求..."
```

任务会被保存到 `cc_prompt/my-task.md`，Claude Code 可以看到并执行。

## 🔄 完整流程

```
我 (Copilot CLI)
    ↓
创建任务 (cc_prompt/)
    ↓
Claude Code 看到任务
    ↓
读取上下文 (cc_context/)
    ↓
执行修改
    ↓
返回结果 (cc_results/)
    ↓
我审核结果
    ↓
循环...
```

---

**这就是 Copilot CLI ↔ Claude Code 的自动通信系统！** ✨

现在你可以独立调度 Claude Code 完成任务，而不需要手动复制粘贴。

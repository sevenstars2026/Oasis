# 🚀 快速开始 - 3 分钟上手

## 第一步：生成项目上下文（解决 CC 短上下文问题）

```bash
cd /home/sevenstars/CLionProjects/Oasis
python dispatch_cc.py context
```

✅ 生成完成：`cc_context/PROJECT_CONTEXT.md`

## 第二步：发送第一个任务

```bash
python dispatch_cc.py fix-auth
```

✅ 任务已生成：`cc_prompt/fix-auth.md`

现在 Claude Code 可以在你的 IDE 中看到这个任务提示。

## 第三步：Claude Code 执行任务

在你的 Claude Code IDE 中：
1. 打开文件 `cc_prompt/fix-auth.md`
2. 按照任务说明修改代码
3. 完成后保存结果到 `cc_results/fix-auth_result.md`

## 第四步：我审核结果

```bash
cat cc_results/fix-auth_result.md
```

查看 Claude Code 是否完成了任务。

---

## 🎯 可用命令

```bash
# 列出所有可用任务
python dispatch_cc.py list-tasks

# 执行某个任务
python dispatch_cc.py <task_id>
  # 示例: python dispatch_cc.py fix-auth
  #       python dispatch_cc.py add-dependency
  #       python dispatch_cc.py fix-cors

# 自定义任务
python dispatch_cc.py execute <id> "<title>" "<content>"
  # 示例: python dispatch_cc.py execute my-task "我的任务" "详细说明..."

# 重建上下文
python dispatch_cc.py context
```

## 📚 完整任务列表

### 高优先级（P0）
- `fix-auth` - 修复认证契约不一致
- `add-dependency` - 添加缺失的 python-jose

### 中优先级（P1）
- `fix-cors` - 修复 CORS 不安全配置
- `fix-websocket` - 修复 WebSocket 字段错误
- `fix-trade-logic` - 完善交易经济逻辑
- `add-concurrency-lock` - 添加交易并发锁

---

## 💡 工作流总结

```
┌─────────────────┐
│ Copilot CLI     │
│ 生成任务 MD     │
└────────┬────────┘
         ↓
┌─────────────────┐
│  cc_prompt/     │ ← Claude Code 看到任务
│  task_id.md     │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Claude Code IDE │
│ 执行修改        │
└────────┬────────┘
         ↓
┌─────────────────┐
│  cc_results/    │ ← 我审核结果
│  task_id_result │
└─────────────────┘
```

---

**准备好了？开始吧！** 🎉

```bash
python dispatch_cc.py context
python dispatch_cc.py fix-auth
```


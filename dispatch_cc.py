#!/usr/bin/env python3
"""
Copilot CLI 任务调度工具 - 控制 Claude Code

使用方法:
  python dispatch_cc.py fix-auth           # 修复认证
  python dispatch_cc.py list-tasks         # 列出所有任务
  python dispatch_cc.py context            # 重建项目上下文
"""

import sys
from pathlib import Path

TASKS = {
    "fix-auth": {
        "title": "修复认证契约不一致问题",
        "content": """
## 问题
`get_current_player` 返回 `Player` 对象，但所有受保护路由期望 `dict["player_id"]`，导致 AttributeError。

## 需要修改
- `backend/utils/auth.py` - 统一返回类型
- `backend/api/routes/*.py` - 所有路由的参数解析

## 验收标准
✓ 认证返回类型一致
✓ 所有受保护路由都能正确获取 player_id
✓ 没有 AttributeError
"""
    },
    
    "add-dependency": {
        "title": "添加缺失的 python-jose 依赖",
        "content": """
## 问题
代码使用 `python-jose` 但 requirements.txt 中没有。

## 需要修改
- `backend/requirements.txt` - 添加 `python-jose[cryptography]`

## 验收标准
✓ requirements.txt 已更新
✓ 依赖能成功安装
"""
    },
    
    "fix-cors": {
        "title": "修复 CORS 不安全配置",
        "content": """
## 问题
CORS 配置用 `allow_origins=["*"]` 配合 `allow_credentials=True`，这是不安全的。

## 修改
- `backend/main.py` 中的 CORS middleware
- 将 `allow_origins=["*"]` 改为 `allow_origins=["http://localhost:3000", "http://localhost:8000"]`

## 验收标准
✓ CORS 配置已修改为安全模式
✓ 本地开发能正常运行
"""
    },
}

def show_usage():
    print("""
📊 Copilot CLI 任务调度工具

用法:
  python dispatch_cc.py <command> [args]

可用命令:
  list-tasks              列出所有预定义任务
  context                 重建项目上下文
  <task_id>              执行指定任务
  execute <id> <title> <content>  执行自定义任务

任务列表:
""")
    for task_id in TASKS.keys():
        title = TASKS[task_id]["title"]
        print(f"  • {task_id:20} - {title}")
    
    print("""
示例:
  python dispatch_cc.py list-tasks
  python dispatch_cc.py fix-auth
  python dispatch_cc.py context
""")

def dispatch_task(task_id, title, content):
    """生成任务文件"""
    root = Path("/home/sevenstars/CLionProjects/Oasis")
    prompt_dir = root / "cc_prompt"
    prompt_dir.mkdir(exist_ok=True)
    
    prompt_file = prompt_dir / f"{task_id}.md"
    
    full_prompt = f"""# 🎯 任务: {title}

**任务ID**: {task_id}

---

## 📋 任务详情

{content}

---

## 🔍 项目上下文

项目路径: `/home/sevenstars/CLionProjects/Oasis`

已实现功能:
- 身份验证系统
- 任务系统（Capability Binding）
- 交易系统
- WebSocket 实时通信
- 地图、工作、属性系统

已知问题:
- P0: 认证契约不一致
- P0: 缺少 python-jose 依赖
- P1: CORS 不安全
- P1: WebSocket 字段错误
- P1: 交易逻辑不完整
- P1: 并发竞争风险

---

## ✅ 完成后

请提交详细的执行报告，包括:
1. 修改的文件列表
2. 每个文件的具体改动
3. 验收标准检查
4. 任何注意事项

---

**请开始执行任务！** 任务文件已保存在 `cc_prompt/{task_id}.md`
"""
    
    prompt_file.write_text(full_prompt, encoding='utf-8')
    print(f"\n✅ 任务已生成: {prompt_file}\n")
    print(f"📌 任务标题: {title}")
    print(f"📌 任务 ID: {task_id}\n")
    print("内容预览:")
    print("="*60)
    print(full_prompt)
    print("="*60)
    print(f"\n📝 Claude Code 可以在 {prompt_file} 中看到这个任务\n")

def build_context():
    """构建项目上下文"""
    root = Path("/home/sevenstars/CLionProjects/Oasis")
    context_dir = root / "cc_context"
    context_dir.mkdir(exist_ok=True)
    
    context_file = context_dir / "PROJECT_CONTEXT.md"
    
    context = """# 🌍 Oasis 项目完整上下文

## 📁 项目结构

```
Oasis/
├── backend/
│   ├── api/routes/       # API 路由
│   ├── utils/auth.py     # 认证工具
│   ├── main.py           # 应用入口
│   └── requirements.txt   # 依赖
├── frontend/             # React 前端
└── cc_*/                 # 通信文件夹
```

## 🎯 已实现功能

✅ 身份验证 (JWT)
✅ 任务系统 (Capability Binding)
✅ 交易系统
✅ WebSocket 实时通信
✅ 地图/工作/属性系统

## ⚠️ 已知问题

| 优先级 | 问题 | 位置 |
|--------|------|------|
| P0 | 认证契约不一致 | backend/utils/auth.py |
| P0 | 缺少 python-jose | backend/requirements.txt |
| P1 | CORS 不安全 | backend/main.py |
| P1 | WebSocket 字段错误 | WebSocket 代码 |
| P1 | 交易逻辑不完整 | trades.py |
| P1 | 并发竞争风险 | trades.py |

---

项目路径: `/home/sevenstars/CLionProjects/Oasis`
"""
    
    context_file.write_text(context, encoding='utf-8')
    print(f"✅ 项目上下文已生成: {context_file}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_usage()
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "list-tasks":
        print("📋 可用的预定义任务:\n")
        for task_id in TASKS.keys():
            title = TASKS[task_id]["title"]
            print(f"  • {task_id}")
            print(f"    {title}\n")
    
    elif cmd == "context":
        print("🔄 重建项目上下文...")
        build_context()
    
    elif cmd in TASKS:
        task = TASKS[cmd]
        dispatch_task(cmd, task["title"], task["content"])
    
    elif cmd == "execute":
        if len(sys.argv) < 5:
            print("用法: python dispatch_cc.py execute <task_id> <title> <content>")
            sys.exit(1)
        task_id = sys.argv[2]
        title = sys.argv[3]
        content = sys.argv[4]
        dispatch_task(task_id, title, content)
    
    else:
        print(f"❌ 未知命令: {cmd}\n")
        show_usage()
        sys.exit(1)

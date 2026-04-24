#!/usr/bin/env python3
"""
Agent CLI - 为 Codex 和 Haiku 提供的命令行接口

用法示例:
  # Codex: 创建任务规范
  python agent_cli.py create-task fix-auth --from codex --to haiku --title "修复认证链路" --content "..."
  
  # Haiku: 查询待做任务
  python agent_cli.py list-pending --for haiku
  
  # Haiku: 标记任务完成
  python agent_cli.py complete-task fix-auth --result "已修复..."
  
  # Codex: 查询待审查任务
  python agent_cli.py list-review --for codex
  
  # Codex: 审批通过
  python agent_cli.py approve-task fix-auth
  
  # Codex: 驳回任务
  python agent_cli.py reject-task fix-auth --feedback "还需要改..."
"""

import sys
import json
import argparse
from agent_bridge import bridge, AgentRole, TaskStatus


def cmd_create_task(args):
    """创建任务"""
    task = bridge.create_task(
        task_id=args.task_id,
        from_agent=AgentRole(args.from_agent),
        to_agent=AgentRole(args.to_agent),
        title=args.title,
        content=args.content,
    )
    print(json.dumps(task.to_dict(), indent=2, ensure_ascii=False))


def cmd_list_pending(args):
    """列出待做任务"""
    tasks = bridge.get_pending_tasks(AgentRole(args.for_agent))
    print(f"共 {len(tasks)} 个待做任务:\n")
    for task in tasks:
        print(f"  [{task.id}] {task.title}")
        print(f"    来自: {task.agent_from.value} | 状态: {task.status.value}")
        print(f"    内容预览: {task.content[:100]}...")
        print()


def cmd_list_review(args):
    """列出待审查任务"""
    tasks = bridge.get_review_tasks(AgentRole(args.for_agent))
    print(f"共 {len(tasks)} 个待审查任务:\n")
    for task in tasks:
        print(f"  [{task.id}] {task.title}")
        print(f"    执行者: {task.agent_to.value} | 状态: {task.status.value}")
        print(f"    结果预览: {(task.result or '')[:100]}...")
        print()


def cmd_start_task(args):
    """标记任务开始执行"""
    task = bridge.start_task(args.task_id, AgentRole(args.agent))
    print(f"✓ 任务 [{task.id}] 已标记为执行中")


def cmd_complete_task(args):
    """完成任务"""
    task = bridge.complete_task(
        args.task_id,
        AgentRole(args.agent),
        args.result,
    )
    print(f"✓ 任务 [{task.id}] 已完成")
    print(f"结果长度: {len(task.result)} 字符")


def cmd_get_task(args):
    """查看任务详情"""
    task = bridge.get_task(args.task_id)
    if not task:
        print(f"✗ 任务 [{args.task_id}] 不存在")
        sys.exit(1)
    
    print(json.dumps(task.to_dict(), indent=2, ensure_ascii=False))
    print("\n日志:")
    logs = bridge.get_logs(args.task_id)
    for log in logs:
        print(f"  [{log['timestamp']}] {log['agent']}: {log['action']} - {log['message']}")


def cmd_approve_task(args):
    """审批通过"""
    task = bridge.approve_task(args.task_id, AgentRole(args.agent))
    print(f"✓ 任务 [{task.id}] 已批准通过")


def cmd_reject_task(args):
    """驳回任务"""
    task = bridge.reject_task(
        args.task_id,
        AgentRole(args.agent),
        args.feedback,
    )
    print(f"✓ 任务 [{task.id}] 已驳回")
    print(f"反馈: {task.feedback}")


def cmd_stats(args):
    """显示统计信息"""
    stats = bridge.stats()
    print("任务统计:\n")
    for status, count in stats.items():
        print(f"  {status}: {count}")


def main():
    parser = argparse.ArgumentParser(
        description="Agent Bridge CLI - Codex 与 Haiku 通信工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # create-task
    p = subparsers.add_parser("create-task", help="创建新任务")
    p.add_argument("task_id", help="任务 ID")
    p.add_argument("--from", dest="from_agent", choices=["codex", "haiku"], default="codex", help="来自哪个 Agent")
    p.add_argument("--to", dest="to_agent", choices=["codex", "haiku"], default="haiku", help="发送给哪个 Agent")
    p.add_argument("--title", required=True, help="任务标题")
    p.add_argument("--content", required=True, help="任务内容")
    p.set_defaults(func=cmd_create_task)

    # list-pending
    p = subparsers.add_parser("list-pending", help="列出待做任务")
    p.add_argument("--for", dest="for_agent", choices=["codex", "haiku"], required=True, help="为哪个 Agent")
    p.set_defaults(func=cmd_list_pending)

    # list-review
    p = subparsers.add_parser("list-review", help="列出待审查任务")
    p.add_argument("--for", dest="for_agent", choices=["codex", "haiku"], required=True, help="为哪个 Agent")
    p.set_defaults(func=cmd_list_review)

    # start-task
    p = subparsers.add_parser("start-task", help="标记任务开始执行")
    p.add_argument("task_id", help="任务 ID")
    p.add_argument("--agent", choices=["codex", "haiku"], default="haiku", help="执行 Agent")
    p.set_defaults(func=cmd_start_task)

    # complete-task
    p = subparsers.add_parser("complete-task", help="完成任务")
    p.add_argument("task_id", help="任务 ID")
    p.add_argument("--agent", choices=["codex", "haiku"], default="haiku", help="执行 Agent")
    p.add_argument("--result", required=True, help="任务结果")
    p.set_defaults(func=cmd_complete_task)

    # get-task
    p = subparsers.add_parser("get-task", help="查看任务详情")
    p.add_argument("task_id", help="任务 ID")
    p.set_defaults(func=cmd_get_task)

    # approve-task
    p = subparsers.add_parser("approve-task", help="批准任务")
    p.add_argument("task_id", help="任务 ID")
    p.add_argument("--agent", choices=["codex", "haiku"], default="codex", help="审批 Agent")
    p.set_defaults(func=cmd_approve_task)

    # reject-task
    p = subparsers.add_parser("reject-task", help="驳回任务")
    p.add_argument("task_id", help="任务 ID")
    p.add_argument("--agent", choices=["codex", "haiku"], default="codex", help="审批 Agent")
    p.add_argument("--feedback", required=True, help="驳回反馈")
    p.set_defaults(func=cmd_reject_task)

    # stats
    p = subparsers.add_parser("stats", help="显示统计信息")
    p.set_defaults(func=cmd_stats)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()

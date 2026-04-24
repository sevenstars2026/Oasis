"""
Agent Bridge - Codex 与 Haiku 通信中枢

实现多 Agent 任务协作的消息队列和生命周期管理。
任务流向: Codex (规划) → Haiku (实现) → Codex (审查) → 反馈

使用 SQLite 作为事务型消息存储，避免文件竞争。
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, List, Any
from enum import Enum
from dataclasses import dataclass, asdict
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "agent_bridge.db")


class TaskStatus(Enum):
    PENDING = "pending"  # Codex 已创建，等待 Haiku
    IN_PROGRESS = "in_progress"  # Haiku 正在执行
    COMPLETED = "completed"  # Haiku 完成，等待 Codex 审查
    REVIEW = "review"  # Codex 审查中
    APPROVED = "approved"  # 通过
    REJECTED = "rejected"  # 需修改


class AgentRole(Enum):
    CODEX = "codex"
    HAIKU = "haiku"


@dataclass
class AgentTask:
    id: str
    agent_from: AgentRole
    agent_to: AgentRole
    title: str
    content: str
    status: TaskStatus
    created_at: str
    updated_at: str
    result: Optional[str] = None
    feedback: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d['agent_from'] = d['agent_from'].value
        d['agent_to'] = d['agent_to'].value
        d['status'] = d['status'].value
        return d


class AgentBridge:
    """Agent 通信中枢"""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """初始化数据库架构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_tasks (
            id TEXT PRIMARY KEY,
            agent_from TEXT NOT NULL,
            agent_to TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            status TEXT NOT NULL,
            result TEXT,
            feedback TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL,
            agent TEXT NOT NULL,
            action TEXT NOT NULL,
            message TEXT,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (task_id) REFERENCES agent_tasks(id)
        )
        """)

        conn.commit()
        conn.close()

    def create_task(
        self,
        task_id: str,
        from_agent: AgentRole,
        to_agent: AgentRole,
        title: str,
        content: str,
    ) -> AgentTask:
        """创建任务（Codex 创建规范 → Haiku 执行）"""
        now = datetime.now().isoformat()
        task = AgentTask(
            id=task_id,
            agent_from=from_agent,
            agent_to=to_agent,
            title=title,
            content=content,
            status=TaskStatus.PENDING,
            created_at=now,
            updated_at=now,
        )

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO agent_tasks 
        (id, agent_from, agent_to, title, content, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task.id, task.agent_from.value, task.agent_to.value,
            task.title, task.content, task.status.value, task.created_at, task.updated_at
        ))

        self._log(cursor, task_id, from_agent.value, "CREATE", f"任务已创建: {title}")
        conn.commit()
        conn.close()

        return task

    def get_task(self, task_id: str) -> Optional[AgentTask]:
        """获取任务"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM agent_tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return self._row_to_task(row)

    def get_pending_tasks(self, for_agent: AgentRole) -> List[AgentTask]:
        """获取等待中的任务（Haiku 查询自己的任务）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM agent_tasks 
        WHERE agent_to = ? AND status = ? 
        ORDER BY created_at ASC
        """, (for_agent.value, TaskStatus.PENDING.value))

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_task(row) for row in rows]

    def get_review_tasks(self, for_agent: AgentRole) -> List[AgentTask]:
        """获取待审查的任务（Codex 查询 Haiku 完成的任务）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM agent_tasks 
        WHERE agent_from = ? AND status = ? 
        ORDER BY updated_at DESC
        """, (for_agent.value, TaskStatus.COMPLETED.value))

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_task(row) for row in rows]

    def start_task(self, task_id: str, agent: AgentRole) -> AgentTask:
        """标记任务为执行中（Haiku 开始干活）"""
        now = datetime.now().isoformat()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE agent_tasks 
        SET status = ?, updated_at = ? 
        WHERE id = ?
        """, (TaskStatus.IN_PROGRESS.value, now, task_id))

        self._log(cursor, task_id, agent.value, "START", "开始执行任务")
        conn.commit()
        conn.close()

        return self.get_task(task_id)

    def complete_task(self, task_id: str, agent: AgentRole, result: str) -> AgentTask:
        """完成任务（Haiku 返回结果）"""
        now = datetime.now().isoformat()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE agent_tasks 
        SET status = ?, result = ?, updated_at = ? 
        WHERE id = ?
        """, (TaskStatus.COMPLETED.value, result, now, task_id))

        self._log(cursor, task_id, agent.value, "COMPLETE", "任务已完成")
        conn.commit()
        conn.close()

        return self.get_task(task_id)

    def approve_task(self, task_id: str, agent: AgentRole) -> AgentTask:
        """审批通过（Codex 同意）"""
        now = datetime.now().isoformat()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE agent_tasks 
        SET status = ?, updated_at = ? 
        WHERE id = ?
        """, (TaskStatus.APPROVED.value, now, task_id))

        self._log(cursor, task_id, agent.value, "APPROVE", "任务已通过审批")
        conn.commit()
        conn.close()

        return self.get_task(task_id)

    def reject_task(self, task_id: str, agent: AgentRole, feedback: str) -> AgentTask:
        """驳回（Codex 需要修改）"""
        now = datetime.now().isoformat()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE agent_tasks 
        SET status = ?, feedback = ?, updated_at = ? 
        WHERE id = ?
        """, (TaskStatus.REJECTED.value, feedback, now, task_id))

        self._log(cursor, task_id, agent.value, "REJECT", f"驳回: {feedback}")
        conn.commit()
        conn.close()

        return self.get_task(task_id)

    def get_logs(self, task_id: str) -> List[Dict[str, str]]:
        """获取任务日志"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT agent, action, message, timestamp FROM agent_logs 
        WHERE task_id = ? 
        ORDER BY timestamp ASC
        """, (task_id,))

        logs = [{"agent": row[0], "action": row[1], "message": row[2], "timestamp": row[3]} 
                for row in cursor.fetchall()]
        conn.close()

        return logs

    def _log(self, cursor: sqlite3.Cursor, task_id: str, agent: str, action: str, message: str):
        """记录日志"""
        cursor.execute("""
        INSERT INTO agent_logs (task_id, agent, action, message, timestamp)
        VALUES (?, ?, ?, ?, ?)
        """, (task_id, agent, action, message, datetime.now().isoformat()))

    def _row_to_task(self, row: tuple) -> AgentTask:
        """数据库行转换为 Task 对象"""
        return AgentTask(
            id=row[0],
            agent_from=AgentRole(row[1]),
            agent_to=AgentRole(row[2]),
            title=row[3],
            content=row[4],
            status=TaskStatus(row[5]),
            result=row[6],
            feedback=row[7],
            created_at=row[8],
            updated_at=row[9],
        )

    def stats(self) -> Dict[str, int]:
        """统计任务状态"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stats = {}
        for status in TaskStatus:
            cursor.execute("SELECT COUNT(*) FROM agent_tasks WHERE status = ?", (status.value,))
            count = cursor.fetchone()[0]
            stats[status.value] = count

        conn.close()
        return stats


# 全局单例
bridge = AgentBridge()

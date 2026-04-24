"""任务系统服务层 - 处理所有任务相关的业务逻辑"""

import json
from datetime import datetime
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_

from models import Task, Player
from schemas import TaskCreate, TaskResponse, TaskProgressResponse
from utils.exceptions import GameException


class TaskService:
    """任务管理服务"""
    
    @staticmethod
    def create_task(db: Session, creator_id: int, task_data: TaskCreate) -> Task:
        """
        创建新任务
        
        规则:
        - 创建者必须存在
        - 任务不能被同一玩家立刻接受
        """
        # 验证创建者存在
        creator = db.query(Player).filter(Player.id == creator_id).first()
        if not creator:
            raise GameException(code=404, message="玩家不存在")
        
        # 创建任务
        task = Task(
            title=task_data.title,
            description=task_data.description,
            required_job=task_data.required_job,
            reward_gold=task_data.reward,
            required_count=task_data.required_players,
            status="pending",
            creator_id=creator_id,
            accepted_by=json.dumps([]),
            completed_by=json.dumps([])
        )
        
        db.add(task)
        db.commit()
        db.refresh(task)
        return task
    
    @staticmethod
    def accept_task(db: Session, task_id: int, player_id: int) -> Task:
        """
        接受任务

        规则:
        - 玩家必须存在且职业与任务匹配（citizen可以接任何任务）
        - 不能重复接受同一任务（已接受者无法再次接受）
        - 不能接受已完成的任务
        """
        # 查询任务
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise GameException(code=404, message="任务不存在")

        # 查询玩家
        player = db.query(Player).filter(Player.id == player_id).first()
        if not player:
            raise GameException(code=404, message="玩家不存在")

        # 验证玩家职业（citizen可以接任何任务）
        if task.required_job and player.job != 'citizen':
            if player.job != task.required_job:
                raise GameException(
                    code=400,
                    message=f"职业不匹配。任务需要{task.required_job}，你是{player.job}"
                )
        
        # 验证任务状态
        if task.status == "completed":
            raise GameException(code=400, message="任务已完成，无法接受")
        
        if task.status == "cancelled":
            raise GameException(code=400, message="任务已取消，无法接受")
        
        # 检查玩家是否已接受
        accepted_list = json.loads(task.accepted_by or "[]")
        accepted_player_ids = [item["player_id"] for item in accepted_list]
        
        if player_id in accepted_player_ids:
            raise GameException(code=400, message="你已经接受过此任务")
        
        # 检查是否已达到所需人数
        if len(accepted_player_ids) >= task.required_count:
            raise GameException(
                code=400,
                message=f"任务已满员（需要{task.required_count}人）"
            )
        
        # 添加玩家到接受列表
        accepted_list.append({
            "player_id": player_id,
            "accepted_at": datetime.now().isoformat()
        })
        
        task.accepted_by = json.dumps(accepted_list)
        
        # 如果达到所需人数，状态变为in_progress
        if len(accepted_list) >= task.required_count:
            task.status = "in_progress"
        
        db.commit()
        db.refresh(task)
        return task
    
    @staticmethod
    def complete_task(db: Session, task_id: int, player_id: int) -> Task:
        """
        完成任务
        
        规则:
        - 玩家必须已接受此任务
        - 所有接受任务的玩家必须全部完成才能标记为已完成
        - 完成时分配奖励
        """
        # 查询任务
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise GameException(code=404, message="任务不存在")
        
        # 查询玩家
        player = db.query(Player).filter(Player.id == player_id).first()
        if not player:
            raise GameException(code=404, message="玩家不存在")
        
        # 检查玩家是否已接受
        accepted_list = json.loads(task.accepted_by or "[]")
        accepted_player_ids = [item["player_id"] for item in accepted_list]
        
        if player_id not in accepted_player_ids:
            raise GameException(code=400, message="你未接受此任务，无法完成")
        
        # 检查玩家是否已完成
        completed_list = json.loads(task.completed_by or "[]")
        completed_player_ids = [item["player_id"] for item in completed_list]
        
        if player_id in completed_player_ids:
            raise GameException(code=400, message="你已完成过此任务")
        
        # 添加玩家到完成列表
        completed_list.append({
            "player_id": player_id,
            "completed_at": datetime.now().isoformat()
        })
        
        task.completed_by = json.dumps(completed_list)
        
        # 如果所有接受者都完成了，标记任务为已完成
        if len(completed_list) >= len(accepted_player_ids):
            task.status = "completed"
            task.completed_at = datetime.now()
            
            # 分配奖励给所有完成者
            reward_per_player = task.reward_gold / len(completed_list)
            for item in completed_list:
                p = db.query(Player).filter(Player.id == item["player_id"]).first()
                if p:
                    p.gold += reward_per_player
        
        db.commit()
        db.refresh(task)
        return task
    
    @staticmethod
    def get_task_by_id(db: Session, task_id: int) -> Task:
        """根据ID获取任务"""
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise GameException(code=404, message="任务不存在")
        return task
    
    @staticmethod
    def get_tasks(
        db: Session,
        status: Optional[str] = None,
        job_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Task]:
        """
        获取任务列表
        
        可按状态、职业类型筛选
        """
        query = db.query(Task)
        
        if status:
            query = query.filter(Task.status == status)
        
        if job_type:
            query = query.filter(Task.required_job == job_type)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_task_progress(db: Session, task_id: int) -> Dict:
        """获取任务进度信息"""
        task = TaskService.get_task_by_id(db, task_id)
        
        accepted_list = json.loads(task.accepted_by or "[]")
        completed_list = json.loads(task.completed_by or "[]")
        
        accepted_count = len(accepted_list)
        completed_count = len(completed_list)
        required_count = task.required_count
        
        progress_percent = (completed_count / required_count * 100) if required_count > 0 else 0
        reward_per_player = task.reward_gold / required_count if required_count > 0 else 0
        
        return {
            "task_id": task.id,
            "title": task.title,
            "status": task.status,
            "accepted_count": accepted_count,
            "completed_count": completed_count,
            "required_count": required_count,
            "progress_percent": min(progress_percent, 100),
            "reward_per_player": reward_per_player
        }
    
    @staticmethod
    def cancel_task(db: Session, task_id: int, player_id: int) -> Task:
        """
        取消任务
        
        规则:
        - 只有创建者才能取消
        - 无法取消已完成的任务
        """
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise GameException(code=404, message="任务不存在")
        
        if task.creator_id != player_id:
            raise GameException(code=403, message="只有创建者才能取消任务")
        
        if task.status == "completed":
            raise GameException(code=400, message="已完成的任务无法取消")
        
        task.status = "cancelled"
        db.commit()
        db.refresh(task)
        return task

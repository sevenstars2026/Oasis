"""任务系统API路由 - 处理HTTP请求"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from utils.database import get_db
from schemas import TaskCreate, TaskResponse, TaskProgressResponse
from services.task_service import TaskService
from utils.auth import get_current_player
from utils.exceptions import GameException


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/create", response_model=TaskResponse)
def create_task(
    task_data: TaskCreate,
    current_player: dict = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    创建新任务
    
    - 需要登陆
    - 职业无限制（任务创建者不需要匹配required_job）
    """
    try:
        task = TaskService.create_task(db, current_player["player_id"], task_data)
        return task
    except GameException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.get("", response_model=list[TaskResponse])
def get_tasks(
    status: str = Query(None, description="任务状态: pending/in_progress/completed/cancelled"),
    job_type: str = Query(None, description="职业类型: warrior/merchant/crafter/scholar"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    获取任务列表
    
    - 无需登陆
    - 支持按状态和职业筛选
    """
    tasks = TaskService.get_tasks(db, status=status, job_type=job_type, skip=skip, limit=limit)
    return tasks


@router.post("/{task_id}/accept", response_model=TaskResponse)
def accept_task(
    task_id: int,
    current_player: dict = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    接受任务
    
    - 需要登陆
    - 职业必须匹配
    - 无法重复接受同一任务
    """
    try:
        task = TaskService.accept_task(db, task_id, current_player["player_id"])
        return task
    except GameException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.post("/{task_id}/complete", response_model=TaskResponse)
def complete_task(
    task_id: int,
    current_player: dict = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    完成任务
    
    - 需要登陆
    - 必须已接受此任务
    - 所有接受者都完成后，任务标记为已完成并分配奖励
    """
    try:
        task = TaskService.complete_task(db, task_id, current_player["player_id"])
        return task
    except GameException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.get("/{task_id}/progress", response_model=TaskProgressResponse)
def get_task_progress(
    task_id: int,
    db: Session = Depends(get_db)
):
    """
    获取任务进度
    
    - 无需登陆
    - 返回接受人数、完成人数、进度百分比等信息
    """
    try:
        progress = TaskService.get_task_progress(db, task_id)
        return progress
    except GameException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.delete("/{task_id}/cancel", response_model=TaskResponse)
def cancel_task(
    task_id: int,
    current_player: dict = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """
    取消任务
    
    - 需要登陆
    - 只有创建者才能取消
    - 已完成的任务无法取消
    """
    try:
        task = TaskService.cancel_task(db, task_id, current_player["player_id"])
        return task
    except GameException as e:
        raise HTTPException(status_code=e.code, detail=e.message)

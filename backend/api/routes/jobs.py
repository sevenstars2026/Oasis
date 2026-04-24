"""工作系统API路由"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from utils.database import get_db
from utils.auth import get_current_player
from utils.exceptions import GameException
from services.job_service import JobService
from pydantic import BaseModel
from models import Player


router = APIRouter(prefix="/jobs", tags=["jobs"])


# ============ Schemas ============

class JobResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    job_type: str
    required_job_class: str
    required_level: int
    location_id: Optional[int]
    base_pay: float
    is_available: bool
    max_workers: int
    current_workers: int
    employer_type: str

    class Config:
        from_attributes = True


class WorkSessionResponse(BaseModel):
    id: int
    player_id: int
    job_id: int
    start_time: datetime
    end_time: Optional[datetime]
    duration_minutes: int
    earnings: float
    status: str

    class Config:
        from_attributes = True


class StartWorkRequest(BaseModel):
    job_id: int


class EndWorkRequest(BaseModel):
    work_session_id: int


# ============ Routes ============

@router.get("/available", response_model=List[JobResponse])
def get_available_jobs(
    location_id: Optional[int] = Query(None, description="位置ID筛选"),
    job_class: Optional[str] = Query(None, description="职业筛选"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取可用工作列表"""
    jobs = JobService.get_available_jobs(db, location_id, job_class, skip, limit)
    return jobs


@router.get("/current")
def get_current_work(
    current_player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """获取当前工作会话"""
    work_session = JobService.get_active_work_session(db, current_player.id)

    if not work_session:
        return {"active": False, "work_session": None}

    # 计算已工作时长
    duration = (datetime.now() - work_session.start_time).total_seconds() / 60

    return {
        "active": True,
        "work_session": work_session,
        "duration_minutes": int(duration)
    }


@router.get("/history", response_model=List[WorkSessionResponse])
def get_work_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """获取工作历史"""
    history = JobService.get_work_history(db, current_player.id, skip, limit)
    return history


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    """获取工作详情"""
    job = JobService.get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="工作不存在")
    return job


@router.post("/start")
def start_work(
    request: StartWorkRequest,
    current_player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """开始工作"""
    try:
        work_session = JobService.start_work(db, current_player.id, request.job_id)
        return {
            "success": True,
            "work_session_id": work_session.id,
            "job_id": work_session.job_id,
            "started_at": work_session.start_time
        }
    except GameException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.post("/end")
def end_work(
    request: EndWorkRequest,
    current_player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """结束工作并结算"""
    try:
        result = JobService.end_work(db, current_player.id, request.work_session_id)
        return result
    except GameException as e:
        raise HTTPException(status_code=e.code, detail=e.message)

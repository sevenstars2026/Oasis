"""地图系统API路由"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from utils.database import get_db
from utils.auth import get_current_player
from utils.exceptions import GameException
from services.map_service import MapService
from pydantic import BaseModel


router = APIRouter(prefix="/map", tags=["map"])


# ============ Schemas ============

class LocationResponse(BaseModel):
    id: int
    name: str
    display_name: Optional[str]
    x: float
    y: float
    zone_type: str
    description: Optional[str]
    capacity: int
    current_players: int
    is_unlocked: bool

    class Config:
        from_attributes = True


class MoveRequest(BaseModel):
    location_id: int
    x: Optional[float] = None
    y: Optional[float] = None


class HarvestRequest(BaseModel):
    resource_id: int
    duration_minutes: int = 10


# ============ Routes ============

@router.get("/locations", response_model=List[LocationResponse])
def get_locations(
    zone_type: Optional[str] = Query(None, description="区域类型筛选"),
    include_locked: bool = Query(False, description="是否包含未解锁区域"),
    db: Session = Depends(get_db)
):
    """获取所有地图位置"""
    if zone_type:
        locations = MapService.get_locations_by_zone(db, zone_type)
    else:
        locations = MapService.get_all_locations(db, include_locked)

    return locations


@router.get("/locations/{location_id}")
def get_location_details(
    location_id: int,
    db: Session = Depends(get_db)
):
    """获取位置详细信息（包括玩家、资源等）"""
    try:
        details = MapService.get_location_details(db, location_id)
        return details
    except GameException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.post("/move")
def move_player(
    move_data: MoveRequest,
    current_player: dict = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """移动玩家到新位置"""
    try:
        result = MapService.move_player(
            db,
            current_player["player_id"],
            move_data.location_id,
            move_data.x,
            move_data.y
        )
        return result
    except GameException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.get("/locations/{location_id}/players")
def get_players_at_location(
    location_id: int,
    db: Session = Depends(get_db)
):
    """获取某位置的所有在线玩家"""
    players = MapService.get_players_at_location(db, location_id)
    return {"location_id": location_id, "players": players, "count": len(players)}


@router.post("/harvest")
def harvest_resource(
    harvest_data: HarvestRequest,
    current_player: dict = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """采集资源"""
    try:
        result = MapService.harvest_resource(
            db,
            current_player["player_id"],
            harvest_data.resource_id,
            harvest_data.duration_minutes
        )
        return result
    except GameException as e:
        raise HTTPException(status_code=e.code, detail=e.message)

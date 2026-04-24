"""房产系统API路由"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from utils.database import get_db
from utils.auth import get_current_player
from utils.exceptions import GameException
from services.property_service import PropertyService
from pydantic import BaseModel
from models import Player


router = APIRouter(prefix="/properties", tags=["properties"])


# ============ Schemas ============

class PropertyResponse(BaseModel):
    id: int
    location_id: int
    property_type: str
    size: int
    owner_id: Optional[int]
    current_value: float
    is_rented: bool
    tenant_id: Optional[int]
    rent_price: float
    condition: float
    upgrade_level: int

    class Config:
        from_attributes = True


class BuyPropertyRequest(BaseModel):
    property_id: int


class RentOutRequest(BaseModel):
    property_id: int
    rent_price: float


class RentPropertyRequest(BaseModel):
    property_id: int


class UpgradeRequest(BaseModel):
    property_id: int
    upgrade_type: str


# ============ Routes ============

@router.get("/for-sale", response_model=List[PropertyResponse])
def get_properties_for_sale(
    location_id: Optional[int] = Query(None, description="位置ID筛选"),
    property_type: Optional[str] = Query(None, description="房产类型筛选"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取可售房产列表"""
    properties = PropertyService.get_properties_for_sale(db, location_id, property_type, skip, limit)
    return properties


@router.get("/my-properties", response_model=List[PropertyResponse])
def get_my_properties(
    current_player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """获取我的房产"""
    properties = PropertyService.get_player_properties(db, current_player.id)
    return properties


@router.get("/{property_id}", response_model=PropertyResponse)
def get_property(
    property_id: int,
    db: Session = Depends(get_db)
):
    """获取房产详情"""
    property = PropertyService.get_property_by_id(db, property_id)
    if not property:
        raise HTTPException(status_code=404, detail="房产不存在")
    return property


@router.post("/buy")
def buy_property(
    request: BuyPropertyRequest,
    current_player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """购买房产"""
    try:
        result = PropertyService.buy_property(db, current_player.id, request.property_id)
        return result
    except GameException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.post("/rent-out")
def rent_out_property(
    request: RentOutRequest,
    current_player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """出租房产"""
    try:
        result = PropertyService.rent_out_property(
            db,
            current_player.id,
            request.property_id,
            request.rent_price
        )
        return result
    except GameException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.post("/rent")
def rent_property(
    request: RentPropertyRequest,
    current_player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """租赁房产"""
    try:
        result = PropertyService.rent_property(db, current_player.id, request.property_id)
        return result
    except GameException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.post("/upgrade")
def upgrade_property(
    request: UpgradeRequest,
    current_player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """升级房产"""
    try:
        result = PropertyService.upgrade_property(
            db,
            current_player.id,
            request.property_id,
            request.upgrade_type
        )
        return result
    except GameException as e:
        raise HTTPException(status_code=e.code, detail=e.message)

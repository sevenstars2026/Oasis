"""交易系统API路由"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from utils.database import get_db
from schemas import TradeCreate, TradeResponse, MarketStatsResponse
from services.trade_service import TradeService
from utils.auth import get_current_player
from utils.exceptions import GameException
from models import Player

router = APIRouter(prefix="/trades", tags=["trades"])


@router.post("/create", response_model=TradeResponse)
def create_trade(
    trade_data: TradeCreate,
    current_player: Player = Depends(get_current_player),
    db: Session = Depends(get_db),
):
    """创建交易挂单；若可匹配则自动撮合并返回已接受交易"""
    try:
        trade = TradeService.create_trade(db, current_player.id, trade_data)
        return TradeResponse.model_validate(trade)
    except GameException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.get("/market", response_model=list[TradeResponse])
def get_market(
    status: str = Query("pending", description="交易状态: pending/accepted/completed/cancelled"),
    item_name: str = Query(None, description="物品名"),
    trade_type: str = Query(None, description="交易类型: sell/buy"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """获取市场交易列表"""
    trades = TradeService.get_market_trades(
        db,
        status=status,
        item_name=item_name,
        trade_type=trade_type,
        skip=skip,
        limit=limit,
    )
    return [TradeResponse.model_validate(t) for t in trades]


@router.get("/stats", response_model=MarketStatsResponse)
def get_market_stats(db: Session = Depends(get_db)):
    """获取市场统计"""
    return TradeService.get_market_stats(db)


@router.post("/{trade_id}/accept", response_model=TradeResponse)
def accept_trade(
    trade_id: int,
    current_player: Player = Depends(get_current_player),
    db: Session = Depends(get_db),
):
    """接受挂单"""
    try:
        trade = TradeService.accept_trade(db, trade_id, current_player.id)
        return TradeResponse.model_validate(trade)
    except GameException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.post("/{trade_id}/complete", response_model=TradeResponse)
def complete_trade(
    trade_id: int,
    current_player: Player = Depends(get_current_player),
    db: Session = Depends(get_db),
):
    """确认完成交易（双确认后结算）"""
    try:
        trade = TradeService.complete_trade(db, trade_id, current_player.id)
        return TradeResponse.model_validate(trade)
    except GameException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.delete("/{trade_id}/cancel", response_model=TradeResponse)
def cancel_trade(
    trade_id: int,
    current_player: Player = Depends(get_current_player),
    db: Session = Depends(get_db),
):
    """取消交易挂单"""
    try:
        trade = TradeService.cancel_trade(db, trade_id, current_player.id)
        return TradeResponse.model_validate(trade)
    except GameException as e:
        raise HTTPException(status_code=e.code, detail=e.message)

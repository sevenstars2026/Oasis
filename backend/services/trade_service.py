"""交易系统服务层 - 处理挂单、撮合、结算等业务逻辑"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func

from models import Trade, Player
from schemas import TradeCreate
from utils.exceptions import GameException


class TradeService:
    """交易管理服务"""

    @staticmethod
    def create_trade(db: Session, creator_id: int, trade_data: TradeCreate) -> Trade:
        """
        创建交易挂单。
        若存在可匹配挂单，则直接自动接受对方挂单（不再创建新挂单）。
        """
        creator = db.query(Player).filter(Player.id == creator_id).first()
        if not creator:
            raise GameException(code=404, message="玩家不存在")

        match = TradeService._find_match_candidate(db, creator_id, trade_data)
        if match:
            return TradeService.accept_trade(db, match.id, creator_id)

        trade = Trade(
            seller_id=creator_id,
            buyer_id=creator_id,  # pending阶段占位，避免破坏旧表的非空约束
            item_name=trade_data.item_name,
            quantity=trade_data.quantity,
            price=trade_data.price,
            trade_type=trade_data.trade_type,
            status="pending",
            seller_confirmed=False,
            buyer_confirmed=False,
            timestamp=datetime.now(),
            created_at=datetime.now(),
        )
        db.add(trade)
        db.commit()
        db.refresh(trade)
        return trade

    @staticmethod
    def accept_trade(db: Session, trade_id: int, player_id: int) -> Trade:
        """接受挂单"""
        trade = db.query(Trade).filter(Trade.id == trade_id).first()
        if not trade:
            raise GameException(code=404, message="交易不存在")

        if trade.status != "pending":
            raise GameException(code=400, message="该交易不在可接受状态")

        if trade.seller_id == player_id:
            raise GameException(code=400, message="不能接受自己创建的挂单")

        player = db.query(Player).filter(Player.id == player_id).first()
        if not player:
            raise GameException(code=404, message="玩家不存在")

        trade.buyer_id = player_id
        trade.status = "accepted"
        trade.accepted_at = datetime.now()
        trade.buyer_confirmed = False
        trade.seller_confirmed = False

        db.commit()
        db.refresh(trade)
        return trade

    @staticmethod
    def complete_trade(db: Session, trade_id: int, player_id: int) -> Trade:
        """
        完成交易（双确认）。
        参与双方都调用一次完成后，执行金币结算并标记completed。
        """
        trade = db.query(Trade).filter(Trade.id == trade_id).first()
        if not trade:
            raise GameException(code=404, message="交易不存在")

        if trade.status != "accepted":
            raise GameException(code=400, message="仅accepted状态交易可完成")

        if player_id not in (trade.seller_id, trade.buyer_id):
            raise GameException(code=403, message="你不是该交易参与者")

        if player_id == trade.seller_id:
            trade.seller_confirmed = True
        if player_id == trade.buyer_id:
            trade.buyer_confirmed = True

        if trade.seller_confirmed and trade.buyer_confirmed:
            settlement = TradeService._resolve_settlement_roles(trade)
            seller = db.query(Player).filter(Player.id == settlement["seller_id"]).first()
            buyer = db.query(Player).filter(Player.id == settlement["buyer_id"]).first()

            if not seller or not buyer:
                raise GameException(code=404, message="交易参与者不存在")

            total_price = trade.price * trade.quantity
            if buyer.gold < total_price:
                raise GameException(code=400, message="买方金币不足，无法完成交易")

            buyer.gold -= total_price
            seller.gold += total_price

            trade.status = "completed"
            trade.completed_at = datetime.now()

        db.commit()
        db.refresh(trade)
        return trade

    @staticmethod
    def cancel_trade(db: Session, trade_id: int, player_id: int) -> Trade:
        """取消交易挂单（仅创建者，且仅pending）"""
        trade = db.query(Trade).filter(Trade.id == trade_id).first()
        if not trade:
            raise GameException(code=404, message="交易不存在")

        if trade.seller_id != player_id:
            raise GameException(code=403, message="只有创建者可以取消交易")

        if trade.status != "pending":
            raise GameException(code=400, message="仅pending状态交易可取消")

        trade.status = "cancelled"
        db.commit()
        db.refresh(trade)
        return trade

    @staticmethod
    def get_market_trades(
        db: Session,
        status: Optional[str] = "pending",
        item_name: Optional[str] = None,
        trade_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Trade]:
        """获取市场挂单列表"""
        query = db.query(Trade)
        if status:
            query = query.filter(Trade.status == status)
        if item_name:
            query = query.filter(Trade.item_name == item_name)
        if trade_type:
            query = query.filter(Trade.trade_type == trade_type)

        return query.order_by(Trade.created_at.desc(), Trade.id.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_market_stats(db: Session) -> Dict:
        """获取市场统计信息"""
        since_24h = datetime.now() - timedelta(hours=24)

        pending_orders = db.query(func.count(Trade.id)).filter(Trade.status == "pending").scalar() or 0
        accepted_orders = db.query(func.count(Trade.id)).filter(Trade.status == "accepted").scalar() or 0
        completed_orders_24h = db.query(func.count(Trade.id)).filter(
            Trade.status == "completed",
            Trade.completed_at >= since_24h
        ).scalar() or 0

        total_volume_24h = db.query(func.sum(Trade.price * Trade.quantity)).filter(
            Trade.status == "completed",
            Trade.completed_at >= since_24h
        ).scalar() or 0.0

        avg_rows = db.query(
            Trade.item_name,
            func.avg(Trade.price).label("avg_price")
        ).filter(
            Trade.status == "completed"
        ).group_by(Trade.item_name).all()

        average_price_by_item = {item_name: float(avg_price) for item_name, avg_price in avg_rows}

        return {
            "pending_orders": pending_orders,
            "accepted_orders": accepted_orders,
            "completed_orders_24h": completed_orders_24h,
            "total_volume_24h": float(total_volume_24h),
            "average_price_by_item": average_price_by_item,
        }

    @staticmethod
    def _find_match_candidate(db: Session, creator_id: int, trade_data: TradeCreate) -> Optional[Trade]:
        """基于价格和品类寻找可自动撮合的对手挂单"""
        opposite_type = "buy" if trade_data.trade_type == "sell" else "sell"
        query = db.query(Trade).filter(
            Trade.status == "pending",
            Trade.trade_type == opposite_type,
            Trade.item_name == trade_data.item_name,
            Trade.quantity == trade_data.quantity,
            Trade.seller_id != creator_id,
        )

        if trade_data.trade_type == "sell":
            query = query.filter(Trade.price >= trade_data.price).order_by(Trade.price.desc(), Trade.created_at.asc())
        else:
            query = query.filter(Trade.price <= trade_data.price).order_by(Trade.price.asc(), Trade.created_at.asc())

        return query.first()

    @staticmethod
    def _resolve_settlement_roles(trade: Trade) -> Dict[str, int]:
        """
        根据trade_type解析结算双方：
        - sell单：创建者卖，接受者买
        - buy单：创建者买，接受者卖
        """
        if trade.trade_type == "sell":
            return {"seller_id": trade.seller_id, "buyer_id": trade.buyer_id}
        return {"seller_id": trade.buyer_id, "buyer_id": trade.seller_id}

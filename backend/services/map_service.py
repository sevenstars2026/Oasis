"""地图与位置服务层"""

from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from models import Location, Resource, PlayerState, Player
from utils.exceptions import GameException


class MapService:
    """地图管理服务"""

    @staticmethod
    def get_all_locations(db: Session, include_locked: bool = False) -> List[Location]:
        """获取所有地图位置"""
        query = db.query(Location)
        if not include_locked:
            query = query.filter(Location.is_unlocked == True)
        return query.order_by(Location.id).all()

    @staticmethod
    def get_location_by_id(db: Session, location_id: int) -> Optional[Location]:
        """根据ID获取位置"""
        return db.query(Location).filter(Location.id == location_id).first()

    @staticmethod
    def get_location_by_name(db: Session, name: str) -> Optional[Location]:
        """根据名称获取位置"""
        return db.query(Location).filter(Location.name == name).first()

    @staticmethod
    def get_locations_by_zone(db: Session, zone_type: str) -> List[Location]:
        """根据区域类型获取位置"""
        return db.query(Location).filter(
            Location.zone_type == zone_type,
            Location.is_unlocked == True
        ).all()

    @staticmethod
    def move_player(db: Session, player_id: int, location_id: int, x: float = None, y: float = None) -> Dict:
        """移动玩家到新位置"""
        # 验证位置存在
        location = db.query(Location).filter(Location.id == location_id).first()
        if not location:
            raise GameException(code=404, message="位置不存在")

        if not location.is_unlocked:
            raise GameException(code=403, message="该区域尚未解锁")

        # 检查容量
        if location.current_players >= location.capacity:
            raise GameException(code=400, message="该区域已满员")

        # 获取或创建玩家状态
        player_state = db.query(PlayerState).filter(PlayerState.player_id == player_id).first()

        if player_state:
            # 更新旧位置的玩家数
            if player_state.location_id:
                old_location = db.query(Location).filter(Location.id == player_state.location_id).first()
                if old_location and old_location.current_players > 0:
                    old_location.current_players -= 1

            # 更新玩家状态
            player_state.location_id = location_id
            player_state.x = x if x is not None else location.x
            player_state.y = y if y is not None else location.y
            player_state.last_active = datetime.now()
            player_state.updated_at = datetime.now()
        else:
            # 创建新的玩家状态
            player_state = PlayerState(
                player_id=player_id,
                location_id=location_id,
                x=x if x is not None else location.x,
                y=y if y is not None else location.y,
                is_online=True,
                current_activity="idle"
            )
            db.add(player_state)

        # 更新新位置的玩家数
        location.current_players += 1

        # 更新玩家表中的位置
        player = db.query(Player).filter(Player.id == player_id).first()
        if player:
            player.location = location.name

        db.commit()
        db.refresh(player_state)
        db.refresh(location)

        return {
            "success": True,
            "location": location,
            "player_state": player_state
        }

    @staticmethod
    def get_players_at_location(db: Session, location_id: int) -> List[Dict]:
        """获取某位置的所有玩家"""
        player_states = db.query(PlayerState, Player).join(
            Player, PlayerState.player_id == Player.id
        ).filter(
            PlayerState.location_id == location_id,
            PlayerState.is_online == True
        ).all()

        return [
            {
                "player_id": state.player_id,
                "name": player.name,
                "job": player.job,
                "x": state.x,
                "y": state.y,
                "activity": state.current_activity
            }
            for state, player in player_states
        ]

    @staticmethod
    def get_location_details(db: Session, location_id: int) -> Dict:
        """获取位置详细信息（包括玩家、资源等）"""
        location = db.query(Location).filter(Location.id == location_id).first()
        if not location:
            raise GameException(code=404, message="位置不存在")

        # 获取该位置的玩家
        players = MapService.get_players_at_location(db, location_id)

        # 获取该位置的资源
        resources = db.query(Resource).filter(
            Resource.location_id == location_id,
            Resource.is_depleted == False
        ).all()

        return {
            "location": location,
            "players": players,
            "resources": resources,
            "player_count": len(players)
        }

    @staticmethod
    def harvest_resource(db: Session, player_id: int, resource_id: int, duration_minutes: int = 10) -> Dict:
        """采集资源"""
        resource = db.query(Resource).filter(Resource.id == resource_id).first()
        if not resource:
            raise GameException(code=404, message="资源点不存在")

        if resource.is_depleted:
            raise GameException(code=400, message="资源已枯竭")

        # 验证玩家在该位置
        player_state = db.query(PlayerState).filter(PlayerState.player_id == player_id).first()
        if not player_state or player_state.location_id != resource.location_id:
            raise GameException(code=400, message="你不在该资源点所在位置")

        # 计算采集量（基于时间和难度）
        base_amount = duration_minutes * 5  # 每分钟基础采集5单位
        actual_amount = min(base_amount / resource.difficulty, resource.amount)

        # 更新资源
        resource.amount -= actual_amount
        resource.last_harvested = datetime.now()

        if resource.amount <= 0:
            resource.is_depleted = True
            resource.amount = 0

        # 更新玩家活动状态
        player_state.current_activity = "harvesting"
        player_state.last_active = datetime.now()

        db.commit()
        db.refresh(resource)

        return {
            "success": True,
            "resource_type": resource.resource_type,
            "amount_harvested": actual_amount,
            "resource_remaining": resource.amount,
            "is_depleted": resource.is_depleted
        }

    @staticmethod
    def regenerate_resources(db: Session):
        """资源再生（定时任务调用）"""
        resources = db.query(Resource).filter(Resource.is_depleted == False).all()

        for resource in resources:
            if resource.amount < resource.max_amount:
                # 计算自上次采集以来的时间
                if resource.last_harvested:
                    hours_passed = (datetime.now() - resource.last_harvested).total_seconds() / 3600
                else:
                    hours_passed = 1

                # 恢复资源
                regenerated = resource.regeneration_rate * hours_passed
                resource.amount = min(resource.amount + regenerated, resource.max_amount)
                resource.updated_at = datetime.now()

        # 恢复已枯竭的资源
        depleted_resources = db.query(Resource).filter(Resource.is_depleted == True).all()
        for resource in depleted_resources:
            if resource.last_harvested:
                hours_since_depleted = (datetime.now() - resource.last_harvested).total_seconds() / 3600
                if hours_since_depleted >= 24:  # 24小时后恢复
                    resource.is_depleted = False
                    resource.amount = resource.max_amount * 0.5  # 恢复到50%
                    resource.updated_at = datetime.now()

        db.commit()
        return {"regenerated_count": len(resources), "restored_count": len(depleted_resources)}

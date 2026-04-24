"""房产系统服务层"""

from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json

from models import Property, Location, Player
from utils.exceptions import GameException


class PropertyService:
    """房产管理服务"""

    @staticmethod
    def get_properties_for_sale(
        db: Session,
        location_id: Optional[int] = None,
        property_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Property]:
        """获取可售房产列表"""
        query = db.query(Property).filter(Property.owner_id == None)

        if location_id:
            query = query.filter(Property.location_id == location_id)

        if property_type:
            query = query.filter(Property.property_type == property_type)

        return query.order_by(Property.current_value).offset(skip).limit(limit).all()

    @staticmethod
    def get_property_by_id(db: Session, property_id: int) -> Optional[Property]:
        """根据ID获取房产"""
        return db.query(Property).filter(Property.id == property_id).first()

    @staticmethod
    def get_player_properties(db: Session, player_id: int) -> List[Property]:
        """获取玩家拥有的房产"""
        return db.query(Property).filter(Property.owner_id == player_id).all()

    @staticmethod
    def buy_property(db: Session, player_id: int, property_id: int) -> Dict:
        """购买房产"""
        # 验证房产存在
        property = db.query(Property).filter(Property.id == property_id).first()
        if not property:
            raise GameException(code=404, message="房产不存在")

        if property.owner_id is not None:
            raise GameException(code=400, message="该房产已被购买")

        # 验证玩家
        player = db.query(Player).filter(Player.id == player_id).first()
        if not player:
            raise GameException(code=404, message="玩家不存在")

        # 验证金币
        if player.gold < property.current_value:
            raise GameException(code=400, message=f"金币不足，需要 {property.current_value}，当前 {player.gold}")

        # 扣除金币
        player.gold -= property.current_value

        # 转移所有权
        property.owner_id = player_id
        property.purchase_price = property.current_value
        property.updated_at = datetime.now()

        db.commit()
        db.refresh(property)
        db.refresh(player)

        return {
            "success": True,
            "property": property,
            "remaining_gold": player.gold
        }

    @staticmethod
    def rent_out_property(db: Session, player_id: int, property_id: int, rent_price: float) -> Dict:
        """出租房产"""
        property = db.query(Property).filter(
            Property.id == property_id,
            Property.owner_id == player_id
        ).first()

        if not property:
            raise GameException(code=404, message="房产不存在或你不是房主")

        if property.is_rented:
            raise GameException(code=400, message="该房产已出租")

        if rent_price <= 0:
            raise GameException(code=400, message="租金必须大于0")

        property.rent_price = rent_price
        property.is_rented = True
        property.updated_at = datetime.now()

        db.commit()
        db.refresh(property)

        return {
            "success": True,
            "property": property,
            "message": "房产已挂牌出租"
        }

    @staticmethod
    def rent_property(db: Session, player_id: int, property_id: int) -> Dict:
        """租赁房产"""
        property = db.query(Property).filter(Property.id == property_id).first()
        if not property:
            raise GameException(code=404, message="房产不存在")

        if not property.is_rented:
            raise GameException(code=400, message="该房产未挂牌出租")

        if property.tenant_id is not None:
            raise GameException(code=400, message="该房产已被租赁")

        if property.owner_id == player_id:
            raise GameException(code=400, message="不能租赁自己的房产")

        # 验证玩家
        player = db.query(Player).filter(Player.id == player_id).first()
        if not player:
            raise GameException(code=404, message="玩家不存在")

        # 验证金币（首月租金）
        if player.gold < property.rent_price:
            raise GameException(code=400, message=f"金币不足，需要 {property.rent_price}，当前 {player.gold}")

        # 扣除租金
        player.gold -= property.rent_price

        # 支付给房主
        owner = db.query(Player).filter(Player.id == property.owner_id).first()
        if owner:
            owner.gold += property.rent_price

        # 设置租户
        property.tenant_id = player_id
        property.rent_due_date = datetime.now() + timedelta(days=30)
        property.updated_at = datetime.now()

        db.commit()
        db.refresh(property)
        db.refresh(player)

        return {
            "success": True,
            "property": property,
            "rent_due_date": property.rent_due_date,
            "remaining_gold": player.gold
        }

    @staticmethod
    def upgrade_property(db: Session, player_id: int, property_id: int, upgrade_type: str) -> Dict:
        """升级房产"""
        property = db.query(Property).filter(
            Property.id == property_id,
            Property.owner_id == player_id
        ).first()

        if not property:
            raise GameException(code=404, message="房产不存在或你不是房主")

        # 升级配置
        upgrade_costs = {
            "storage": {"cost": 1000, "feature": "storage_+50"},
            "crafting_bench": {"cost": 2000, "feature": "crafting_bench"},
            "shop_license": {"cost": 5000, "feature": "shop_license"},
            "security": {"cost": 3000, "feature": "security_system"}
        }

        if upgrade_type not in upgrade_costs:
            raise GameException(code=400, message="无效的升级类型")

        upgrade_config = upgrade_costs[upgrade_type]

        # 验证玩家金币
        player = db.query(Player).filter(Player.id == player_id).first()
        if not player:
            raise GameException(code=404, message="玩家不存在")

        if player.gold < upgrade_config["cost"]:
            raise GameException(code=400, message=f"金币不足，需要 {upgrade_config['cost']}，当前 {player.gold}")

        # 检查是否已有该升级
        try:
            features = json.loads(property.features) if property.features else []
        except:
            features = []

        if upgrade_config["feature"] in features:
            raise GameException(code=400, message="该升级已存在")

        # 扣除金币
        player.gold -= upgrade_config["cost"]

        # 添加升级
        features.append(upgrade_config["feature"])
        property.features = json.dumps(features)
        property.upgrade_level += 1
        property.current_value += upgrade_config["cost"] * 0.8  # 升级增加房产价值
        property.updated_at = datetime.now()

        db.commit()
        db.refresh(property)
        db.refresh(player)

        return {
            "success": True,
            "property": property,
            "new_features": features,
            "remaining_gold": player.gold
        }

    @staticmethod
    def collect_rent(db: Session):
        """收取租金（定时任务调用）"""
        # 查找租金到期的房产
        now = datetime.now()
        due_properties = db.query(Property).filter(
            Property.is_rented == True,
            Property.tenant_id != None,
            Property.rent_due_date <= now
        ).all()

        collected_count = 0
        evicted_count = 0

        for property in due_properties:
            tenant = db.query(Player).filter(Player.id == property.tenant_id).first()
            owner = db.query(Player).filter(Player.id == property.owner_id).first()

            if not tenant or not owner:
                continue

            # 如果租户有足够金币，自动扣除
            if tenant.gold >= property.rent_price:
                tenant.gold -= property.rent_price
                owner.gold += property.rent_price
                property.rent_due_date = now + timedelta(days=30)
                collected_count += 1
            else:
                # 金币不足，驱逐租户
                property.tenant_id = None
                property.rent_due_date = None
                evicted_count += 1

        db.commit()
        return {
            "collected_count": collected_count,
            "evicted_count": evicted_count
        }

    @staticmethod
    def update_property_values(db: Session):
        """更新房产估值（定时任务调用，基于市场供需）"""
        locations = db.query(Location).all()

        for location in locations:
            # 获取该位置的所有房产
            properties = db.query(Property).filter(Property.location_id == location.id).all()

            if not properties:
                continue

            # 基于位置热度调整房价
            popularity_factor = min(location.current_players / location.capacity, 1.0) if location.capacity > 0 else 0.5

            for property in properties:
                # 基础增值率
                base_appreciation = 0.01  # 1%

                # 根据位置热度调整
                appreciation_rate = base_appreciation * (1 + popularity_factor)

                # 根据房产状态调整
                condition_factor = property.condition / 100.0

                # 计算新价值
                new_value = property.current_value * (1 + appreciation_rate * condition_factor)
                property.current_value = new_value

                # 房产状态自然衰减
                if property.condition > 0:
                    property.condition = max(0, property.condition - 0.1)

                property.updated_at = datetime.now()

        db.commit()
        return {"updated_count": len(properties)}

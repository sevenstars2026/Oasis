"""
Oasis - 数据模型层
定义所有核心的数据结构
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Player(Base):
    """玩家模型"""
    __tablename__ = "players"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # 身份与属性
    job = Column(String(20), default="merchant")  # merchant, warrior, crafter, scholar
    location = Column(String(50), default="plaza")
    gold = Column(Float, default=1000.0)
    
    # 关系
    reputation = Column(Text, default="{}")  # JSON: {"merchant": 50, "security": 30}
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<Player {self.name} - {self.job}>"


class Task(Base):
    """任务模型"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    
    # 任务类型：personal, cooperative, public
    task_type = Column(String(20), default="personal")
    
    # 需求
    required_job = Column(String(50))  # 可以是多个，用逗号分隔
    required_count = Column(Integer, default=1)
    
    # 奖励
    reward_gold = Column(Float, default=0)
    reward_item = Column(String(100))  # 物品奖励
    
    # 状态
    status = Column(String(20), default="available")  # available, in_progress, completed, expired
    progress = Column(Float, default=0.0)  # 0-1
    deadline = Column(DateTime)
    
    # 参与者
    creator_id = Column(Integer, ForeignKey("players.id"))
    player_id = Column(Integer, ForeignKey("players.id"), nullable=True)
    
    # 多人协作追踪（JSON格式存储ID列表）
    # 格式: [{"player_id": 1, "accepted_at": "2026-04-23T20:00:00"}, ...]
    accepted_by = Column(Text, nullable=True)  # JSON array of acceptances
    completed_by = Column(Text, nullable=True)  # JSON array of completions
    
    created_at = Column(DateTime, default=datetime.now)
    completed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Task {self.title} - {self.status}>"


class Trade(Base):
    """交易记录模型"""
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True)
    
    # 交易双方
    seller_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    # 为兼容旧表结构，挂单阶段用seller_id作为buyer_id占位，状态为pending
    buyer_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    
    # 交易内容
    item_name = Column(String(100), nullable=False)
    quantity = Column(Integer, default=1)
    price = Column(Float, nullable=False)  # 单价
    trade_type = Column(String(20), default="sell")  # sell, buy
    status = Column(String(20), default="pending")  # pending, accepted, completed, cancelled
    seller_confirmed = Column(Boolean, default=False)
    buyer_confirmed = Column(Boolean, default=False)
    
    # 时间
    timestamp = Column(DateTime, default=datetime.now)  # 兼容旧字段
    created_at = Column(DateTime, default=datetime.now)
    accepted_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Trade {self.item_name} x{self.quantity} @ {self.price}g>"


class CityEvent(Base):
    """城市事件模型（历史记录）"""
    __tablename__ = "city_events"

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    
    # 事件类型：task_completed, trade, monster_invasion, policy_change
    event_type = Column(String(50), nullable=False)
    
    # 参与者
    participants = Column(Text)  # JSON数组
    
    # 时间
    occurred_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<Event {self.title} - {self.event_type}>"


class CityState(Base):
    """城市状态模型"""
    __tablename__ = "city_state"

    id = Column(Integer, primary_key=True, default=1)
    
    # 城市信息
    name = Column(String(50), default="波尔城")
    population = Column(Integer, default=0)  # 在线玩家数
    gold_reserves = Column(Float, default=10000)
    
    # 指数
    security_level = Column(Float, default=75.0)  # 0-100
    economy_index = Column(Float, default=85.0)   # 0-100
    happiness_index = Column(Float, default=70.0) # 0-100
    
    # 政策
    tax_rate = Column(Float, default=0.05)  # 5%
    last_tax_collected = Column(DateTime)
    
    # 时间
    current_game_day = Column(Integer, default=1)
    last_tick = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<CityState {self.name} - Day {self.current_game_day}>"


class Inventory(Base):
    """背包/商店模型"""
    __tablename__ = "inventories"

    id = Column(Integer, primary_key=True)
    
    # 所有者
    owner_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    
    # 物品
    item_name = Column(String(100), nullable=False)
    quantity = Column(Integer, default=0)
    
    # 时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<Inventory {self.item_name} x{self.quantity}>"


class NPC(Base):
    """NPC模型"""
    __tablename__ = "npcs"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    # 角色
    job = Column(String(20))  # 市长、商会长、卫队长等
    location = Column(String(50))

    # 性格
    personality = Column(Text, default="{}")  # JSON

    # 状态
    mood = Column(String(20), default="neutral")
    fatigue = Column(Float, default=0.0)  # 0-1

    # 日志
    interaction_history = Column(Text, default="[]")  # JSON数组

    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<NPC {self.name} - {self.job}>"


class Location(Base):
    """地图位置模型"""
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(100))

    # 位置信息
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    zone_type = Column(String(50), index=True)  # residential, commercial, industrial, wilderness

    # 属性
    description = Column(Text)
    capacity = Column(Integer, default=50)
    current_players = Column(Integer, default=0)

    # 资源点（JSON格式）
    resources = Column(Text, default="[]")  # [{"type": "wood", "amount": 100}, ...]

    # 建筑/设施（JSON格式）
    buildings = Column(Text, default="[]")  # [{"type": "shop", "owner_id": 1}, ...]

    # 状态
    is_unlocked = Column(Boolean, default=True)
    unlock_requirement = Column(Text)  # JSON: {"gold": 1000, "reputation": 50}

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<Location {self.display_name} ({self.zone_type})>"


class Property(Base):
    """房产模型"""
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False, index=True)

    # 基本信息
    property_type = Column(String(50), index=True)  # apartment, house, shop, warehouse
    size = Column(Integer)  # 面积（平方米）

    # 所有权
    owner_id = Column(Integer, ForeignKey("players.id"), nullable=True, index=True)
    purchase_price = Column(Float)
    current_value = Column(Float)

    # 租赁
    is_rented = Column(Boolean, default=False)
    tenant_id = Column(Integer, ForeignKey("players.id"), nullable=True)
    rent_price = Column(Float, default=0)
    rent_due_date = Column(DateTime, nullable=True)

    # 状态
    condition = Column(Float, default=100.0)  # 0-100
    upgrade_level = Column(Integer, default=1)

    # 功能（JSON格式）
    features = Column(Text, default="[]")  # ["storage_+50", "crafting_bench", ...]

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<Property {self.property_type} @ Location {self.location_id}>"


class Job(Base):
    """工作模型（持续性工作，不是一次性任务）"""
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)

    # 工作信息
    title = Column(String(100), nullable=False)
    description = Column(Text)
    job_type = Column(String(50), index=True)  # mining, crafting, trading, guarding, researching

    # 需求
    required_job_class = Column(String(50), index=True)  # warrior, merchant, crafter, scholar
    required_level = Column(Integer, default=1)
    location_id = Column(Integer, ForeignKey("locations.id"), index=True)

    # 报酬
    base_pay = Column(Float)  # 基础工资（每小时）
    bonus_conditions = Column(Text)  # JSON: {"efficiency": 1.5, "quality": 1.2}

    # 状态
    is_available = Column(Boolean, default=True, index=True)
    max_workers = Column(Integer, default=1)
    current_workers = Column(Integer, default=0)

    # 雇主
    employer_id = Column(Integer, ForeignKey("players.id"), nullable=True)
    employer_type = Column(String(20), default="system")  # system, player, npc

    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Job {self.title} - {self.job_type}>"


class WorkSession(Base):
    """工作会话记录"""
    __tablename__ = "work_sessions"

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)

    # 时间
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, default=0)

    # 产出（JSON格式）
    output = Column(Text)  # {"items": [...], "quality": 0.85}
    earnings = Column(Float, default=0)

    # 状态
    status = Column(String(20), default="active", index=True)  # active, completed, interrupted

    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<WorkSession Player {self.player_id} - Job {self.job_id}>"


class Resource(Base):
    """资源点模型"""
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False, index=True)

    # 资源信息
    resource_type = Column(String(50), index=True)  # wood, stone, ore, herbs
    amount = Column(Float)
    max_amount = Column(Float)

    # 采集
    regeneration_rate = Column(Float)  # 每小时恢复量
    difficulty = Column(Float, default=1.0)

    # 状态
    is_depleted = Column(Boolean, default=False)
    last_harvested = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<Resource {self.resource_type} @ Location {self.location_id}>"


class PlayerState(Base):
    """玩家实时状态（用于 WebSocket 同步）"""
    __tablename__ = "player_states"

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"), unique=True, nullable=False, index=True)

    # 位置
    location_id = Column(Integer, ForeignKey("locations.id"), index=True)
    x = Column(Float, default=0)
    y = Column(Float, default=0)

    # 状态
    is_online = Column(Boolean, default=False, index=True)
    current_activity = Column(String(50))  # idle, working, trading, moving

    # 工作状态
    current_job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    work_session_id = Column(Integer, ForeignKey("work_sessions.id"), nullable=True)

    # 社交
    current_chat_room = Column(String(100), nullable=True)

    last_active = Column(DateTime, default=datetime.now, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<PlayerState Player {self.player_id} - {'Online' if self.is_online else 'Offline'}>"


class MarketPrice(Base):
    """市场价格历史（用于经济分析）"""
    __tablename__ = "market_prices"

    id = Column(Integer, primary_key=True)
    item_name = Column(String(100), nullable=False, index=True)

    # 价格
    average_price = Column(Float)
    min_price = Column(Float)
    max_price = Column(Float)

    # 交易量
    volume = Column(Integer)
    trade_count = Column(Integer)

    # 时间
    date = Column(DateTime, nullable=False, index=True)

    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<MarketPrice {self.item_name} @ {self.date.date()}>"

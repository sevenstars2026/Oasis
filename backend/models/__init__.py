"""
Oasis - 数据模型层
定义所有核心的数据结构
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Table
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
    buyer_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    
    # 交易内容
    item_name = Column(String(100), nullable=False)
    quantity = Column(Integer, default=1)
    price = Column(Float, nullable=False)
    
    # 时间
    timestamp = Column(DateTime, default=datetime.now)
    
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

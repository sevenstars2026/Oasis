from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict
from datetime import datetime


class PlayerCreate(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=3, max_length=32)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    job_type: str = Field(default="citizen")


class PlayerLogin(BaseModel):
    """用户登陆请求"""
    email: EmailStr
    password: str


class PlayerResponse(BaseModel):
    """玩家信息响应"""
    id: int
    name: str
    email: str
    job: str
    gold: float

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """登陆成功返回的Token"""
    access_token: str
    token_type: str = "Bearer"
    player: PlayerResponse


# ============ Task Schemas ============

class TaskCreate(BaseModel):
    """创建任务请求"""
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    required_job: str = Field(..., pattern="^(warrior|merchant|crafter|scholar)$")
    reward: float = Field(..., gt=0, le=10000)
    required_players: int = Field(default=1, ge=1, le=5)


class TaskUpdate(BaseModel):
    """更新任务状态"""
    status: str = Field(..., pattern="^(pending|in_progress|completed|cancelled)$")


class TaskResponse(BaseModel):
    """任务响应"""
    id: int
    title: str
    description: str
    required_job: str
    reward: float  # 从reward_gold映射
    required_players: int  # 从required_count映射
    status: str
    creator_id: int
    accepted_by: Optional[str] = None  # JSON array
    completed_by: Optional[str] = None  # JSON array
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        
    @classmethod
    def model_validate(cls, obj):
        # Pydantic v2 兼容的字段映射
        data = {
            'id': obj.id,
            'title': obj.title,
            'description': obj.description,
            'required_job': obj.required_job,
            'reward': obj.reward_gold,  # 映射reward_gold -> reward
            'required_players': obj.required_count,  # 映射required_count -> required_players
            'status': obj.status,
            'creator_id': obj.creator_id,
            'accepted_by': obj.accepted_by,
            'completed_by': obj.completed_by,
            'created_at': obj.created_at,
            'completed_at': obj.completed_at,
        }
        return super().model_validate(data)


class TaskProgressResponse(BaseModel):
    """任务进度响应"""
    task_id: int
    title: str
    status: str
    accepted_count: int
    completed_count: int
    required_count: int
    progress_percent: float
    reward_per_player: float


# ============ Trade Schemas ============

class TradeCreate(BaseModel):
    """创建交易挂单请求"""
    item_name: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(..., ge=1, le=9999)
    price: float = Field(..., gt=0, le=1_000_000)
    trade_type: str = Field(default="sell", pattern="^(sell|buy)$")


class TradeResponse(BaseModel):
    """交易响应"""
    id: int
    seller_id: int
    buyer_id: Optional[int] = None
    item_name: str
    quantity: int
    price: float
    total_price: float
    trade_type: str
    status: str
    seller_confirmed: bool
    buyer_confirmed: bool
    created_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @classmethod
    def model_validate(cls, obj):
        # Pydantic v2 兼容的验证方法
        raw_buyer_id = getattr(obj, "buyer_id", None)
        raw_status = getattr(obj, "status", "pending")
        buyer_id = None if raw_status == "pending" and raw_buyer_id == obj.seller_id else raw_buyer_id
        return cls(
            id=obj.id,
            seller_id=obj.seller_id,
            buyer_id=buyer_id,
            item_name=obj.item_name,
            quantity=obj.quantity,
            price=obj.price,
            total_price=obj.price * obj.quantity,
            trade_type=getattr(obj, "trade_type", "sell"),
            status=raw_status,
            seller_confirmed=bool(getattr(obj, "seller_confirmed", False)),
            buyer_confirmed=bool(getattr(obj, "buyer_confirmed", False)),
            created_at=getattr(obj, "created_at", None),
            accepted_at=getattr(obj, "accepted_at", None),
            completed_at=getattr(obj, "completed_at", None),
        )


class MarketStatsResponse(BaseModel):
    """市场统计响应"""
    pending_orders: int
    accepted_orders: int
    completed_orders_24h: int
    total_volume_24h: float
    average_price_by_item: Dict[str, float]

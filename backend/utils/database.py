"""
数据库连接与初始化
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import Base
import os

# 数据库URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./oasis.db")

# 创建引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """初始化数据库（创建所有表）"""
    Base.metadata.create_all(bind=engine)
    _ensure_trade_schema()
    print("✅ Database initialized")


def get_db():
    """获取数据库会话（供FastAPI依赖注入使用）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _ensure_trade_schema():
    """
    为已有SQLite数据库补齐trade系统新增字段。
    仅在缺失列时执行ALTER TABLE，避免重建数据库。
    """
    if "sqlite" not in DATABASE_URL:
        return

    required_columns = {
        "trade_type": "TEXT DEFAULT 'sell'",
        "status": "TEXT DEFAULT 'pending'",
        "seller_confirmed": "BOOLEAN DEFAULT 0",
        "buyer_confirmed": "BOOLEAN DEFAULT 0",
        "created_at": "DATETIME",
        "accepted_at": "DATETIME",
        "completed_at": "DATETIME",
    }

    with engine.begin() as conn:
        existing = conn.execute(text("PRAGMA table_info(trades)")).fetchall()
        if not existing:
            return

        existing_names = {row[1] for row in existing}
        for name, column_sql in required_columns.items():
            if name not in existing_names:
                conn.execute(text(f"ALTER TABLE trades ADD COLUMN {name} {column_sql}"))

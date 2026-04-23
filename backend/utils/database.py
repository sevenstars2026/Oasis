"""
数据库连接与初始化
"""

from sqlalchemy import create_engine
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
    print("✅ Database initialized")


def get_db():
    """获取数据库会话（供FastAPI依赖注入使用）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

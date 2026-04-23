from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import Player
from schemas import PlayerCreate
from utils.auth import hash_password, verify_password
from utils.exceptions import (
    EmailAlreadyExistsError,
    UsernameAlreadyExistsError,
    InvalidCredentialsError,
    PlayerNotFoundError,
)


class PlayerService:
    """玩家业务逻辑"""

    @staticmethod
    def create_player(db: Session, player_create: PlayerCreate) -> Player:
        """创建新玩家"""
        hashed_password = hash_password(player_create.password)
        
        db_player = Player(
            name=player_create.username,  # schema用username，模型用name
            email=player_create.email,
            password_hash=hashed_password,
            job=player_create.job_type,  # schema用job_type，模型用job
            gold=1000.0,  # 初始金币
        )
        
        try:
            db.add(db_player)
            db.commit()
            db.refresh(db_player)
            return db_player
        except IntegrityError as e:
            db.rollback()
            if "email" in str(e):
                raise EmailAlreadyExistsError(player_create.email)
            elif "name" in str(e):
                raise UsernameAlreadyExistsError(player_create.username)
            raise

    @staticmethod
    def authenticate_player(db: Session, email: str, password: str) -> Player:
        """验证玩家登陆凭证"""
        player = db.query(Player).filter(Player.email == email).first()
        
        if not player or not verify_password(password, player.password_hash):
            raise InvalidCredentialsError()
        
        return player

    @staticmethod
    def get_player_by_id(db: Session, player_id: int) -> Player:
        """获取玩家信息"""
        player = db.query(Player).filter(Player.id == player_id).first()
        if not player:
            raise PlayerNotFoundError(player_id)
        return player

    @staticmethod
    def get_player_by_email(db: Session, email: str) -> Player:
        """按邮箱获取玩家"""
        return db.query(Player).filter(Player.email == email).first()

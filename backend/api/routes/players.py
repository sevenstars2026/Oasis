from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import PlayerCreate, PlayerLogin, TokenResponse, PlayerResponse
from services.player_service import PlayerService
from utils.auth import create_access_token, get_current_player
from utils.exceptions import OasisError
from utils.database import get_db
from models import Player

router = APIRouter(prefix="/players", tags=["players"])


@router.post("/register", response_model=TokenResponse)
def register(player_create: PlayerCreate, db: Session = Depends(get_db)):
    """用户注册"""
    try:
        player = PlayerService.create_player(db, player_create)
        access_token = create_access_token({"sub": player.id})
        return TokenResponse(
            access_token=access_token,
            player=PlayerResponse.model_validate(player)
        )
    except OasisError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/login", response_model=TokenResponse)
def login(player_login: PlayerLogin, db: Session = Depends(get_db)):
    """用户登陆"""
    try:
        player = PlayerService.authenticate_player(
            db, player_login.email, player_login.password
        )
        access_token = create_access_token({"sub": player.id})
        return TokenResponse(
            access_token=access_token,
            player=PlayerResponse.model_validate(player)
        )
    except OasisError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/me", response_model=PlayerResponse)
def get_me(current_player: Player = Depends(get_current_player)):
    """获取当前登录玩家信息"""
    return PlayerResponse.model_validate(current_player)


@router.get("/{player_id}", response_model=PlayerResponse)
def get_player(player_id: int, db: Session = Depends(get_db)):
    """获取玩家信息"""
    try:
        player = PlayerService.get_player_by_id(db, player_id)
        return PlayerResponse.model_validate(player)
    except OasisError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

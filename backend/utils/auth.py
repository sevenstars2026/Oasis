from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, Header

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


def hash_password(password: str) -> str:
    """密码加密"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(player_id: int, expires_in: Optional[timedelta] = None) -> str:
    """生成JWT Token"""
    if expires_in is None:
        expires_in = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
    expire = datetime.utcnow() + expires_in
    to_encode = {"sub": str(player_id), "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[int]:
    """验证并解析JWT Token，返回player_id"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        player_id: str = payload.get("sub")
        if player_id is None:
            return None
        return int(player_id)
    except jwt.InvalidTokenError:
        return None


async def get_current_player(authorization: str = Header(None)) -> dict:
    """
    获取当前登陆的玩家信息（从Authorization头提取）
    
    期望格式: "Bearer {token}"
    返回格式: {"player_id": int, "token": str}
    """
    if not authorization:
        raise HTTPException(status_code=403, detail="Missing authorization header")
    
    # 解析 "Bearer {token}" 格式
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=403, detail="Invalid authorization header format")
    
    token = parts[1]
    player_id = decode_access_token(token)
    
    if player_id is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return {"player_id": player_id, "token": token}

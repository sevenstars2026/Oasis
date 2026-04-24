from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from models import Player
from utils.database import get_db

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10080

security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    # bcrypt限制密码最长72字节
    return pwd_context.hash(password[:72])

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password[:72], hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    # 确保 sub 是字符串
    if "sub" in to_encode and not isinstance(to_encode["sub"], str):
        to_encode["sub"] = str(to_encode["sub"])
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Player:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        player_id_str: str = payload.get("sub")
        if player_id_str is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        player_id = int(player_id_str)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    player = db.query(Player).filter(Player.id == player_id).first()
    if player is None:
        raise HTTPException(status_code=401, detail="Player not found")

    return player

async def get_current_user_ws(token: str, db: Session) -> Player:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        player_id_str: str = payload.get("sub")
        if player_id_str is None:
            return None
        player_id = int(player_id_str)
    except JWTError:
        return None

    player = db.query(Player).filter(Player.id == player_id).first()
    return player

# 别名，兼容旧代码
get_current_player = get_current_user

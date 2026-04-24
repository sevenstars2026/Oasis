I'll diagnose and fix the JWT authentication and dependency issues. Let me start by examining the current state of the authentication system.

<read_code>
<path>backend/api/routes/players.py</path>
</read_code>

<read_file>
<path>backend/requirements.txt</path>
</read_file>

<read_code>
<path>backend/core/security.py</path>
</read_code>

<read_code>
<path>backend/schemas/player.py</path>
</read_code>

Now let me check if there are any JWT-related utilities or configurations:

<read_code>
<path>backend/core/config.py</path>
</read_code>

Let me also check the dependencies structure:

<list_dir>
<path>backend</path>
</list_dir>

<list_dir>
<path>backend/api</path>
</list_dir>

<list_dir>
<path>backend/core</path>
</list_dir>

Based on my analysis, here are the issues and fixes:

## 🔍 诊断结论

### 发现的问题：

1. **缺少 `python-jose` 依赖** - requirements.txt 中没有 JWT 处理所需的包
2. **缺少 JWT 安全模块** - 没有找到 `backend/core/security.py` 文件
3. **缺少配置文件** - 没有找到 `backend/core/config.py` 用于 JWT 密钥配置
4. **Schema 定义可能不完整** - 需要确认 TokenResponse 的格式

让我创建完整的 JWT 认证系统：

## ✅ 修复步骤

### 1. 更新 requirements.txt

<write_file>
<path>backend/requirements.txt</path>
<content>fastapi==0.115.5
uvicorn[standard]==0.32.1
sqlalchemy==2.0.36
alembic==1.14.0
psycopg2-binary==2.9.10
pydantic==2.10.3
pydantic-settings==2.6.1
python-multipart==0.0.17
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
email-validator==2.1.0
python-dotenv==1.0.1
</content>
</write_file>

### 2. 创建配置文件

<write_file>
<path>backend/core/config.py</path>
<content>from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Oasis API"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str
    
    # JWT Settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
</content>
</write_file>

### 3. 创建安全工具模块

<write_file>
<path>backend/core/security.py</path>
<content>from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.db.database import get_db
from backend.models.player import Player

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token scheme
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """解码 JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_player(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Player:
    """获取当前认证的玩家"""
    token = credentials.credentials
    
    payload = decode_access_token(token)
    player_id: str = payload.get("sub")
    
    if player_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    player = db.query(Player).filter(Player.id == int(player_id)).first()
    
    if player is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Player not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return player
</content>
</write_file>

### 4. 更新 Player Schema

<write_file>
<path>backend/schemas/player.py</path>
<content>from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class PlayerBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class PlayerCreate(PlayerBase):
    password: str = Field(..., min_length=6)


class PlayerLogin(BaseModel):
    username: str
    password: str


class PlayerResponse(BaseModel):
    id: int
    username: str
    email: str
    level: int
    experience: int
    coins: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"  # 标准 OAuth2 格式使用大写 "Bearer"
    player: PlayerResponse


class PlayerUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)
</content>
</write_file>

### 5. 更新认证路由

<write_file>
<path>backend/api/routes/players.py</path>
<content>from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.models.player import Player
from backend.schemas.player import (
    PlayerCreate,
    PlayerLogin,
    PlayerResponse,
    TokenResponse,
    PlayerUpdate
)
from backend.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_player
)

router = APIRouter(prefix="/players", tags=["players"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(player_data: PlayerCreate, db: Session = Depends(get_db)):
    """注册新玩家"""
    # 检查用户名是否已存在
    existing_player = db.query(Player).filter(Player.username == player_data.username).first()
    if existing_player:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # 检查邮箱是否已存在
    existing_email = db.query(Player).filter(Player.email == player_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 创建新玩家
    hashed_password = get_password_hash(player_data.password)
    new_player = Player(
        username=player_data.username,
        email=player_data.email,
        password_hash=hashed_password
    )
    
    db.add(new_player)
    db.commit()
    db.refresh(new_player)
    
    # 生成 JWT token
    access_token = create_access_token(data={"sub": str(new_player.id)})
    
    return TokenResponse(
        access_token=access_token,
        token_type="Bearer",
        player=PlayerResponse.model_validate(new_player)
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: PlayerLogin, db: Session = Depends(get_db)):
    """玩家登录"""
    # 查找玩家
    player = db.query(Player).filter(Player.username == credentials.username).first()
    
    if not player or not verify_password(credentials.password, player.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 生成 JWT token
    access_token = create_access_token(data={"sub": str(player.id)})
    
    return TokenResponse(
        access_token=access_token,
        token_type="Bearer",
        player=PlayerResponse.model_validate(player)
    )


@router.get("/me", response_model=PlayerResponse)
async def get_current_player_info(current_player: Player = Depends(get_current_player)):
    """获取当前登录玩家信息"""
    return PlayerResponse.model_validate(current_player)


@router.put("/me", response_model=PlayerResponse)
async def update_player(
    player_update: PlayerUpdate,
    current_player: Player = Depends(get_current_player),
    db: Session = Depends(get_db)
):
    """更新当前玩家信息"""
    if player_update.email:
        # 检查邮箱是否被其他用户使用
        existing = db.query(Player).filter(
            Player.email == player_update.email,
            Player.id != current_player.id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        current_player.email = player_update.email
    
    if player_update.password:
        current_player.password_hash = get_password_hash(player_update.password)
    
    db.commit()
    db.refresh(current_player)
    
    return PlayerResponse.model_validate(current_player)


@router.get("/{player_id}", response_model=PlayerResponse)
async def get_player(player_id: int, db: Session = Depends(get_db)):
    """获取指定玩家信息（公开信息）"""
    player = db.query(Player).filter(Player.id == player_id).first()
    
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    
    return PlayerResponse.model_validate(player)
</content>
</write_file>

### 6. 创建 .env.example 文件

<write_file>
<path>backend/.env.example</path>
<content># Application
APP_NAME=Oasis API
DEBUG=True

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/oasis_db

# JWT Settings (生成方式: openssl rand -hex 32)
SECRET_KEY=your-secret-key-here-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
</content>
</write_file>

## 📋 安装和验证步骤

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 生成 SECRET_KEY

```bash
# 生成安全的密钥
openssl rand -hex 32
```

### 3. 配置环境变量

```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env 文件，设置：
# - DATABASE_URL
# - SECRET_KEY (使用上面生成的密钥)
```

### 4. 验证安装

```bash
# 检查 python-jose 是否安装
pip list | grep python-jose

# 应该看到：
# python-jose    3.3.0
```

### 5. 测试认证流程

```bash
# 启动服务器
uvicorn backend.main:app --reload

# 测试注册
curl -X POST "http://localhost:8000/api/players/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'

# 测试登录
curl -X POST "http://localhost:8000/api/players/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'

# 测试受保护的端点（使用返回的 token）
curl -X GET "http://localhost:8000/api/players/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🎯 关键修复点总结

1. **token_type 使用 "Bearer"** - 符合 OAuth2 标准（大写 B）
2. **完整的 JWT 生成和验证逻辑** - 使用 python-jose
3. **密码哈希** - 使用 bcrypt
4. **HTTPBearer 认证方案** - 标准的 Authorization header 处理
5. **依赖注入** - 使用 FastAPI 的 Depends 系统
6. **错误处理** - 正确的 HTTP 状态码和错误消息

前端现在可以这样使用：

```typescript
// 登录后保存 token
const response = await fetch('/api/players/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username, password })
});

const { access_token, token_type, player } = await response.json();

// 使用 token 访问受保护的端点
fetch('/api/players/me', {
  headers: {
    'Authorization': `${token_type} ${access_token}` // "Bearer <token>"
  }
});
```
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from utils.database import Base, get_db

# 使用内存SQLite数据库进行测试
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


Base.metadata.create_all(bind=engine)
app.dependency_overrides[get_db] = override_get_db

# 创建测试客户端
client = TestClient(app)


class TestPlayerRegistration:
    """玩家注册测试"""

    def test_register_success(self):
        """成功注册"""
        response = client.post(
            "/players/register",
            json={
                "username": "warrior_john",
                "email": "john@example.com",
                "password": "securepass123",
                "job_type": "warrior"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"]
        assert data["player"]["name"] == "warrior_john"
        assert data["player"]["job"] == "warrior"
        assert data["player"]["gold"] == 1000.0

    def test_register_duplicate_email(self):
        """重复邮箱注册"""
        client.post(
            "/players/register",
            json={
                "username": "user1",
                "email": "test@example.com",
                "password": "password123",
                "job_type": "merchant"
            }
        )
        response = client.post(
            "/players/register",
            json={
                "username": "user2",
                "email": "test@example.com",
                "password": "password123",
                "job_type": "scholar"
            }
        )
        assert response.status_code == 409
        assert response.json()["detail"] == "Email test@example.com already registered"

    def test_register_invalid_job(self):
        """无效职业"""
        response = client.post(
            "/players/register",
            json={
                "username": "user",
                "email": "user@example.com",
                "password": "password123",
                "job_type": "invalid_job"
            }
        )
        assert response.status_code == 422  # Pydantic validation error

    def test_register_short_password(self):
        """密码太短"""
        response = client.post(
            "/players/register",
            json={
                "username": "user",
                "email": "user@example.com",
                "password": "short",
                "job_type": "warrior"
            }
        )
        assert response.status_code == 422


class TestPlayerLogin:
    """玩家登陆测试"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """为每个测试创建用户"""
        client.post(
            "/players/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "correctpass123",
                "job_type": "warrior"
            }
        )

    def test_login_success(self):
        """成功登陆"""
        response = client.post(
            "/players/login",
            json={
                "email": "test@example.com",
                "password": "correctpass123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"]
        assert data["player"]["email"] == "test@example.com"

    def test_login_wrong_password(self):
        """错误密码"""
        response = client.post(
            "/players/login",
            json={
                "email": "test@example.com",
                "password": "wrongpass123"
            }
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid email or password"

    def test_login_nonexistent_email(self):
        """邮箱不存在"""
        response = client.post(
            "/players/login",
            json={
                "email": "nonexistent@example.com",
                "password": "anypass123"
            }
        )
        assert response.status_code == 401


class TestPlayerProfile:
    """玩家信息测试"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """创建用户"""
        response = client.post(
            "/players/register",
            json={
                "username": "alice",
                "email": "alice@example.com",
                "password": "password123",
                "job_type": "crafter"
            }
        )
        self.player_id = response.json()["player"]["id"]

    def test_get_player_success(self):
        """获取玩家信息"""
        response = client.get(f"/players/{self.player_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "alice"
        assert data["job"] == "crafter"

    def test_get_nonexistent_player(self):
        """获取不存在的玩家"""
        response = client.get("/players/9999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Player 9999 not found"

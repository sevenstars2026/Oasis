"""
集成测试 - 验证API正常工作
运行方式：python -m pytest tests/test_integration.py -v
"""
import requests
import time
import json

BASE_URL = "http://localhost:8000"
TIMEOUT = 5


def test_health():
    """检查服务器健康状态"""
    response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register_and_login():
    """测试注册和登陆流程"""
    # 1. 注册新用户
    register_data = {
        "username": f"testuser_{int(time.time())}",
        "email": f"test_{int(time.time())}@example.com",
        "password": "SecurePassword123",
        "job_type": "warrior"
    }
    
    response = requests.post(
        f"{BASE_URL}/players/register",
        json=register_data,
        timeout=TIMEOUT
    )
    assert response.status_code == 200
    register_result = response.json()
    assert "access_token" in register_result
    assert register_result["player"]["name"] == register_data["username"]
    assert register_result["player"]["job"] == register_data["job_type"]
    assert register_result["player"]["gold"] == 1000.0
    
    player_id = register_result["player"]["id"]
    
    # 2. 用同一邮箱再次注册应失败
    response = requests.post(
        f"{BASE_URL}/players/register",
        json=register_data,
        timeout=TIMEOUT
    )
    assert response.status_code == 409  # Email already exists
    
    # 3. 登陆
    login_data = {
        "email": register_data["email"],
        "password": register_data["password"]
    }
    response = requests.post(
        f"{BASE_URL}/players/login",
        json=login_data,
        timeout=TIMEOUT
    )
    assert response.status_code == 200
    login_result = response.json()
    assert "access_token" in login_result
    assert login_result["player"]["id"] == player_id
    
    # 4. 获取玩家信息
    response = requests.get(
        f"{BASE_URL}/players/{player_id}",
        timeout=TIMEOUT
    )
    assert response.status_code == 200
    player_info = response.json()
    assert player_info["name"] == register_data["username"]
    assert player_info["email"] == register_data["email"]


def test_invalid_job_type():
    """测试无效职业类型"""
    response = requests.post(
        f"{BASE_URL}/players/register",
        json={
            "username": "invalidjob",
            "email": "invalid@example.com",
            "password": "password123",
            "job_type": "invalid_job"
        },
        timeout=TIMEOUT
    )
    assert response.status_code == 422  # Validation error


def test_invalid_credentials():
    """测试错误的登陆凭证"""
    # 先注册用户
    register_data = {
        "username": f"user_{int(time.time())}",
        "email": f"email_{int(time.time())}@example.com",
        "password": "password123",
        "job_type": "merchant"
    }
    requests.post(
        f"{BASE_URL}/players/register",
        json=register_data,
        timeout=TIMEOUT
    )
    
    # 用错误密码登陆
    response = requests.post(
        f"{BASE_URL}/players/login",
        json={
            "email": register_data["email"],
            "password": "wrongpassword"
        },
        timeout=TIMEOUT
    )
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


if __name__ == "__main__":
    print("运行集成测试...")
    print("确保服务器运行在 http://localhost:8000")

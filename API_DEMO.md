# API 功能演示

**日期**: 2026-04-23  
**服务器状态**: ✅ 运行中（localhost:8000）

## 🎮 演示场景

### 1. 健康检查 ✅

```bash
GET /health

响应:
{
  "status": "ok",
  "message": "Oasis is running"
}
```

### 2. 用户注册 - 战士职业 ✅

```bash
POST /players/register

请求:
{
  "username": "dragon_slayer",
  "email": "warrior@oasis.com",
  "password": "SecurePass123",
  "job_type": "warrior"
}

响应:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "player": {
    "id": 4,
    "name": "dragon_slayer",
    "email": "warrior@oasis.com",
    "job": "warrior",
    "gold": 1000.0
  }
}
```

### 3. 用户注册 - 商人职业 ✅

```bash
POST /players/register

请求:
{
  "username": "rich_merchant",
  "email": "merchant@oasis.com",
  "password": "MyPassword456",
  "job_type": "merchant"
}

响应:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "player": {
    "id": 5,
    "name": "rich_merchant",
    "email": "merchant@oasis.com",
    "job": "merchant",
    "gold": 1000.0
  }
}
```

### 4. 用户登陆 ✅

```bash
POST /players/login

请求:
{
  "email": "warrior@oasis.com",
  "password": "SecurePass123"
}

响应:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "player": {
    "id": 4,
    "name": "dragon_slayer",
    "email": "warrior@oasis.com",
    "job": "warrior",
    "gold": 1000.0
  }
}
```

### 5. 获取玩家信息 - 战士 ✅

```bash
GET /players/4

响应:
{
  "id": 4,
  "name": "dragon_slayer",
  "email": "warrior@oasis.com",
  "job": "warrior",
  "gold": 1000.0
}
```

### 6. 获取玩家信息 - 商人 ✅

```bash
GET /players/5

响应:
{
  "id": 5,
  "name": "rich_merchant",
  "email": "merchant@oasis.com",
  "job": "merchant",
  "gold": 1000.0
}
```

## ❌ 错误处理演示

### 错误1: 邮箱重复注册

```bash
POST /players/register

请求: (使用已存在的邮箱)
{
  "username": "another_user",
  "email": "warrior@oasis.com",
  "password": "password123",
  "job_type": "warrior"
}

响应 (409):
{
  "detail": "Email warrior@oasis.com already registered"
}
```

### 错误2: 错误密码登陆

```bash
POST /players/login

请求:
{
  "email": "warrior@oasis.com",
  "password": "WrongPassword"
}

响应 (401):
{
  "detail": "Invalid email or password"
}
```

### 错误3: 无效职业类型

```bash
POST /players/register

请求:
{
  "username": "invalid_user",
  "email": "invalid@oasis.com",
  "password": "password123",
  "job_type": "invalid_job"
}

响应 (422):
{
  "detail": [
    {
      "type": "string_pattern_mismatch",
      "loc": ["body", "job_type"],
      "msg": "String should match pattern '^(warrior|merchant|crafter|scholar)$'",
      "input": "invalid_job"
    }
  ]
}
```

## ✅ 功能检查清单

- ✅ 用户注册
- ✅ 密码加密（Argon2）
- ✅ 用户登陆
- ✅ JWT令牌生成
- ✅ 获取用户信息
- ✅ 邮箱唯一性验证
- ✅ 职业类型枚举
- ✅ 错误消息处理
- ✅ HTTP状态码正确
- ✅ 输入验证

## 📊 当前数据库

| 用户ID | 用户名 | 邮箱 | 职业 | 金币 |
|--------|--------|------|------|------|
| 4 | dragon_slayer | warrior@oasis.com | warrior | 1000.0 |
| 5 | rich_merchant | merchant@oasis.com | merchant | 1000.0 |

## 🔗 可交互的文档

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

在这些页面中可以：
1. 查看所有API端点
2. 直接测试API
3. 看到完整的请求/响应示例
4. 下载OpenAPI规范

## 🎯 下一步

- [ ] 任务系统 (Day 4-5)
- [ ] 交易系统 (Day 6-7)
- [ ] 前端开发 (Week 2)

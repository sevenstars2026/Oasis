# Oasis 认证和依赖问题修复请求

## 问题 1: 认证契约不一致

### 现象
- 认证系统返回的 token 格式与前端期望的格式不匹配
- 可能导致 JWT 验证失败

### 需要检查
1. `PlayerResponse` schema 中的 `player` 字段返回格式
2. `TokenResponse` 中 `token_type` 的值 ("bearer" vs "Bearer")
3. JWT token 的生成和验证逻辑

### 后端路由文件位置
- `backend/api/routes/players.py` - 登录和注册端点

### 问题代码示例（可能）
```python
# ❌ 可能问题
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"  # 应该是 "Bearer"?
    player: PlayerResponse
```

## 问题 2: 缺少 python-jose 依赖

### 现象
- JWT 处理相关代码会导入 `python-jose`
- 但 requirements.txt 中没有这个包

### 需要的包
```
python-jose[cryptography]==3.3.0
email-validator==2.1.0
```

### 检查命令
```bash
pip list | grep python-jose
```

## 任务清单

1. **诊断 JWT 问题**
   - 检查 `backend/api/routes/players.py` 的登录逻辑
   - 确认 token_type 是 "Bearer" 还是 "bearer"
   - 检查前端期望的格式

2. **修复依赖**
   - 更新 `backend/requirements.txt` 添加 python-jose
   - 生成更新命令

3. **修复认证逻辑**
   - 确保 JWT 生成和验证一致
   - 确保 token 返回格式正确
   - 提供完整的修复代码

## 期望输出

给出：
1. ✅ 修复后的 `backend/requirements.txt`
2. ✅ 修复后的 `backend/api/routes/players.py`（认证部分）
3. ✅ 完整的安装和验证步骤
4. ✅ 诊断结论：认证系统的问题根源


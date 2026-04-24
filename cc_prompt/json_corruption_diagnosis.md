# 【紧急】前后端JSON乱码问题诊断

## 问题陈述
用户反馈：打开前端后端网址都显示JSON乱码

## 诊断结果

### 环境
- 前端 (5173): ✅ Vite dev server 运行正常
- 后端 (8000): ✅ Uvicorn 运行，但存在问题
- 系统：Linux，Python虚拟环境

### 症状分析
```
✅ http://localhost:8000/health → 200 OK {"status": "ok"}
✅ http://localhost:8000/ → 200 OK {"name": "Oasis", ...}
✅ http://localhost:8000/docs → 200 OK (HTML正常)
❌ http://localhost:8000/openapi.json → 200 OK (但内容为空/乱码)
```

### 代码问题发现

**main.py 第36行**
```python
@app.on_event("startup")  # ← 已弃用
async def startup_event():
    init_db()
```

应该改为 lifespan 模式（FastAPI 0.93+）

**启动问题**
- 无法以 `python main.py` 启动（reload=True需要import string）
- 应该使用 `uvicorn main:app --reload`

### 需要检查的文件
1. **backend/schemas.py** - 所有数据模型定义
   - 是否有无法序列化的字段？（datetime, UUID, Enum, 自定义类）
   
2. **backend/api/routes/*.py** - 6个路由文件
   - 是否有错误的类型注解？
   - 是否有循环引用或嵌套模型问题？
   
3. **backend/requirements.txt** - 依赖版本
   - FastAPI版本是否过旧或过新？
   - Pydantic版本兼容性？

4. **backend/utils/database.py** - 初始化逻辑
   - init_db() 是否有异常会被吞掉？

## 请执行

### 诊断步骤
1. **检查并修复 main.py** 中的启动问题
2. **验证 schemas.py** 中所有模型的 JSON 序列化能力
3. **检查所有路由** 的返回类型标注
4. **修复 CORS 和中间件** 可能的冲突
5. **给出完整的修复代码** 和执行步骤

### 需要的信息
我会提供以下文件内容供你分析：
- backend/schemas.py (数据模型)
- backend/requirements.txt (依赖版本)
- backend/api/routes/*.py (所有路由，可精简)

## 期望输出
✅ 修复后端启动问题
✅ 确保 /openapi.json 返回有效的JSON
✅ 所有API端点返回格式正常
✅ 前端能正确解析所有响应


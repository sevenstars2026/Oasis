# 🌍 Oasis 项目完整上下文

## 📁 项目结构

```
Oasis/
├── backend/
│   ├── api/routes/       # API 路由
│   ├── utils/auth.py     # 认证工具
│   ├── main.py           # 应用入口
│   └── requirements.txt   # 依赖
├── frontend/             # React 前端
└── cc_*/                 # 通信文件夹
```

## 🎯 已实现功能

✅ 身份验证 (JWT)
✅ 任务系统 (Capability Binding)
✅ 交易系统
✅ WebSocket 实时通信
✅ 地图/工作/属性系统

## ⚠️ 已知问题

| 优先级 | 问题 | 位置 |
|--------|------|------|
| P0 | 认证契约不一致 | backend/utils/auth.py |
| P0 | 缺少 python-jose | backend/requirements.txt |
| P1 | CORS 不安全 | backend/main.py |
| P1 | WebSocket 字段错误 | WebSocket 代码 |
| P1 | 交易逻辑不完整 | trades.py |
| P1 | 并发竞争风险 | trades.py |

---

项目路径: `/home/sevenstars/CLionProjects/Oasis`

# 🎯 任务: 修复认证契约不一致问题

**任务ID**: fix-auth

---

## 📋 任务详情


## 问题
`get_current_player` 返回 `Player` 对象，但所有受保护路由期望 `dict["player_id"]`，导致 AttributeError。

## 需要修改
- `backend/utils/auth.py` - 统一返回类型
- `backend/api/routes/*.py` - 所有路由的参数解析

## 验收标准
✓ 认证返回类型一致
✓ 所有受保护路由都能正确获取 player_id
✓ 没有 AttributeError


---

## 🔍 项目上下文

项目路径: `/home/sevenstars/CLionProjects/Oasis`

已实现功能:
- 身份验证系统
- 任务系统（Capability Binding）
- 交易系统
- WebSocket 实时通信
- 地图、工作、属性系统

已知问题:
- P0: 认证契约不一致
- P0: 缺少 python-jose 依赖
- P1: CORS 不安全
- P1: WebSocket 字段错误
- P1: 交易逻辑不完整
- P1: 并发竞争风险

---

## ✅ 完成后

请提交详细的执行报告，包括:
1. 修改的文件列表
2. 每个文件的具体改动
3. 验收标准检查
4. 任何注意事项

---

**请开始执行任务！** 任务文件已保存在 `cc_prompt/fix-auth.md`

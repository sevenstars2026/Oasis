# Task: 模型真实性诊断测试

Project: /home/sevenstars/CLionProjects/Oasis

# 🧪 Claude Code 模型诊断测试

**任务 ID**: diagnostic_test
**目的**: 验证你背后模型的真实水平

---

## 测试 1: 代码理解深度

分析这段代码，指出所有的问题（包括隐藏的）：

```python
async def complete_trade(trade_id: int, db: Session):
    trade = db.query(Trade).filter(Trade.id == trade_id).first()
    if not trade:
        return {"error": "Trade not found"}
    
    seller = db.query(Player).filter(Player.id == trade.seller_id).first()
    buyer = db.query(Player).filter(Player.id == trade.buyer_id).first()
    
    # 更新库存
    seller.inventory.remove(trade.item_id)
    buyer.inventory.append(trade.item_id)
    
    # 更新交易状态
    trade.status = "COMPLETED"
    db.commit()
    
    return {"success": True}
```

**期望的回答包含**：
1. 原子性问题（没有事务锁）
2. 异常处理缺失
3. 库存验证缺失
4. Race condition 风险
5. 并发问题
6. 返回值类型不一致
7. 异步/同步不匹配问题

---

## 测试 2: 架构设计思考

给出 3 个不同层次的解决方案来修复上面的代码：

1. **最小改进** - 快速修补，最少改动
2. **生产级别** - 企业级解决方案，包括事务、日志、监控
3. **未来扩展** - 考虑高并发、分布式场景

对每个方案说明权衡（成本 vs 收益）。

**期望**：
- 展示多层次思考
- 理解不同权衡
- 企业级思维

---

## 测试 3: 代码生成质量

用 FastAPI + SQLAlchemy 重写上面的函数，要求：
- 完整的错误处理
- 输入验证
- 并发锁机制
- 日志记录
- 类型提示
- 文档字符串

---

## 测试 4: 自我审视

完成上面的代码后，自己做一遍代码审查：

1. 这段代码有什么潜在问题？
2. 在什么样的流量下会暴露？
3. 还需要什么改进？

---

## 评判标准

### Opus 级别的回答特征：
✅ 深入分析，找到 6+ 个问题
✅ 多层次思考（最小→生产→未来）
✅ 企业级解决方案代码
✅ 能自我批评和改进
✅ 理解权衡和设计选择

### Sonnet 级别的回答特征：
⚠️ 分析比较表面（3-4 个问题）
⚠️ 单一解决方案，没有权衡
⚠️ 代码质量一般，缺少完善的错误处理
⚠️ 自我审视有限

### Haiku 级别的回答特征：
❌ 分析不够深入（1-2 个问题）
❌ 代码简单，很多漏洞
❌ 缺少企业级思维
❌ 无法自我批评

---

**现在请开始回答，展示你的真实水平。**
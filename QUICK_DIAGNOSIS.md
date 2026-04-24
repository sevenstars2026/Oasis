# ⚡ 快速诊断（你在 Claude Code 中直接做）

由于 API 路由问题，改用最简单的方式验证你的真实水平。

## 在 Claude Code 中，我需要你做这些：

### 1️⃣ 分析这段代码的问题

```python
async def complete_trade(trade_id: int, db: Session):
    trade = db.query(Trade).filter(Trade.id == trade_id).first()
    if not trade:
        return {"error": "Trade not found"}
    
    seller = db.query(Player).filter(Player.id == trade.seller_id).first()
    buyer = db.query(Player).filter(Player.id == trade.buyer_id).first()
    
    seller.inventory.remove(trade.item_id)
    buyer.inventory.append(trade.item_id)
    
    trade.status = "COMPLETED"
    db.commit()
    
    return {"success": True}
```

**在 Claude Code 中告诉我：**
- 这段代码有哪些问题？（尽量列出所有，包括隐藏问题）
- 最严重的是什么？
- 怎么修复？

### 2️⃣ 生成修复代码

用 FastAPI + SQLAlchemy 重写上面的函数，要求：
- 有错误处理
- 有验证
- 有并发控制
- 有日志
- 有类型提示

### 3️⃣ 自己审查

写完代码后，自己找出还有什么问题？

---

## 快速评分

根据你的回答，我会判断真实水平：

**Opus 特征** ✅
- 找到 6+ 个问题
- 能指出并发问题和 race condition
- 生成的代码完整、企业级
- 自我批评能指出潜在漏洞

**Sonnet 特征** ⚠️
- 找到 3-4 个问题
- 代码一般
- 自我审视有限

**Haiku 特征** ❌
- 找到 1-2 个问题
- 代码简单
- 无深度思维

---

现在就在 Claude Code 中完成上面的 3 个部分，然后告诉我你的分析和代码。


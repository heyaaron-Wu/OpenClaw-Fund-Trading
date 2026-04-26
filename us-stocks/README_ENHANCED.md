# 🇺🇸 美股交易系统 (Iwencai 增强版)

**集成 Iwencai 问财选美股技能**，提供全方位美股筛选和分析能力。

---

## 📦 集成技能 (问财选美股)

### 筛选维度
| 类型 | 筛选标准 | 说明 |
|------|---------|------|
| **价值股** | PE<20, PB<3, 股息>2% | 低估值 + 高分红 |
| **成长股** | 营收增长>20%, 利润增长>25% | 高成长性 |
| **科技股** | AI/芯片/半导体/云计算 | 科技创新 |
| **动量股** | 近 1 月涨幅>15%, 成交量放大 | 强势股 |

### 分析功能
- ✅ 研报评级分析 (买入/持有/卖出)
- ✅ 行业情绪分析 (纳斯达克/标普/道琼斯)
- ✅ 综合评分排序 (多因子加权)
- ✅ 飞书推送通知

---

## 📁 目录结构

```
us-stocks/
├── scripts/
│   ├── us_stock_selector_enhanced.py  # ⭐ 美股筛选器 (增强版)
│   └── daily_review.py                # 日终复盘脚本
├── data/
│   ├── state.json                     # 持仓状态
│   ├── ledger.jsonl                   # 交易记录
│   ├── us_stock_selection.json        # ⭐ 筛选结果 (每日更新)
│   └── reviews/                       # 复盘报告
└── README_ENHANCED.md                 # 本文档
```

---

## 🔄 定时任务

### 已配置任务

| 任务名 | 时间 | 说明 | 状态 |
|--------|------|------|------|
| **us-stock-selector** | 周一至周五 10:00 | ⭐ 美股筛选 (价值 + 成长 + 科技 + 动量) | ✅ 已配置 |
| us-premarket-check | 美股开盘前 | 盘前检查 | ⏸️ 待配置 |
| us-daily-review | 美股盘后 | 日终复盘 | ⏸️ 待配置 |

### 配置方法

```bash
# 查看任务
openclaw cron list | grep us-

# 编辑任务
openclaw cron edit us-stock-selector

# 启用任务
# 设置 enabled=true
```

---

## 🚀 使用方法

### 手动运行筛选
```bash
cd /home/admin/.openclaw/workspace/us-stocks/scripts
python3.11 us_stock_selector_enhanced.py
```

### 输出文件
- **路径**: `/home/admin/.openclaw/workspace/us-stocks/data/us_stock_selection.json`
- **内容**: 
  - value_stocks: 价值股列表
  - growth_stocks: 成长股列表
  - tech_stocks: 科技股列表
  - momentum_stocks: 动量股列表
  - stock_pool: 综合股票池 (Top 50)
  - research_ratings: 研报评级统计

---

## 📊 筛选结果示例

```json
{
  "timestamp": "2026-04-24T10:00:00",
  "summary": {
    "value_count": 25,
    "growth_count": 30,
    "tech_count": 28,
    "momentum_count": 18,
    "total_unique": 85
  },
  "stock_pool": [
    {
      "code": "AAPL",
      "name": "苹果公司",
      "composite_score": 85.5,
      "style": "tech",
      "sector": "technology"
    },
    ...
  ],
  "research_ratings": {
    "buy": 45,
    "hold": 30,
    "sell": 5
  }
}
```

---

## 📈 飞书推送

**推送时间**: 每个交易日 10:00  
**推送内容**:
- 筛选结果汇总 (价值/成长/科技/动量)
- 研报评级统计 (买入/持有/卖出)
- Top 3 股票

**推送群**: 美股群

---

## 🎯 综合评分算法

```python
综合评分 = 基础分 (50) + 因子加分

# 价值股因子
- PE < 15: +15 分
- 股息率 > 3%: +10 分

# 成长股因子
- 营收增长 > 30%: +20 分
- 利润增长 > 40%: +20 分

# 科技股因子
- 科技行业：+10 分

# 动量股因子
- 近 1 月涨幅 > 20%: +15 分

# 上限：100 分
```

---

## ⚠️ 注意事项

### 数据隔离
- ✅ 美股数据独立于 A 股基金
- ✅ 不同的飞书 Webhook
- ✅ 不同的数据目录

### API 限制
- Iwencai API 有调用频率限制
- 缓存 24 小时减少重复调用
- 失败时自动降级

### 投资风险提示
- 筛选结果仅供参考，不构成投资建议
- 美股市场波动较大，注意风险控制
- 建议结合基本面和技术面综合分析

---

## 📝 下一步

### 待开发功能
- [ ] 美股持仓管理
- [ ] 美股交易决策 (类似 A 股 14:00 决策)
- [ ] 美股执行门控
- [ ] 美股日终复盘增强

### 可选扩展
- [ ] 集成机器学习策略 (预测美股走势)
- [ ] 集成地缘政治风险分析 (评估国际风险)
- [ ] 集成新闻搜索 (美股相关新闻)

---

**最后更新**: 2026-04-24  
**版本**: v1.0 (Iwencai 增强版)  
**技能**: 问财选美股

# 📊 基金日终复盘 - {{date}}

## 基本信息

- **日期**: {{date}}
- **交易日**: {{is_trading_day}}
- **复盘时间**: {{review_time}}

---

## 📊 持仓概览

| 项目 | 数值 |
|------|------|
| 持仓数量 | {{positions_count}} 只 |
| 投入本金 | {{total_invested}} 元 |
| 浮动盈亏 | {{unrealized_pnl}} 元 |
| 组合总值 | {{portfolio_value}} 元 |
| 当日收益 | {{daily_pnl}} 元 |
| 累计收益 | {{total_pnl}} 元 |
| 收益率 | {{pnl_rate}}% |

---

## 📈 持仓明细

| 基金代码 | 基金名称 | 持仓金额 | 当日盈亏 | 累计盈亏 | 收益率 |
|----------|----------|----------|----------|----------|--------|
{{#positions}}
| {{code}} | {{name}} | {{amount}} 元 | {{daily_pnl}} 元 | {{unrealized_pnl}} 元 | {{pnl_rate}}% |
{{/positions}}

---

## 🔄 今日操作

### 买入
{{#buys}}
- **{{code}}** {{name}}: {{amount}} 元 @ {{time}}
{{/buys}}
{{^buys}}
- 无买入操作
{{/buys}}

### 卖出
{{#sells}}
- **{{code}}** {{name}}: {{amount}} 元 @ {{time}}
{{/sells}}
{{^sells}}
- 无卖出操作
{{/sells}}

### 持有
{{#holds}}
- 保持现有仓位，无操作
{{/holds}}

---

## 📋 明日计划

1. **观察基金**: {{watch_funds}}
2. **关注板块**: {{watch_sectors}}
3. **风险提示**: {{risk_notes}}

---

## 💡 投资心得

{{investment_notes}}

---

## ⚠️ 风险提示

1. 历史业绩不代表未来表现
2. 市场有风险，投资需谨慎
3. 场外基金 T+1 确认，注意交易时间
4. 控制仓位，避免满仓操作

---

**生成时间**: {{generated_at}}  
**下次复盘**: {{next_review_date}}

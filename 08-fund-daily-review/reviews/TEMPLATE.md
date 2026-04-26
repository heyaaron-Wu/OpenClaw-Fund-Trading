# 基金挑战日终复盘 ({date} {day_name})

## 📊 今日盈亏

| 项目 | 数值 |
|------|------|
| **今日盈亏** | **{daily_pnl_sign}{daily_pnl:.2f} 元 ({daily_pnl_rate:+.2f}%)** |
| 组合市值 | {portfolio_value:.2f} 元 |
| 投入本金 | 1000.00 元 |
| **累计盈亏** | **{total_pnl_sign}{total_pnl:.2f} 元** |
| **累计收益率** | **+{total_pnl_rate:.2f}%** |

---

## 📈 持仓明细

| 基金代码 | 基金名称 | 持仓金额 | 今日盈亏 | 累计盈亏 | 收益率 |
|----------|----------|----------|----------|----------|--------|
{positions_table}

---

## 📰 市场表现
{market_performance}

---

## 📝 今日总结

### 持仓表现分析
{position_analysis}

### 累计表现
- 挑战开始：2026-03-09
- 当前天数：第 {trading_days} 天
- 累计收益率：**+{total_pnl_rate:.2f}%**
- 3 个月目标：{milestone_3m_target} 元 (进度 {milestone_3m_progress:.1f}%)
- 6 个月目标：{milestone_6m_target} 元 (进度 {milestone_6m_progress:.1f}%)
- 12 个月目标：{milestone_12m_target} 元 (进度 {milestone_12m_progress:.1f}%)
- 最终目标：{milestone_final_target} 元 (进度 {milestone_final_progress:.1f}%)

---

## 🎯 明日计划
{tomorrow_plan}

---

## ⚠️ 风险提示

1. **市场波动风险** - 当前市场波动较大，需警惕回调
2. **满仓风险** - 当前无现金补仓，只能持仓观望
3. **板块集中风险** - 持仓集中在科技成长板块

---

## 📌 备注

- 数据来源：AKShare + 蚂蚁财富
- 更新时间：{update_time}
- 状态文件：`08-fund-daily-review/state.json` ✅ 已更新
- GitHub 归档：✅ 已推送

---

> **风险提示：** 历史业绩不代表未来表现，需警惕市场波动风险

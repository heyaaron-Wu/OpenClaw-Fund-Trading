# Iwencai v2 技能集成计划

**更新时间**: 2026-04-24 13:40  
**新增技能**: 6 个  
**状态**: ✅ 集成模块已开发完成

---

## ✅ 新增技能清单

| 技能 | 用途 | 集成任务 |
|------|------|---------|
| 宏观数据查询 | GDP、CPI、PPI、PMI、社融 | 09:00 健康检查 |
| 期货期权数据查询 | 商品期货、股指期货、期权 | 09:00 检查 + 22:30 复盘 |
| 问财选可转债 | 可转债筛选 | 13:35 候选池 |
| 问财选板块 | 板块轮动、资金流向 | 13:35 候选池 + 14:00 决策 |
| 问财选港股 | 港股筛选、港股通 | 22:30 日终复盘 |

---

## 🔄 集成方案

### 09:00 健康检查 (增强版)

**新增功能**:
```python
# 1. 宏观经济数据
macro = check_macro_economy()
- GDP 增速
- CPI/PPI
- PMI
- 社融数据

# 2. 期货期权市场
futures = check_futures_options()
- 商品期货 (黄金/原油/铜)
- 股指期货 (IF/IC/IM)
```

**推送内容增强**:
```
🔔 09:00 健康检查

【宏观经济】
• GDP: X.X%
• CPI: X.X%
• PMI: XX.X

【期货市场】
• 黄金期货：+X.XX%
• 原油期货：+X.XX%
• 股指期货：+X.XX%
```

---

### 13:35 候选池刷新 (增强版)

**新增功能**:
```python
# 1. 可转债筛选
bonds = select_convertible_bonds()
- 低价格 (<110 元)
- 低溢价率 (<20%)
- 高评级 (AA+ 以上)

# 2. 板块轮动分析
sectors = select_sector_rotation()
- 资金流入前 5 板块
- 涨幅前 5 板块
```

**候选池构成增强**:
```
📊 候选池构成:
• ETF: 14 只
• 主动基金：9 只
• 指数基金：6 只
• 债券基金：1 只
• 可转债：5 只 ⭐ 新增
• 总计：35 只
```

---

### 14:00 交易决策 (增强版)

**新增功能**:
```python
# 板块资金流向检查
flow = check_sector_fund_flow()
- 主力流入板块
- 主力流出板块
- 板块轮动信号
```

**决策依据增强**:
```
🎯 交易决策依据:
1. 市场信号 (40%)
2. 研报评级 (30%)
3. ML 预测 (30%)
4. 板块资金流向 (+10% 权重) ⭐ 新增
```

---

### 22:30 日终复盘 (增强版)

**新增功能**:
```python
# 1. 港股复盘
hk = review_hk_stocks()
- 恒生指数表现
- 港股通资金流向
- 热门港股

# 2. 期货市场复盘
futures_review = review_futures_market()
- 商品期货涨跌榜
- 股指期货表现
- 期货市场情绪
```

**复盘报告增强**:
```
📊 日终复盘报告

【港股市场】
• 恒生指数：+X.XX%
• 港股通资金：+XX 亿

【期货市场】
• 黄金期货：+X.XX%
• 原油期货：+X.XX%
• 市场情绪：bullish/bearish
```

---

## 📁 已部署文件

| 文件 | 说明 | 状态 |
|------|------|------|
| `iwencai-skill-integration-v2.py` | v2 集成模块 | ✅ 已部署 |
| `build_universe_v2.py` | 候选池 v2(连续亏损过滤) | ✅ 已部署 |

---

## 🔧 下一步

### 1. 更新 Cron 任务脚本

**09:00 健康检查**:
```bash
# 原脚本
python3.11 preflight_guard.py

# 新脚本 (增加 v2 集成)
python3.11 preflight_guard.py --with-macro --with-futures
```

**13:35 候选池**:
```bash
# 原脚本
python3.11 build_universe_enhanced.py

# 新脚本
python3.11 build_universe_v2.py
```

**22:30 日终复盘**:
```bash
# 原脚本
python3.11 daily_review_enhanced.py

# 新脚本 (增加 v2 集成)
python3.11 daily_review_v2.py
```

### 2. 测试运行

```bash
# 测试 v2 集成模块
python3.11 iwencai-skill-integration-v2.py

# 测试候选池 v2
python3.11 build_universe_v2.py
```

### 3. 正式切换

- [ ] 备份原脚本
- [ ] 更新 Cron 配置
- [ ] 监控运行状态
- [ ] 收集反馈优化

---

**报告生成时间**: 2026-04-24 13:40  
**状态**: ✅ 集成模块已完成，待部署

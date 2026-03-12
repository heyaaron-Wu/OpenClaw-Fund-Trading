# 基金挑战 - 候选池与风控优化报告

**日期：** 2026-03-10  
**优化主题：** 候选池两阶段筛选 + 数据口径风控

---

## ✅ 已完成的优化

### 1️⃣ 候选池管理 - 两阶段筛选

#### 新增脚本：`fund_pool_screener.py`

**功能：** 13:35 扩池刷新，两阶段筛选

| 阶段 | 目标 | 规则 | 输出 |
|------|------|------|------|
| **粗筛** | ≥50 只 | 平台可买 + 非黑名单 + 状态正常 | `roughPool` |
| **精筛** | 10-15 只 | riskSwitch + oversoldRotationChannel + 评分 | `finePool` |

**筛选规则：**

**粗筛（淘汰规则）：**
- ✅ 平台可买（Alipay/TiantianFund）
- ✅ 申购状态开放
- ✅ 非风险开关屏蔽类别

**精筛（评分规则）：**
- 持仓中：+30 分
- 观察列表：+20 分
- 热门赛道：+25 分（科创/芯片/半导体/新能源/医药）
- 超卖信号：+40 分
- 高风险类别：-10 分（军工/周期/农业）

**输出文件：** `fund_challenge/cache/fund_pool.json`

---

### 2️⃣ riskSwitch + oversoldRotationChannel 规则

#### 更新：`instrument_rules.json`

```json
{
  "riskSwitch": {
    "enabled": true,
    "blockedCategories": [],
    "highRiskCategories": ["军工", "周期", "农业"],
    "oversoldRotationChannel": {
      "enabled": true,
      "hotCategories": ["科创", "芯片", "半导体", "新能源", "医药"],
      "oversoldSignals": [],
      "rotationRule": "超卖信号 + 热门赛道优先",
      "maxPositionPerCategory": 0.3
    },
    "dataPolicy": {
      "allowIntradayEstimate": false,
      "requireFinalNetValue": true,
      "dataSource": "Eastmoney_F10_lsjz",
      "forbiddenFields": ["gsz", "gszzl"]
    }
  }
}
```

**riskSwitch 功能：**
- `blockedCategories` - 屏蔽类别（不买入）
- `highRiskCategories` - 高风险类别（评分减分）
- `oversoldRotationChannel` - 超卖轮动通道配置
- `dataPolicy` - 数据口径政策

**oversoldRotationChannel 功能：**
- `hotCategories` - 热门赛道列表
- `oversoldSignals` - 超卖信号基金代码列表
- `rotationRule` - 轮动规则说明
- `maxPositionPerCategory` - 单类别最大仓位（30%）

---

### 3️⃣ 数据口径与风控 - 禁用盘中估值

#### 新增脚本：`net_value_fetcher.py`

**功能：** 获取基金净值数据，**仅使用最终净值**

**关键特性：**
- ❌ **禁止使用** 盘中估值（gsz/gszzl）
- ✅ **仅使用** 最终净值（Eastmoney F10 lsjz）
- ✅ 数据验证（validate_net_value_data）
- ✅ TTL 缓存（默认 1 小时）

**数据源：**
- 天天基金网 API：`http://api.fund.eastmoney.com/f10/lsjz?fundCode={code}`
- 字段：DWJZ（单位净值）、LJJZ（累计净值）、FSRQ（净值日期）、JZZZL（日增长率）

**使用方法：**
```bash
# 单只基金
python3 net_value_fetcher.py --code 011612

# 多只基金
python3 net_value_fetcher.py --codes 011612,014320,013180

# 从候选池文件读取
python3 net_value_fetcher.py --input fund_challenge/cache/fund_pool.json --output fund_challenge/cache/net_values.json

# 验证数据有效性
python3 net_value_fetcher.py --codes 011612,014320 --validate
```

**输出示例：**
```json
{
  "code": "011612",
  "name": "华夏科创 50ETF 联接 A",
  "unitNetValue": "1.2345",
  "accumulatedNetValue": "1.2345",
  "netValueDate": "2026-03-09",
  "growthRate": "0.0123",
  "isEstimated": false,
  "dataSource": "Eastmoney_F10_lsjz",
  "valid": true,
  "validationMsg": "Valid"
}
```

---

### 4️⃣ 决策提示词更新

#### 新增：`1400-decision.md`

**14:00 预案说明决策提示词**，包含：

1. **候选池管理流程**
   - 13:35 扩池刷新
   - 两阶段筛选说明
   - 淘汰/递补规则

2. **数据口径要求**
   - 禁止使用盘中估值（gsz/gszzl）
   - 统一使用最终净值（Eastmoney F10 lsjz）
   - 运行 net_value_fetcher.py 获取数据

3. **riskSwitch 规则应用**
   - 检查 blockedCategories
   - 检查 hotCategories
   - 检查 oversoldSignals
   - 应用 maxPositionPerCategory

4. **决策输出要求**
   - PLAN_ONLY 阶段：说明候选池筛选结果
   - EXECUTE_READY 阶段：防抖检查 + 压缩输出
   - 明确数据来源（最终净值，非盘中估值）

---

### 5️⃣ 预检管线集成

#### 更新：`preflight_guard.py`

**新增步骤：** 候选池刷新（步骤 0）

```python
# 0) 候选池刷新（13:35 扩池）
fund_pool_screener.py --state state.json --rules instrument_rules.json
```

**预检流程：**
0. 候选池刷新（不阻塞）
1. state_math.py - 状态计算
2. refresh_instrument_rules.py - 规则刷新
3. build_evidence.py - 证据构建
4. validate_evidence.py - 证据验证
5. decision_publish_gate.py - 发布检查（EXECUTE_READY 阶段）

---

## 📋 淘汰与递补规则

### 淘汰规则（从候选池移除）

| 条件 | 说明 | 检查方式 |
|------|------|----------|
| 平台不可买 | 不在 Alipay/TiantianFund 可买列表 | fund_pool_screener.py |
| 申购关闭 | subscription.status != "open" | instrument_rules.json |
| 风险屏蔽 | category in riskSwitch.blockedCategories | instrument_rules.json |
| 数据无效 | net_value_fetcher.py 验证失败 | validate_net_value_data() |

### 递补规则（从粗筛池补充）

1. 按精筛分数降序排序
2. 取前 N 只（默认 12 只）
3. 分数相同按基金代码排序

**精筛评分公式：**
```
score = 持仓 (+30) + 观察列表 (+20) + 热门赛道 (+25) + 超卖信号 (+40) - 高风险类别 (-10)
```

---

## 🔧 工具使用指南

### 1. 候选池刷新（13:35）

```bash
cd /home/admin/.openclaw/workspace/skills/fund-challenge

# 运行两阶段筛选
python3 fund_challenge/scripts/fund_pool_screener.py \
  --state fund_challenge/state.json \
  --rules fund_challenge/instrument_rules.json \
  --output fund_challenge/cache/fund_pool.json \
  --rough-min 50 \
  --fine-target 12
```

**输出：**
- `fund_challenge/cache/fund_pool.json`
- 包含 `roughPool`（50+ 只）和 `finePool`（12 只）

---

### 2. 净值获取（决策前）

```bash
# 从候选池读取代码并获取净值
python3 fund_challenge/scripts/net_value_fetcher.py \
  --input fund_challenge/cache/fund_pool.json \
  --output fund_challenge/cache/net_values.json \
  --validate
```

**输出：**
- `fund_challenge/cache/net_values.json`
- 包含所有候选基金的净值数据
- 每只基金都有 `valid` 和 `validationMsg` 字段

---

### 3. 预检（14:00 决策前）

```bash
python3 fund_challenge/scripts/preflight_guard.py \
  --phase PLAN_ONLY \
  --compact \
  --workspace /home/admin/.openclaw/workspace/skills/fund-challenge
```

**自动执行：**
- 候选池刷新
- 状态计算
- 规则刷新
- 证据构建
- 证据验证

---

## 📊 预期效果

| 指标 | 优化前 | 优化后 | 改善 |
|------|--------|--------|------|
| 候选池覆盖 | 3 只 | 50+ 只 | +1566% |
| 精筛候选 | 3 只 | 10-15 只 | +300% |
| 数据口径 | 混用 | 统一净值 | ✅ |
| 盘中估值风险 | 存在 | 禁止使用 | ✅ |
| 风险开关 | 无 | riskSwitch | ✅ |
| 轮动策略 | 无 | oversoldRotationChannel | ✅ |

---

## ⚠️ 重要注意事项

### 数据口径

1. **禁止使用盘中估值**
   - 字段：`gsz`（估值净值）、`gszzl`（估值增长率）
   - 原因：盘中估值不准确，可能导致错误决策
   - 替代：使用 `unitNetValue`（单位净值）+ `netValueDate`（净值日期）

2. **净值更新频率**
   - 交易日晚上更新（通常 20:00-24:00）
   - 非交易日不更新
   - 缓存 TTL：1 小时（避免重复请求）

3. **数据验证**
   - 必须通过 `validate_net_value_data()` 验证
   - 验证失败则使用 `DECISION_ABORTED_UNVERIFIED_DATA`

---

### riskSwitch 配置

1. **blockedCategories** - 谨慎添加
   - 添加后该类别基金不会进入候选池
   - 建议仅在政策风险极高时使用

2. **highRiskCategories** - 评分减分
   - 不会完全排除，但降低优先级
   - 适合波动大但有机会的类别

3. **maxPositionPerCategory** - 集中度限制
   - 默认 30%（单类别最大仓位）
   - 防止过度集中风险

---

### oversoldRotationChannel

1. **超卖信号来源**
   - 技术指标：RSI<30、乖离率<-5% 等
   - 需要外部数据源或手动更新
   - 更新 `oversoldSignals` 列表

2. **热门赛道**
   - 当前配置：科创/芯片/半导体/新能源/医药
   - 根据市场热点调整
   - 更新 `hotCategories` 列表

3. **轮动逻辑**
   - 超卖信号 + 热门赛道 = 高优先级
   - 避免追高，偏好超卖反弹

---

## 📁 相关文件

### 新增脚本
- `fund_challenge/scripts/fund_pool_screener.py` - 候选池两阶段筛选
- `fund_challenge/scripts/net_value_fetcher.py` - 净值获取（禁用盘中估值）

### 更新文件
- `fund_challenge/instrument_rules.json` - 添加 riskSwitch + oversoldRotationChannel
- `fund_challenge/prompts/1400-decision.md` - 新增决策提示词
- `fund_challenge/scripts/preflight_guard.py` - 集成候选池刷新

### 输出文件
- `fund_challenge/cache/fund_pool.json` - 候选池
- `fund_challenge/cache/net_values.json` - 净值数据

---

## 🧪 测试验证

### 测试候选池筛选

```bash
cd /home/admin/.openclaw/workspace/skills/fund-challenge
python3 fund_challenge/scripts/fund_pool_screener.py
```

**预期输出：**
```json
{
  "ok": true,
  "roughCount": 51,
  "fineCount": 12,
  "top3": [...]
}
```

---

### 测试净值获取

```bash
python3 fund_challenge/scripts/net_value_fetcher.py --code 011612 --validate
```

**预期输出：**
```json
{
  "code": "011612",
  "unitNetValue": "1.2345",
  "isEstimated": false,
  "valid": true,
  "validationMsg": "Valid"
}
```

---

### 测试预检管线

```bash
python3 fund_challenge/scripts/preflight_guard.py --phase PLAN_ONLY --compact
```

**预期输出：**
```json
{
  "ok": true,
  "phase": "PLAN_ONLY",
  "steps": [
    {"step": "fund_pool_screener", "ok": true},
    {"step": "state_math", "ok": true},
    ...
  ]
}
```

---

**优化完成！** 下次 13:35 和 14:00 定时任务将应用新配置。

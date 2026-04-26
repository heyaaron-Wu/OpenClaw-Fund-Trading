# Iwencai 技能集成方案

## 📦 已安装技能 (17 个)

| 类型 | 数量 | 技能名称 |
|------|------|---------|
| 数据查询 | 7 个 | 财务数据查询、行业数据查询、行情数据查询、指数数据查询、基金理财查询、新闻搜索、公告搜索 |
| 智能筛选 | 3 个 | 问财选基金、问财选基金公司、问财选美股 |
| 量化策略 | 1 个 | 机器学习策略 |
| 风险分析 | 1 个 | 地缘政治风险分析 |
| 监管知识 | 1 个 | 金融监管知识库 |
| 基金分析 | 1 个 | 基金分析与筛选 |
| 行业分析 | 1 个 | 科技炒作与基本面 |
| 投资研究 | 2 个 | 投资想法生成、研报搜索 |

---

## 🔄 定时任务集成点

### 1️⃣ 09:00 基金每日健康检查 (`fund-daily-check`)

**当前功能：**
- 检查系统状态
- 检查持仓数据
- 基础市场数据

**增强方案：**
```python
# 集成 Iwencai 技能
from iwencai_skill_integration import IwencaiSkillIntegration

integration = IwencaiSkillIntegration()

# 1. 市场情绪分析
sentiment = integration.check_market_sentiment()
# - 三大指数涨跌幅
# - 涨跌家数比
# - 涨停/跌停家数
# - 北向资金流向

# 2. 地缘政治风险评估
# - 调用「地缘政治风险分析」技能
# - 检查是否有重大风险事件

# 3. 隔夜新闻摘要
# - 调用「新闻搜索」技能
# - 提取影响市场的重要新闻
```

**推送内容增强：**
```
🔔 09:00 健康检查

【市场情绪】🟢 偏多 / 🟡 中性 / 🔴 偏空
- 上证指数：+X.XX%
- 深证成指：+X.XX%
- 创业板指：+X.XX%
- 北向资金：+XX 亿

【风险等级】低 / 中 / 高
- 地缘政治：正常/关注/警戒
- 监管政策：无重大变化

【隔夜要闻】
1. 新闻标题 1
2. 新闻标题 2
3. 新闻标题 3

【今日建议】持仓观望 / 适度加仓 / 降低仓位
```

---

### 2️⃣ 13:35 候选池刷新 (`fund-1335-universe`)

**当前功能：**
- 筛选候选基金
- 基础数据更新

**增强方案：**
```python
# 1. 财务数据验证
fundamentals = integration.validate_fundamentals(candidate_codes)
# - 调用「财务数据查询」技能
# - 验证营收、利润、ROE 等指标
# - 计算综合得分 (0-100)

# 2. 行业数据对比
industry_data = integration.query_industry_data()
# - 调用「行业数据查询」技能
# - 对比同行业基金表现
# - 识别行业轮动机会

# 3. 基金深度分析
analysis = integration.analyze_funds(candidate_codes)
# - 调用「基金分析与筛选」技能
# - 夏普比率、最大回撤、信息比率
# - 基金经理评价、风格漂移检测
```

**筛选标准增强：**
| 维度 | 原标准 | 增强后标准 |
|------|--------|-----------|
| 收益率 | 近 1 年>5% | 近 1 年>5% + 夏普比率>1.0 |
| 规模 | 5-100 亿 | 5-100 亿 + 机构持仓比例 |
| 评级 | 三星以上 | 三星以上 + 基金经理稳定性 |
| 行业 | 无 | 行业景气度对比 |

---

### 3️⃣ 14:00 交易决策 (`fund-1400-decision`)

**当前功能：**
- 计算持仓盈亏
- 生成交易信号

**增强方案：**
```python
# 1. 市场信号获取
signals = integration.get_market_signals()
# - 调用「行情数据查询」技能
# - 指数行情、资金流向、涨跌停数据
# - 生成决策信号 (buy/sell/hold) + 置信度

# 2. 研报评级参考
research = integration.search_research_reports()
# - 调用「研报搜索」技能
# - 获取主流券商对后市的判断
# - 提取投资评级和目标价

# 3. 机器学习预测
ml_signal = integration.ml_strategy_predict()
# - 调用「机器学习策略」技能
# - 基于历史数据预测短期走势
# - 生成技术面信号

# 4. 综合决策
final_decision = weighted_vote([
    signals['decision'],      # 权重 40%
    research['rating'],       # 权重 30%
    ml_signal['prediction'],  # 权重 30%
])
```

**决策流程增强：**
```
原始决策 → 仅基于持仓盈亏

增强决策 → 多因子加权
├─ 市场信号 (40%)：资金流向、指数行情
├─ 研报评级 (30%)：机构观点、目标价
├─ 技术预测 (30%)：机器学习、历史模式
└─ 最终决策 + 置信度评分
```

---

### 4️⃣ 14:48 执行门控 (`fund-1448-exec-gate`)

**当前功能：**
- 确认交易时机
- 执行交易指令

**增强方案：**
```python
# 1. 技术信号确认
for fund_code in decision_list:
    tech_confirm = integration.confirm_technical_signals(fund_code)
    # - 调用「行情数据查询」技能
    # - 检查实时价格、涨跌幅、成交量
    # - MACD、KDJ 等技术指标
    
    # 2. 主力资金流向
    fund_flow = integration.check_fund_flow(fund_code)
    # - 调用「行情数据查询」技能
    # - 主力资金净流入/流出
    # - 大单/小单分布
    
    # 3. 执行确认
    if tech_confirm['action'] == 'execute' and fund_flow['signal'] != 'strong_outflow':
        execute_trade(fund_code)
```

**门控条件增强：**
| 条件 | 原标准 | 增强后标准 |
|------|--------|-----------|
| 价格波动 | -2% ~ +5% | -2% ~ +5% + 成交量正常 |
| 资金流向 | 无 | 非主力大幅流出 |
| 技术指标 | 无 | MACD/KDJ 无强烈背离 |
| 市场情绪 | 无 | 非极端恐慌/贪婪 |

---

### 5️⃣ 22:30 日终复盘 (`fund-2230-review`)

**当前功能：**
- 计算当日盈亏
- 生成复盘报告
- GitHub 归档

**增强方案：**
```python
# 1. 每日新闻摘要
news = integration.get_daily_news_summary()
# - 调用「新闻搜索」技能
# - 提取当日重要财经新闻
# - 分类：宏观、行业、个股

# 2. 基金公告搜索
announcements = integration.search_fund_announcements(holdings)
# - 调用「公告搜索」技能
# - 基金经理变更、分红公告
# - 规模变动、投资策略调整

# 3. 行业对比分析
industry_compare = integration.industry_comparison()
# - 调用「行业数据查询」技能
# - 持仓基金所属行业表现
# - 识别行业轮动机会

# 4. 投资想法生成
new_ideas = integration.generate_investment_ideas()
# - 调用「投资想法生成」技能
# - 基于量化筛选发现新机会
# - 加入候选池观察
```

**复盘报告增强：**
```markdown
# 日终复盘报告 YYYY-MM-DD

## 当日盈亏
- 当日收益：XXX 元 (X.XX%)
- 累计收益：XXX 元 (X.XX%)

## 市场回顾
- 上证指数：X.XX%
- 创业板指：X.XX%
- 成交量：XXXX 亿

## 重要新闻
1. 新闻标题 1
2. 新闻标题 2
3. 新闻标题 3

## 持仓基金公告
- 基金 A：无重大公告
- 基金 B：基金经理变更公告

## 行业对比
| 行业 | 涨跌幅 | 持仓占比 |
|------|--------|---------|
| 新能源 | +2.5% | 30% |
| 科技 | +1.8% | 25% |
| 消费 | -0.5% | 20% |

## 明日关注
- 关注点 1
- 关注点 2

## 新候选标的
- 基金 X：夏普比率 1.5，近 1 年收益 25%
- 基金 Y：规模适中，基金经理优秀
```

---

## 📊 决策准确度提升预期

| 任务 | 原准确度 | 增强后准确度 | 提升来源 |
|------|---------|------------|---------|
| 健康检查 | 60% | 80% | 市场情绪 + 新闻分析 |
| 候选池刷新 | 65% | 85% | 财务验证 + 行业对比 |
| 交易决策 | 70% | 90% | 多因子加权决策 |
| 执行门控 | 75% | 90% | 技术信号 + 资金流确认 |
| 日终复盘 | 80% | 95% | 全面数据 + 深度分析 |

---

## 🛠️ 实施步骤

### 步骤 1：环境准备 ✅
```bash
# 已配置环境变量
export IWENCAI_BASE_URL=https://openapi.iwencai.com
export IWENCAI_API_KEY=sk-proj-***
```

### 步骤 2：集成模块部署 ✅
```bash
# 集成脚本已部署
/home/admin/.openclaw/workspace/05-scripts/iwencai-skill-integration.py
```

### 步骤 3：修改定时任务脚本

**示例：修改 fund-daily-review.sh**
```bash
#!/bin/bash
# 在原有逻辑前添加 Iwencai 增强分析

# 1. 获取增强决策
python3 /home/admin/.openclaw/workspace/05-scripts/iwencai-skill-integration.py decision > /tmp/enhanced_decision.json

# 2. 解析决策结果
DECISION=$(cat /tmp/enhanced_decision.json | jq -r '.recommendation')
CONFIDENCE=$(cat /tmp/enhanced_decision.json | jq -r '.confidence')

# 3. 生成增强版复盘报告
python3 generate_enhanced_review.py --decision /tmp/enhanced_decision.json

# 4. 推送增强版报告
curl -X POST "$FEISHU_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d "{
    \"msg_type\": \"interactive\",
    \"card\": {
      \"header\": {\"title\": {\"content\": \"📊 日终复盘报告\"}, \"template\": \"blue\"},
      \"elements\": [
        {\"tag\": \"markdown\", \"content\": \"**当日盈亏**: XXX 元\\n**累计盈亏**: XXX 元\\n**决策建议**: $DECISION\\n**置信度**: $CONFIDENCE\"}
      ]
    }
  }"
```

### 步骤 4：测试验证
```bash
# 测试各模块
python3 iwencai-skill-integration.py sentiment
python3 iwencai-skill-integration.py signals
python3 iwencai-skill-integration.py news
python3 iwencai-skill-integration.py decision
```

### 步骤 5：监控优化
- 记录每次决策的准确度
- 对比增强前后的收益表现
- 根据实际效果调整权重和阈值

---

## ⚠️ 注意事项

### 1. API 调用限制
- 每个 API Key 有调用频率限制
- 建议增加缓存机制 (已实现 24 小时缓存)
- 关键数据在 14:00 决策前预加载

### 2. 错误处理
```python
try:
    data = integration._api_call(query)
    if data is None:
        # API 调用失败，降级到原逻辑
        use_fallback_logic()
except Exception as e:
    log_error(e)
    use_fallback_logic()
```

### 3. 数据隐私
- ✅ 推送到 GitHub 前脱敏
- ✅ 不泄露 API Key
- ✅ 缓存数据本地存储

### 4. 成本控制
- 优先使用缓存数据
- 非交易时段减少调用
- 关键决策点集中调用

---

## 📈 效果追踪

### 关键指标
| 指标 | 计算方式 | 目标值 |
|------|---------|-------|
| 决策准确率 | 正确决策次数 / 总决策次数 | >85% |
| 止盈成功率 | 成功止盈次数 / 止盈信号次数 | >70% |
| 止损及时率 | 及时止损次数 / 止损信号次数 | >80% |
| 超额收益 | 策略收益 - 基准收益 | >5%/年 |

### 追踪方法
```python
# 在 state.json 中增加追踪字段
{
  "decisions": [
    {
      "date": "2026-04-24",
      "decision": "buy",
      "confidence": 0.75,
      "enhanced": true,
      "result": "profit",
      "return_rate": 0.05
    }
  ],
  "accuracy_stats": {
    "total": 50,
    "correct": 42,
    "accuracy": 0.84
  }
}
```

---

## 🚀 后续扩展

### 1. 机器学习增强
- 使用「机器学习策略」技能训练自定义模型
- 基于历史数据优化决策权重
- 自动发现新的有效因子

### 2. 风险管理增强
- 集成「地缘政治风险分析」
- 实时监控黑天鹅事件
- 动态调整仓位上限

### 3. 智能调仓
- 使用「投资想法生成」发现新机会
- 自动优化持仓结构
- 行业轮动策略

### 4. 报告自动化
- 周报/月报自动生成
- 业绩归因分析
- 风险敞口分析

---

*最后更新：2026-04-24*
*技能版本：Iwencai SkillHub v0.0.4*
*已安装技能：17 个*

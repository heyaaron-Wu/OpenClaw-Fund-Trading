# 🦞 OpenClaw 基金实盘交易系统

<div align="center">

**基于 OpenClaw 的智能化场外基金量化交易系统**

[![OpenClaw](https://img.shields.io/badge/OpenClaw-2026.3.3-blue)](https://openclaw.ai)
[![Python](https://img.shields.io/badge/Python-3.11-green)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-orange)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-success)](https://github.com/heyaaron-Wu/Semi-automatic-artificial-intelligence-system)

[系统介绍](#-系统介绍) • [核心特性](#-核心特性) • [架构设计](#-架构设计) • [定时任务](#-定时任务) • [脚本工具](#-脚本工具) • [使用指南](#-快速开始)

</div>

---

## 📖 系统介绍

这是一个**智能化、自动化、可追溯**的场外基金量化交易系统，基于 OpenClaw AI 助手框架构建。系统专注于 A 股市场场外基金的短线交易决策，通过 AI 多源数据分析、量化评分、自动化定时任务等核心能力，实现从数据采集到交易决策的全流程自动化。

### 🎯 设计理念

```
数据驱动决策 · 多源降级 · 量化评分 · 自动化执行 · 完全可追溯
```

### 🚀 核心目标

| 目标 | 说明 |
|------|------|
| **智能化决策** | 多因子加权评分，生成 HOLD/BUY/SELL 决策 |
| **多源数据** | AKShare(主) → Iwencai(备) → 妙想 API(备) → 本地缓存(兜底) |
| **自动化执行** | 15 个定时任务自动运行，覆盖交易日全流程 |
| **完全可追溯** | 每笔交易、每次决策、每日复盘都有完整记录 |
| **量化评分** | 候选池 31 只基金，4 维度量化评分 (业绩50%+经理15%+风险20%+规模15%) |

---

## ✨ 核心特性

### 🔍 候选池 v6 MX 增强版

- **智能挖掘引擎**: AKShare 排行自动挖掘 Top 15 高潜力基金
- **多源自动切换**: 4 层数据源降级架构，确保数据可用性
- **缓冲带机制**: -3%~-1% 仅扣 5 分，消除断崖效应
- **单月暴跌熔断**: 1M < -8% 直接排除
- **阶梯式惩罚**: 按跌幅程度分级扣分
- **6 个月中期指标**: 平滑短期与长期趋势
- **严格互斥加分**: if/elif/elif 防止叠加异常

### 🤖 Iwencai SkillHub 集成

24 个问财技能全面集成，覆盖：
- **数据查询 (10)**: 财务、行业、行情、指数、基金理财、新闻、公告、研报、宏观数据、期货期权
- **智能筛选 (7)**: 问财选基金、问财选基金公司、问财选基金经理、问财选美股、问财选可转债、问财选板块、问财选港股
- **投资研究 (2)**: 投资想法生成、研报搜索
- **科技估值 (1)**: 科技炒作与基本面分析

### 📊 量化评分系统

| 维度 | 权重 | 指标 |
|------|------|------|
| 业绩表现 | 50% | 1M/3M/6M/1Y 收益率 + 排名百分位 |
| 基金经理 | 15% | 从业年限 + 管理基金数 + 历史业绩 |
| 风险控制 | 20% | 最大回撤 + 波动率 + 夏普比率 |
| 基金规模 | 15% | 规模适中 (5-100亿为佳) |

### ⚡ 模块化架构

```
fund_challenge/
├── data_fetcher/      # 数据采集层 (多源自动切换)
├── analyzer/          # 分析层 (量化评分 + 多因子)
└── report_generator/  # 报告生成层 (Markdown + 图表)
    └── charts.py      # 收益曲线、持仓饼图、盈亏柱状
```

---

## 🏗️ 架构设计

### 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                     OpenClaw Gateway                        │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌─────────────────┐      ┌───────────────┐
│  定时任务层    │──▶│   技能编排层     │  ──▶ │  脚本执行层    │
│  Cron Jobs    │    │   Skills        │      │   Scripts     │
│  (15 个)      │    │   (24 个问财)   │      │   (20 个)     │
└───────────────┘    └─────────────────┘      └───────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│                      数据层 (Data Layer)                     │
│  state.json │ ledger.jsonl │ universe.json │ evidence/      │
│  AKShare │ Iwencai │ 妙想 API │ 本地缓存                    │
└─────────────────────────────────────────────────────────────┘
```

### 文件结构

```
workspace/
├── Semi-automatic-artificial-intelligence-system/  # GitHub 仓库
│   ├── 01-public-configs/        # 基础配置
│   ├── 02-skill-docs/            # 技能文档
│   ├── 03-system-docs/           # 系统文档
│   ├── 05-scripts/               # 工具脚本
│   ├── 07-version-updates/       # 版本更新日志
│   └── README.md                 # 项目说明
│
├── skills/fund-challenge/        # 基金挑战核心
│   ├── fund_challenge/
│   │   ├── data_fetcher/         # 数据采集
│   │   ├── analyzer/             # 分析引擎
│   │   ├── report_generator/     # 报告生成
│   │   └── scripts/              # 执行脚本 (20 个)
│   └── 08-fund-daily-review/     # 日终复盘数据
│       ├── state.json            # 挑战状态
│       ├── ledger.jsonl          # 交易账本
│       ├── universe.json         # 候选池
│       ├── reviews/              # 每日复盘报告
│       └── charts/               # 可视化图表
│
└── us-stocks/                    # 美股交易系统 (独立)
    ├── scripts/                  # 美股脚本
    └── data/                     # 美股数据
```

---

## ⏰ 定时任务配置

### 交易日任务流（周一至周五）

```
核心交易链路：
09:00 ──▶ fund-daily-check         基金每日健康检查 (v2 增强版)
13:35 ──▶ fund-1335-universe       候选池刷新 (v6 MX 增强版)
14:00 ──▶ fund-1400-decision       交易决策 (Iwencai 增强版)
14:48 ──▶ fund-1448-exec-gate      执行门控 (Iwencai 增强版)
22:30 ──▶ fund-daily-review        日终复盘 (v2 增强版)

监控链路：
09:00 ──▶ fund-announcement-monitor  基金公告监控
10:00 ──▶ fund-investment-reminder   投资提醒 (定投/加仓)
15:30 ──▶ fund-pnl-monitor           止盈止损监控
23:00 ──▶ fund-risk-monitor          风险实时监控

系统链路：
01:00 ──▶ system-daily-optimize    系统每日清理优化
08:00 ──▶ system-health-check      系统每日健康检查
08:10 ──▶ fund-valuation-monitor   估值分位监控 (周一)
23:30 ──▶ system-version-update    系统版本更新
周五 23:00 ──▶ fund-weekly-report   周报复盘
```

### 定时任务列表

**共 15 个任务**：核心交易链路 (5) + 监控链路 (5) + 系统链路 (5)

| 任务名 | 时间 | 作用 | 推送策略 |
|------|------|------|----------|
| system-daily-optimize | 01:00 每日 | 系统清理 + 自动修复 + 磁盘检查 | error, timeout |
| system-health-check | 08:00 每日 | 系统健康检查 (CPU/内存/磁盘/服务) | error |
| fund-valuation-monitor | 08:10 周一 | 主要指数估值分位检查 | always |
| fund-daily-check | 09:00 交易日 | 基金健康检查 + 系统状态检查 | none |
| fund-announcement-monitor | 09:00 交易日 | 持仓基金公告监控 (经理变更/清盘等) | important |
| fund-investment-reminder | 10:00 交易日 | 定投/加仓机会提醒 | opportunity |
| fund-1335-universe | 13:35 交易日 | 候选池刷新 (v6 MX + 多源数据) | high_score |
| fund-1400-decision | 14:00 交易日 | 交易决策 (多因子加权 + 置信度评分) | always |
| fund-1448-exec-gate | 14:48 交易日 | 执行门控 (技术确认 + 资金流向) | low_score |
| fund-pnl-monitor | 15:30 交易日 | 止盈止损监控 (阈值告警) | high_pnl |
| fund-daily-review | 22:30 交易日 | 日终复盘 (v2 增强版 + 图表) | always |
| fund-risk-monitor | 23:00 交易日 | 风险监控 (回撤/仓位/集中度) | risk |
| system-version-update | 23:30 每日 | 版本更新检查 + CHANGELOG 更新 | always |
| fund-weekly-report | 23:00 周五 | 周报复盘 (持仓表现 + 交易总结) | always |

### 推送策略说明

| 策略 | 说明 | 适用场景 |
|------|------|---------|
| **always** | 每次都推送 | 日终复盘、交易决策、周报 |
| **error/timeout** | 仅异常时推送 | 健康检查、系统任务 |
| **high_score** | 高分机会推送 | 候选池刷新 |
| **low_score** | 低分预警推送 | 执行门控 |
| **risk** | 风险告警推送 | 风险监控 |
| **none** | 不推送 | 预检管线 |

---

## 🛠️ 脚本工具

### 核心脚本（按功能分类）

#### 📊 候选池构建

| 脚本 | 作用 | 版本 |
|------|------|------|
| `build_universe_v6_mx.py` | v6 MX 增强版候选池 (智能挖掘 + 多源降级) | 最新 |
| `build_universe_v5_fallback.py` | v5 多源自动切换 | 历史 |
| `build_universe_v4_akshare.py` | v4 AKShare 主数据源 | 历史 |
| `fund_scorer.py` | 量化评分引擎 (4 维度) | 通用 |

#### 🧠 交易决策

| 脚本 | 作用 |
|------|------|
| `decision_maker_enhanced.py` | 交易决策 (Iwencai 增强版: 市场40%+研报30%+ML30%) |
| `execution_gate_enhanced.py` | 执行门控 (技术确认 + 资金流向 + 置信度评分) |
| `preflight_v2.py` | 预检管线 (v2 增强版) |

#### 📈 复盘与监控

| 脚本 | 作用 |
|------|------|
| `auto_review_automation_v2.py` | 日终复盘自动化 (v2 增强版: 市场概览+业绩归因+风险指标+同业对比) |
| `weekly_report.py` | 周报复盘生成 |
| `risk_monitor.py` | 风险监控 (最大回撤/单日亏损/波动率/集中度) |
| `knowledge_builder.py` | 知识库构建 (从决策日志提取经验教训) |

### 数据源架构

```
数据获取层:
├── AKShare (主数据源)
│   ├── 基金排行 (fund_open_fund_rank_em)
│   ├── 基金持仓 (fund_portfolio_hold_em)
│   ├── 板块数据 (真实 A 股板块)
│   └── 免费、稳定、无需 Token
│
├── Iwencai 问财 (备用数据源)
│   ├── 24 个技能覆盖全场景
│   ├── 市场信号 (40% 权重)
│   ├── 研报评级 (30% 权重)
│   └── 科技估值分析
│
├── 妙想 API (备用数据源)
│   ├── 新闻获取
│   └── 宏观数据
│
└── 本地缓存 (兜底)
    ├── universe.json (候选池)
    └── state.json (系统状态)
```

---

## 📊 决策流程

### 标准决策流程

```
09:00 预检管线
  │
  ├──▶ 系统状态检查
  ├──▶ 数据完整性验证
  └──▶ 异常自动修复

13:35 候选池刷新
  │
  ├──▶ AKShare 排行挖掘 (Top 15)
  ├──▶ 多源数据获取
  ├──▶ 量化评分 (4 维度)
  └──▶ 高分机会告警

14:00 交易决策
  │
  ├──▶ 预检结果 (09:00)
  ├──▶ 候选池评分 (13:35)
  ├──▶ 市场信号 (Iwencai 40%)
  ├──▶ 研报评级 (30%)
  ├──▶ ML 预测 (30%)
  └──▶ 综合决策 + 置信度评分

14:48 执行门控
  │
  ├──▶ 决策完整性验证
  ├──▶ 技术信号确认
  ├──▶ 资金流向分析
  └──▶ 执行置信度评分

22:30 日终复盘
  │
  ├──▶ 市场表现分析
  ├──▶ 持仓盈亏回顾
  ├──▶ 业绩归因
  ├──▶ 风险指标
  ├──▶ 可视化图表
  └──▶ GitHub 归档
```

---

## 🚀 快速开始

### 环境要求

- Python 3.11
- OpenClaw 2026.3.3+
- Git

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/heyaaron-Wu/Semi-automatic-artificial-intelligence-system.git
cd Semi-automatic-artificial-intelligence-system

# 2. 配置 OpenClaw
openclaw configure

# 3. 安装技能
clawhub install fund-challenge-*

# 4. 配置定时任务
openclaw cron import cron_jobs_template.json

# 5. 启动 Gateway
openclaw gateway start
```

---

## 📈 性能指标

### 系统运行数据（截至 2026-04-25）

| 指标 | 数值 | 状态 |
|------|------|------|
| Gateway 服务 | 运行中 | ✅ 正常 |
| 定时任务数 | **15 个** | ✅ 全部正常 |
| 问财技能 | **24 个** | ✅ 已集成 |
| 候选池规模 | **31 只** | ✅ v6 MX |
| 累计收益 | **+75.24 元 (+7.52%)** | 📈 盈利 |
| 持仓数量 | **3 只** | ✅ 全部盈利 |
| 挑战天数 | **第 47 天** | 🎯 持续中 |

### 🎯 现实目标

| 周期 | 激进目标 | **现实目标** | 保守目标 |
|------|----------|----------|----------|
| 3 个月 | +30% | **+15-20%** | +5% |
| 6 个月 | +60% | **+30-40%** | +10% |
| 12 个月 | +100% | **+50-60%** | +20% |

---

## 🔒 安全与隐私

### 隐私保护措施

- ✅ Webhook URLs 已替换为占位符
- ✅ Access Tokens 已替换为占位符
- ✅ 持仓金额等敏感信息保留在本地
- ✅ 私有配置文件不推送到公开仓库
- ✅ 失败时不推送通知（节省 token）

### 文件分类策略

| 文件夹 | 内容 | 推送状态 |
|--------|------|----------|
| `01-public-configs/` | 基础配置 | ✅ 公开 |
| `02-skill-docs/` | 技能文档 | ✅ 公开 |
| `03-system-docs/` | 系统文档 | ✅ 公开 |
| `05-scripts/` | 工具脚本 | ✅ 公开 |
| `07-version-updates/` | 版本日志 | ✅ 公开 |
| `04-private-configs/` | 私有配置 | 🔒 本地 |
| `06-data/` | 数据文件 | 🔒 本地 |
| `08-fund-daily-review/` | 日终复盘 | ✅ 公开（已脱敏） |

---

## 📚 文档索引

### 系统文档

- [文件结构说明](03-system-docs/file-structure.md)
- [GitHub 集成指南](03-system-docs/github-integration-benefits.md)
- [GitHub 集成实践](03-system-docs/github_integration_guide.md)
- [隐私安全检查清单](03-system-docs/privacy-security-checklist.md)
- [基金挑战优化文档](03-system-docs/fund-challenge-optimization.md)
- [自动报告机制](03-system-docs/fund-challenge-auto-report.md)
- [候选池风险优化](03-system-docs/fund-challenge-pool-risk-optimization.md)
- [版本更新日志](07-version-updates/CHANGELOG.md)

---

## 🤝 贡献指南

### 提交代码

```bash
# 1. Fork 仓库
# 2. 创建功能分支
git checkout -b feature/your-feature

# 3. 提交更改
git add .
git commit -m "feat: 添加新功能"

# 4. 推送到远程
git push origin feature/your-feature

# 5. 创建 Pull Request
```

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

## ⚠️ 免责声明

> **🔒 个人实验项目 · 不构成投资建议**
>
> **本项目性质：**
> - 这是一个**个人技术实验项目**，用于探索 AI 在投资决策中的应用
> - **不是**投资理财产品，**不是**投资咨询服务，**不是**推荐系统
> - 所有交易决策由 AI 自动生成，**仅供参考和学习**
>
> **⚠️ 风险提示：**
> - 市场有风险，投资需谨慎
> - AI 决策可能存在错误、滞后、偏差
> - 历史业绩不代表未来表现
> - 过往收益不代表未来收益
> - 可能导致本金损失，甚至全部亏损
>
> **🤖 AI 局限性：**
> - AI 无法预测黑天鹅事件
> - AI 无法获取未公开信息
> - AI 决策基于历史数据和公开信息
> - AI 不保证盈利，不承诺收益
>
> **💡 正确使用方式：**
> - ✅ 作为学习和研究 AI 投资的案例
> - ✅ 作为自动化决策系统的技术参考
> - ✅ 作为个人投资管理的辅助工具
> - ❌ **不要**盲目跟随 AI 决策进行投资
> - ❌ **不要**将此作为唯一投资依据
> - ❌ **不要**推荐给他人作为投资建议
>
> **如果您不同意以上条款，请勿参考或使用本项目。**

---

## 📞 联系方式

- **GitHub**: [heyaaron-Wu](https://github.com/heyaaron-Wu)
- **仓库**: [Semi-automatic-artificial-intelligence-system](https://github.com/heyaaron-Wu/Semi-automatic-artificial-intelligence-system)

---

<div align="center">

**🦞 如果觉得有用，请给个 Star ⭐**

*该仓库全部由 OpenClaw 独立进行管理*

[⬆ 返回顶部](#-openclaw-基金实盘交易系统)

</div>

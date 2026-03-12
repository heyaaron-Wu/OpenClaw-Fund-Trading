# 系统对比分析报告

## 参考系统
**GitHub:** https://github.com/onlinewithjun/OpenClaw-Fund-Real-Time-Trading-Challenge-
**分支:** fund-challenge-only
**更新时间:** 2026-03-11

---

## 一、核心技能对比

### ✅ 当前系统已具备 (12/12)
| 技能 | 状态 | 路径 |
|------|------|------|
| fund-challenge-orchestrator | ✅ | skills/fund-challenge-orchestrator |
| fund-challenge-daily-trader-core | ✅ | skills/fund-challenge-daily-trader-core |
| fund-challenge-data-guard | ✅ | skills/fund-challenge-data-guard |
| fund-challenge-evidence-audit | ✅ | skills/fund-challenge-evidence-audit |
| fund-challenge-execution-engine | ✅ | skills/fund-challenge-execution-engine |
| fund-challenge-identity-freshness-guard | ✅ | skills/fund-challenge-identity-freshness-guard |
| fund-challenge-instrument-rules | ✅ | skills/fund-challenge-instrument-rules |
| fund-challenge-ledger-postmortem | ✅ | skills/fund-challenge-ledger-postmortem |
| fund-challenge-market-calendar-gate | ✅ | skills/fund-challenge-market-calendar-gate |
| fund-challenge-offexchange-exec-sim | ✅ | skills/fund-challenge-offexchange-exec-sim |
| fund-challenge-position-risk-engine | ✅ | skills/fund-challenge-position-risk-engine |
| fund-challenge-signal-fusion-engine | ✅ | skills/fund-challenge-signal-fusion-engine |

**结论:** 核心技能完整 ✅

---

## 二、脚本文件对比

### ✅ 当前系统已有脚本 (35 个)
```
build_evidence.py          ✅
cache_key_builder.py       ✅
confirm_and_apply.py       ✅
daily_bundle_runner.py     ✅
decision_delta_guard.py    ✅
decision_id_linker.py      ✅
decision_packet_builder.py ✅
decision_publish_gate.py   ✅
decision_template_shortener.py ✅
evidence_compactor.py      ✅
execution_receipt_updater.py ✅
fast_fail_report.py        ✅
preflight_guard.py         ✅
receipt_from_text.py       ✅
refresh_instrument_rules.py ✅
run_decision_pipeline.py   ✅
runtime_cache.py           ✅
source_fetch_minifier.py   ✅
state_math.py              ✅
status_brief.py            ✅
validate_evidence.py       ✅
daily_pnl_updater.py       ✅ (额外)
evidence_data_collector.py ✅ (额外)
fund_pool_screener.py      ✅ (额外)
is_trading_day.py          ✅ (额外)
market_signal_fetcher.py   ✅ (额外)
net_value_fetcher.py       ✅ (额外)
preflight_alert.py         ✅ (额外)
preflight_fail_alert.py    ✅ (额外)
preflight_guard_v2.py      ✅ (额外)
trading_calendar.py        ✅ (额外)
weekly_report.py           ✅ (额外)
backtest_engine.py         ✅ (额外)
```

### ❌ 缺失脚本 (11 个)
| 脚本 | 用途 | 优先级 |
|------|------|--------|
| `apply_mark_to_market.py` | 盯市计价 | 中 |
| `execute_gate_script_only.py` | 执行门控脚本 | 高 |
| `plan_script_only.py` | 计划脚本 | 高 |
| `universe_refresh_script_only.py` | 候选池刷新脚本 | 高 |
| `run_universe_refresh_no_proxy.ps1` | 无代理候选池刷新 (PowerShell) | 低 |
| `update_refresh_retry.py` | 更新刷新重试 | 中 |
| `state_refresh.py` | 状态刷新 | 中 |
| `healthcheck_brief.py` | 健康检查简报 | 中 |
| `nav_snapshot_fetch.py` | 净值快照获取 | 高 |
| `gate_scoring.py` | 门控评分 | 高 |
| `token_weekly_report.py` | Token 优化周报 | 低 |

---

## 三、提示词模板对比

### ✅ 当前系统已有
| 模板 | 状态 |
|------|------|
| healthcheck.md | ✅ |
| plan.md | ✅ |
| execute-gate.md | ✅ |
| review.md | ✅ |

### ❌ 缺失模板 (4 个)
| 模板 | 用途 | 优先级 |
|------|------|--------|
| `1420-track.md` | 14:20 盘中跟踪 | 高 |
| `2000-update.md` | 20:00 更新协议 | 高 |
| `post-summary.md` | 后置总结 | 中 |
| `universe-refresh.md` | 候选池刷新提示词 | 高 |

---

## 四、定时任务对比

### 参考系统时间表
| 时间 | 任务 | 当前系统 |
|------|------|----------|
| 09:00 | Healthcheck | ✅ fund-daily-check |
| 13:35 | Universe refresh | ❌ **缺失** |
| 14:00 | PLAN_ONLY | ✅ fund-1400-decision |
| 14:48 | EXECUTE_READY | ❌ **缺失** |
| 20:05 | 日终复盘 | ✅ fund-2005-review |
| 21:00 | Update (STEP1) | ❌ **缺失** |
| 21:30 | PostSummary (STEP2) | ❌ **缺失** |
| 21:45 | Review | ❌ **缺失** |
| 22:00 | Maintenance | ❌ **缺失** |
| 周五 20:00 | 周报 | ✅ fund-weekly-report |

### ❌ 缺失任务 (6 个)
1. **基金挑战 -13:35-候选池刷新** - 每日候选基金扫描
2. **基金挑战 -14:48-执行门控** - 最终执行确认
3. **基金挑战 -21:00-Update** - 轻量更新 (STEP1)
4. **基金挑战 -21:30-PostSummary** - 后置总结 (STEP2)
5. **基金挑战 -21:45-Review** - 日终复盘
6. **基金挑战 -22:00-Maintenance** - 缓存清理维护

---

## 五、其他缺失组件

### ❌ 配置文件
| 文件 | 用途 |
|------|------|
| `fund_challenge/receipt.template.json` | 执行确认回执模板 |
| `fund_challenge/decision_history.jsonl` | 决策指纹历史 (运行时创建) |
| `fund_challenge/evidence/template.json` | 证据模板基线 |
| `fund_challenge/evidence/latest.compact.json` | 压缩版证据 (运行时) |
| `fund_challenge/checklists/daily-checklist.md` | 每日检查清单 |

### ❌ 工具
| 工具 | 用途 |
|------|------|
| `tools/dashscope-embed-proxy.mjs` | DashScope embeddings 代理 |
| `tools/start-embed-proxy.ps1` | 代理启动脚本 (PowerShell) |

### ❌ 文档
| 文档 | 用途 |
|------|------|
| `docs/upgrades/*/upgrade-log.*.md` | 每日升级日志 |
| `fund_challenge/README-OPS.md` | 运维手册 |

---

## 六、优先级建议

### 🔴 高优先级 (立即补充)
1. **14:48 执行门控任务** - 确保执行前最终验证
2. **13:35 候选池刷新任务** - 每日候选基金扫描
3. **缺失脚本:**
   - `execute_gate_script_only.py`
   - `plan_script_only.py`
   - `universe_refresh_script_only.py`
   - `nav_snapshot_fetch.py`
   - `gate_scoring.py`
4. **缺失提示词:**
   - `1420-track.md`
   - `2000-update.md`
   - `universe-refresh.md`

### 🟡 中优先级 (近期补充)
1. **21:00-22:00 晚间任务链** - Update/PostSummary/Review/Maintenance
2. **缺失脚本:**
   - `apply_mark_to_market.py`
   - `state_refresh.py`
   - `healthcheck_brief.py`
   - `update_refresh_retry.py`
3. **配置文件:**
   - `receipt.template.json`
   - `evidence/template.json`
   - `daily-checklist.md`

### 🟢 低优先级 (可选)
1. `token_weekly_report.py` - Token 优化版本
2. `run_universe_refresh_no_proxy.ps1` - PowerShell 版本
3. `post-summary.md` - 后置总结提示词
4. embeddings 代理工具 (如不需要向量搜索)

---

## 七、当前系统优势

### ✅ 当前系统额外功能
1. **飞书推送集成** - 已迁移完成，支持文本/卡片格式
2. **额外数据脚本:**
   - `daily_pnl_updater.py` - 每日盈亏更新
   - `evidence_data_collector.py` - 证据数据采集
   - `fund_pool_screener.py` - 基金池筛选
   - `market_signal_fetcher.py` - 市场信号获取
   - `net_value_fetcher.py` - 净值获取
   - `trading_calendar.py` - 交易日历
3. **preflight_guard_v2.py** - 增强版预检
4. **SYSTEM_OVERVIEW.md** - 系统概览文档
5. **SCRIPTS_AND_PLANS.md** - 脚本和计划文档

---

## 八、总结

**整体评估:** 当前系统核心功能完整 (12/12 技能)，但在以下方面需要补充:

| 类别 | 缺失数量 | 完成度 |
|------|----------|--------|
| 核心技能 | 0/12 | 100% ✅ |
| 脚本文件 | 11/43 | 74% |
| 提示词模板 | 4/8 | 50% |
| 定时任务 | 6/11 | 45% |
| 配置文件 | 5+ | 需补充 |

**建议行动:**
1. 优先补充 13:35 和 14:48 任务 (完善交易时段覆盖)
2. 补充晚间任务链 (21:00-22:00)
3. 创建缺失的提示词模板
4. 补充配置文件模板

---

*报告生成时间: 2026-03-11 18:45*

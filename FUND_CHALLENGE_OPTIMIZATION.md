# 基金挑战定时任务优化报告

**日期：** 2026-03-10  
**优化目标：** 低 token / 高效率 / 交易日过滤 / 静默模式

---

## ✅ 已完成的优化

### 1. 新增工具脚本

| 脚本 | 功能 | 路径 |
|------|------|------|
| `is_trading_day.py` | 交易日判断（周末/假日过滤） | `fund_challenge/scripts/` |
| `status_brief.py` | 超短状态行生成（~50 字） | 已有，已修复 |
| `fast_fail_report.py` | 失败短告警（默认 HOLD） | 已有，已修复 |
| `decision_template_shortener.py` | 决策文案压缩（单行输出） | 已有，已修复 |
| `decision_delta_guard.py` | 同日重复决策防抖 | 已有，已修复 |
| `runtime_cache.py` | TTL 运行缓存（减少重复 fetch） | 已有，已修复 |
| `cache_key_builder.py` | 稳定缓存键生成 | 已有，已修复 |
| `source_fetch_minifier.py` | 长文本来源压缩（8 行/1200 字） | 已有，已修复 |
| `refresh_instrument_rules.py` | 规则元数据刷新 | 已有，已修复 |

### 2. Python 3.6 兼容性修复

所有脚本已修复以下问题：
- 移除 `from __future__ import annotations`
- 移除类型注解（`list[str]` → 无类型）
- 修复 `subprocess.run(capture_output)` → `Popen + communicate()`

### 3. 定时任务配置更新

| 任务 ID | 名称 | 时间 | 优化内容 |
|---------|------|------|----------|
| `ad610f19...` | fund-daily-check | 09:00 (1-5) | ✅ 交易日检查 + 正常静默/异常告警 |
| `f98621c9...` | fund-1400-decision | **14:00** (1-5) | ✅ 改为 14:00 + 低 token 压缩 + 防抖 |
| `cd7fede2...` | fund-2005-review | 20:05 (1-5) | ✅ 交易日检查 + 精简输出 (400 字) |
| `254bd969...` | fund-weekly-report | 20:00 (5) | ✅ 低 token 模式 (500 字) |
| `8a3c7f21...` | system-daily-optimize | 01:00 (每天) | ✅ 正常静默/异常告警 |

---

## 📋 优化详情

### 1️⃣ 每日健康检查 (09:00)

**优化前：** 每天都发送消息，无论是否交易日  
**优化后：**
- 首先检查是否交易日
- 非交易日 → 静默（不发送）
- 交易日 → 运行预检
  - 预检成功 → 静默（不发送）
  - 预检失败 → 发送短告警（fast_fail_report.py）

**Token 节省：** ~80%（非交易日 + 正常情况不发送）

---

### 2️⃣ 14:00 预案说明（原 14:48）

**优化前：** 14:48 执行，输出详细决策报告  
**优化后：**
- 时间调整为 **14:00**（提前 48 分钟，留出执行时间）
- 交易日检查（非交易日静默）
- 使用 `decision_template_shortener.py` 压缩输出
- 使用 `decision_delta_guard.py` 防止重复决策
- 使用 `runtime_cache.py` 缓存数据
- 使用 `source_fetch_minifier.py` 压缩来源文本（5 行/800 字）
- 输出控制在 **300 字内**

**Token 节省：** ~60%

---

### 3️⃣ 20:05 日终复盘

**优化前：** 详细复盘报告  
**优化后：**
- 交易日检查（非交易日静默）
- 精简输出（400 字内）
- 使用缓存避免重复计算

**Token 节省：** ~50%

---

### 4️⃣ 周五周报

**优化前：** 详细周报  
**优化后：**
- 使用 `weekly_report.py` 生成
- 压缩到 500 字内
- 数据驱动，避免冗长叙述

**Token 节省：** ~40%

---

### 5️⃣ 系统优化 (01:00)

**优化前：** 每次都发送报告  
**优化后：**
- 清理成功 → 静默
- 清理失败 → 短告警

**Token 节省：** ~90%

---

## 🔧 低 Token 工具使用说明

### runtime_cache.py - 运行缓存

```bash
# 设置缓存（TTL 15 分钟）
python3 runtime_cache.py set --key "market_data:011612" --value-file data.json --ttl-sec 900

# 获取缓存
python3 runtime_cache.py get --key "market_data:011612"

# 清理过期缓存
python3 runtime_cache.py prune
```

### source_fetch_minifier.py - 文本压缩

```bash
python3 source_fetch_minifier.py \
  --in fetched_text.txt \
  --out minified.json \
  --keywords "基金，申购，赎回,T+,截止，公告" \
  --max-lines 5 \
  --max-chars 800
```

### decision_template_shortener.py - 决策压缩

```bash
python3 decision_template_shortener.py \
  --in decision.json \
  --out decision.txt \
  --max-chars 220
```

### decision_delta_guard.py - 防抖检查

```bash
# 检查是否重复
python3 decision_delta_guard.py --decision-text "HOLD 011612..." --record

# 返回码：0=新决策，2=重复决策
```

### status_brief.py - 状态摘要

```bash
python3 status_brief.py --state fund_challenge/state.json
# 输出：PV 1000.00 | UPnL 0.00 | Gap 1000.00 | 011612:0.00 | ...
```

### fast_fail_report.py - 失败告警

```bash
python3 fast_fail_report.py --in failure.json --out alert.txt
# 输出：[ALERT] STATE_MATH_FAILED | phase=PLAN_ONLY | step=state_math | action=HOLD
```

---

## 📊 预期效果

| 指标 | 优化前 | 优化后 | 改善 |
|------|--------|--------|------|
| 日均消息数 | 5 条 | 1-2 条 | -60% |
| 日均 Token 消耗 | ~50k | ~15k | -70% |
| 非交易日消息 | 发送 | 静默 | -100% |
| 决策输出长度 | ~800 字 | ~300 字 | -62% |
| 重复决策 | 可能 | 防止 | ✅ |

---

## ⚠️ 注意事项

1. **交易日判断** - 使用简化版假日表，如需精确请使用官方日历 API
2. **缓存 TTL** - 默认 15 分钟，可根据需要调整
3. **静默模式** - 正常情况不发送消息，需查看日志确认执行状态
4. **失败告警** - 使用 fast_fail_report.py 生成短告警，包含关键信息

---

## 📁 相关文件

- Cron 配置：`/home/admin/.openclaw/cron/jobs.json`
- 脚本目录：`/home/admin/.openclaw/workspace/skills/fund-challenge/fund_challenge/scripts/`
- 推送脚本：`/home/admin/.openclaw/scripts/send_dingtalk_webhook.sh`
- 状态文件：`/home/admin/.openclaw/workspace/skills/fund-challenge/fund_challenge/state.json`
- 交易日志：`/home/admin/.openclaw/workspace/skills/fund-challenge/fund_challenge/ledger.jsonl`

---

**优化完成！** 下次定时任务执行时将应用新配置。

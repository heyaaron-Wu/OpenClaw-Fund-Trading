# 美股交易系统

**独立于 A 股基金挑战系统**，美股交易有自己独立的数据和配置。

---

## 📁 目录结构

```
us-stocks/
├── scripts/              # 美股脚本
│   └── daily_review.py   # 日终复盘脚本
├── data/                 # ✅ 美股独立数据（与 A 股完全分离）
│   ├── state.json        # 持仓状态
│   ├── ledger.jsonl      # 交易记录
│   └── reviews/          # 复盘报告
└── README.md             # 本文档
```

---

## 🔧 定时任务

| 任务名 | 时间 | 说明 | 状态 |
|--------|------|------|------|
| us-premarket-check | 美股开盘前 | 盘前检查 | ⏸️ 已禁用 |
| us-signal-scan | 盘中 | 信号扫描 | ⏸️ 已禁用 |
| us-daily-review | 美股盘后 | 日终复盘 | ⏸️ 已禁用 |

**启用方法：**
```bash
# 编辑 cron 配置
openclaw cron edit us-daily-review

# 设置 enabled=true
```

---

## 📊 数据隔离

**A 股 vs 美股 完全分离：**

| 项目 | A 股基金 | 美股 |
|------|---------|------|
| 数据目录 | `08-fund-daily-review/` | `us-stocks/data/` |
| 状态文件 | `08-fund-daily-review/state.json` | `us-stocks/data/state.json` |
| 复盘报告 | `08-fund-daily-review/reviews/` | `us-stocks/data/reviews/` |
| GitHub 归档 | ✅ 推送到 GitHub | ❌ 仅本地保存 |
| 飞书群 | A 股群 | 美股群 |
| Webhook | `f1286a3e...` | `f0f9c2ca...` |

---

## 🚀 快速开始

1. **初始化持仓** - 编辑 `data/state.json` 添加持仓
2. **启用定时任务** - 在 OpenClaw 中启用美股相关 cron
3. **自动复盘** - 每天美股盘后自动生成报告并推送

---

## 📌 数据归档

- ✅ **本地保存** - 复盘报告保存在 `us-stocks/data/reviews/`
- ⚠️ **不上传 GitHub** - 美股数据目前仅本地保存，不推送到 GitHub
- ✅ **飞书推送** - 盘后复盘通知推送到美股群

---

## ⚠️ 注意事项

- ✅ 美股和 A 股数据完全独立，互不影响
- ✅ 推送到不同的飞书群
- ✅ GitHub 归档到不同目录
- ⚠️ 当前美股系统暂无真实持仓，定时任务已禁用

---

**最后更新：** 2026-04-23（系统分离完成）

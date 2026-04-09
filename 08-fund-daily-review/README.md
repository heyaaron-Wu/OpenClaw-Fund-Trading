# 基金日终复盘系统

自动化的基金投资复盘系统，每日 22:30 自动生成复盘报告并推送到 GitHub 归档。

---

## 📊 核心功能

- **自动复盘**：每日 22:30 自动生成日终复盘报告
- **数据校验**：每日 22:00 自动校验数据一致性
- **自动备份**：每日 22:00 自动备份关键数据
- **GitHub 归档**：复盘报告自动推送到 GitHub
- **飞书通知**：关键操作结果自动推送

---

## 📂 文件结构

```
08-fund-daily-review/
├── state.json              # 当前持仓状态（权威数据源）
├── ledger.jsonl            # 每日盈亏明细（流水账）
├── decision_records/       # 每日决策记录
│   └── YYYY-MM-DD.json
├── reviews/                # 复盘报告
│   ├── YYYY-MM-DD.md       # 每日复盘
│   └── YYYY-MM-复盘.md      # 月度复盘
├── backups/                # 自动备份目录
└── README.md               # 本文档
```

---

## 🔄 数据流向

```
蚂蚁财富截图 → state.json（手动/自动更新）
                ↓
        ledger.jsonl（每日盈亏记录）
                ↓
        复盘报告（自动生成）
                ↓
        GitHub 归档（自动推送）
```

**核心原则：**
- ✅ **state.json 是权威数据源**（来自蚂蚁财富实际持仓）
- ✅ **ledger.jsonl 是辅助记录**（应与 state.json 一致）
- ✅ **每日校验**：自动校验两者一致性

---

## ⏰ 定时任务清单

### 交易日任务（周一至周五）

| 时间 | 任务名 | 作用 |
|------|--------|------|
| 09:00 | fund-daily-check | 每日健康检查 |
| 13:35 | fund-1335-universe | 候选池刷新 |
| 14:00 | fund-1400-decision | 交易决策 |
| 14:48 | fund-1448-exec-gate | 执行门控 |
| 22:00 | **data-validate** | **数据校验** ⭐ |
| 22:00 | **backup-data** | **自动备份** ⭐ |
| 22:30 | fund-2230-review | 日终复盘 + GitHub 归档 |

### 每日任务

| 时间 | 任务名 | 作用 |
|------|--------|------|
| 01:00 | system-daily-optimize | 系统清理 |
| 23:30 | system-version-update | 版本更新 + GitHub 归档 |

---

## 🛠️ 维护指南

### 数据校验

```bash
# 手动运行数据校验
python3 /home/admin/.openclaw/workspace/05-scripts/validate_data.py
```

### 数据备份

```bash
# 手动备份
bash /home/admin/.openclaw/workspace/05-scripts/backup_data.sh

# 备份位置
/home/admin/.openclaw/workspace/Semi-automatic-artificial-intelligence-system/08-fund-daily-review/backups/
```

### 故障排查

#### 问题 1：数据不一致

**症状：** 校验脚本报错
**解决：**
1. 以 state.json 为准（来自蚂蚁财富实际持仓）
2. 修正 ledger.jsonl 使其与 state.json 一致
3. 重新运行校验脚本

#### 问题 2：Git 推送失败

**症状：** 复盘报告无法推送到 GitHub
**解决：**
```bash
cd /home/admin/.openclaw/workspace/Semi-automatic-artificial-intelligence-system
git pull --rebase origin OpenClaw-Fund-Trading
git push origin OpenClaw-Fund-Trading
```

#### 问题 3：cron 任务异常

**症状：** 任务未执行或显示 error
**解决：**
```bash
# 查看 cron 状态
openclaw cron list

# 重启 Gateway
openclaw gateway restart
```

---

## 📈 数据标准

### state.json 字段说明

| 字段 | 说明 | 示例 |
|------|------|------|
| `total_pnl` | 累计盈亏 | -34.37 元 |
| `portfolio_value` | 组合市值 | 965.15 元 |
| `positions` | 持仓明细 | 数组 |
| `positions[].unrealized_pnl` | 单只基金累计盈亏 | -10.98 元 |

### ledger.jsonl 字段说明

| 字段 | 说明 | 示例 |
|------|------|------|
| `date` | 日期 | 2026-04-08 |
| `total_pnl` | 当日总盈亏 | 51.37 元 |
| `positions` | 各基金盈亏明细 | 数组 |
| `positions[].daily_pnl` | 单只基金当日盈亏 | 21.57 元 |

---

## 🔒 安全与隐私

### 禁止推送的数据

- ❌ API tokens / keys
- ❌ 飞书 Webhook URL
- ❌ 个人身份信息
- ❌ 财务数据（持仓明细、基金代码）- 已脱敏处理

### 可以推送的数据

- ✅ 复盘报告（已脱敏）
- ✅ 系统配置文档
- ✅ 脚本文件

---

## 📞 支持

- 系统文档：`/opt/openclaw/docs`
- GitHub 仓库：https://github.com/heyaaron-Wu/Semi-automatic-artificial-intelligence-system
- 飞书通知 Webhook：已配置

---

**最后更新：** 2026-04-09
**版本：** v1.2.0

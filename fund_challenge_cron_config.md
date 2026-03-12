# OpenClaw Cron Configuration for Fund Challenge
# 基金挑战自动汇报配置

## 📅 每日定时任务（交易日）

# 1. 09:00 - 健康检查（简短播报）
# CRON_EXPRESSION   JOB_NAME          TASK
"0 9 * * 1-5"       "fund-check"      "基金挑战健康检查"

# 2. 14:48 - 最终下单方案（买入决策）
"48 14 * * 1-5"     "fund-decision"   "基金挑战 14:48 最终决策"

# 3. 20:25 - 日终复盘（盈亏汇总）
"25 20 * * 1-5"     "fund-review"     "基金挑战日终复盘"

## 📊 每周定时任务

# 4. 周五 20:00 - 周报生成和发送
"0 20 * * 5"        "fund-weekly"     "基金挑战周报复盘"

---

## 🔧 使用方法

# 添加定时任务（示例）
openclaw cron add "fund-check" \
  --schedule "0 9 * * 1-5" \
  --task "基金挑战健康检查"

openclaw cron add "fund-decision" \
  --schedule "48 14 * * 1-5" \
  --task "基金挑战 14:48 最终决策"

openclaw cron add "fund-review" \
  --schedule "25 20 * * 1-5" \
  --task "基金挑战日终复盘"

openclaw cron add "fund-weekly" \
  --schedule "0 20 * * 5" \
  --task "基金挑战周报复盘"

# 启动所有定时任务
openclaw cron start fund-check
openclaw cron start fund-decision
openclaw cron start fund-review
openclaw cron start fund-weekly

# 查看状态
openclaw cron status fund-check

# 暂停某个任务
openclaw cron stop fund-check

# 删除某个任务
openclaw cron remove fund-check

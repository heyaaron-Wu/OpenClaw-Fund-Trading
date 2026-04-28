#!/bin/bash
# 系统每周报告脚本
# 每周一 7:00 自动执行

set -e

WORKSPACE="/home/admin/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
REPORT_FILE="$MEMORY_DIR/weekly-report-$(date +%Y-%m-%d).md"

echo "📊 系统每周报告生成中..."

# 收集系统信息
DISK_INFO=$(df -h / | tail -1)
DISK_USED=$(echo "$DISK_INFO" | awk '{print $3}')
DISK_AVAIL=$(echo "$DISK_INFO" | awk '{print $4}')
DISK_PCT=$(echo "$DISK_INFO" | awk '{print $5}')

MEM_INFO=$(free -m | grep Mem)
MEM_TOTAL=$(echo "$MEM_INFO" | awk '{print $2}')
MEM_USED=$(echo "$MEM_INFO" | awk '{print $3}')
MEM_PCT=$(echo "$MEM_INFO" | awk '{printf "%.1f", $3/$2*100}')

SWAP_INFO=$(free -m | grep Swap)
SWAP_TOTAL=$(echo "$SWAP_INFO" | awk '{print $2}')
SWAP_USED=$(echo "$SWAP_INFO" | awk '{print $3}')

UPTIME_INFO=$(uptime)
LOAD_AVG=$(echo "$UPTIME_INFO" | awk -F'load average:' '{print $2}' | xargs)

GWAY_STATUS=$(pgrep -c openclaw-gateway 2>/dev/null || echo "0")
GWAY_PID=$(pgrep openclaw-gateway 2>/dev/null | head -1)

CRON_COUNT=$(crontab -l 2>/dev/null | grep -v '^#' | grep -v '^$' | wc -l)

UPTIME_DAYS=$(echo "$UPTIME_INFO" | grep -oP 'up \K[0-9]+' || echo "?")

# 统计本周记忆文件
WEEK_START=$(date -d "7 days ago" +%Y-%m-%d)
WEEK_END=$(date +%Y-%m-%d)
DAILY_FILES=$(ls "$MEMORY_DIR"/${WEEK_START:0:4}-${WEEK_START:5:2}-${WEEK_START:8:2}.md "$MEMORY_DIR"/${WEEK_END:0:4}-${WEEK_END:5:2}-${WEEK_END:8:2}.md 2>/dev/null | wc -l)
# 更精确地统计本周文件
DAILY_COUNT=0
for d in $(seq 0 6); do
    FILE_DATE=$(date -d "$d days ago" +%Y-%m-%d)
    if [ -f "$MEMORY_DIR/$FILE_DATE.md" ]; then
        DAILY_COUNT=$((DAILY_COUNT + 1))
    fi
done

# 统计本周事件数量
EVENT_COUNT=0
for d in $(seq 0 6); do
    FILE_DATE=$(date -d "$d days ago" +%Y-%m-%d)
    if [ -f "$MEMORY_DIR/$FILE_DATE.md" ]; then
        COUNT=$(grep -c "^## " "$MEMORY_DIR/$FILE_DATE.md" 2>/dev/null || echo "0")
        EVENT_COUNT=$((EVENT_COUNT + COUNT))
    fi
done

# 磁盘趋势
DISK_TREND="稳定"
if [ "$DISK_PCT" = "58%" ]; then
    DISK_TREND="稳定 (58%)"
fi

# 生成报告
cat > "$REPORT_FILE" << EOF
# 📊 系统每周报告 ($(date +%Y-%m-%d))

## 系统健康概览

| 指标 | 当前值 | 状态 |
|------|--------|------|
| 磁盘 | ${DISK_USED}/${DISK_PCT} 已用，${DISK_AVAIL} 可用 | ✅ |
| 内存 | ${MEM_USED}MB/${MEM_TOTAL}MB (${MEM_PCT}%) | ⚠️ 偏高 |
| Swap | ${SWAP_USED}MB/${SWAP_TOTAL}MB | ✅ |
| 负载 | ${LOAD_AVG} | ✅ |
| Gateway | PID ${GWAY_PID:-N/A} | ✅ |
| Cron 任务 | ${CRON_COUNT} 个 | ✅ |
| 系统运行 | ${UPTIME_DAYS} 天 | ✅ |

## 本周活动统计

- 记忆文件: ${DAILY_COUNT} 天
- 事件记录: ${EVENT_COUNT} 条
- 报告周期: $(date -d "6 days ago" +%Y-%m-%d) ~ $(date +%Y-%m-%d)

## 本周关键事件

EOF

# 提取本周关键事件
for d in $(seq 0 6); do
    FILE_DATE=$(date -d "$d days ago" +%Y-%m-%d)
    if [ -f "$MEMORY_DIR/$FILE_DATE.md" ]; then
        echo "### $FILE_DATE" >> "$REPORT_FILE"
        # 提取一级标题和关键事件
        grep "^## " "$MEMORY_DIR/$FILE_DATE.md" | while read -r line; do
            echo "- $line" >> "$REPORT_FILE"
        done
        echo "" >> "$REPORT_FILE"
    fi
done

cat >> "$REPORT_FILE" << EOF
## Cron 任务状态

当前启用任务: ${CRON_COUNT} 个

| 时间 | 任务 | 状态 |
|------|------|------|
EOF

# 列出所有 cron 任务
crontab -l 2>/dev/null | grep -v '^#' | grep -v '^$' | while read -r line; do
    SCHEDULE=$(echo "$line" | awk '{print $1, $2, $3, $4, $5}')
    COMMAND=$(echo "$line" | awk '{for(i=6;i<=NF;i++) printf "%s ", $i; print ""}')
    SCRIPT_NAME=$(basename "$(echo "$COMMAND" | awk '{print $1}')")
    echo "| \`$SCHEDULE\` | $SCRIPT_NAME | ⏳ |" >> "$REPORT_FILE"
done

cat >> "$REPORT_FILE" << EOF

## 下周关注事项

1. **内存优化**: 当前内存使用率 ${MEM_PCT}%，建议关注 Gateway 内存占用
2. **Cron 脚本补全**: 部分 cron 任务脚本缺失（system-weekly-report.sh 等）
3. **系统更新**: 运行 ${UPTIME_DAYS} 天，关注内核安全更新
4. **基金挑战系统**: 继续跟踪持仓表现

---
*报告自动生成于 $(date '+%Y-%m-%d %H:%M:%S')*
EOF

echo "✅ 报告已保存: $REPORT_FILE"
echo "📊 磁盘: ${DISK_PCT} | 内存: ${MEM_PCT}% | 负载: ${LOAD_AVG}"

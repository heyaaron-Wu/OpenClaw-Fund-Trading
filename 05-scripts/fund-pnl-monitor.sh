#!/bin/bash
# 基金止盈止损监控 - Shell Wrapper
# 交易日 15:30 检查持仓盈亏，止盈/止损阈值告警

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_SCRIPT="${SCRIPT_DIR}/fund-pnl-monitor.py"

if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "❌ Python script not found: $PYTHON_SCRIPT"
    exit 1
fi

# 检查是否为交易日（简单判断：周一到周五）
DAY_OF_WEEK=$(date +%u)
if [ "$DAY_OF_WEEK" -ge 6 ]; then
    echo "📅 周末，跳过基金止盈止损监控"
    exit 0
fi

# 检查是否在交易时间内（15:00-15:30 之后）
CURRENT_HOUR=$(date +%H)
CURRENT_MIN=$(date +%M)
if [ "$CURRENT_HOUR" -lt 15 ] || ([ "$CURRENT_HOUR" -eq 15 ] && [ "$CURRENT_MIN" -lt 0 ]); then
    echo "🕐 非交易时段（当前 ${CURRENT_HOUR}:${CURRENT_MIN}），跳过"
    exit 0
fi

exec python3 "$PYTHON_SCRIPT"

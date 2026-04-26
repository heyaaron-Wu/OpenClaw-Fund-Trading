#!/bin/bash
# 系统健康检查脚本
# 每日 08:00 执行

echo "🏥 开始系统健康检查..."

# 检查磁盘使用率
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
echo "💾 磁盘使用率：${DISK_USAGE}%"

if [ "$DISK_USAGE" -gt 90 ]; then
    echo "⚠️  磁盘使用率过高！"
fi

# 检查内存使用
MEM_USAGE=$(free | awk 'NR==2 {printf("%.1f"), $3*100/$2}')
echo "🧠 内存使用率：${MEM_USAGE}%"

# 检查 OpenClaw 状态
if pgrep -x "openclaw" > /dev/null; then
    echo "✅ OpenClaw 运行正常"
else
    echo "❌ OpenClaw 未运行"
fi

# 检查 Cron 任务
echo "📅 Cron 任务状态:"
openclaw cron list 2>/dev/null | grep -E "fund-|us-" | head -10

echo "✅ 健康检查完成"

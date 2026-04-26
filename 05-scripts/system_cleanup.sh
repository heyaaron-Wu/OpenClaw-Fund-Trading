#!/bin/bash
# 系统每日清理脚本
# 每日 01:00 执行

echo "🧹 开始系统清理..."

# 清理临时文件
find /tmp -type f -mtime +7 -delete 2>/dev/null
echo "✅ 临时文件已清理"

# 清理旧日志
find /home/admin/.openclaw/logs -name "*.log" -mtime +30 -delete 2>/dev/null
echo "✅ 旧日志已清理"

# 清理缓存
find /home/admin/.openclaw/workspace/06-data/cache -type f -mtime +7 -delete 2>/dev/null
echo "✅ 缓存已清理"

echo "✅ 系统清理完成"

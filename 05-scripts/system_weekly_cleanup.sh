#!/bin/bash
# 系统每周清理脚本（可手动执行）
# 每周一 8:00 自动执行

set -e

echo "🔧 系统每周清理开始..."
echo ""

# 清理浏览器缓存
echo "🗑️  清理浏览器缓存..."
rm -rf ~/.openclaw/browser/openclaw/Default/Cache/*
rm -rf ~/.openclaw/browser/openclaw/Default/CacheStorage/*
echo "✅ 浏览器缓存清理完成"

# 清理 Cron 执行记录（7 天前）
echo ""
echo "🗑️  清理过期 Cron 记录..."
find ~/.openclaw/cron/runs -name "*.jsonl" -mtime +7 -delete
echo "✅ Cron 记录清理完成"

# 清理临时文件
echo ""
echo "🗑️  清理临时文件..."
find /tmp -name "openclaw*" -mtime +7 -delete 2>/dev/null || true
find ~/.cache -type f -mtime +30 -delete 2>/dev/null || true
echo "✅ 临时文件清理完成"

echo ""
echo "================================"
echo "✅ 系统每周清理完成！"
echo ""

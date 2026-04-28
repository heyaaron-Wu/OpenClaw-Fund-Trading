#!/bin/bash
# 基金日终复盘
set -e

# 加载环境变量（cron 环境不自动加载 .bashrc）
source ~/.bashrc 2>/dev/null || true

BASE="/home/admin/.openclaw/workspace/Semi-automatic-artificial-intelligence-system"
SCRIPTS="/home/admin/.openclaw/workspace/skills/fund-challenge/fund_challenge/scripts"

echo "=== 基金日终复盘 $(date '+%Y-%m-%d %H:%M:%S') ==="

cd "$SCRIPTS"
python3.11 daily_review_v2.py --base "$BASE" --alert --save 2>&1

echo "=== 复盘完成 ==="

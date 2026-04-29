#!/bin/bash
# 基金日终复盘
set -e

# 直接加载环境变量（避免 cron 环境 source bashrc 失败）
export IWENCAI_BASE_URL=https://openapi.iwencai.com
export IWENCAI_API_KEY=sk-proj-00-_MxrDE-yg8MMUrPrkV-w1f3yX2OfmbRbSMTqkVegQgOKdL8m3LMvFU1cZ0tUfXM-56jq9e9P77WZ3tTvF6yGXbOtVHQcsm2bLzXEB6IBuAKRfetZGD91wh__A8-6EZ4n6onQRQ
export MX_APIKEY="mkt_Xg7DpYQnNvdb96dGvULmrwVdMCzxYM-QWdM1IkkSEoc"

BASE="/home/admin/.openclaw/workspace/Semi-automatic-artificial-intelligence-system"
SCRIPTS="/home/admin/.openclaw/workspace/skills/fund-challenge/fund_challenge/scripts"

echo "=== 基金日终复盘 $(date '+%Y-%m-%d %H:%M:%S') ==="

cd "$SCRIPTS"
python3.11 daily_review_v2.py --base "$BASE" --alert --save 2>&1

echo "=== 复盘完成 ==="

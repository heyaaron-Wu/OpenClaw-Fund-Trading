#!/bin/bash
# 基金公告监控 - Shell Wrapper
# Cron: 10 9 * * 1-5

# 加载环境变量
export IWENCAI_BASE_URL=https://openapi.iwencai.com
export IWENCAI_API_KEY=sk-proj-00-_MxrDE-yg8MMUrPrkV-w1f3yX2OfmbRbSMTqkVegQgOKdL8m3LMvFU1cZ0tUfXM-56jq9e9P77WZ3tTvF6yGXbOtVHQcsm2bLzXEB6IBuAKRfetZGD91wh__A8-6EZ4n6onQRQ
export MX_APIKEY="mkt_Xg7DpYQnNvdb96dGvULmrwVdMCzxYM-QWdM1IkkSEoc"

cd /home/admin/.openclaw/workspace
source /home/admin/.openclaw/workspace/.env 2>/dev/null || true

/usr/bin/python3.11 05-scripts/fund-announcement-monitor.py

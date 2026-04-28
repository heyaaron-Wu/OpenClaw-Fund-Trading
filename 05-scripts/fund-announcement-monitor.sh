#!/bin/bash
# 基金公告监控 - Shell Wrapper
# Cron: 10 9 * * 1-5

cd /home/admin/.openclaw/workspace
source /home/admin/.openclaw/workspace/.env 2>/dev/null || true

/usr/bin/python3.11 05-scripts/fund-announcement-monitor.py

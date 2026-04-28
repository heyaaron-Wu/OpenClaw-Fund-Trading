#!/usr/bin/env python3
"""Cron 健康监控 - 每小时检查 cron 任务执行情况"""
import subprocess
import json
import os
from datetime import datetime

def check_cron_health():
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    results = []
    
    # 检查最近24小时的 cron 日志
    try:
        result = subprocess.run(
            ["journalctl", "-u", "crond", "--since", f"{today} 00:00:00", "--no-pager"],
            capture_output=True, text=True, timeout=10
        )
        lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        # 统计执行的命令
        cmd_count = sum(1 for l in lines if 'CMD' in l)
        
        # 检查错误
        errors = [l for l in lines if 'error' in l.lower() or 'failed' in l.lower()]
        
        status = "OK" if cmd_count > 0 else "NO_EXECUTIONS"
        if errors:
            status = "HAS_ERRORS"
        
        results.append({
            "time": now.strftime("%H:%M"),
            "status": status,
            "cmds_today": cmd_count,
            "errors": len(errors)
        })
    except Exception as e:
        results.append({"time": now.strftime("%H:%M"), "status": "CHECK_FAILED", "error": str(e)})
    
    # 输出结果
    for r in results:
        print(f"[{r['time']}] {r['status']} - cmds_today={r.get('cmds_today', 'N/A')}, errors={r.get('errors', 'N/A')}")

if __name__ == "__main__":
    check_cron_health()

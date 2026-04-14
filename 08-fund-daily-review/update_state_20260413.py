#!/usr/bin/env python3
"""
手动更新 2026-04-13 日终数据
根据用户截图数据更新 state.json 和 ledger.jsonl
"""

import json
from datetime import datetime

BASE_DIR = "/home/admin/.openclaw/workspace/Semi-automatic-artificial-intelligence-system/08-fund-daily-review"

# 从截图提取的数据（2026-04-13）
# 格式：{code: {daily_pnl, cumulative_pnl, pnl_rate, market_value}}
today_data = {
    "011612": {
        "name": "华夏科创 50ETF 联接 A",
        "daily_pnl": 2.95,      # 今日收益
        "cumulative_pnl": 6.24,  # 累计收益 (3.29 + 2.95)
        "pnl_rate": 1.56,        # 累计收益率
        "market_value": 405.76   # 持仓市值 (399.52 + 6.24)
    },
    "013180": {
        "name": "广发新能源车电池 ETF 联接 C",
        "daily_pnl": 5.70,
        "cumulative_pnl": 1.68,   # -4.02 + 5.70
        "pnl_rate": 0.56,
        "market_value": 301.68
    },
    "014320": {
        "name": "德邦半导体产业混合 C",
        "daily_pnl": 1.24,
        "cumulative_pnl": 13.42,  # 12.18 + 1.24
        "pnl_rate": 4.47,
        "market_value": 313.42
    }
}

# 计算总计
total_daily_pnl = sum(d["daily_pnl"] for d in today_data.values())
total_cumulative_pnl = sum(d["cumulative_pnl"] for d in today_data.values())
total_market_value = sum(d["market_value"] for d in today_data.values())

print(f"📊 2026-04-13 数据更新")
print(f"   今日盈亏：+{total_daily_pnl:.2f} 元")
print(f"   累计盈亏：+{total_cumulative_pnl:.2f} 元")
print(f"   组合市值：{total_market_value:.2f} 元")

# 读取当前 state.json
with open(f"{BASE_DIR}/state.json", "r") as f:
    state = json.load(f)

# 更新 positions
for pos in state["positions"]:
    code = pos["code"]
    if code in today_data:
        data = today_data[code]
        pos["daily_pnl"] = data["daily_pnl"]
        pos["last_pnl"] = data["cumulative_pnl"]  # last_pnl 表示累计盈亏
        pos["pnl_rate"] = data["pnl_rate"]
        pos["market_value"] = data["market_value"]
        pos["nav_date"] = "2026-04-13"
        pos["last_updated"] = "2026-04-13T22:30:00.000000"
        pos["last_pnl_date"] = "2026-04-13"
        pos["last_update_time"] = "2026-04-13T22:30:00.000000"

# 更新总体数据
state["portfolio_value"] = total_market_value
state["total_market_value"] = total_market_value
state["total_pnl"] = total_cumulative_pnl
state["total_pnl_rate"] = round((total_cumulative_pnl / state["principal"]) * 100, 2)
state["last_updated"] = "2026-04-13T22:30:00.000000"
state["last_update_time"] = "2026-04-13T22:30:00.000000"
state["manual_update"] = True
state["last_manual_date"] = "2026-04-13"
state["last_manual_note"] = "根据 4 月 13 日截图手动更新数据"

# 保存 state.json
with open(f"{BASE_DIR}/state.json", "w") as f:
    json.dump(state, f, indent=2, ensure_ascii=False)

print(f"✅ state.json 已更新")

# 添加到 ledger.jsonl
ledger_entry = {
    "timestamp": "2026-04-13T22:30:00+08:00",
    "source": "manual",
    "action": "daily_pnl_update",
    "date": "2026-04-13",
    "total_pnl": total_daily_pnl,
    "positions": [
        {"code": code, "name": data["name"], "daily_pnl": data["daily_pnl"]}
        for code, data in today_data.items()
    ],
    "note": "4 月 13 日收益（根据用户截图手动更新）"
}

with open(f"{BASE_DIR}/ledger.jsonl", "a") as f:
    f.write(json.dumps(ledger_entry, ensure_ascii=False) + "\n")

print(f"✅ ledger.jsonl 已追加记录")
print(f"\n📋 更新详情：")
for code, data in today_data.items():
    print(f"   {code} {data['name']}: 今日 +{data['daily_pnl']:.2f} 元，累计 +{data['cumulative_pnl']:.2f} 元")

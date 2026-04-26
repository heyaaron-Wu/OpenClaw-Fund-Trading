#!/usr/bin/env python3
"""
基金止盈止损监控脚本
交易日 15:30 检查持仓盈亏，止盈/止损阈值告警

功能:
1. 加载持仓数据和当日盈亏
2. 分析各基金盈亏状态
3. 识别止盈 (>15%) / 止损 (<-8%) 机会
4. 飞书推送告警
"""

import sys
import json
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

# 配置
STATE_PATH = Path("/home/admin/.openclaw/workspace/Semi-automatic-artificial-intelligence-system/08-fund-daily-review/state.json")
LEDGER_PATH = Path("/home/admin/.openclaw/workspace/Semi-automatic-artificial-intelligence-system/08-fund-daily-review/ledger.jsonl")
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/f1286a3e-4e41-4809-a0bc-fd2bbbbc3f10"

# 止盈止损阈值
TAKE_PROFIT_THRESHOLD = 0.15  # 15% 止盈
STOP_LOSS_THRESHOLD = -0.08   # -8% 止损
WARNING_HIGH = 0.10           # 10% 高位预警
WARNING_LOW = -0.05           # -5% 低位预警


def load_state():
    """加载状态文件"""
    if not STATE_PATH.exists():
        return None
    return json.loads(STATE_PATH.read_text(encoding='utf-8'))


def load_latest_ledger():
    """加载最新交易日账本"""
    if not LEDGER_PATH.exists():
        return None
    
    lines = LEDGER_PATH.read_text(encoding='utf-8').strip().split('\n')
    if not lines:
        return None
    
    # 读取最后一行 (最新交易日)
    return json.loads(lines[-1])


def check_pnl_thresholds(state, ledger):
    """
    检查盈亏阈值
    
    返回:
    - alerts: 需要告警的基金列表
    - summary: 汇总信息
    """
    alerts = []
    total_pnl = state.get('total_pnl', 0) if state else 0
    total_pnl_rate = state.get('total_pnl_rate', 0) if state else 0
    
    # 检查组合整体状态
    portfolio_alert = None
    if total_pnl_rate >= TAKE_PROFIT_THRESHOLD * 100:
        portfolio_alert = {
            'type': 'take_profit',
            'level': 'critical',
            'message': f'组合整体止盈信号！累计收益 {total_pnl_rate:+.2f}%',
            'pnl_rate': total_pnl_rate
        }
    elif total_pnl_rate <= STOP_LOSS_THRESHOLD * 100:
        portfolio_alert = {
            'type': 'stop_loss',
            'level': 'critical',
            'message': f'组合整体止损信号！累计收益 {total_pnl_rate:+.2f}%',
            'pnl_rate': total_pnl_rate
        }
    elif total_pnl_rate >= WARNING_HIGH * 100:
        portfolio_alert = {
            'type': 'warning_high',
            'level': 'warning',
            'message': f'组合高位预警！累计收益 {total_pnl_rate:+.2f}%',
            'pnl_rate': total_pnl_rate
        }
    elif total_pnl_rate <= WARNING_LOW * 100:
        portfolio_alert = {
            'type': 'warning_low',
            'level': 'warning',
            'message': f'组合低位预警！累计收益 {total_pnl_rate:+.2f}%',
            'pnl_rate': total_pnl_rate
        }
    
    if portfolio_alert:
        alerts.append(portfolio_alert)
    
    # 检查单个基金 (如果有持仓详情)
    positions = state.get('positions', []) if state else []
    for pos in positions:
        code = pos.get('code', '未知')
        name = pos.get('name', pos.get('fund', '未知基金'))
        pnl_rate = pos.get('pnl_rate', 0)
        unrealized_pnl = pos.get('unrealized_pnl', 0)
        
        fund_alert = None
        if pnl_rate >= TAKE_PROFIT_THRESHOLD * 100:
            fund_alert = {
                'type': 'take_profit',
                'level': 'critical',
                'code': code,
                'name': name,
                'message': f'🎯 止盈信号：{name} ({code}) 收益 {pnl_rate:+.2f}% ({unrealized_pnl:+.2f}元)',
                'pnl_rate': pnl_rate
            }
        elif pnl_rate <= STOP_LOSS_THRESHOLD * 100:
            fund_alert = {
                'type': 'stop_loss',
                'level': 'critical',
                'code': code,
                'name': name,
                'message': f'🛑 止损信号：{name} ({code}) 收益 {pnl_rate:+.2f}% ({unrealized_pnl:+.2f}元)',
                'pnl_rate': pnl_rate
            }
        elif pnl_rate >= WARNING_HIGH * 100:
            fund_alert = {
                'type': 'warning_high',
                'level': 'warning',
                'code': code,
                'name': name,
                'message': f'⚠️ 高位预警：{name} ({code}) 收益 {pnl_rate:+.2f}%',
                'pnl_rate': pnl_rate
            }
        elif pnl_rate <= WARNING_LOW * 100:
            fund_alert = {
                'type': 'warning_low',
                'level': 'warning',
                'code': code,
                'name': name,
                'message': f'⚠️ 低位预警：{name} ({code}) 收益 {pnl_rate:+.2f}%',
                'pnl_rate': pnl_rate
            }
        
        if fund_alert:
            alerts.append(fund_alert)
    
    summary = {
        'total_pnl': total_pnl,
        'total_pnl_rate': total_pnl_rate,
        'alert_count': len(alerts),
        'critical_count': sum(1 for a in alerts if a.get('level') == 'critical'),
        'warning_count': sum(1 for a in alerts if a.get('level') == 'warning')
    }
    
    return alerts, summary


def send_feishu_alert(alerts, summary, ledger):
    """发送飞书告警"""
    if not alerts:
        print("✅ 无阈值告警，跳过推送")
        return True
    
    # 构建告警卡片
    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d %H:%M')
    trading_date = ledger.get('date', '未知') if ledger else '未知'
    
    # 确定卡片颜色和标题
    if summary['critical_count'] > 0:
        template = 'red'
        title = '🚨 止盈止损告警'
    else:
        template = 'orange'
        title = '⚠️ 盈亏预警'
    
    # 构建告警内容
    alert_lines = []
    for alert in alerts:
        alert_lines.append(f"{alert['message']}")
    
    alert_content = '\n'.join(alert_lines)
    
    card = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": title},
                "template": template
            },
            "elements": [
                {
                    "tag": "markdown",
                    "content": f"**交易日期**: {trading_date}\n**检查时间**: {date_str}\n\n{alert_content}"
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**组合累计**: {summary['total_pnl']:+.2f}元 ({summary['total_pnl_rate']:+.2f}%)"
                    }
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": f"告警数量：{summary['alert_count']} (严重：{summary['critical_count']}, 预警：{summary['warning_count']})"
                        }
                    ]
                }
            ]
        }
    }
    
    # 发送请求
    try:
        data = json.dumps(card, ensure_ascii=False).encode('utf-8')
        req = urllib.request.Request(
            FEISHU_WEBHOOK,
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get('code') == 0:
                print(f"✅ 飞书告警已发送 ({len(alerts)} 条)")
                return True
            else:
                print(f"❌ 飞书推送失败：{result}")
                return False
    except Exception as e:
        print(f"❌ 发送告警异常：{e}")
        return False


def main():
    print(f"🔍 基金止盈止损监控 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 加载数据
    state = load_state()
    ledger = load_latest_ledger()
    
    if not state:
        print("❌ 无法加载状态文件")
        return 1
    
    if not ledger:
        print("❌ 无法加载账本数据")
        return 1
    
    print(f"📊 交易日期：{ledger.get('date', '未知')}")
    print(f"📈 组合总值：{state.get('portfolio_value', 0):.2f} 元")
    print(f"📊 累计盈亏：{state.get('total_pnl', 0):+.2f} 元 ({state.get('total_pnl_rate', 0):+.2f}%)")
    print()
    
    # 检查阈值
    alerts, summary = check_pnl_thresholds(state, ledger)
    
    print(f"🔔 告警数量：{summary['alert_count']} (严重：{summary['critical_count']}, 预警：{summary['warning_count']})")
    
    if alerts:
        print()
        print("告警详情:")
        for alert in alerts:
            print(f"  - {alert['message']}")
        print()
        
        # 发送飞书告警
        send_feishu_alert(alerts, summary, ledger)
    else:
        print("✅ 无阈值告警")
    
    print("=" * 50)
    print("✅ 监控完成")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

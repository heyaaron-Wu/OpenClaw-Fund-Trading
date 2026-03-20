#!/usr/bin/env python3
"""
场外执行模拟器 (Off-Exchange Execution Simulator)
验证 T+ 确认、结算、现金可用性

T+ 规则:
- T 日 15:00 前申购：T+1 确认，T+2 可赎
- T 日 15:00 前赎回：T+1 确认，T+2-T+4 现金可用
- 禁止同日申赎 (round-trip)
"""

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys

# 导入交易日历
sys.path.insert(0, str(Path(__file__).parent))
from trading_calendar import is_trading_day, get_next_trading_day, get_prev_trading_day


def parse_date(date_str: str) -> datetime:
    """解析日期字符串"""
    if not date_str:
        return datetime.now()
    
    formats = ['%Y%m%d', '%Y-%m-%d', '%Y/%m/%d']
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"无法解析日期：{date_str}")


def simulate_subscription(fund_code: str, 
                         execution_date: str,
                         execution_time: str = None) -> dict:
    """
    模拟基金申购执行
    
    Args:
        fund_code: 基金代码
        execution_date: 执行日期 (YYYYMMDD 或 YYYY-MM-DD)
        execution_time: 执行时间 (HH:MM，可选)
        
    Returns:
        模拟结果字典
    """
    
    exec_dt = parse_date(execution_date)
    exec_date_str = exec_dt.strftime('%Y%m%d')
    
    # 检查是否交易日
    if not is_trading_day(exec_date_str):
        return {
            'feasible': False,
            'action': 'SUBSCRIBE',
            'fund_code': fund_code,
            'reason': f'{exec_date_str} 不是交易日',
            'next_feasible_date': get_next_trading_day(exec_date_str)
        }
    
    # 检查截止时间
    if execution_time:
        hour, minute = map(int, execution_time.split(':'))
        exec_minutes = hour * 60 + minute
        deadline_minutes = 15 * 60  # 15:00
        
        if exec_minutes >= deadline_minutes:
            return {
                'feasible': False,
                'action': 'SUBSCRIBE',
                'fund_code': fund_code,
                'reason': f'已过今日 15:00 截止时间 (当前：{execution_time})',
                'next_feasible_date': get_next_trading_day(exec_date_str)
            }
    
    # 计算关键日期
    t_date = exec_date_str
    t1_date = get_next_trading_day(t_date)
    t2_date = get_next_trading_day(t1_date)
    
    return {
        'feasible': True,
        'action': 'SUBSCRIBE',
        'fund_code': fund_code,
        'timeline': {
            'execution_date': t_date,
            'execution_datetime': f"{t_date} {execution_time or '15:00'}",
            'confirmation_date': t1_date,
            'available_for_redemption': t2_date
        },
        'cash_impact': {
            'type': 'immediate_debit',
            'description': '申购资金立即冻结，T+1 日确认份额'
        },
        'rules': {
            't_plus_confirmation': 'T+1',
            't_plus_settlement': 'T+1',
            'earliest_redemption': 'T+2'
        }
    }


def simulate_redemption(fund_code: str,
                       execution_date: str,
                       execution_time: str = None,
                       current_shares: float = None) -> dict:
    """
    模拟基金赎回执行
    
    Args:
        fund_code: 基金代码
        execution_date: 执行日期
        execution_time: 执行时间
        current_shares: 当前持有份额 (可选)
        
    Returns:
        模拟结果字典
    """
    
    exec_dt = parse_date(execution_date)
    exec_date_str = exec_dt.strftime('%Y%m%d')
    
    # 检查是否交易日
    if not is_trading_day(exec_date_str):
        return {
            'feasible': False,
            'action': 'REDEEM',
            'fund_code': fund_code,
            'reason': f'{exec_date_str} 不是交易日',
            'next_feasible_date': get_next_trading_day(exec_date_str)
        }
    
    # 检查截止时间
    if execution_time:
        hour, minute = map(int, execution_time.split(':'))
        exec_minutes = hour * 60 + minute
        deadline_minutes = 15 * 60
        
        if exec_minutes >= deadline_minutes:
            return {
                'feasible': False,
                'action': 'REDEEM',
                'fund_code': fund_code,
                'reason': f'已过今日 15:00 截止时间',
                'next_feasible_date': get_next_trading_day(exec_date_str)
            }
    
    # 计算关键日期
    t_date = exec_date_str
    t1_date = get_next_trading_day(t_date)
    t2_date = get_next_trading_day(t1_date)
    t3_date = get_next_trading_day(t2_date)
    t4_date = get_next_trading_day(t3_date)
    
    return {
        'feasible': True,
        'action': 'REDEEM',
        'fund_code': fund_code,
        'timeline': {
            'execution_date': t_date,
            'execution_datetime': f"{t_date} {execution_time or '15:00'}",
            'confirmation_date': t1_date,
            'cash_available_date': t4_date,
            'cash_available_range': f"{t2_date} ~ {t4_date}"
        },
        'cash_impact': {
            'type': 'delayed_credit',
            'description': '赎回资金 T+2 到 T+4 日到账',
            'current_shares': current_shares
        },
        'rules': {
            't_plus_confirmation': 'T+1',
            't_plus_settlement': 'T+2 ~ T+4',
            'cash_availability': 'T+2 ~ T+4'
        }
    }


def check_round_trip(subscribe_date: str, 
                    redeem_date: str) -> dict:
    """
    检查同日申赎 (禁止的 round-trip 操作)
    
    Args:
        subscribe_date: 申购日期
        redeem_date: 赎回日期
        
    Returns:
        检查结果
    """
    
    if subscribe_date == redeem_date:
        return {
            'allowed': False,
            'reason': '场外基金禁止同日申赎 (T+ 规则限制)',
            'min_holding_period': '2 个交易日',
            'earliest_redemption_date': get_next_trading_day(
                get_next_trading_day(subscribe_date)
            )
        }
    
    # 检查是否满足最短持有期
    t1 = parse_date(subscribe_date)
    t2 = parse_date(redeem_date)
    
    # 计算交易日间隔
    trading_days = 0
    current = get_next_trading_day(subscribe_date)
    while current <= redeem_date:
        trading_days += 1
        current = get_next_trading_day(current)
    
    if trading_days < 2:
        return {
            'allowed': False,
            'reason': f'持有期不足 (当前：{trading_days} 交易日，要求：>=2)',
            'min_holding_period': '2 个交易日',
            'earliest_redemption_date': get_next_trading_day(
                get_next_trading_day(subscribe_date)
            )
        }
    
    return {
        'allowed': True,
        'holding_period_days': trading_days,
        'message': '满足持有期要求'
    }


def simulate_execution(fund_code: str,
                      action: str,
                      execution_date: str,
                      execution_time: str = None,
                      **kwargs) -> dict:
    """
    通用执行模拟入口
    
    Args:
        fund_code: 基金代码
        action: 操作类型 ('SUBSCRIBE', 'REDEEM', 'CHECK_ROUND_TRIP')
        execution_date: 执行日期
        execution_time: 执行时间
        **kwargs: 其他参数
        
    Returns:
        模拟结果
    """
    
    if action.upper() == 'SUBSCRIBE':
        return simulate_subscription(
            fund_code, execution_date, execution_time
        )
    
    elif action.upper() == 'REDEEM':
        return simulate_redemption(
            fund_code, execution_date, execution_time,
            kwargs.get('current_shares')
        )
    
    elif action.upper() == 'CHECK_ROUND_TRIP':
        return check_round_trip(
            kwargs.get('subscribe_date', execution_date),
            kwargs.get('redeem_date')
        )
    
    else:
        return {
            'feasible': False,
            'reason': f'未知操作类型：{action}',
            'supported_actions': ['SUBSCRIBE', 'REDEEM', 'CHECK_ROUND_TRIP']
        }


def format_execution_report(result: dict, compact: bool = False) -> str:
    """
    格式化执行模拟报告
    
    Args:
        result: 模拟结果
        compact: 是否精简输出
        
    Returns:
        格式化文本
    """
    
    if not result.get('feasible', False):
        if compact:
            return f"❌ 不可行：{result.get('reason', '未知原因')}"
        
        lines = []
        lines.append("=" * 60)
        lines.append("❌ 执行不可行")
        lines.append("=" * 60)
        lines.append(f"原因：{result.get('reason')}")
        
        if result.get('next_feasible_date'):
            lines.append(f"下一可行日期：{result['next_feasible_date']}")
        
        if result.get('earliest_redemption_date'):
            lines.append(f"最早赎回日期：{result['earliest_redemption_date']}")
        
        return "\n".join(lines)
    
    # 可行的执行
    if compact:
        timeline = result.get('timeline', {})
        return (
            f"✅ 可行 | "
            f"确认：{timeline.get('confirmation_date', 'N/A')} | "
            f"可用：{timeline.get('cash_available_date', timeline.get('available_for_redemption', 'N/A'))}"
        )
    
    lines = []
    lines.append("=" * 60)
    lines.append(f"✅ 执行可行 - {result['action']} {result['fund_code']}")
    lines.append("=" * 60)
    lines.append("")
    
    # 时间线
    timeline = result.get('timeline', {})
    if timeline:
        lines.append("时间线:")
        for key, value in timeline.items():
            key_zh = key.replace('_', ' ').title()
            lines.append(f"  {key_zh}: {value}")
        lines.append("")
    
    # 资金影响
    cash_impact = result.get('cash_impact', {})
    if cash_impact:
        lines.append("资金影响:")
        lines.append(f"  类型：{cash_impact.get('type', 'N/A')}")
        lines.append(f"  说明：{cash_impact.get('description', 'N/A')}")
        lines.append("")
    
    # 规则
    rules = result.get('rules', {})
    if rules:
        lines.append("T+ 规则:")
        for key, value in rules.items():
            key_zh = key.replace('_', ' ').title()
            lines.append(f"  {key_zh}: {value}")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description='场外执行模拟器')
    parser.add_argument('--fund', type=str, required=True, help='基金代码')
    parser.add_argument('--action', type=str, required=True,
                       choices=['subscribe', 'redeem', 'round-trip'],
                       help='操作类型')
    parser.add_argument('--date', type=str, default='',
                       help='执行日期 (YYYYMMDD 或 YYYY-MM-DD，默认今天)')
    parser.add_argument('--time', type=str, default=None,
                       help='执行时间 (HH:MM)')
    parser.add_argument('--subscribe-date', type=str,
                       help='申购日期 (用于 round-trip 检查)')
    parser.add_argument('--redeem-date', type=str,
                       help='赎回日期 (用于 round-trip 检查)')
    parser.add_argument('--shares', type=float, default=None,
                       help='当前持有份额 (用于赎回模拟)')
    parser.add_argument('--output', type=str, help='输出 JSON 文件路径')
    parser.add_argument('--compact', action='store_true', help='精简输出')
    
    args = parser.parse_args()
    
    # 执行模拟
    if args.action == 'round-trip':
        result = check_round_trip(
            args.subscribe_date or args.date,
            args.redeem_date or args.date
        )
    else:
        result = simulate_execution(
            fund_code=args.fund,
            action=args.action.upper(),
            execution_date=args.date,
            execution_time=args.time,
            current_shares=args.shares
        )
    
    # 输出报告
    report = format_execution_report(result, compact=args.compact)
    print(report)
    
    # 保存到文件
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2, default=str),
            encoding='utf-8'
        )
        print(f"\n[INFO] 结果已保存至：{args.output}")


if __name__ == "__main__":
    main()

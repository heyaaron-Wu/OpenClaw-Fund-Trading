#!/usr/bin/env python3
"""
市场门控检查器 (Market Gate Checker)
整合交易日历 + 时间窗口 + 执行截止

时间窗口规则:
- 09:00-11:30: 早盘可执行
- 13:00-14:48: 午盘可执行 (推荐)
- 14:48-15:00: 最后确认窗口
- 15:00 后：禁止执行
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
import sys

# 导入交易日历
sys.path.insert(0, str(Path(__file__).parent))
from trading_calendar import is_trading_day, check_market_status, get_next_trading_day


def validate_execution_window(action_time: str = None) -> dict:
    """
    验证执行时间窗口
    
    Args:
        action_time: 执行时间 (HH:MM:SS 或 HH:MM，默认当前时间)
        
    Returns:
        验证结果字典
    """
    
    # 获取当前市场状态
    status = check_market_status()
    
    # 解析执行时间
    if action_time:
        try:
            if len(action_time.split(':')) == 2:
                hour, minute = map(int, action_time.split(':'))
                second = 0
            else:
                hour, minute, second = map(int, action_time.split(':'))
            
            now = datetime.now()
            current_dt = now.replace(hour=hour, minute=minute, second=second, microsecond=0)
            current_minutes = hour * 60 + minute
        except ValueError as e:
            return {
                'allowed': False,
                'reason': f'时间格式错误：{action_time} (应为 HH:MM 或 HH:MM:SS)',
                'error': str(e)
            }
    else:
        # 使用当前时间
        now = datetime.now()
        current_dt = now
        current_minutes = now.hour * 60 + now.minute
    
    # === 检查是否交易日 ===
    date_str = current_dt.strftime('%Y%m%d')
    if not is_trading_day(date_str):
        return {
            'allowed': False,
            'reason': '非交易日',
            'date': date_str,
            'next_trading_day': get_next_trading_day(date_str),
            'market_status': 'closed'
        }
    
    # === 时间窗口检查 ===
    
    # 定义时间窗口 (分钟数)
    MORNING_START = 9 * 60 + 30    # 09:30
    MORNING_END = 11 * 60 + 30     # 11:30
    AFTERNOON_START = 13 * 60      # 13:00
    AFTERNOON_OPTIMAL_END = 14 * 60 + 48  # 14:48
    AFTERNOON_FINAL_END = 15 * 60  # 15:00
    
    # 判断时间段
    if current_minutes < MORNING_START:
        # 开盘前
        minutes_to_open = MORNING_START - current_minutes
        return {
            'allowed': False,
            'reason': '未到开盘时间',
            'current_time': current_dt.strftime('%H:%M:%S'),
            'market_open': '09:30',
            'minutes_to_open': minutes_to_open,
            'market_status': 'pre_market'
        }
    
    elif MORNING_START <= current_minutes <= MORNING_END:
        # 早盘时段
        remaining_minutes = MORNING_END - current_minutes
        return {
            'allowed': True,
            'reason': '早盘交易时段',
            'current_time': current_dt.strftime('%H:%M:%S'),
            'time_window': 'morning',
            'time_window_zh': '早盘',
            'recommendation': 'ALLOWED_BUT_NOT_OPTIMAL',
            'recommendation_zh': '可执行但非最优',
            'remaining_minutes': remaining_minutes,
            'optimal_window': '13:00-14:48 (午盘)',
            'market_status': 'open'
        }
    
    elif MORNING_END < current_minutes < AFTERNOON_START:
        # 午休时段
        minutes_to_afternoon = AFTERNOON_START - current_minutes
        return {
            'allowed': False,
            'reason': '午休时段',
            'current_time': current_dt.strftime('%H:%M:%S'),
            'afternoon_open': '13:00',
            'minutes_to_afternoon': minutes_to_afternoon,
            'market_status': 'lunch_break'
        }
    
    elif AFTERNOON_START <= current_minutes <= AFTERNOON_OPTIMAL_END:
        # 午盘最优时段 (13:00-14:48)
        remaining_minutes = AFTERNOON_FINAL_END - current_minutes
        return {
            'allowed': True,
            'reason': '午盘交易时段 (最优窗口)',
            'current_time': current_dt.strftime('%H:%M:%S'),
            'time_window': 'afternoon_optimal',
            'time_window_zh': '午盘 (最优)',
            'recommendation': 'OPTIMAL',
            'recommendation_zh': '最优执行窗口',
            'remaining_minutes': remaining_minutes,
            'deadline': '15:00',
            'deadline_message': f'距离截止还有 {remaining_minutes // 60}小时{remaining_minutes % 60}分钟',
            'market_status': 'open'
        }
    
    elif AFTERNOON_OPTIMAL_END < current_minutes < AFTERNOON_FINAL_END:
        # 最后确认窗口 (14:48-15:00)
        remaining_minutes = AFTERNOON_FINAL_END - current_minutes
        return {
            'allowed': True,
            'reason': '最后确认窗口',
            'current_time': current_dt.strftime('%H:%M:%S'),
            'time_window': 'final_confirmation',
            'time_window_zh': '最后确认',
            'recommendation': 'URGENT',
            'recommendation_zh': '紧急 - 即将截止',
            'remaining_minutes': remaining_minutes,
            'deadline': '15:00',
            'deadline_message': f'⚠️ 距离截止仅剩 {remaining_minutes} 分钟',
            'market_status': 'open',
            'warning': '请立即执行决策'
        }
    
    else:
        # 15:00 后
        return {
            'allowed': False,
            'reason': '已过交易截止时间',
            'current_time': current_dt.strftime('%H:%M:%S'),
            'deadline': '15:00',
            'next_execution_window': f'{get_next_trading_day(date_str)} 09:30',
            'market_status': 'closed'
        }


def check_gate_conditions(evidence_freshness_minutes: int = None,
                         evidence_path: str = None) -> dict:
    """
    检查门控条件
    
    Args:
        evidence_freshness_minutes: 证据新鲜度 (分钟)
        evidence_path: 证据文件路径 (可选，用于自动检查新鲜度)
        
    Returns:
        门控检查结果
    """
    
    # 检查时间窗口
    time_check = validate_execution_window()
    
    if not time_check['allowed']:
        return {
            'gate_passed': False,
            'reason': time_check['reason'],
            'time_check': time_check,
            'evidence_check': None
        }
    
    # 检查证据新鲜度
    evidence_check = None
    if evidence_path:
        try:
            evidence_path_obj = Path(evidence_path)
            if evidence_path_obj.exists():
                mtime = datetime.fromtimestamp(evidence_path_obj.stat().st_mtime)
                freshness = (datetime.now() - mtime).total_seconds() / 60
                
                evidence_check = {
                    'file': str(evidence_path),
                    'freshness_minutes': round(freshness, 1),
                    'fresh': freshness <= 30,
                    'warning': freshness > 30
                }
            else:
                evidence_check = {
                    'file': str(evidence_path),
                    'error': '文件不存在'
                }
        except Exception as e:
            evidence_check = {
                'file': str(evidence_path),
                'error': str(e)
            }
    
    elif evidence_freshness_minutes is not None:
        evidence_check = {
            'freshness_minutes': evidence_freshness_minutes,
            'fresh': evidence_freshness_minutes <= 30,
            'warning': evidence_freshness_minutes > 30
        }
    
    # 综合判断
    gate_passed = time_check['allowed']
    if evidence_check and 'fresh' in evidence_check:
        gate_passed = gate_passed and evidence_check['fresh']
    
    return {
        'gate_passed': gate_passed,
        'time_check': time_check,
        'evidence_check': evidence_check,
        'checked_at': datetime.now().isoformat()
    }


def format_gate_report(result: dict, compact: bool = False) -> str:
    """
    格式化门控检查报告
    
    Args:
        result: 检查结果
        compact: 是否精简输出
        
    Returns:
        格式化文本
    """
    
    if compact:
        if result['gate_passed']:
            time_info = result.get('time_check', {})
            remaining = time_info.get('remaining_minutes', 0)
            return f"✅ 门控通过 | 剩余 {remaining} 分钟"
        else:
            reason = result.get('reason', '未知原因')
            return f"❌ 门控未通过：{reason}"
    
    lines = []
    lines.append("=" * 60)
    
    if result['gate_passed']:
        lines.append("✅ 门控检查通过")
    else:
        lines.append("❌ 门控检查未通过")
    
    lines.append("=" * 60)
    lines.append("")
    
    # 时间窗口检查
    time_check = result.get('time_check', {})
    if time_check:
        lines.append("时间窗口检查:")
        lines.append(f"  状态：{'✅ 允许' if time_check.get('allowed') else '❌ 禁止'}")
        lines.append(f"  原因：{time_check.get('reason', 'N/A')}")
        
        if time_check.get('current_time'):
            lines.append(f"  当前时间：{time_check['current_time']}")
        
        if time_check.get('recommendation'):
            rec_zh = time_check.get('recommendation_zh', time_check['recommendation'])
            lines.append(f"  建议：{rec_zh}")
        
        if time_check.get('remaining_minutes'):
            lines.append(f"  剩余时间：{time_check['remaining_minutes']} 分钟")
        
        if time_check.get('deadline_message'):
            lines.append(f"  截止：{time_check['deadline_message']}")
        
        lines.append("")
    
    # 证据新鲜度检查
    evidence_check = result.get('evidence_check', {})
    if evidence_check:
        lines.append("证据新鲜度检查:")
        
        if 'error' in evidence_check:
            lines.append(f"  错误：{evidence_check['error']}")
        else:
            freshness = evidence_check.get('freshness_minutes', 0)
            fresh = evidence_check.get('fresh', False)
            lines.append(f"  新鲜度：{freshness} 分钟")
            lines.append(f"  状态：{'✅ 新鲜 (<=30 分钟)' if fresh else '⚠️ 过期 (>30 分钟)'}")
            
            if evidence_check.get('warning'):
                lines.append("  ⚠️ 警告：证据可能过期，建议刷新")
        
        lines.append("")
    
    # 最终结论
    lines.append("-" * 60)
    if result['gate_passed']:
        lines.append("结论：✅ 可以执行交易决策")
    else:
        lines.append("结论：❌ 禁止执行交易决策")
        
        if time_check.get('next_execution_window'):
            lines.append(f"下一执行窗口：{time_check['next_execution_window']}")
        elif time_check.get('next_trading_day'):
            lines.append(f"下一交易日：{time_check['next_trading_day']}")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description='市场门控检查器')
    parser.add_argument('--time', type=str, default=None,
                       help='检查时间 (HH:MM:SS 或 HH:MM，默认当前时间)')
    parser.add_argument('--evidence', type=str, default=None,
                       help='证据文件路径 (用于检查新鲜度)')
    parser.add_argument('--freshness', type=int, default=None,
                       help='证据新鲜度 (分钟，手动指定)')
    parser.add_argument('--output', type=str, help='输出 JSON 文件路径')
    parser.add_argument('--compact', action='store_true', help='精简输出')
    
    args = parser.parse_args()
    
    # 执行门控检查
    result = check_gate_conditions(
        evidence_freshness_minutes=args.freshness,
        evidence_path=args.evidence
    )
    
    # 输出报告
    report = format_gate_report(result, compact=args.compact)
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
    
    # 返回退出码 (用于 cron 脚本)
    if not result['gate_passed']:
        sys.exit(1)


if __name__ == "__main__":
    main()

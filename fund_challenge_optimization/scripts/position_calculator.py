#!/usr/bin/env python3
"""
仓位计算器 (Position Calculator)
根据置信度和风险限制计算目标仓位

仓位分档:
- High confidence: +35% to +55% incremental exposure
- Medium confidence: +20% to +35%
- Low confidence: 0% (HOLD)

风险限制:
- Max single-day additional exposure: 55%
- Max single-theme concentration: 60%
- Portfolio de-risk trigger: drawdown <= -8%
"""

import argparse
import json
from datetime import datetime
from pathlib import Path


def calculate_position(confidence: str, 
                       current_exposure: float,
                       theme_concentration: float,
                       total_drawdown: float = 0.0) -> dict:
    """
    计算目标仓位
    
    Args:
        confidence: 置信度 ('high', 'medium', 'low')
        current_exposure: 当前总仓位 (0.0-1.0, 负数表示空仓/亏损)
        theme_concentration: 单一主题集中度 (0.0-1.0)
        total_drawdown: 组合总回撤 (负数表示亏损)
        
    Returns:
        包含 action、incremental_exposure、target_exposure、risk_checks 的字典
    """
    
    # 置信度映射到加仓区间
    confidence_bands = {
        'high': (0.35, 0.55),
        'medium': (0.20, 0.35),
        'low': (0.0, 0.0)
    }
    
    min_add, max_add = confidence_bands.get(confidence.lower(), (0.0, 0.0))
    
    # === 应用风险限制 ===
    
    # 1. 单日最大新增限制 (55%)
    single_day_limit = 0.55
    
    # 2. 主题集中度限制 (60%)
    theme_limit = max(0, 0.60 - theme_concentration)
    
    # 3. 总仓位限制 (不超过 100%)
    total_position_limit = max(0, 1.0 - current_exposure)
    
    # 4. 回撤保护 (总回撤 <= -8% 时禁止加仓)
    if total_drawdown <= -0.08:
        max_allowed = 0.0
        de_risk_triggered = True
    else:
        # 取所有限制的最小值
        max_allowed = min(
            max_add,
            single_day_limit,
            theme_limit,
            total_position_limit
        )
        de_risk_triggered = False
    
    # 确定操作
    if max_allowed > 0:
        action = 'BUY'
        # 在允许范围内取中间值
        incremental_exposure = (min_add + max_allowed) / 2
    else:
        action = 'HOLD'
        incremental_exposure = 0.0
    
    target_exposure = current_exposure + incremental_exposure
    
    # 风险检查详情
    risk_checks = {
        'single_day_limit_ok': incremental_exposure <= single_day_limit,
        'theme_concentration_ok': theme_concentration <= 0.60,
        'total_position_ok': target_exposure <= 1.0,
        'drawdown_protection_ok': total_drawdown > -0.08,
        'de_risk_triggered': de_risk_triggered
    }
    
    return {
        'action': action,
        'confidence': confidence,
        'incremental_exposure': round(incremental_exposure, 4),
        'target_exposure': round(target_exposure, 4),
        'current_exposure': round(current_exposure, 4),
        'risk_checks': risk_checks,
        'calculated_at': datetime.now().isoformat()
    }


def calculate_take_profit_position(current_pnl: float, 
                                   catalyst_strength: str,
                                   current_exposure: float) -> dict:
    """
    计算止盈仓位
    
    规则:
    - Soft take-profit: trim if short-window gain >= +7%
    
    Args:
        current_pnl: 当前盈亏比例 (正数表示盈利)
        catalyst_strength: 催化剂强度 ('strong', 'normal', 'weakened')
        current_exposure: 当前仓位
        
    Returns:
        包含 action、trim_ratio、reason 的字典
    """
    
    if current_pnl >= 0.07:  # 盈利 >= 7%
        # 根据催化剂强度决定止盈比例
        if catalyst_strength == 'weakened':
            trim_ratio = 0.5  # 催化剂减弱，止盈 50%
            reason = f"止盈触发 (+{current_pnl:.1%}) + 催化剂减弱"
        elif catalyst_strength == 'normal':
            trim_ratio = 0.3  # 正常催化剂，止盈 30%
            reason = f"止盈触发 (+{current_pnl:.1%})"
        else:  # strong
            trim_ratio = 0.1  # 强催化剂，止盈 10%
            reason = f"部分止盈 (+{current_pnl:.1%})，催化剂仍强"
        
        return {
            'action': 'TRIM',
            'trim_ratio': trim_ratio,
            'remaining_exposure': current_exposure * (1 - trim_ratio),
            'reason': reason,
            'urgency': 'medium'
        }
    else:
        return {
            'action': 'HOLD',
            'trim_ratio': 0.0,
            'remaining_exposure': current_exposure,
            'reason': f"未达止盈线 (+{current_pnl:.1%} < +7%)",
            'urgency': 'low'
        }


def calculate_stop_loss_position(current_pnl: float,
                                 catalyst_strength: str,
                                 current_exposure: float) -> dict:
    """
    计算止损仓位
    
    规则:
    - Hard risk cut: reduce if leg loss <= -5% without strengthened catalyst
    
    Args:
        current_pnl: 当前盈亏比例 (负数表示亏损)
        catalyst_strength: 催化剂强度 ('strong', 'normal', 'weakened')
        current_exposure: 当前仓位
        
    Returns:
        包含 action、cut_ratio、reason 的字典
    """
    
    if current_pnl <= -0.05:  # 亏损 >= 5%
        # 根据催化剂强度决定止损比例
        if catalyst_strength == 'weakened':
            cut_ratio = 1.0  # 催化剂减弱，清仓止损
            reason = f"止损触发 (-{abs(current_pnl):.1%}) + 催化剂减弱"
            urgency = 'high'
        elif catalyst_strength == 'normal':
            cut_ratio = 0.5  # 催化剂正常，止损 50%
            reason = f"止损触发 (-{abs(current_pnl):.1%})"
            urgency = 'high'
        else:  # strong
            cut_ratio = 0.2  # 催化剂仍强，止损 20%
            reason = f"部分止损 (-{abs(current_pnl):.1%})，催化剂仍强"
            urgency = 'medium'
        
        return {
            'action': 'CUT',
            'cut_ratio': cut_ratio,
            'remaining_exposure': current_exposure * (1 - cut_ratio),
            'reason': reason,
            'urgency': urgency
        }
    else:
        return {
            'action': 'HOLD',
            'cut_ratio': 0.0,
            'remaining_exposure': current_exposure,
            'reason': f"未达止损线 (-{abs(current_pnl):.1%} > -5%)",
            'urgency': 'low'
        }


def calculate_portfolio_allocation(signals: list, 
                                   total_capital: float,
                                   max_positions: int = 5) -> dict:
    """
    计算组合仓位分配
    
    Args:
        signals: 信号列表 (每个信号包含 fund_code, confidence, score 等)
        total_capital: 总资金
        max_positions: 最大持仓数量
        
    Returns:
        包含 allocations、total_allocated、remaining_capital 的字典
    """
    
    # 按评分/置信度排序
    sorted_signals = sorted(
        signals, 
        key=lambda x: (x.get('score', 0), x.get('confidence', 'low')),
        reverse=True
    )
    
    # 置信度到仓位的映射
    confidence_to_position = {
        'high': 0.55,
        'medium': 0.35,
        'low': 0.0
    }
    
    allocations = []
    total_allocated = 0.0
    
    for signal in sorted_signals[:max_positions]:
        confidence = signal.get('confidence', 'low')
        position_ratio = confidence_to_position.get(confidence, 0.0)
        
        if position_ratio > 0:
            # 确保不超过总仓位限制
            remaining_ratio = 1.0 - total_allocated
            actual_ratio = min(position_ratio, remaining_ratio)
            
            if actual_ratio > 0:
                allocations.append({
                    'fund_code': signal.get('fund_code'),
                    'fund_name': signal.get('fund_name'),
                    'confidence': confidence,
                    'position_ratio': round(actual_ratio, 4),
                    'capital': round(total_capital * actual_ratio, 2),
                    'score': signal.get('score', 0)
                })
                total_allocated += actual_ratio
    
    return {
        'allocations': allocations,
        'total_allocated': round(total_allocated, 4),
        'remaining_capital': round(total_capital * (1 - total_allocated), 2),
        'position_count': len(allocations),
        'calculated_at': datetime.now().isoformat()
    }


def format_position_report(position_result: dict) -> str:
    """
    格式化仓位报告
    
    Args:
        position_result: 仓位计算结果
        
    Returns:
        格式化文本报告
    """
    lines = []
    lines.append("=" * 60)
    lines.append("仓位计算报告")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"操作：{position_result['action']}")
    lines.append(f"置信度：{position_result['confidence']}")
    lines.append(f"当前仓位：{position_result['current_exposure']:.1%}")
    lines.append(f"新增仓位：{position_result['incremental_exposure']:.1%}")
    lines.append(f"目标仓位：{position_result['target_exposure']:.1%}")
    lines.append("")
    lines.append("风险检查:")
    
    for check, passed in position_result['risk_checks'].items():
        status = "✅" if passed else "❌"
        check_name = check.replace('_', ' ').title()
        lines.append(f"  {status} {check_name}")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description='仓位计算器')
    parser.add_argument('--confidence', type=str, default='medium',
                       choices=['high', 'medium', 'low'],
                       help='置信度级别')
    parser.add_argument('--current-exposure', type=float, default=0.0,
                       help='当前总仓位 (0.0-1.0)')
    parser.add_argument('--theme-concentration', type=float, default=0.0,
                       help='单一主题集中度 (0.0-1.0)')
    parser.add_argument('--drawdown', type=float, default=0.0,
                       help='组合总回撤 (负数表示亏损)')
    parser.add_argument('--pnl', type=float, default=0.0,
                       help='当前盈亏比例')
    parser.add_argument('--catalyst', type=str, default='normal',
                       choices=['strong', 'normal', 'weakened'],
                       help='催化剂强度')
    parser.add_argument('--mode', type=str, default='position',
                       choices=['position', 'take-profit', 'stop-loss', 'allocation'],
                       help='计算模式')
    parser.add_argument('--output', type=str, help='输出 JSON 文件路径')
    parser.add_argument('--compact', action='store_true', help='精简输出')
    
    args = parser.parse_args()
    
    result = None
    
    if args.mode == 'position':
        result = calculate_position(
            confidence=args.confidence,
            current_exposure=args.current_exposure,
            theme_concentration=args.theme_concentration,
            total_drawdown=args.drawdown
        )
        
        if args.compact:
            print(f"[{result['action']}] {result['incremental_exposure']:.1%} "
                  f"(目标：{result['target_exposure']:.1%})")
        else:
            print(format_position_report(result))
    
    elif args.mode == 'take-profit':
        result = calculate_take_profit_position(
            current_pnl=args.pnl,
            catalyst_strength=args.catalyst,
            current_exposure=args.current_exposure
        )
        
        if args.compact:
            print(f"[{result['action']}] {result.get('trim_ratio', 0):.0%} - {result['reason']}")
        else:
            print(f"止盈建议: {result['action']}")
            print(f"比例：{result.get('trim_ratio', 0):.0%}")
            print(f"理由：{result['reason']}")
            print(f"紧急度：{result['urgency']}")
    
    elif args.mode == 'stop-loss':
        result = calculate_stop_loss_position(
            current_pnl=args.pnl,
            catalyst_strength=args.catalyst,
            current_exposure=args.current_exposure
        )
        
        if args.compact:
            print(f"[{result['action']}] {result.get('cut_ratio', 0):.0%} - {result['reason']}")
        else:
            print(f"止损建议：{result['action']}")
            print(f"比例：{result.get('cut_ratio', 0):.0%}")
            print(f"理由：{result['reason']}")
            print(f"紧急度：{result['urgency']}")
    
    elif args.mode == 'allocation':
        # 示例信号数据
        signals = [
            {'fund_code': '018737', 'confidence': 'high', 'score': 85},
            {'fund_code': '017572', 'confidence': 'medium', 'score': 72},
            {'fund_code': '014620', 'confidence': 'medium', 'score': 68}
        ]
        result = calculate_portfolio_allocation(signals, total_capital=1000)
        
        if args.compact:
            print(f"分配：{len(result['allocations'])} 只基金，"
                  f"总仓位 {result['total_allocated']:.1%}")
        else:
            print("组合仓位分配:")
            for alloc in result['allocations']:
                print(f"  {alloc['fund_code']}: {alloc['position_ratio']:.1%} "
                      f"({alloc['capital']} CNY)")
    
    # 输出到文件
    if args.output and result:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2), 
            encoding='utf-8'
        )
        print(f"\n[INFO] 结果已保存至：{args.output}")


if __name__ == "__main__":
    main()

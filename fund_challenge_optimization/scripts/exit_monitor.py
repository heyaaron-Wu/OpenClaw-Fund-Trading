#!/usr/bin/env python3
"""
退出监控器 (Exit Monitor)
监控止损/止盈信号

退出规则:
- Soft take-profit: trim if short-window gain >= +7%
- Hard risk cut: reduce if leg loss <= -5% without strengthened catalyst
"""

import argparse
import json
from datetime import datetime
from pathlib import Path


def check_exit_signals(positions: list, 
                       catalyst_strength_map: dict = None) -> list:
    """
    检查所有持仓的退出信号
    
    Args:
        positions: 持仓列表，每个持仓包含:
            - fund_code: 基金代码
            - fund_name: 基金名称
            - unrealized_pnl_pct: 未实现盈亏比例 (正数盈利，负数亏损)
            - current_exposure: 当前仓位比例
            - catalyst_strength: 催化剂强度 ('strong', 'normal', 'weakened')
        catalyst_strength_map: 基金代码到催化剂强度的映射 (可选)
        
    Returns:
        退出信号列表，按紧急度排序
    """
    
    exit_signals = []
    
    for pos in positions:
        fund_code = pos.get('fund_code', 'N/A')
        fund_name = pos.get('fund_name', 'N/A')
        pnl = pos.get('unrealized_pnl_pct', 0)
        exposure = pos.get('current_exposure', 0)
        
        # 获取催化剂强度 (优先使用持仓中的，其次使用映射表)
        catalyst = pos.get('catalyst_strength', 'normal')
        if catalyst_strength_map and fund_code in catalyst_strength_map:
            catalyst = catalyst_strength_map[fund_code]
        
        signal = None
        
        # === 止盈检查 (PnL >= +7%) ===
        if pnl >= 0.07:
            if catalyst == 'weakened':
                # 催化剂减弱，止盈 50%
                signal = {
                    'fund_code': fund_code,
                    'fund_name': fund_name,
                    'action': 'TRIM',
                    'action_zh': '止盈',
                    'ratio': 0.5,
                    'pnl': pnl,
                    'reason': f'止盈触发 (+{pnl:.1%}) + 催化剂减弱',
                    'urgency': 'medium',
                    'urgency_zh': '中',
                    'suggested_action': f"卖出 {exposure * 0.5:.1%} 仓位"
                }
            elif catalyst == 'normal':
                # 催化剂正常，止盈 30%
                signal = {
                    'fund_code': fund_code,
                    'fund_name': fund_name,
                    'action': 'TRIM',
                    'action_zh': '止盈',
                    'ratio': 0.3,
                    'pnl': pnl,
                    'reason': f'止盈触发 (+{pnl:.1%})',
                    'urgency': 'medium',
                    'urgency_zh': '中',
                    'suggested_action': f"卖出 {exposure * 0.3:.1%} 仓位"
                }
            else:  # strong
                # 催化剂仍强，止盈 10%
                signal = {
                    'fund_code': fund_code,
                    'fund_name': fund_name,
                    'action': 'TRIM',
                    'action_zh': '部分止盈',
                    'ratio': 0.1,
                    'pnl': pnl,
                    'reason': f'部分止盈 (+{pnl:.1%})，催化剂仍强',
                    'urgency': 'low',
                    'urgency_zh': '低',
                    'suggested_action': f"卖出 {exposure * 0.1:.1%} 仓位"
                }
        
        # === 止损检查 (PnL <= -5%) ===
        elif pnl <= -0.05:
            if catalyst == 'weakened':
                # 催化剂减弱，清仓止损
                signal = {
                    'fund_code': fund_code,
                    'fund_name': fund_name,
                    'action': 'CUT',
                    'action_zh': '止损',
                    'ratio': 1.0,
                    'pnl': pnl,
                    'reason': f'止损触发 (-{abs(pnl):.1%}) + 催化剂减弱',
                    'urgency': 'high',
                    'urgency_zh': '高',
                    'suggested_action': f"清仓卖出"
                }
            elif catalyst == 'normal':
                # 催化剂正常，止损 50%
                signal = {
                    'fund_code': fund_code,
                    'fund_name': fund_name,
                    'action': 'CUT',
                    'action_zh': '止损',
                    'ratio': 0.5,
                    'pnl': pnl,
                    'reason': f'止损触发 (-{abs(pnl):.1%})',
                    'urgency': 'high',
                    'urgency_zh': '高',
                    'suggested_action': f"卖出 {exposure * 0.5:.1%} 仓位"
                }
            else:  # strong
                # 催化剂仍强，止损 20%
                signal = {
                    'fund_code': fund_code,
                    'fund_name': fund_name,
                    'action': 'CUT',
                    'action_zh': '部分止损',
                    'ratio': 0.2,
                    'pnl': pnl,
                    'reason': f'部分止损 (-{abs(pnl):.1%})，催化剂仍强',
                    'urgency': 'medium',
                    'urgency_zh': '中',
                    'suggested_action': f"卖出 {exposure * 0.2:.1%} 仓位"
                }
        
        if signal:
            signal['checked_at'] = datetime.now().isoformat()
            exit_signals.append(signal)
    
    # 按紧急度排序 (high > medium > low)
    urgency_order = {'high': 0, 'medium': 1, 'low': 2}
    exit_signals.sort(key=lambda x: urgency_order.get(x['urgency'], 99))
    
    return exit_signals


def get_portfolio_exit_summary(exit_signals: list) -> dict:
    """
    获取组合退出汇总
    
    Args:
        exit_signals: 退出信号列表
        
    Returns:
        汇总统计字典
    """
    
    if not exit_signals:
        return {
            'total_signals': 0,
            'high_urgency': 0,
            'medium_urgency': 0,
            'low_urgency': 0,
            'trim_count': 0,
            'cut_count': 0,
            'recommendation': '无退出信号，继续持仓'
        }
    
    high_count = sum(1 for s in exit_signals if s['urgency'] == 'high')
    medium_count = sum(1 for s in exit_signals if s['urgency'] == 'medium')
    low_count = sum(1 for s in exit_signals if s['urgency'] == 'low')
    
    trim_count = sum(1 for s in exit_signals if s['action'] == 'TRIM')
    cut_count = sum(1 for s in exit_signals if s['action'] == 'CUT')
    
    # 生成建议
    if high_count > 0:
        recommendation = f"⚠️ 紧急：{high_count} 只基金需要立即处理 (高优先级止损)"
    elif cut_count > 0:
        recommendation = f"建议执行 {cut_count} 只基金的止损操作"
    elif trim_count > 0:
        recommendation = f"建议执行 {trim_count} 只基金的止盈操作"
    else:
        recommendation = "继续监控"
    
    return {
        'total_signals': len(exit_signals),
        'high_urgency': high_count,
        'medium_urgency': medium_count,
        'low_urgency': low_count,
        'trim_count': trim_count,
        'cut_count': cut_count,
        'recommendation': recommendation,
        'generated_at': datetime.now().isoformat()
    }


def format_exit_report(exit_signals: list, compact: bool = False) -> str:
    """
    格式化退出报告
    
    Args:
        exit_signals: 退出信号列表
        compact: 是否精简输出
        
    Returns:
        格式化文本报告
    """
    
    if not exit_signals:
        return "✅ 无退出信号 - 继续持仓"
    
    summary = get_portfolio_exit_summary(exit_signals)
    
    if compact:
        lines = []
        for signal in exit_signals[:3]:  # 只显示前 3 个
            emoji = "🔴" if signal['urgency'] == 'high' else "🟡" if signal['urgency'] == 'medium' else "🟢"
            lines.append(
                f"{emoji} {signal['fund_code']} {signal['action_zh']} "
                f"({signal['pnl']:+.1%}) - {signal['ratio']:.0%}"
            )
        return "\n".join(lines)
    
    # 完整报告
    lines = []
    lines.append("=" * 60)
    lines.append("退出监控报告")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"总计：{summary['total_signals']} 个退出信号")
    lines.append(f"  🔴 高优先级：{summary['high_urgency']}")
    lines.append(f"  🟡 中优先级：{summary['medium_urgency']}")
    lines.append(f"  🟢 低优先级：{summary['low_urgency']}")
    lines.append("")
    lines.append(f"操作类型：{summary['trim_count']} 止盈 / {summary['cut_count']} 止损")
    lines.append("")
    lines.append(f"建议：{summary['recommendation']}")
    lines.append("")
    lines.append("-" * 60)
    lines.append("详细信号:")
    lines.append("")
    
    for i, signal in enumerate(exit_signals, 1):
        urgency_emoji = "🔴" if signal['urgency'] == 'high' else "🟡" if signal['urgency'] == 'medium' else "🟢"
        
        lines.append(f"{i}. {urgency_emoji} {signal['fund_code']} {signal['fund_name']}")
        lines.append(f"   操作：{signal['action_zh']} ({signal['action']})")
        lines.append(f"   盈亏：{signal['pnl']:+.1%}")
        lines.append(f"   比例：{signal['ratio']:.0%}")
        lines.append(f"   紧急度：{signal['urgency_zh']} ({signal['urgency']})")
        lines.append(f"   理由：{signal['reason']}")
        lines.append(f"   建议：{signal['suggested_action']}")
        lines.append("")
    
    return "\n".join(lines)


def send_exit_alert_feishu(webhook: str, exit_signals: list) -> bool:
    """
    发送退出告警到飞书
    
    Args:
        webhook: 飞书机器人 webhook
        exit_signals: 退出信号列表
        
    Returns:
        发送是否成功
    """
    
    if not exit_signals:
        return False
    
    # 只发送高优先级和中优先级信号
    urgent_signals = [s for s in exit_signals if s['urgency'] in ['high', 'medium']]
    if not urgent_signals:
        return False
    
    # 构建消息
    lines = ["## 🔔 退出监控告警", ""]
    
    for signal in urgent_signals[:5]:  # 最多 5 个
        urgency_emoji = "🔴" if signal['urgency'] == 'high' else "🟡"
        pnl_sign = "+" if signal['pnl'] > 0 else ""
        
        lines.append(f"{urgency_emoji} **{signal['fund_code']} {signal['action_zh']}**")
        lines.append(f"- 盈亏：{pnl_sign}{signal['pnl']:.1%}")
        lines.append(f"- 操作：卖出 {signal['ratio']:.0%} 仓位")
        lines.append(f"- 理由：{signal['reason']}")
        lines.append(f"- 紧急度：{signal['urgency_zh']}")
        lines.append("")
    
    summary = get_portfolio_exit_summary(exit_signals)
    lines.append("---")
    lines.append(f"**总计**: {summary['total_signals']} 个信号 | ")
    lines.append(f"**止盈**: {summary['trim_count']} | **止损**: {summary['cut_count']}")
    lines.append("")
    lines.append(f"建议：{summary['recommendation']}")
    
    content = "\n".join(lines)
    
    try:
        import requests
        
        payload = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": "🔔 退出监控告警"
                    },
                    "template": "red" if any(s['urgency'] == 'high' for s in urgent_signals) else "yellow"
                },
                "elements": [
                    {
                        "tag": "markdown",
                        "content": content
                    }
                ]
            }
        }
        
        response = requests.post(webhook, json=payload, timeout=10)
        result = response.json()
        
        return result.get('StatusCode', 1) == 0 or result.get('code', 1) == 0
    except Exception as e:
        print(f"[ERROR] 发送飞书消息失败：{e}")
        return False


def load_positions_from_file(file_path: str) -> list:
    """
    从文件加载持仓数据
    
    Args:
        file_path: JSON 文件路径
        
    Returns:
        持仓列表
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在：{file_path}")
    
    data = json.loads(path.read_text(encoding='utf-8'))
    
    # 支持多种格式
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        return data.get('positions', [])
    else:
        raise ValueError("无效的持仓数据格式")


def main():
    parser = argparse.ArgumentParser(description='退出监控器')
    parser.add_argument('--input', type=str, help='持仓数据 JSON 文件路径')
    parser.add_argument('--output', type=str, help='输出报告文件路径')
    parser.add_argument('--compact', action='store_true', help='精简输出')
    parser.add_argument('--feishu', action='store_true', help='发送飞书告警')
    parser.add_argument('--webhook', type=str,
                       default='https://open.feishu.cn/open-apis/bot/v2/hook/f1286a3e-4e41-4809-a0bc-fd2bbbbc3f10',
                       help='飞书机器人 webhook URL')
    parser.add_argument('--min-pnl', type=float, default=0.07,
                       help='止盈阈值 (默认 7%)')
    parser.add_argument('--max-loss', type=float, default=-0.05,
                       help='止损阈值 (默认 -5%)')
    
    args = parser.parse_args()
    
    # 加载持仓数据
    if args.input:
        try:
            positions = load_positions_from_file(args.input)
        except Exception as e:
            print(f"[ERROR] 加载持仓数据失败：{e}")
            return
    else:
        # 使用示例数据
        print("[WARN] 未指定输入文件，使用示例持仓数据")
        positions = [
            {
                'fund_code': '018737',
                'fund_name': '华夏科创 50ETF 联接 A',
                'unrealized_pnl_pct': 0.085,
                'current_exposure': 0.35,
                'catalyst_strength': 'normal'
            },
            {
                'fund_code': '017572',
                'fund_name': '广发新能源车电池 ETF 联接 C',
                'unrealized_pnl_pct': -0.062,
                'current_exposure': 0.25,
                'catalyst_strength': 'weakened'
            },
            {
                'fund_code': '014620',
                'fund_name': '德邦半导体产业混合 C',
                'unrealized_pnl_pct': 0.045,
                'current_exposure': 0.20,
                'catalyst_strength': 'strong'
            }
        ]
    
    # 检查退出信号
    exit_signals = check_exit_signals(positions)
    
    # 输出报告
    report = format_exit_report(exit_signals, compact=args.compact)
    print(report)
    
    # 保存到文件
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存 JSON 格式
        output_data = {
            'exit_signals': exit_signals,
            'summary': get_portfolio_exit_summary(exit_signals)
        }
        output_path.write_text(
            json.dumps(output_data, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        print(f"\n[INFO] 报告已保存至：{args.output}")
    
    # 发送飞书告警
    if args.feishu and exit_signals:
        success = send_exit_alert_feishu(args.webhook, exit_signals)
        if success:
            print("\n[INFO] 飞书告警已发送")
        else:
            print("\n[WARN] 飞书告警发送失败")


if __name__ == "__main__":
    main()

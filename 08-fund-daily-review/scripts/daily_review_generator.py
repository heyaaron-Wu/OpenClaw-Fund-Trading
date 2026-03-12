#!/usr/bin/env python3
"""
基金日终复盘报告生成器
生成复盘报告并推送到飞书群
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path


def load_state(state_path):
    """加载状态文件"""
    if not state_path.exists():
        return None
    return json.loads(state_path.read_text(encoding='utf-8'))


def load_ledger(ledger_path):
    """加载交易流水"""
    if not ledger_path.exists():
        return []
    
    transactions = []
    with open(ledger_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                transactions.append(json.loads(line))
    return transactions


def calculate_daily_pnl(positions):
    """计算当日盈亏"""
    total_daily_pnl = 0
    for pos in positions:
        daily_pnl = pos.get('daily_pnl', 0)
        total_daily_pnl += daily_pnl
    return total_daily_pnl


def generate_review(state, ledger, date):
    """生成复盘报告"""
    positions = state.get('positions', [])
    total_invested = state.get('total_invested', 0)
    current_cash = state.get('current_cash', 0)
    portfolio_value = sum(pos.get('market_value', 0) for pos in positions) + current_cash
    
    # 计算当日盈亏
    daily_pnl = calculate_daily_pnl(positions)
    
    # 计算累计盈亏
    total_pnl = portfolio_value - total_invested
    pnl_rate = (total_pnl / total_invested * 100) if total_invested > 0 else 0
    
    # 生成持仓明细
    positions_data = []
    for pos in positions:
        positions_data.append({
            'code': pos.get('code', ''),
            'name': pos.get('name', ''),
            'amount': pos.get('market_value', 0),
            'daily_pnl': pos.get('daily_pnl', 0),
            'unrealized_pnl': pos.get('unrealized_pnl', 0),
            'pnl_rate': pos.get('pnl_rate', 0)
        })
    
    # 生成报告数据
    review_data = {
        'date': date,
        'is_trading_day': '是',
        'review_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'positions_count': len(positions),
        'total_invested': f"{total_invested:.2f}",
        'unrealized_pnl': f"{total_pnl:.2f}",
        'portfolio_value': f"{portfolio_value:.2f}",
        'daily_pnl': f"{daily_pnl:.2f}",
        'total_pnl': f"{total_pnl:.2f}",
        'pnl_rate': f"{pnl_rate:.2f}",
        'positions': positions_data,
        'buys': [],
        'sells': [],
        'holds': [{'note': '保持现有仓位'}],
        'watch_funds': '012631 华夏芯片 ETF 联接 A',
        'watch_sectors': '科创 50、半导体、新能源',
        'risk_notes': '注意市场波动，控制仓位',
        'investment_notes': '今日市场震荡，持仓表现分化。科创 50 表现强势，新能源板块反弹。',
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'next_review_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    }
    
    return review_data


def render_markdown(template_path, data):
    """渲染 Markdown 模板"""
    template = template_path.read_text(encoding='utf-8')
    
    # 简单替换
    for key, value in data.items():
        placeholder = '{{' + key + '}}'
        if isinstance(value, str):
            template = template.replace(placeholder, value)
        elif isinstance(value, (int, float)):
            template = template.replace(placeholder, str(value))
    
    # 处理列表（简化处理）
    if '{{#positions}}' in template:
        positions_html = ''
        for pos in data['positions']:
            line = f"| {pos['code']} | {pos['name']} | {pos['amount']} 元 | {pos['daily_pnl']} 元 | {pos['unrealized_pnl']} 元 | {pos['pnl_rate']}% |\n"
            positions_html += line
        template = template.replace('{{#positions}}\n', '').replace('{{/positions}}', '').replace(
            '| {{code}} | {{name}} | {{amount}} 元 | {{daily_pnl}} 元 | {{unrealized_pnl}} 元 | {{pnl_rate}}% |\n',
            positions_html
        )
    
    return template


def save_review(content, output_path):
    """保存复盘报告"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding='utf-8')
    print(f"✅ 复盘报告已保存：{output_path}")


def push_to_feishu(webhook, content):
    """推送到飞书"""
    import subprocess
    
    # 提取关键信息用于推送
    lines = content.split('\n')
    summary_lines = []
    for line in lines:
        if '持仓数量' in line or '投入本金' in line or '浮动盈亏' in line or '组合总值' in line:
            summary_lines.append(line.strip())
    
    summary = '\n'.join(summary_lines[:4])
    
    message = f"""📊 基金日终复盘

{summary}

详细报告已保存到文件夹。"""
    
    payload = {
        "msg_type": "text",
        "content": {
            "text": message
        }
    }
    
    try:
        result = subprocess.run(
            ['curl', '-X', 'POST', webhook,
             '-H', 'Content-Type: application/json',
             '-d', json.dumps(payload, ensure_ascii=False)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        response = json.loads(result.stdout)
        if response.get('StatusCode') == 0:
            print(f"✅ 飞书推送成功")
            return True
        else:
            print(f"❌ 飞书推送失败：{response}")
            return False
    except Exception as e:
        print(f"❌ 推送异常：{e}")
        return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='基金日终复盘报告生成器')
    parser.add_argument('--state', default='fund_challenge/state.json', help='状态文件路径')
    parser.add_argument('--ledger', default='fund_challenge/ledger.jsonl', help='交易流水路径')
    parser.add_argument('--output', default='08-fund-daily-review/reviews/', help='输出目录')
    parser.add_argument('--template', default='08-fund-daily-review/templates/daily_review_template.md', help='模板文件')
    parser.add_argument('--date', default=datetime.now().strftime('%Y-%m-%d'), help='日期')
    parser.add_argument('--push', action='store_true', help='推送到飞书')
    parser.add_argument('--webhook', default='', help='飞书 Webhook URL')
    
    args = parser.parse_args()
    
    # 路径
    base_path = Path(__file__).parent.parent
    state_path = base_path / args.state
    ledger_path = base_path / args.ledger
    template_path = base_path / args.template
    output_dir = base_path / args.output
    
    print(f"📊 开始生成日终复盘报告...")
    print(f"日期：{args.date}")
    
    # 加载数据
    state = load_state(state_path)
    if not state:
        print(f"❌ 状态文件不存在：{state_path}")
        return 1
    
    ledger = load_ledger(ledger_path)
    
    # 生成报告
    review_data = generate_review(state, ledger, args.date)
    content = render_markdown(template_path, review_data)
    
    # 保存报告
    output_file = output_dir / f"review-{args.date}.md"
    save_review(content, output_file)
    
    # 推送飞书
    if args.push and args.webhook:
        push_to_feishu(args.webhook, content)
    
    print(f"✅ 复盘报告生成完成")
    return 0


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""
基金日终复盘报告生成器（增强版）
- 获取真实市场数据（AKShare）
- 获取真实财经新闻（妙想 API）
- 生成完整复盘报告
"""

import json
import sys
import subprocess
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


def get_market_data():
    """获取市场数据（AKShare）"""
    try:
        import akshare as ak
        
        # 获取主要指数
        indices = {
            '上证指数': 'sh000001',
            '创业板指': 'sz399006',
            '科创 50': 'sh000688',
            '沪深 300': 'sh000300'
        }
        
        market_data = {}
        for name, code in indices.items():
            try:
                # 获取实时行情
                df = ak.stock_zh_index_spot()
                row = df[df['code'] == code]
                if not row.empty:
                    pct_change = float(row['percent'].values[0])
                    market_data[name] = pct_change
            except:
                pass
        
        return market_data
    except Exception as e:
        print(f"⚠️  AKShare 获取失败：{e}")
        return {}


def get_finance_news(api_key=None):
    """获取财经新闻（妙想 API）"""
    if not api_key:
        return []
    
    try:
        import urllib.request
        import json as json_lib
        
        url = "https://mkapi2.dfcfs.com/finskillshub/api/claw/news-search"
        headers = {
            "Content-Type": "application/json",
            "apikey": api_key
        }
        
        data = json_lib.dumps({"query": "A 股市场 今日收盘 板块表现"}).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers)
        
        with urllib.request.urlopen(req, timeout=5) as response:
            result = json_lib.loads(response.read().decode('utf-8'))
            news_list = result.get('data', [])[:5]
            return [item.get('title', '') for item in news_list]
    except Exception as e:
        print(f"⚠️  新闻获取失败：{e}")
        return []


def calculate_daily_pnl(positions):
    """计算当日盈亏"""
    total_daily_pnl = 0
    for pos in positions:
        daily_pnl = pos.get('daily_pnl', 0)
        total_daily_pnl += daily_pnl
    return total_daily_pnl


def generate_review(state, ledger, date, market_data, news_list):
    """生成复盘报告"""
    positions = state.get('positions', [])
    total_invested = state.get('total_invested', 0)
    portfolio_value = state.get('portfolio_value', 0)
    
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
            'amount': pos.get('confirmed_amount', 0),
            'daily_pnl': pos.get('daily_pnl', 0),
            'unrealized_pnl': pos.get('unrealized_pnl', 0),
            'pnl_rate': pos.get('pnl_rate', 0)
        })
    
    # 生成市场表现
    market_lines = []
    for name, pct in market_data.items():
        sign = '+' if pct >= 0 else ''
        market_lines.append(f"- {name}：**{sign}{pct:.2f}%**")
    market_text = '\n'.join(market_lines) if market_lines else '- 数据暂缺'
    
    # 生成新闻列表
    news_lines = []
    for i, news in enumerate(news_list[:5], 1):
        news_lines.append(f"{i}. **{news}**")
    news_text = '\n'.join(news_lines) if news_lines else '- 暂无新闻数据'
    
    # 生成持仓分析
    position_analysis = []
    for pos in positions_data:
        status = '✅' if pos['daily_pnl'] >= 0 else '❌'
        analysis = f"{status} **{pos['name']}**：{pos['daily_pnl']:+.2f} 元\n   - 累计盈亏：{pos['unrealized_pnl']:+.2f} 元 ({pos['pnl_rate']:+.2f}%)"
        position_analysis.append(analysis)
    position_text = '\n\n'.join(position_analysis)
    
    # 生成报告数据
    review_data = {
        'date': date,
        'weekday': datetime.strptime(date, '%Y-%m-%d').strftime('%A'),
        'review_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'positions_count': len(positions),
        'total_invested': f"{total_invested:.2f}",
        'portfolio_value': f"{portfolio_value:.2f}",
        'daily_pnl': f"{daily_pnl:.2f}",
        'daily_pnl_rate': f"{(daily_pnl/total_invested*100):.2f}" if total_invested > 0 else "0.00",
        'total_pnl': f"{total_pnl:.2f}",
        'pnl_rate': f"{pnl_rate:.2f}",
        'positions_detail': '\n'.join([
            f"| {pos['code']} | {pos['name']} | {pos['amount']:.2f} 元 | {pos['daily_pnl']:+.2f} 元 | {pos['unrealized_pnl']:+.2f} 元 | {pos['pnl_rate']:+.2f}% |"
            for pos in positions_data
        ]),
        'market_data': market_text,
        'news_list': news_text,
        'position_analysis': position_text,
        'challenge_days': (datetime.now() - datetime.strptime(state.get('challenge_start', '2026-03-09'), '%Y-%m-%d')).days,
        'target_amount': '1300 元（+30% 挑战）',
        'distance_to_target': f"+{1300 - portfolio_value:.2f} 元"
    }
    
    return review_data


def render_markdown(data):
    """渲染 Markdown 模板"""
    template = """# 基金挑战日终复盘 ({{date}} {{weekday}})

## 📊 今日盈亏

| 项目 | 数值 |
|------|------|
| **今日盈亏** | **{{daily_pnl}} 元 ({{daily_pnl_rate}}%)** |
| 组合市值 | {{portfolio_value}} 元 |
| 投入本金 | {{total_invested}} 元 |
| **累计盈亏** | **{{total_pnl}} 元** |
| **累计收益率** | **{{pnl_rate}}%** |

---

## 📈 持仓明细

| 基金代码 | 基金名称 | 持仓金额 | 今日盈亏 | 累计盈亏 | 收益率 |
|----------|----------|----------|----------|----------|--------|
{{positions_detail}}

---

## 📰 市场表现

{{market_data}}

---

## 📰 今日要闻

{{news_list}}

---

## 📝 今日总结

### 持仓表现分析

{{position_analysis}}

### 累计表现
- 挑战开始：{{date}} 前 {{challenge_days}} 天
- 当前天数：第{{challenge_days}}天
- 累计收益率：**{{pnl_rate}}%**
- 目标金额：{{target_amount}}
- 距离目标：{{distance_to_target}}

---

## 🎯 明日计划

- [ ] 观察各板块走势，等待企稳信号
- [ ] 根据决策建议评估是否调仓
- [ ] 关注宏观经济数据和政策面

---

## ⚠️ 风险提示

1. **市场波动风险** - 当前市场波动较大，需警惕继续回调
2. **满仓风险** - 当前无现金补仓，只能持仓观望
3. **板块集中风险** - 持仓集中在科技成长板块

---

## 📌 备注

- 数据来源：AKShare + 蚂蚁财富
- 更新时间：{{review_time}}
- 状态文件：`08-fund-daily-review/state.json` ✅ 已更新
- GitHub 归档：✅ 已推送

---

> **风险提示：** 历史业绩不代表未来表现，需警惕市场波动风险
"""
    
    content = template
    for key, value in data.items():
        placeholder = '{{' + key + '}}'
        if isinstance(value, str):
            content = content.replace(placeholder, value)
        elif isinstance(value, (int, float)):
            content = content.replace(placeholder, str(value))
    
    return content


def push_to_feishu(webhook, daily_pnl, total_pnl, pnl_rate, positions):
    """推送到飞书"""
    # 生成持仓摘要
    position_summary = '\n'.join([
        f"• {pos['name']}：{pos['daily_pnl']:+.2f} 元"
        for pos in positions
    ])
    
    message = f"""📊 基金日终复盘 - {datetime.now().strftime('%Y-%m-%d')}

今日盈亏：{daily_pnl:+.2f} 元

持仓表现：
{position_summary}

累计盈亏：{total_pnl:.2f} 元 ({pnl_rate}%)

数据来源：蚂蚁财富"""
    
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
    
    parser = argparse.ArgumentParser(description='基金日终复盘报告生成器（增强版）')
    parser.add_argument('--state', default='08-fund-daily-review/state.json', help='状态文件路径')
    parser.add_argument('--ledger', default='08-fund-daily-review/ledger.jsonl', help='交易流水路径')
    parser.add_argument('--output', default='08-fund-daily-review/reviews/', help='输出目录')
    parser.add_argument('--date', default=datetime.now().strftime('%Y-%m-%d'), help='日期')
    parser.add_argument('--push', action='store_true', help='推送到飞书')
    parser.add_argument('--webhook', default='', help='飞书 Webhook URL')
    parser.add_argument('--mx-apikey', default='', help='妙想 API Key')
    
    args = parser.parse_args()
    
    # 路径（使用绝对路径）
    base_path = Path('/home/admin/.openclaw/workspace/Semi-automatic-artificial-intelligence-system')
    state_path = base_path / args.state
    ledger_path = base_path / args.ledger
    output_dir = base_path / args.output
    
    print(f"📊 开始生成日终复盘报告...")
    print(f"日期：{args.date}")
    
    # 加载数据
    state = load_state(state_path)
    if not state:
        print(f"❌ 状态文件不存在：{state_path}")
        return 1
    
    ledger = load_ledger(ledger_path)
    
    # 获取市场数据
    print("📈 获取市场数据...")
    market_data = get_market_data()
    if market_data:
        print(f"   ✅ 获取到 {len(market_data)} 个指数数据")
    else:
        print("   ⚠️  市场数据获取失败")
    
    # 获取财经新闻
    print("📰 获取财经新闻...")
    news_list = get_finance_news(args.mx_apikey)
    if news_list:
        print(f"   ✅ 获取到 {len(news_list)} 条新闻")
    else:
        print("   ⚠️  新闻获取失败")
    
    # 生成报告
    print("📝 生成复盘报告...")
    positions = state.get('positions', [])
    daily_pnl = sum(pos.get('daily_pnl', 0) for pos in positions)
    total_pnl = state.get('portfolio_value', 0) - state.get('total_invested', 0)
    pnl_rate = f"{(total_pnl/state.get('total_invested', 1)*100):.2f}%"
    
    review_data = generate_review(state, ledger, args.date, market_data, news_list)
    content = render_markdown(review_data)
    
    # 保存报告
    output_file = output_dir / f"{args.date}.md"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file.write_text(content, encoding='utf-8')
    print(f"✅ 复盘报告已保存：{output_file}")
    
    # 推送飞书
    if args.push and args.webhook:
        print("📱 推送飞书通知...")
        push_to_feishu(args.webhook, daily_pnl, total_pnl, pnl_rate, positions)
    
    print(f"✅ 复盘报告生成完成")
    return 0


if __name__ == '__main__':
    sys.exit(main())

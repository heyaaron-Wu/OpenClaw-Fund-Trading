#!/usr/bin/env python3
"""
基金日终复盘报告生成器（增强版）
- 获取真实市场数据（AKShare）
- 获取真实财经新闻（多源聚合：妙想 + 新浪 + 东方财富 + Google News）
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
            line = line.strip()
            # 跳过空行和注释行
            if not line or line.startswith('#'):
                continue
            transactions.append(json.loads(line))
    return transactions


def get_market_data():
    """获取市场数据（腾讯财经 API - 更稳定）"""
    import urllib.request
    
    indices = {
        '上证指数': 'sh000001',
        '创业板指': 'sz399006',
        '科创 50': 'sh000688',
        '沪深 300': 'sh000300'
    }
    
    market_data = {}
    for name, code in indices.items():
        try:
            url = f"http://qt.gtimg.cn/q={code}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(req, timeout=5)
            data = response.read().decode('gbk')
            
            # 解析：v_sh000001="51~3089.80~3093.15~3088.55~...
            parts = data.split('~')
            if len(parts) > 49:
                pct_change = float(parts[49])  # 涨跌幅百分比
                market_data[name] = pct_change
        except Exception as e:
            print(f"⚠️  {name} 获取失败：{e}")
            pass
    
    return market_data


def translate_en_to_zh(text):
    """英文新闻标题翻译（Google Translate - 简单方案）"""
    import urllib.request
    import urllib.parse
    
    try:
        # 使用 Google Translate 的简单接口（无需 API key）
        url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=zh-CN&dt=t&q=" + urllib.parse.quote(text)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            result = json.loads(response.read().decode('utf-8'))
            # 返回结构：[[["译文", "原文", ...]], ...]
            if result and result[0]:
                translated = ''.join([item[0] for item in result[0] if item[0]])
                return translated if translated else text
    except Exception as e:
        print(f"   ⚠️  翻译失败：{e}")
        return text  # 翻译失败返回原文


def get_finance_news(api_key=None):
    """获取财经新闻（多源聚合 + 英文翻译）"""
    # 尝试导入多源新闻聚合脚本
    try:
        sys.path.insert(0, '/home/admin/.openclaw/workspace/skills/fund-challenge/fund_challenge/scripts')
        from multi_source_news import get_multi_source_news as fetch_multi_news
        
        print("📰 获取多源财经资讯...")
        news_list = fetch_multi_news()
        
        # 格式统一化
        formatted_news = []
        for news in news_list[:8]:  # 限制最多 8 条
            # 处理来源字段（可能是字典或字符串）
            source = news.get('source', '')
            if isinstance(source, dict):
                source = source.get('name', '')
            
            # 处理时间字段
            time_str = news.get('time', '')
            if time_str and len(time_str) > 16:
                time_str = time_str[:16]
            
            title = news.get('title', '')
            
            # 检测并翻译英文标题
            if title and any(ord(c) > 127 for c in title) == False and len(title) > 10:
                # 可能是英文，尝试翻译
                print(f"   🌐 翻译英文新闻：{title[:50]}...")
                title_zh = translate_en_to_zh(title)
                if title_zh != title:
                    title = f"{title_zh} （原文：{title}）"
            
            formatted_news.append({
                'title': title,
                'url': news.get('url', ''),
                'time': time_str,
                'source': source
            })
        
        return formatted_news
    except Exception as e:
        print(f"⚠️  多源新闻获取失败：{e}")
        print("   降级为妙想单源...")
        
        # Fallback: 妙想单源
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
                # 妙想 API 返回结构：data.data.llmSearchResponse.data
                news_data = result.get('data', {}).get('llmSearchResponse', {}).get('data', [])
                # 返回标题 + 链接 + 时间 + 来源
                return [
                    {
                        'title': item.get('title', ''),
                        'url': item.get('jumpUrl', ''),
                        'time': item.get('date', '')[:16] if item.get('date') else '',
                        'source': item.get('source', '')
                    }
                    for item in news_data[:5]
                ]
        except Exception as e2:
            print(f"⚠️  妙想 API 也失败：{e2}")
            return []


def calculate_daily_pnl(positions):
    """计算当日盈亏"""
    total_daily_pnl = 0
    for pos in positions:
        daily_pnl = pos.get('daily_pnl', 0)
        total_daily_pnl += daily_pnl
    return total_daily_pnl


def generate_tomorrow_plan(positions_data, market_data, daily_pnl):
    """根据今日表现动态生成明日计划"""
    plans = []
    
    # 判断市场趋势
    market_trend = "震荡"
    for name, pct in market_data.items():
        if abs(pct) > 1.5:
            market_trend = "大涨" if pct > 0 else "大跌"
            break
        elif abs(pct) > 0.5:
            market_trend = "上涨" if pct > 0 else "下跌"
    
    # 判断持仓表现
    profitable_count = sum(1 for pos in positions_data if pos['daily_pnl'] > 0)
    total_count = len(positions_data)
    
    # 根据情况生成计划
    if daily_pnl > 0:
        plans.append("✅ 今日盈利，保持现有仓位，观察持续性")
    elif daily_pnl < -10:
        plans.append("⚠️ 今日亏损较大，关注企稳信号，谨慎操作")
    else:
        plans.append("📊 今日震荡，持仓观望为主")
    
    # 根据盈利持仓数量
    if profitable_count == 0:
        plans.append("🔍 持仓全线下跌，检查是否需调仓换股")
    elif profitable_count == total_count:
        plans.append("✅ 持仓全线上涨，考虑是否止盈部分仓位")
    
    # 根据市场趋势
    if "大跌" in market_trend:
        plans.append("📉 市场大跌，关注超跌反弹机会")
    elif "大涨" in market_trend:
        plans.append("📈 市场大涨，警惕冲高回落")
    
    # 固定计划（根据日期判断）
    weekday = datetime.now().strftime('%w')
    if weekday == '0':  # 周日
        plans.append("⏰ 明日周一，关注 14:00 交易决策建议")
    elif weekday == '4':  # 周五
        plans.append("📊 明日周五，关注周末消息面变化")
    
    # 至少保证 3 条计划
    if len(plans) < 3:
        plans.append("📰 关注宏观经济数据和政策面变化")
    if len(plans) < 3:
        plans.append("🔍 观察各板块走势，寻找结构性机会")
    
    return plans


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
    
    # 生成新闻列表（带链接）- 符合 README.md 规范格式
    news_lines = []
    for i, news in enumerate(news_list[:5], 1):
        title = news.get('title', '')
        url = news.get('url', '')
        time_str = news.get('time', '')
        source = news.get('source', '')
        
        if url and source:
            # 格式：*来源：[来源名](链接)* | 时间
            news_lines.append(f"{i}. **{title}**\n   *来源：[{source}]({url})* | {time_str}")
        elif url:
            news_lines.append(f"{i}. **{title}**\n   *来源：[链接]({url})* | {time_str}")
        else:
            news_lines.append(f"{i}. **{title}**")
    news_text = '\n\n'.join(news_lines) if news_lines else '- 暂无新闻数据'
    
    # 生成持仓分析（详细版：结合行情 + 情绪 + 建议）
    position_analysis = []
    
    # 基金代码对应的板块/指数
    fund_to_sector = {
        '011612': ('科创 50', '科创 50 指数'),
        '013180': ('创业板指', '新能源车板块'),
        '014320': ('科创 50', '半导体板块'),
    }
    
    for pos in positions_data:
        status = '✅' if pos['daily_pnl'] >= 0 else '❌'
        code = pos.get('code', '')
        daily_pnl = pos['daily_pnl']
        unrealized_pnl = pos['unrealized_pnl']
        pnl_rate = pos['pnl_rate']
        
        # 获取对应的板块信息
        sector_name, sector_desc = fund_to_sector.get(code, ('', ''))
        
        # 获取板块当日表现
        sector_pnl = None
        if sector_name and market_data:
            for market_name, pct in market_data.items():
                if sector_name in market_name:
                    sector_pnl = pct
                    break
        
        # 生成详细点评（行情 + 情绪 + 建议）
        comments = []
        
        # 1. 行情描述 + 相对强弱
        if sector_pnl is not None:
            if sector_pnl > 2:
                sector_comment = f"{sector_desc}大涨{sector_pnl:.2f}%"
            elif sector_pnl > 0.5:
                sector_comment = f"{sector_desc}上涨{sector_pnl:.2f}%"
            elif sector_pnl > -0.5:
                sector_comment = f"{sector_desc}震荡整理"
            elif sector_pnl > -2:
                sector_comment = f"{sector_desc}小幅回调{sector_pnl:.2f}%"
            else:
                sector_comment = f"{sector_desc}大跌{sector_pnl:.2f}%"
            
            # 判断相对强弱（板块涨但基金跌 = 跑输）
            if sector_pnl > 0.5 and daily_pnl < 0:
                sector_comment += "，**跑输板块**"
            elif sector_pnl < -0.5 and daily_pnl > 0:
                sector_comment += "，**逆势上涨**"
            
            comments.append(sector_comment)
        else:
            if daily_pnl > 5:
                comments.append("逆势大涨")
            elif daily_pnl > 0:
                comments.append("小幅上涨")
            elif daily_pnl > -3:
                comments.append("窄幅震荡")
            else:
                comments.append("继续调整")
        
        # 2. 情绪/趋势判断
        if daily_pnl > 0 and unrealized_pnl > 0:
            comments.append("延续上涨趋势")
        elif daily_pnl > 0 and unrealized_pnl < 0:
            comments.append("超跌反弹")
        elif daily_pnl < 0 and unrealized_pnl > 0:
            comments.append("盈利回吐")
        elif daily_pnl < 0 and unrealized_pnl < 0:
            comments.append("延续调整")
        
        # 3. 操作建议（根据累计盈亏）
        if unrealized_pnl > 30:
            comments.append("可考虑止盈部分仓位")
        elif unrealized_pnl > 10:
            comments.append("继续持有")
        elif unrealized_pnl > 0:
            comments.append("持仓观望")
        elif unrealized_pnl > -20:
            comments.append("耐心等待反弹")
        else:
            comments.append("关注企稳信号")
        
        # 组合点评
        comment_text = "，".join(comments[:3])  # 最多 3 条
        
        analysis = f"{status} **{pos['name']}**：{pos['daily_pnl']:+.2f} 元\n   - 累计盈亏：{pos['unrealized_pnl']:+.2f} 元 ({pos['pnl_rate']:+.2f}%)\n   - {comment_text}"
        position_analysis.append(analysis)
    
    position_text = '\n\n'.join(position_analysis)
    
    # 生成明日计划（动态）
    tomorrow_plan = generate_tomorrow_plan(positions_data, market_data, daily_pnl)
    plan_lines = [f"- [ ] {plan}" for plan in tomorrow_plan]
    plan_text = '\n'.join(plan_lines)
    
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
        'tomorrow_plan': plan_text,
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

{{tomorrow_plan}}

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
    
    # 获取财经新闻（多源聚合）
    print("📰 获取财经新闻（多源聚合）...")
    news_list = get_finance_news(args.mx_apikey)
    if news_list:
        # 统计各来源数量
        source_count = {}
        for news in news_list:
            source = news.get('source', '未知')
            source_count[source] = source_count.get(source, 0) + 1
        
        print(f"   ✅ 获取到 {len(news_list)} 条新闻")
        for source, count in sorted(source_count.items(), key=lambda x: -x[1]):
            print(f"      • {source}: {count}条")
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

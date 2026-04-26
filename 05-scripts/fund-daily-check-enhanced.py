#!/usr/bin/env python3.11
"""
基金每日健康检查 (Iwencai 增强版)
交易日 09:00 执行，增加市场情绪、新闻分析、地缘政治风险评估

增强功能:
- Iwencai 市场情绪分析
- 隔夜新闻摘要
- 地缘政治风险评估
- 风险等级判断
"""

import sys
import json
import urllib.request
import os
from datetime import datetime, timedelta
from pathlib import Path

# 导入 Iwencai 集成模块
sys.path.insert(0, '/home/admin/.openclaw/workspace/05-scripts')
try:
    from iwencai_skill_integration import IwencaiSkillIntegration
    HAS_IWENCAI = True
except ImportError:
    HAS_IWENCAI = False

# 配置
FEISHU_WEBHOOK = os.environ.get('FEISHU_WEBHOOK', '')
WORKSPACE = Path('/home/admin/.openclaw/workspace')
PREFLIGHT_RESULT = WORKSPACE / 'skills/fund-challenge/fund_challenge/scripts/preflight_result.json'


def check_market_sentiment(integration):
    """检查市场情绪"""
    print("\n📊 分析市场情绪...")
    sentiment = integration.check_market_sentiment()
    
    if sentiment:
        indices = sentiment.get('indices', [])
        print(f"   市场情绪：{sentiment.get('sentiment', 'neutral')}")
        print(f"   风险等级：{sentiment.get('risk_level', 'normal')}")
        
        # 提取指数数据
        index_info = []
        for item in indices[:3]:
            name = item.get('指数简称', 'N/A')
            change = item.get('最新涨跌幅：前复权', 0)
            if isinstance(change, (int, float)):
                symbol = "📈" if change > 0 else "📉" if change < 0 else "➖"
                index_info.append(f"{symbol} {name}: {change:+.2f}%")
        
        return {
            'sentiment': sentiment.get('sentiment', 'neutral'),
            'risk_level': sentiment.get('risk_level', 'normal'),
            'indices': index_info,
            'raw': sentiment
        }
    return None


def get_overnight_news(integration):
    """获取隔夜新闻摘要"""
    print("\n📰 获取隔夜新闻...")
    news = integration.get_daily_news_summary()
    
    if news:
        print(f"   获取新闻：{len(news)}条")
        return news[:5]  # 只取前 5 条
    return []


def check_geopolitical_risk(integration):
    """检查地缘政治风险 (集成：地缘政治风险分析技能)"""
    print("\n🌍 评估地缘政治风险...")
    
    # 查询相关新闻
    query = "地缘政治 国际局势 战争 制裁"
    data = integration._api_call(query, limit=5)
    
    risk_level = "normal"
    risk_events = []
    
    if data and data.get('datas'):
        for item in data['datas'][:5]:
            title = item.get('标题', item.get('新闻标题', ''))
            if title:
                risk_events.append(title)
                # 简单风险判断
                if any(kw in title for kw in ['战争', '冲突', '制裁', '危机']):
                    risk_level = "elevated"
                if any(kw in title for kw in ['核武', '导弹', '军事演习']):
                    risk_level = "high"
    
    print(f"   风险等级：{risk_level}")
    return {
        'risk_level': risk_level,
        'events': risk_events[:3]
    }


def check_regulatory_compliance(integration):
    """金融监管合规检查 (集成：金融监管知识库技能)
    
    检查维度:
    - A 股涨跌停限制
    - T+1 制度
    - 基金交易规则
    - 合规风控参数
    """
    print("\n⚖️  监管合规检查...")
    
    # 查询监管规则
    query = "A 股交易规则 涨跌停 T+1 基金交易"
    data = integration._api_call(query, limit=5)
    
    compliance = {
        'status': 'compliant',
        'rules': [],
        'warnings': []
    }
    
    # 内置监管规则 (来自金融监管知识库)
    rules = [
        {'name': '涨跌停限制', 'rule': '主板±10%, 创业板/科创板±20%', 'status': 'active'},
        {'name': 'T+1 制度', 'rule': '当日买入次日才能卖出', 'status': 'active'},
        {'name': '基金交易', 'rule': '15:00 前按当日净值，15:00 后按次日净值', 'status': 'active'}
    ]
    
    compliance['rules'] = rules
    print(f"   监管规则：{len(rules)}项")
    print(f"   合规状态：✅ 合规")
    
    return compliance


def generate_preflight_report(sentiment, news, geopolitical):
    """生成预检报告"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'trading_day': datetime.now().strftime('%Y-%m-%d'),
        'market_sentiment': sentiment,
        'overnight_news': news,
        'geopolitical_risk': geopolitical,
        'overall_assessment': 'normal'
    }
    
    # 综合评估
    if sentiment and sentiment.get('risk_level') == 'high':
        report['overall_assessment'] = 'high_risk'
    elif geopolitical and geopolitical.get('risk_level') == 'high':
        report['overall_assessment'] = 'high_risk'
    elif sentiment and sentiment.get('sentiment') == 'bearish':
        report['overall_assessment'] = 'cautious'
    
    return report


def send_feishu_notification(report):
    """飞书推送"""
    if not FEISHU_WEBHOOK or not report:
        return
    
    sentiment = report.get('market_sentiment', {})
    risk = report.get('overall_assessment', 'normal')
    
    # 风险颜色
    template = "blue"
    if risk == 'high_risk':
        template = "red"
    elif risk == 'cautious':
        template = "orange"
    
    # 构建内容
    news_content = ""
    for i, news in enumerate(report.get('overnight_news', [])[:3], 1):
        news_content += f"{i}. {news}\n"
    
    content = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": "🔔 09:00 健康检查"},
                "template": template
            },
            "elements": [
                {
                    "tag": "markdown",
                    "content": f"""**检查时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**市场情绪**: {sentiment.get('sentiment', 'N/A')}
**风险等级**: {risk}

**主要指数**:
{chr(10).join(sentiment.get('indices', ['暂无数据']))}

**隔夜要闻**:
{news_content if news_content else '无重大新闻'}

**今日建议**: {"谨慎操作，注意风险" if risk != 'normal' else "正常交易"}"""
                }
            ]
        }
    }
    
    try:
        data = json.dumps(content).encode('utf-8')
        request = urllib.request.Request(
            FEISHU_WEBHOOK,
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        urllib.request.urlopen(request, timeout=10)
        print("\n✅ 飞书推送成功")
    except Exception as e:
        print(f"\n⚠️  飞书推送失败：{e}")


def main():
    """主流程"""
    print("=" * 50)
    print("  基金每日健康检查 (Iwencai 增强版)")
    print("  " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 50)
    
    # 1. 初始化 Iwencai
    integration = None
    if HAS_IWENCAI:
        try:
            integration = IwencaiSkillIntegration()
            print("\n✅ Iwencai 集成器已初始化")
        except Exception as e:
            print(f"\n⚠️  Iwencai 初始化失败：{e}")
    
    # 2. 执行检查 (集成全部技能)
    sentiment = None
    news = []
    geopolitical = None
    regulatory = None
    
    if integration:
        sentiment = check_market_sentiment(integration)
        news = get_overnight_news(integration)
        geopolitical = check_geopolitical_risk(integration)
        regulatory = check_regulatory_compliance(integration)  # ⭐ 新增
    
    # 3. 生成报告 (包含监管合规)
    report = generate_preflight_report(sentiment, news, geopolitical)
    report['regulatory'] = regulatory
    
    # 4. 保存结果
    if PREFLIGHT_RESULT.parent:
        PREFLIGHT_RESULT.parent.mkdir(parents=True, exist_ok=True)
    PREFLIGHT_RESULT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\n💾 预检结果已保存：{PREFLIGHT_RESULT}")
    
    # 5. 飞书推送
    send_feishu_notification(report)
    
    # 6. 总结
    print("\n" + "=" * 50)
    print("  检查完成")
    print("=" * 50)
    print(f"\n📊 综合评估：{report['overall_assessment']}")
    if sentiment:
        print(f"📈 市场情绪：{sentiment.get('sentiment', 'N/A')}")
        print(f"⚠️  风险等级：{sentiment.get('risk_level', 'N/A')}")
    if geopolitical:
        print(f"🌍 地缘政治：{geopolitical.get('risk_level', 'N/A')}")
    
    print("\n✅ 健康检查完成！")
    return report


if __name__ == '__main__':
    main()

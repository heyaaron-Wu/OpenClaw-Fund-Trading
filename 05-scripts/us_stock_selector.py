#!/usr/bin/env python3.11
"""
美股筛选器 (Iwencai 问财选美股)
集成问财选美股技能，筛选优质美股标的

使用场景:
- 美股投资候选池筛选
- 美股估值分析
- 美股研报评级参考
"""

import sys
import json
import os
from datetime import datetime
from pathlib import Path

# 导入 Iwencai 集成模块
sys.path.insert(0, '/home/admin/.openclaw/workspace/05-scripts')
try:
    from iwencai_skill_integration import IwencaiSkillIntegration
    HAS_IWENCAI = True
except ImportError:
    HAS_IWENCAI = False

# 配置
OUTPUT_PATH = Path('/home/admin/.openclaw/workspace/06-data/us_stock_selection.json')


def select_us_stocks_value(integration):
    """问财选美股 - 价值股筛选"""
    print("\n📊 价值股筛选...")
    
    query = "美股 市盈率低于 20 市净率低于 3 股息率高于 2"
    data = integration._api_call(query, limit=20)
    
    stocks = []
    if data and data.get('datas'):
        for item in data['datas'][:20]:
            stock = {
                'code': item.get('股票代码', ''),
                'name': item.get('股票简称', ''),
                'pe': item.get('市盈率', 0),
                'pb': item.get('市净率', 0),
                'dividend_yield': item.get('股息率', 0),
                'style': 'value'
            }
            stocks.append(stock)
            print(f"   ✅ {stock['name']}: PE={stock['pe']}, PB={stock['pb']}")
    
    return stocks


def select_us_stocks_growth(integration):
    """问财选美股 - 成长股筛选"""
    print("\n📈 成长股筛选...")
    
    query = "美股 营收增长率高于 20 净利润增长率高于 25"
    data = integration._api_call(query, limit=20)
    
    stocks = []
    if data and data.get('datas'):
        for item in data['datas'][:20]:
            stock = {
                'code': item.get('股票代码', ''),
                'name': item.get('股票简称', ''),
                'revenue_growth': item.get('营收增长率', 0),
                'earnings_growth': item.get('净利润增长率', 0),
                'style': 'growth'
            }
            stocks.append(stock)
            print(f"   ✅ {stock['name']}: 营收增长={stock['revenue_growth']}%")
    
    return stocks


def select_us_stocks_tech(integration):
    """问财选美股 - 科技股筛选"""
    print("\n💻 科技股筛选...")
    
    query = "美股 科技 人工智能 芯片 半导体"
    data = integration._api_call(query, limit=20)
    
    stocks = []
    if data and data.get('datas'):
        for item in data['datas'][:20]:
            stock = {
                'code': item.get('股票代码', ''),
                'name': item.get('股票简称', ''),
                'sector': 'technology',
                'style': 'tech'
            }
            stocks.append(stock)
            print(f"   ✅ {stock['name']}: 科技股")
    
    return stocks


def analyze_us_stock_research(integration, stock_list):
    """美股研报评级分析"""
    print("\n📑 研报评级分析...")
    
    ratings = {'buy': 0, 'hold': 0, 'sell': 0}
    
    for stock in stock_list[:10]:
        query = f"{stock['name']} 研报 评级 目标价"
        data = integration._api_call(query, limit=5)
        
        if data and data.get('datas'):
            for item in data['datas'][:5]:
                title = item.get('标题', '')
                if '买入' in title or '增持' in title:
                    ratings['buy'] += 1
                elif '持有' in title or '中性' in title:
                    ratings['hold'] += 1
                elif '卖出' in title or '减持' in title:
                    ratings['sell'] += 1
    
    print(f"   研报评级：买入{ratings['buy']} 持有{ratings['hold']} 卖出{ratings['sell']}")
    return ratings


def main():
    """主流程"""
    print("=" * 50)
    print("  美股筛选器 (Iwencai 问财选美股)")
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
    
    # 2. 执行筛选
    value_stocks = []
    growth_stocks = []
    tech_stocks = []
    research_ratings = {}
    
    if integration:
        value_stocks = select_us_stocks_value(integration)
        growth_stocks = select_us_stocks_growth(integration)
        tech_stocks = select_us_stocks_tech(integration)
        
        # 研报评级分析
        all_stocks = value_stocks + growth_stocks + tech_stocks
        research_ratings = analyze_us_stock_research(integration, all_stocks)
    
    # 3. 生成结果
    result = {
        'timestamp': datetime.now().isoformat(),
        'value_stocks': value_stocks,
        'growth_stocks': growth_stocks,
        'tech_stocks': tech_stocks,
        'research_ratings': research_ratings,
        'summary': {
            'value_count': len(value_stocks),
            'growth_count': len(growth_stocks),
            'tech_count': len(tech_stocks),
            'total': len(value_stocks) + len(growth_stocks) + len(tech_stocks)
        }
    }
    
    # 4. 保存结果
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\n💾 筛选结果已保存：{OUTPUT_PATH}")
    
    # 5. 总结
    print("\n" + "=" * 50)
    print("  美股筛选完成")
    print("=" * 50)
    print(f"\n📊 筛选汇总:")
    print(f"   价值股：{len(value_stocks)}只")
    print(f"   成长股：{len(growth_stocks)}只")
    print(f"   科技股：{len(tech_stocks)}只")
    print(f"   总计：{result['summary']['total']}只")
    
    print("\n✅ 美股筛选完成！")
    return result


if __name__ == '__main__':
    main()

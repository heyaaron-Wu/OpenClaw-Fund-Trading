#!/usr/bin/env python3.11
"""
Iwencai 技能集成模块 v2 (增强版)
集成新增技能：宏观数据、期货期权、可转债、板块、港股

集成场景:
1. 09:00 健康检查 → 增加宏观经济、期货期权
2. 13:35 候选池刷新 → 增加可转债、板块轮动
3. 14:00 交易决策 → 增加板块资金流向
4. 22:30 日终复盘 → 增加港股、期货市场复盘
"""

import sys
import json
import os
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/home/admin/.openclaw/workspace/05-scripts')
try:
    from iwencai_skill_integration import IwencaiSkillIntegration
    HAS_IWENCAI = True
except ImportError:
    HAS_IWENCAI = False


class IwencaiSkillIntegrationV2:
    """Iwencai 技能集成器 v2 (新增技能)"""
    
    def __init__(self):
        self.integration = IwencaiSkillIntegration() if HAS_IWENCAI else None
    
    # ==================== 09:00 健康检查增强 ====================
    
    def check_macro_economy(self):
        """宏观经济数据检查 (新增：宏观数据查询)
        
        返回:
        - GDP 增速
        - CPI/PPI
        - PMI
        - 社融数据
        - 利率汇率
        """
        print("\n📊 宏观经济数据检查...")
        
        if not self.integration:
            return None
        
        # 查询宏观数据
        query = "中国 GDP CPI PPI PMI 社融 利率"
        data = self.integration._api_call(query, limit=10)
        
        macro_data = {
            'timestamp': datetime.now().isoformat(),
            'indicators': []
        }
        
        if data and data.get('datas'):
            macro_data['indicators'] = data['datas'][:10]
            print(f"   ✅ 获取宏观数据：{len(macro_data['indicators'])}项")
        
        return macro_data
    
    def check_futures_options(self):
        """期货期权市场检查 (新增：期货期权数据查询)
        
        返回:
        - 商品期货 (黄金/原油/铜等)
        - 股指期货 (IF/IC/IM)
        - 期权数据
        - 波动率指数
        """
        print("\n📈 期货期权市场检查...")
        
        if not self.integration:
            return None
        
        # 查询期货数据
        query = "期货行情 黄金 原油 铜 股指期货"
        data = self.integration._api_call(query, limit=10)
        
        futures_data = {
            'timestamp': datetime.now().isoformat(),
            'commodities': [],
            'stock_index_futures': []
        }
        
        if data and data.get('datas'):
            for item in data['datas'][:10]:
                name = item.get('期货简称', item.get('合约名称', ''))
                if any(kw in name for kw in ['黄金', '原油', '铜', '大豆', '螺纹钢']):
                    futures_data['commodities'].append(item)
                elif any(kw in name for kw in ['IF', 'IC', 'IM', 'IH', '股指']):
                    futures_data['stock_index_futures'].append(item)
            
            print(f"   ✅ 商品期货：{len(futures_data['commodities'])}个")
            print(f"   ✅ 股指期货：{len(futures_data['stock_index_futures'])}个")
        
        return futures_data
    
    # ==================== 13:35 候选池增强 ====================
    
    def select_convertible_bonds(self):
        """可转债筛选 (新增：问财选可转债)
        
        返回:
        - 低价格可转债 (<110 元)
        - 低溢价率可转债 (<20%)
        - 高评级可转债 (AA+ 以上)
        """
        print("\n🎫 可转债筛选...")
        
        if not self.integration:
            return []
        
        # 查询可转债
        query = "可转债 价格低于 110 溢价率低于 20 评级 AA"
        data = self.integration._api_call(query, limit=20)
        
        bonds = []
        if data and data.get('datas'):
            for item in data['datas'][:20]:
                bonds.append({
                    'code': item.get('债券代码', ''),
                    'name': item.get('债券简称', ''),
                    'price': item.get('最新价', 0),
                    'premium_rate': item.get('溢价率', 0),
                    'rating': item.get('评级', '')
                })
            print(f"   ✅ 筛选可转债：{len(bonds)}只")
        
        return bonds
    
    def select_sector_rotation(self):
        """板块轮动分析 (新增：问财选板块)
        
        返回:
        - 资金流入前 5 板块
        - 涨幅前 5 板块
        - 板块轮动建议
        """
        print("\n🔄 板块轮动分析...")
        
        if not self.integration:
            return None
        
        # 查询板块资金流向
        query = "板块资金净流入 涨幅居前"
        data = self.integration._api_call(query, limit=15)
        
        sectors = {
            'inflow_top': [],
            'gain_top': [],
            'rotation_suggestion': []
        }
        
        if data and data.get('datas'):
            for item in data['datas'][:15]:
                sectors['inflow_top'].append({
                    'name': item.get('板块名称', ''),
                    'inflow': item.get('资金净流入', 0),
                    'change': item.get('涨跌幅', 0)
                })
            
            # 排序
            sectors['inflow_top'].sort(key=lambda x: x['inflow'], reverse=True)
            sectors['gain_top'] = sorted(sectors['inflow_top'][:5], key=lambda x: x['change'], reverse=True)
            
            # 轮动建议
            if sectors['inflow_top']:
                top_sector = sectors['inflow_top'][0]['name']
                sectors['rotation_suggestion'].append(f"关注资金流入：{top_sector}")
            
            print(f"   ✅ 分析板块：{len(sectors['inflow_top'])}个")
        
        return sectors
    
    # ==================== 14:00 交易决策增强 ====================
    
    def check_sector_fund_flow(self):
        """板块资金流向检查 (新增：问财选板块)
        
        返回:
        - 主力流入板块
        - 主力流出板块
        - 板块轮动信号
        """
        print("\n💰 板块资金流向检查...")
        
        if not self.integration:
            return None
        
        query = "板块资金流向 主力净流入"
        data = self.integration._api_call(query, limit=20)
        
        flow_data = {
            'inflow_sectors': [],
            'outflow_sectors': [],
            'signal': 'neutral'
        }
        
        if data and data.get('datas'):
            for item in data['datas'][:20]:
                sector = {
                    'name': item.get('板块名称', ''),
                    'inflow': item.get('主力净流入', 0),
                    'change': item.get('涨跌幅', 0)
                }
                
                if sector['inflow'] > 0:
                    flow_data['inflow_sectors'].append(sector)
                else:
                    flow_data['outflow_sectors'].append(sector)
            
            # 判断信号
            if len(flow_data['inflow_sectors']) > 10:
                flow_data['signal'] = 'bullish'
            elif len(flow_data['outflow_sectors']) > 10:
                flow_data['signal'] = 'bearish'
            
            print(f"   ✅ 流入板块：{len(flow_data['inflow_sectors'])}个")
            print(f"   ✅ 流出板块：{len(flow_data['outflow_sectors'])}个")
        
        return flow_data
    
    # ==================== 22:30 日终复盘增强 ====================
    
    def review_hk_stocks(self):
        """港股复盘 (新增：问财选港股)
        
        返回:
        - 恒生指数表现
        - 港股通资金流向
        - 热门港股
        """
        print("\n🇭🇰 港股复盘...")
        
        if not self.integration:
            return None
        
        query = "港股 恒生指数 港股通 资金流向"
        data = self.integration._api_call(query, limit=10)
        
        hk_data = {
            'indices': [],
            'hk_connect_flow': 0,
            'hot_stocks': []
        }
        
        if data and data.get('datas'):
            for item in data['datas'][:10]:
                name = item.get('指数简称', item.get('股票简称', ''))
                if '恒生' in name or '国企' in name:
                    hk_data['indices'].append(item)
                elif '港股通' in name:
                    hk_data['hk_connect_flow'] = item.get('资金净流入', 0)
                else:
                    hk_data['hot_stocks'].append(item)
            
            print(f"   ✅ 港股指数：{len(hk_data['indices'])}个")
            print(f"   ✅ 港股通资金：{hk_data['hk_connect_flow']:+.2f}亿")
        
        return hk_data
    
    def review_futures_market(self):
        """期货市场复盘 (新增：期货期权数据查询)
        
        返回:
        - 商品期货涨跌榜
        - 股指期货表现
        - 期货市场情绪
        """
        print("\n📊 期货市场复盘...")
        
        if not self.integration:
            return None
        
        query = "期货行情 涨跌幅 成交量"
        data = self.integration._api_call(query, limit=15)
        
        futures_review = {
            'gainers': [],
            'losers': [],
            'sentiment': 'neutral'
        }
        
        if data and data.get('datas'):
            for item in data['datas'][:15]:
                change = item.get('最新涨跌幅：前复权', 0)
                if isinstance(change, (int, float)):
                    if change > 2:
                        futures_review['gainers'].append({
                            'name': item.get('期货简称', ''),
                            'change': change
                        })
                    elif change < -2:
                        futures_review['losers'].append({
                            'name': item.get('期货简称', ''),
                            'change': change
                        })
            
            # 判断情绪
            if len(futures_review['gainers']) > len(futures_review['losers']):
                futures_review['sentiment'] = 'bullish'
            else:
                futures_review['sentiment'] = 'bearish'
            
            print(f"   ✅ 上涨期货：{len(futures_review['gainers'])}个")
            print(f"   ✅ 下跌期货：{len(futures_review['losers'])}个")
        
        return futures_review


# ==================== CLI 入口 ====================

if __name__ == "__main__":
    v2 = IwencaiSkillIntegrationV2()
    
    print("=" * 50)
    print("  Iwencai 技能集成 v2 测试")
    print("=" * 50)
    
    # 测试 09:00 增强
    print("\n📊 09:00 健康检查增强:")
    macro = v2.check_macro_economy()
    futures = v2.check_futures_options()
    
    # 测试 13:35 增强
    print("\n📈 13:35 候选池增强:")
    bonds = v2.select_convertible_bonds()
    sectors = v2.select_sector_rotation()
    
    # 测试 14:00 增强
    print("\n💰 14:00 交易决策增强:")
    flow = v2.check_sector_fund_flow()
    
    # 测试 22:30 增强
    print("\n🌙 22:30 日终复盘增强:")
    hk = v2.review_hk_stocks()
    futures_review = v2.review_futures_market()
    
    print("\n✅ v2 集成测试完成！")

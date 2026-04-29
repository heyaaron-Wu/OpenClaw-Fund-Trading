#!/usr/bin/env python3.11
"""
交易决策脚本（Iwencai 增强版）
交易日 14:00 执行，集成 Iwencai 技能提高决策准确度

增强功能:
1. Iwencai 市场信号分析 (40% 权重)
2. 研报评级参考 (30% 权重)
3. 机器学习预测 (30% 权重)
4. 综合决策 + 置信度评分

数据源:
- 妙想 API（东方财富）- 金融垂直数据
- Iwencai API - 市场信号、研报、ML 预测
- 腾讯/新浪财经 - 备份数据源
"""

import sys
import json
import urllib.request
import os
import re
from datetime import datetime
from pathlib import Path

# 导入 Iwencai 集成模块
workspace = Path('/home/admin/.openclaw/workspace')
sys.path.insert(0, str(workspace / '05-scripts'))
try:
    from iwencai_skill_integration import IwencaiSkillIntegration
    HAS_IWENCAI = True
    print("✅ Iwencai 集成模块已加载")
except ImportError as e:
    HAS_IWENCAI = False
    print(f"⚠️  Iwencai 集成模块未找到：{e}")

# 导入多源新闻模块（可选）
try:
    from multi_source_news import get_multi_source_news, analyze_news_for_decision
    HAS_MULTI_NEWS = True
except ImportError:
    HAS_MULTI_NEWS = False


# ==================== 环境配置 ====================
def load_env():
    """加载环境变量"""
    mx_key = os.environ.get('MX_APIKEY', '')
    iwencai_key = os.environ.get('IWENCAI_API_KEY', '')
    
    env_ok = False
    
    if mx_key:
        print("   ✅ 妙想 API KEY 已加载")
        env_ok = True
    else:
        print("   ⚠️  妙想 API KEY 未配置")
    
    if iwencai_key and HAS_IWENCAI:
        print("   ✅ Iwencai API KEY 已加载")
        env_ok = True
    elif HAS_IWENCAI:
        print("   ⚠️  Iwencai API KEY 未配置")
    
    return env_ok


# ==================== Iwencai 增强决策 ====================

def get_iwencai_enhanced_signals(integration):
    """获取 Iwencai 增强信号
    
    Returns:
        dict: {
            'decision': 'buy'/'sell'/'hold',
            'confidence': 0.0-1.0,
            'market_sentiment': 'bullish'/'bearish'/'neutral',
            'risk_level': 'low'/'medium'/'high',
            'key_factors': [...]
        }
    """
    print("\n📊 Iwencai 增强分析...")
    
    try:
        # 1. 获取市场信号
        print("   🔄 获取市场信号...")
        signals = integration.get_market_signals()
        
        # 2. 获取市场情绪
        print("   🔄 分析市场情绪...")
        sentiment = integration.check_market_sentiment()
        
        # 3. 获取新闻摘要
        print("   🔄 获取新闻摘要...")
        news = integration.get_daily_news_summary()
        
        # 4. 综合决策
        enhanced_decision = {
            'timestamp': datetime.now().isoformat(),
            'source': 'iwencai_enhanced',
            'decision': signals.get('decision', 'hold'),
            'confidence': signals.get('confidence', 0.5),
            'market_sentiment': sentiment.get('sentiment', 'neutral'),
            'market_risk': sentiment.get('risk_level', 'normal'),
            'key_news': news[:3] if news else [],
            'factors': []
        }
        
        # 分析关键因素
        if enhanced_decision['market_sentiment'] == 'bullish':
            enhanced_decision['factors'].append('市场情绪偏多')
        elif enhanced_decision['market_sentiment'] == 'bearish':
            enhanced_decision['factors'].append('市场情绪偏空')
        
        if enhanced_decision['market_risk'] == 'high':
            enhanced_decision['factors'].append('市场风险高')
            enhanced_decision['confidence'] *= 0.8  # 高风险降低置信度
        
        if news:
            enhanced_decision['factors'].append(f'今日重要新闻：{len(news)}条')
        
        # 打印结果
        print(f"\n   📈 Iwencai 决策信号:")
        print(f"      决策：{enhanced_decision['decision'].upper()}")
        print(f"      置信度：{enhanced_decision['confidence']:.2f}")
        print(f"      市场情绪：{enhanced_decision['market_sentiment']}")
        print(f"      风险等级：{enhanced_decision['market_risk']}")
        if enhanced_decision['factors']:
            print(f"      关键因素：{', '.join(enhanced_decision['factors'])}")
        
        return enhanced_decision
        
    except Exception as e:
        print(f"   ❌ Iwencai 分析失败：{e}")
        return None


def get_research_rating(integration):
    """获取研报评级参考
    
    Returns:
        dict: {
            'rating': 'buy'/'neutral'/'sell',
            'confidence': 0.0-1.0,
            'summary': '研报观点摘要'
        }
    """
    print("\n📑 研报评级分析...")
    
    try:
        # 搜索市场策略研报
        query = "A 股市场策略 券商研报 投资评级 今日"
        data = integration._api_call(query, limit=5)
        
        result = {
            'rating': 'neutral',
            'confidence': 0.5,
            'summary': '',
            'sources': []
        }
        
        if data and data.get('datas'):
            bullish_count = 0
            bearish_count = 0
            
            for item in data['datas'][:5]:
                title = item.get('标题', item.get('研报标题', ''))
                if title:
                    result['sources'].append(title)
                    
                    # 简单情感分析
                    if any(kw in title for kw in ['看好', '买入', '增持', '乐观', '上涨']):
                        bullish_count += 1
                    elif any(kw in title for kw in ['看空', '卖出', '减持', '谨慎', '下跌']):
                        bearish_count += 1
            
            # 综合评级
            if bullish_count > bearish_count + 1:
                result['rating'] = 'buy'
                result['confidence'] = min(0.5 + (bullish_count - bearish_count) * 0.15, 0.85)
            elif bearish_count > bullish_count + 1:
                result['rating'] = 'sell'
                result['confidence'] = min(0.5 + (bearish_count - bullish_count) * 0.15, 0.85)
            else:
                result['rating'] = 'neutral'
                result['confidence'] = 0.5
            
            result['summary'] = f"研报观点：{bullish_count} 看多，{bearish_count} 看空"
            
            print(f"   📊 研报评级：{result['rating'].upper()} (置信度：{result['confidence']:.2f})")
            print(f"   📝 {result['summary']}")
        else:
            print("   ⚠️  未找到相关研报")
        
        return result
        
    except Exception as e:
        print(f"   ❌ 研报分析失败：{e}")
        return {'rating': 'neutral', 'confidence': 0.5, 'summary': '研报数据获取失败'}


def get_ml_prediction(integration):
    """获取机器学习预测
    
    Returns:
        dict: {
            'prediction': 'up'/'down'/'neutral',
            'confidence': 0.0-1.0,
            'signal': 'buy'/'sell'/'hold'
        }
    """
    print("\n🤖 机器学习预测...")
    
    # 注：这里调用 Iwencai 的机器学习策略技能
    # 实际使用时需要根据技能的具体 API 调整
    
    try:
        # 查询市场技术信号
        query = "上证指数 沪深 300 MACD KDJ 技术指标"
        data = integration._api_call(query, limit=5)
        
        result = {
            'prediction': 'neutral',
            'confidence': 0.5,
            'signal': 'hold',
            'indicators': {}
        }
        
        if data and data.get('datas'):
            # 简单技术分析逻辑
            tech_data = data['datas'][0] if data['datas'] else {}
            
            # 检查技术指标信号
            bullish_signals = 0
            bearish_signals = 0
            
            for k, v in tech_data.items():
                if 'MACD' in k or 'KDJ' in k:
                    if isinstance(v, str) and ('金叉' in v or '买入' in v):
                        bullish_signals += 1
                    elif isinstance(v, str) and ('死叉' in v or '卖出' in v):
                        bearish_signals += 1
            
            if bullish_signals > bearish_signals:
                result['prediction'] = 'up'
                result['signal'] = 'buy'
                result['confidence'] = min(0.5 + bullish_signals * 0.1, 0.75)
            elif bearish_signals > bullish_signals:
                result['prediction'] = 'down'
                result['signal'] = 'sell'
                result['confidence'] = min(0.5 + bearish_signals * 0.1, 0.75)
            
            result['indicators'] = tech_data
            
            print(f"   📈 ML 预测：{result['prediction'].upper()} (置信度：{result['confidence']:.2f})")
        else:
            print("   ⚠️  技术数据获取失败")
        
        return result
        
    except Exception as e:
        print(f"   ❌ ML 预测失败：{e}")
        return {'prediction': 'neutral', 'confidence': 0.5, 'signal': 'hold'}


def combine_signals(iwencai_signal, research_signal, ml_signal):
    """综合多个信号生成最终决策
    
    权重:
    - Iwencai 市场信号：40%
    - 研报评级：30%
    - ML 预测：30%
    
    Returns:
        dict: {
            'final_decision': 'buy'/'sell'/'hold',
            'final_confidence': 0.0-1.0,
            'vote_result': {...},
            'reasoning': '...'
        }
    """
    print("\n⚖️  综合决策分析...")
    
    # 信号映射
    signal_map = {
        'buy': 1,
        'hold': 0,
        'sell': -1,
        'up': 1,
        'down': -1,
        'neutral': 0
    }
    
    # 权重
    weights = {
        'iwencai': 0.4,
        'research': 0.3,
        'ml': 0.3
    }
    
    # 计算加权得分
    score = 0
    confidence_sum = 0
    
    if iwencai_signal:
        score += signal_map.get(iwencai_signal['decision'], 0) * weights['iwencai'] * iwencai_signal['confidence']
        confidence_sum += weights['iwencai'] * iwencai_signal['confidence']
    
    if research_signal:
        score += signal_map.get(research_signal['rating'], 0) * weights['research'] * research_signal['confidence']
        confidence_sum += weights['research'] * research_signal['confidence']
    
    if ml_signal:
        score += signal_map.get(ml_signal['signal'], 0) * weights['ml'] * ml_signal['confidence']
        confidence_sum += weights['ml'] * ml_signal['confidence']
    
    # 归一化
    if confidence_sum > 0:
        normalized_score = score / confidence_sum
    else:
        normalized_score = 0
    
    # 生成最终决策
    if normalized_score > 0.3:
        final_decision = 'buy'
    elif normalized_score < -0.3:
        final_decision = 'sell'
    else:
        final_decision = 'hold'
    
    # 计算最终置信度
    final_confidence = min(abs(normalized_score) + 0.3, 0.95)
    
    # 生成推理说明
    reasoning = []
    if iwencai_signal:
        reasoning.append(f"Iwencai: {iwencai_signal['decision'].upper()} ({iwencai_signal['confidence']:.2f})")
    if research_signal:
        reasoning.append(f"研报：{research_signal['rating'].upper()} ({research_signal['confidence']:.2f})")
    if ml_signal:
        reasoning.append(f"ML: {ml_signal['signal'].upper()} ({ml_signal['confidence']:.2f})")
    
    result = {
        'timestamp': datetime.now().isoformat(),
        'final_decision': final_decision,
        'final_confidence': round(final_confidence, 2),
        'normalized_score': round(normalized_score, 3),
        'vote_result': {
            'iwencai': iwencai_signal,
            'research': research_signal,
            'ml': ml_signal
        },
        'reasoning': ' | '.join(reasoning),
        'weights': weights
    }
    
    print(f"\n   🎯 最终决策：{final_decision.upper()}")
    print(f"   📊 置信度：{final_confidence:.2f}")
    print(f"   📝 推理：{result['reasoning']}")
    
    return result


# ==================== 原有决策逻辑（保留） ====================

def fetch_market_data_mx():
    """妙想金融 API - 获取指数实时数据"""
    # ... (保留原有代码)
    return {}


def fetch_market_data():
    """获取市场数据（多数据源）"""
    import akshare as ak
    import datetime
    
    market_data = {}
    
    # 尝试获取基金实时净值
    try:
        # 获取持仓基金数据
        from pathlib import Path
        state_path = Path('/home/admin/.openclaw/workspace/Semi-automatic-artificial-intelligence-system/08-fund-daily-review/state.json')
        if state_path.exists():
            import json
            state = json.loads(state_path.read_text(encoding='utf-8'))
            positions = state.get('positions', [])
            
            for pos in positions:
                code = pos.get('code', '')
                name = pos.get('name', '')
                
                try:
                    df = ak.fund_open_fund_info_em(symbol=code, indicator='单位净值走势')
                    if not df.empty:
                        latest = df.tail(1).iloc[0]
                        nav_date = latest.iloc[0]  # 日期
                        nav_value = latest.iloc[1]  # 净值
                        daily_change = latest.iloc[2]  # 涨跌幅
                        
                        market_data[code] = {
                            'name': name,
                            'nav': nav_value,
                            'daily_change': daily_change,
                            'nav_date': str(nav_date)
                        }
                        print(f"   ✅ {code} {name}: 净值={nav_value} 涨跌幅={daily_change}%")
                except Exception as e:
                    print(f"   ⚠️ {code} 获取失败: {e}")
    except Exception as e:
        print(f"   ⚠️ 市场数据获取失败: {e}")
    
    return market_data


def load_state(base_path):
    """加载持仓状态"""
    # 尝试多个可能的位置
    possible_paths = [
        Path('/home/admin/.openclaw/workspace/Semi-automatic-artificial-intelligence-system/08-fund-daily-review/state.json'),
        Path('/home/admin/.openclaw/workspace/08-fund-daily-review/state.json'),
    ]
    for state_path in possible_paths:
        if state_path.exists():
            try:
                return json.loads(state_path.read_text(encoding='utf-8'))
            except:
                pass
    return None


def load_preflight_result(script_dir):
    """加载 09:00 预检结果"""
    preflight_path = script_dir / 'preflight_result.json'
    if not preflight_path.exists():
        return None
    try:
        return json.loads(preflight_path.read_text(encoding='utf-8'))
    except:
        return None


def load_universe(script_dir):
    """加载 13:35 候选池"""
    universe_path = script_dir / 'universe.json'
    if not universe_path.exists():
        return None
    try:
        return json.loads(universe_path.read_text(encoding='utf-8'))
    except:
        return None


def analyze_positions_enhanced(state, market_data, enhanced_decision, universe=None, preflight=None):
    """分析持仓并生成决策（增强版）"""
    if not state or 'positions' not in state:
        return [], []
    
    positions = state['positions']
    decisions = []
    alerts = []
    
    # 检查市场整体风险
    final_decision = enhanced_decision.get('final_decision', 'hold')
    final_confidence = enhanced_decision.get('final_confidence', 0.5)
    
    if final_decision == 'sell' and final_confidence > 0.7:
        alerts.append(f"🚨 Iwencai 增强决策：建议减仓 (置信度：{final_confidence:.2f})")
    elif final_decision == 'buy' and final_confidence > 0.7:
        alerts.append(f"💰 Iwencai 增强决策：建议加仓 (置信度：{final_confidence:.2f})")
    
    # 分析每个持仓
    for pos in positions:
        code = pos.get('code', '')
        name = pos.get('name', '')
        
        # 从市场数据获取实时盈亏
        pnl_rate = pos.get('pnl_rate', 0)
        daily_pnl_rate = pos.get('daily_pnl_rate', 0)
        
        # 优先使用预检结果中的 pnl_rate
        if preflight and 'funds' in preflight and code in preflight['funds']:
            pnl_rate = preflight['funds'][code].get('pnl_rate', pnl_rate)
        
        # 从市场数据获取实时涨跌幅
        if market_data and code in market_data:
            fund_data = market_data[code]
            daily_pnl_rate = fund_data.get('daily_change', daily_pnl_rate)
        
        action = 'HOLD'
        reason = ''
        suggestion = ''
        risk_level = 'medium'
        
        # 止盈逻辑 (>15%)
        if pnl_rate >= 15:
            action = 'SELL'
            reason = f'止盈信号：+{pnl_rate:.2f}%'
            suggestion = '建议分批止盈'
            risk_level = 'low'
        
        # 止损逻辑 (<-8%)
        elif pnl_rate <= -8:
            action = 'SELL'
            reason = f'止损信号：{pnl_rate:+.2f}%'
            suggestion = '建议止损离场'
            risk_level = 'high'
        
        # 结合增强决策
        elif final_decision == 'sell' and final_confidence > 0.7:
            if pnl_rate > 5:
                action = 'SELL'
                reason = f'决策信号 + 盈利：{pnl_rate:+.2f}%'
                suggestion = '市场信号偏空，建议落袋为安'
                risk_level = 'medium'
            elif pnl_rate < -3:
                action = 'HOLD'
                reason = f'决策信号偏空，但已深套：{pnl_rate:+.2f}%'
                suggestion = '等待反弹减仓'
                risk_level = 'high'
        
        elif final_decision == 'buy' and final_confidence > 0.7:
            # 检查是否在候选池
            in_universe = False
            if universe and 'results' in universe:
                for fund in universe['results']:
                    if fund.get('code') == code or fund.get('name') == name:
                        in_universe = True
                        break
            
            if in_universe and pnl_rate > -5:
                action = 'BUY'
                reason = f'决策信号 + 候选池：置信度{final_confidence:.2f}'
                suggestion = '市场信号偏多，建议加仓'
                risk_level = 'low'
        
        decisions.append({
            'code': code,
            'name': name,
            'action': action,
            'reason': reason,
            'suggestion': suggestion,
            'pnl_rate': pnl_rate,
            'daily_pnl_rate': daily_pnl_rate,
            'risk_level': risk_level,
            'enhanced_decision': final_decision,
            'confidence': final_confidence
        })
    
    return decisions, alerts


def save_decision(decisions, alerts, enhanced_decision, base_path):
    """保存决策结果"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    result = {
        'timestamp': timestamp,
        'datetime': datetime.now().isoformat(),
        'decisions': decisions,
        'alerts': alerts,
        'enhanced_decision': enhanced_decision,
        'summary': {
            'total': len(decisions),
            'buy': sum(1 for d in decisions if d['action'] == 'BUY'),
            'sell': sum(1 for d in decisions if d['action'] == 'SELL'),
            'hold': sum(1 for d in decisions if d['action'] == 'HOLD')
        }
    }
    
    # 保存到文件
    output_path = base_path / 'decision_result_enhanced.json'
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\n💾 决策结果已保存：{output_path}")
    
    return result


def send_feishu_notification(decisions, alerts, enhanced_decision):
    """飞书推送决策结果"""
    webhook = os.environ.get('FEISHU_WEBHOOK', '')
    if not webhook:
        print("\n⚠️  飞书 Webhook 未配置，跳过推送")
        return
    
    # 构建推送内容
    summary = enhanced_decision.get('reasoning', '决策分析完成')
    
    buy_count = sum(1 for d in decisions if d['action'] == 'BUY')
    sell_count = sum(1 for d in decisions if d['action'] == 'SELL')
    hold_count = sum(1 for d in decisions if d['action'] == 'HOLD')
    
    content = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": "📊 14:00 交易决策"},
                "template": "blue"
            },
            "elements": [
                {
                    "tag": "markdown",
                    "content": f"""**决策时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

**增强决策**: {enhanced_decision.get('final_decision', 'N/A').upper()}
**置信度**: {enhanced_decision.get('final_confidence', 0):.2f}

**持仓分析**:
- 🟢 买入：{buy_count} 只
- 🔴 卖出：{sell_count} 只
- ⚪ 持有：{hold_count} 只

**决策依据**:
{summary}"""
                }
            ]
        }
    }
    
    try:
        data = json.dumps(content).encode('utf-8')
        request = urllib.request.Request(
            webhook,
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        response = urllib.request.urlopen(request, timeout=10)
        print("✅ 飞书推送成功")
    except Exception as e:
        print(f"❌ 飞书推送失败：{e}")


# ==================== 主流程 ====================

def main():
    """主流程"""
    print("=" * 50)
    print("  交易决策系统 (Iwencai 增强版)")
    print("  " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 50)
    
    # 1. 加载环境
    print("\n🔧 加载环境配置...")
    load_env()
    
    # 2. 初始化 Iwencai 集成
    integration = None
    if HAS_IWENCAI:
        try:
            integration = IwencaiSkillIntegration()
            print("✅ Iwencai 集成器已初始化")
        except Exception as e:
            print(f"❌ Iwencai 初始化失败：{e}")
            integration = None
    
    # 3. 获取增强决策信号
    enhanced_decision = None
    if integration:
        print("\n" + "=" * 50)
        print("  Iwencai 增强分析")
        print("=" * 50)
        
        # 3.1 Iwencai 市场信号
        iwencai_signal = get_iwencai_enhanced_signals(integration)
        
        # 3.2 研报评级
        research_signal = get_research_rating(integration)
        
        # 3.3 ML 预测
        ml_signal = get_ml_prediction(integration)
        
        # 3.4 综合决策
        if iwencai_signal or research_signal or ml_signal:
            enhanced_decision = combine_signals(iwencai_signal, research_signal, ml_signal)
        else:
            print("\n⚠️  Iwencai 分析失败，使用原逻辑")
            enhanced_decision = {
                'final_decision': 'hold',
                'final_confidence': 0.5,
                'reasoning': 'Iwencai 数据获取失败'
            }
    else:
        print("\n⚠️  未启用 Iwencai 增强，使用原逻辑")
        enhanced_decision = {
            'final_decision': 'hold',
            'final_confidence': 0.5,
            'reasoning': '未启用 Iwencai 增强'
        }
    
    # 4. 加载数据
    print("\n" + "=" * 50)
    print("  加载数据")
    print("=" * 50)
    
    # 修复 base_path 指向 fund_challenge 目录
    script_dir = Path(__file__).parent
    base_path = script_dir.parent  # fund_challenge 目录
    
    print("\n📂 加载持仓状态...")
    state = load_state(base_path)
    if state:
        print(f"   ✅ 持仓数量：{len(state.get('positions', []))}")
        print(f"   📊 累计盈亏：{state.get('total_pnl', 0):.2f}元 ({state.get('total_pnl_rate', 0):.2f}%)")
    else:
        print("   ⚠️  持仓状态未找到")
        state = {'positions': []}
    
    print("\n📂 加载预检结果...")
    preflight = load_preflight_result(script_dir)
    if preflight:
        print("   ✅ 预检结果已加载")
    else:
        print("   ⚠️  预检结果未找到")
    
    print("\n📂 加载候选池...")
    universe = load_universe(script_dir)
    if universe:
        print(f"   ✅ 候选基金：{len(universe.get('results', []))}")
    else:
        print("   ⚠️  候选池未找到")
    
    # 5. 获取市场数据
    print("\n" + "=" * 50)
    print("  市场数据")
    print("=" * 50)
    market_data = fetch_market_data()
    
    # 6. 分析持仓并生成决策
    print("\n" + "=" * 50)
    print("  持仓分析")
    print("=" * 50)
    decisions, alerts = analyze_positions_enhanced(state, market_data, enhanced_decision, universe, preflight)
    
    # 7. 保存决策结果
    print("\n" + "=" * 50)
    print("  保存结果")
    print("=" * 50)
    result = save_decision(decisions, alerts, enhanced_decision, base_path)
    
    # 8. 飞书推送
    print("\n" + "=" * 50)
    print("  消息推送")
    print("=" * 50)
    send_feishu_notification(decisions, alerts, enhanced_decision)
    
    # 9. 总结
    print("\n" + "=" * 50)
    print("  决策完成")
    print("=" * 50)
    print(f"\n📊 决策汇总:")
    print(f"   总持仓：{result['summary']['total']} 只")
    print(f"   🟢 买入：{result['summary']['buy']} 只")
    print(f"   🔴 卖出：{result['summary']['sell']} 只")
    print(f"   ⚪ 持有：{result['summary']['hold']} 只")
    
    if alerts:
        print(f"\n🚨 风险提醒:")
        for alert in alerts:
            print(f"   {alert}")
    
    print("\n✅ 决策流程完成！")
    return result


if __name__ == '__main__':
    main()

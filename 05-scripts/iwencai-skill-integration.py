#!/usr/bin/env python3
"""
Iwencai 技能集成模块
将 Iwencai SkillHub 技能集成到基金交易决策流程中，提高决策准确度

集成场景:
1. 09:00 健康检查 → 增加市场情绪、资金流向分析
2. 13:35 候选池刷新 → 增加财务数据验证、行业数据对比
3. 14:00 交易决策 → 增加行情数据、新闻情绪、研报评级
4. 14:48 执行门控 → 增加主力资金流向、技术指标确认
5. 22:30 日终复盘 → 增加公告搜索、行业对比分析

技能清单 (17 个):
- 数据查询 (7 个): 财务、行业、行情、指数、基金理财、新闻、公告
- 智能筛选 (3 个): 问财选基金、问财选基金公司、问财选美股
- 量化策略 (1 个): 机器学习策略
- 风险分析 (1 个): 地缘政治风险分析
- 监管知识 (1 个): 金融监管知识库
- 基金分析 (1 个): 基金分析与筛选
- 行业分析 (1 个): 科技炒作与基本面
- 投资研究 (2 个): 投资想法生成、研报搜索
"""

import os
import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

# API 配置
IWENCAI_BASE_URL = os.environ.get('IWENCAI_BASE_URL', 'https://openapi.iwencai.com')
IWENCAI_API_KEY = os.environ.get('IWENCAI_API_KEY', '')

# 工作区路径
WORKSPACE = Path('/home/admin/.openclaw/workspace')
STATE_PATH = WORKSPACE / '08-fund-daily-review' / 'state.json'
LEDGER_PATH = WORKSPACE / '08-fund-daily-review' / 'ledger.jsonl'
INTEGRATION_CACHE = WORKSPACE / '06-data' / 'iwencai_cache.json'


class IwencaiSkillIntegration:
    """Iwencai 技能集成器"""
    
    def __init__(self):
        self.api_key = IWENCAI_API_KEY
        self.base_url = IWENCAI_BASE_URL
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """加载缓存数据"""
        if INTEGRATION_CACHE.exists():
            try:
                data = json.loads(INTEGRATION_CACHE.read_text(encoding='utf-8'))
                # 清理过期缓存 (超过 24 小时)
                cutoff = datetime.now().timestamp() - 86400
                return {k: v for k, v in data.items() if v.get('timestamp', 0) > cutoff}
            except:
                pass
        return {}
    
    def _save_cache(self):
        """保存缓存数据"""
        INTEGRATION_CACHE.parent.mkdir(parents=True, exist_ok=True)
        INTEGRATION_CACHE.write_text(json.dumps(self.cache, ensure_ascii=False, indent=2), encoding='utf-8')
    
    def _api_call(self, query: str, page: int = 1, limit: int = 10) -> Optional[Dict]:
        """调用 Iwencai API
        
        Args:
            query: 查询语句
            page: 页码
            limit: 每页数量
            
        Returns:
            API 响应数据，失败返回 None
        """
        if not self.api_key:
            print("[ERROR] IWENCAI_API_KEY 未配置")
            return None
        
        url = f"{self.base_url}/v1/query2data"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "query": query,
            "page": str(page),
            "limit": str(limit),
            "is_cache": "1",
            "expand_index": "true"
        }
        
        try:
            data = json.dumps(payload).encode("utf-8")
            request = urllib.request.Request(url, data=data, headers=headers, method="POST")
            response = urllib.request.urlopen(request, timeout=30)
            result = json.loads(response.read().decode("utf-8"))
            
            if result.get("status_code", 1) != 0:
                print(f"[API ERROR] {result.get('status_msg', 'Unknown error')}")
                return None
            
            return result
        except Exception as e:
            print(f"[API ERROR] {str(e)}")
            return None
    
    # ==================== 09:00 健康检查增强 ====================
    
    def check_market_sentiment(self) -> Dict:
        """检查市场情绪 (09:00 健康检查增强)
        
        返回:
        - 三大指数涨跌幅
        - 涨跌家数比
        - 涨停/跌停家数
        - 北向资金流向
        """
        cache_key = "market_sentiment_" + datetime.now().strftime("%Y-%m-%d")
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # 查询市场情绪指标
        queries = [
            "上证指数 深证成指 创业板指 今日涨跌幅",
            "全市场涨跌家数比",
            "涨停板 跌停板 家数",
            "北向资金 今日净流入"
        ]
        
        result = {
            "timestamp": datetime.now().timestamp(),
            "indices": [],
            "sentiment": "neutral",
            "risk_level": "normal"
        }
        
        for query in queries:
            data = self._api_call(query, limit=5)
            if data and data.get("datas"):
                result["indices"].extend(data["datas"][:3])
        
        # 简单情绪判断
        if result["indices"]:
            avg_change = 0
            count = 0
            for item in result["indices"]:
                for k, v in item.items():
                    if "涨跌幅" in k and isinstance(v, str) and '%' in v:
                        try:
                            val = float(v.replace('%', '').replace('+', ''))
                            avg_change += val
                            count += 1
                        except:
                            pass
            if count > 0:
                avg_change /= count
                if avg_change > 1:
                    result["sentiment"] = "bullish"
                    result["risk_level"] = "low"
                elif avg_change < -1:
                    result["sentiment"] = "bearish"
                    result["risk_level"] = "high"
        
        self.cache[cache_key] = result
        self._save_cache()
        return result
    
    # ==================== 13:35 候选池刷新增强 ====================
    
    def validate_fundamentals(self, fund_codes: List[str]) -> Dict[str, Dict]:
        """验证基金基本面数据 (13:35 候选池增强)
        
        Args:
            fund_codes: 基金代码列表
            
        Returns:
            每只基金的基本面验证结果
        """
        result = {}
        
        for code in fund_codes:
            # 查询基金财务数据
            query = f"{code} 基金 规模 收益率 评级"
            data = self._api_call(query, limit=5)
            
            if data and data.get("datas"):
                fund_data = data["datas"][0] if data["datas"] else {}
                result[code] = {
                    "valid": True,
                    "data": fund_data,
                    "score": self._calculate_fund_score(fund_data)
                }
            else:
                result[code] = {
                    "valid": False,
                    "data": {},
                    "score": 0
                }
        
        return result
    
    def _calculate_fund_score(self, fund_data: Dict) -> float:
        """计算基金综合得分"""
        score = 50.0  # 基础分
        
        # 规模加分 (10 亿 -100 亿为佳)
        if "基金规模" in fund_data:
            try:
                size_str = fund_data["基金规模"]
                if "亿" in size_str:
                    size = float(size_str.replace("亿", ""))
                    if 10 <= size <= 100:
                        score += 20
                    elif 5 <= size < 10 or 100 < size <= 200:
                        score += 10
            except:
                pass
        
        # 收益率加分
        if "近 1 年收益率" in fund_data:
            try:
                ret_str = fund_data["近 1 年收益率"]
                ret = float(ret_str.replace("%", "").replace("+", ""))
                if ret > 15:
                    score += 20
                elif ret > 5:
                    score += 10
            except:
                pass
        
        # 评级加分
        if "评级" in fund_data:
            rating = fund_data["评级"]
            if "五星" in rating or "5 星" in rating:
                score += 15
            elif "四星" in rating or "4 星" in rating:
                score += 10
        
        return min(score, 100)
    
    # ==================== 14:00 交易决策增强 ====================
    
    def get_market_signals(self) -> Dict:
        """获取市场信号 (14:00 决策增强)
        
        返回:
        - 指数行情
        - 资金流向
        - 涨跌停数据
        - 决策建议
        """
        cache_key = "market_signals_" + datetime.now().strftime("%Y-%m-%d %H")
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # 查询关键信号
        signals = {
            "timestamp": datetime.now().timestamp(),
            "index_signal": "neutral",
            "fund_flow_signal": "neutral",
            "sentiment_signal": "neutral",
            "decision": "hold",
            "confidence": 0.5
        }
        
        # 1. 指数信号
        index_data = self._api_call("上证指数 沪深 300 今日涨跌幅 成交量", limit=5)
        if index_data and index_data.get("datas"):
            signals["index_data"] = index_data["datas"]
        
        # 2. 资金流向
        flow_data = self._api_call("主力资金净流入 北向资金流向", limit=5)
        if flow_data and flow_data.get("datas"):
            signals["flow_data"] = flow_data["datas"]
        
        # 3. 涨跌停情绪
        sentiment_data = self._api_call("涨停家数 跌停家数", limit=5)
        if sentiment_data and sentiment_data.get("datas"):
            signals["sentiment_data"] = sentiment_data["datas"]
        
        # 简单决策逻辑
        bullish_count = 0
        bearish_count = 0
        
        # 分析指数
        if "index_data" in signals:
            for item in signals["index_data"]:
                for k, v in item.items():
                    if "涨跌幅" in k and isinstance(v, str):
                        try:
                            val = float(v.replace("%", "").replace("+", ""))
                            if val > 0.5:
                                bullish_count += 1
                            elif val < -0.5:
                                bearish_count += 1
                        except:
                            pass
        
        # 分析资金流
        if "flow_data" in signals:
            for item in signals["flow_data"]:
                for k, v in item.items():
                    if "净流入" in k and isinstance(v, str) and "亿" in v:
                        try:
                            val = float(v.replace("亿", "").replace("+", ""))
                            if val > 10:
                                bullish_count += 2
                            elif val < -10:
                                bearish_count += 2
                        except:
                            pass
        
        # 决策
        if bullish_count > bearish_count + 2:
            signals["decision"] = "buy"
            signals["confidence"] = min(0.5 + (bullish_count - bearish_count) * 0.1, 0.9)
        elif bearish_count > bullish_count + 2:
            signals["decision"] = "sell"
            signals["confidence"] = min(0.5 + (bearish_count - bullish_count) * 0.1, 0.9)
        else:
            signals["decision"] = "hold"
            signals["confidence"] = 0.5
        
        self.cache[cache_key] = signals
        self._save_cache()
        return signals
    
    # ==================== 14:48 执行门控增强 ====================
    
    def confirm_technical_signals(self, fund_code: str) -> Dict:
        """确认技术信号 (14:48 执行门控增强)
        
        Args:
            fund_code: 基金代码
            
        Returns:
            技术信号确认结果
        """
        query = f"{fund_code} 实时价格 涨跌幅 成交量 MACD KDJ"
        data = self._api_call(query, limit=5)
        
        result = {
            "fund_code": fund_code,
            "confirmed": False,
            "signals": {},
            "action": "wait"
        }
        
        if data and data.get("datas"):
            tech_data = data["datas"][0]
            result["signals"] = tech_data
            result["confirmed"] = True
            
            # 简单技术判断
            # 如果涨跌幅在合理范围内且成交量正常，确认执行
            for k, v in tech_data.items():
                if "涨跌幅" in k and isinstance(v, str):
                    try:
                        change = float(v.replace("%", "").replace("+", ""))
                        if -2 <= change <= 5:  # 合理波动范围
                            result["action"] = "execute"
                    except:
                        pass
        
        return result
    
    # ==================== 22:30 日终复盘增强 ====================
    
    def get_daily_news_summary(self) -> List[str]:
        """获取每日新闻摘要 (22:30 复盘增强)
        
        Returns:
            重要新闻标题列表
        """
        today = datetime.now().strftime("%Y-%m-%d")
        cache_key = "daily_news_" + today
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        query = f"今日财经新闻 重要事件 {today}"
        data = self._api_call(query, limit=10)
        
        news_list = []
        if data and data.get("datas"):
            for item in data["datas"][:10]:
                # 提取新闻标题
                title = item.get("标题", item.get("新闻标题", ""))
                if title:
                    news_list.append(title)
        
        self.cache[cache_key] = news_list
        self._save_cache()
        return news_list
    
    def search_fund_announcements(self, fund_codes: List[str]) -> Dict[str, List[str]]:
        """搜索基金公告 (22:30 复盘增强)
        
        Args:
            fund_codes: 基金代码列表
            
        Returns:
            每只基金的重要公告列表
        """
        result = {}
        
        for code in fund_codes:
            query = f"{code} 基金公告 分红 经理变更"
            data = self._api_call(query, limit=5)
            
            announcements = []
            if data and data.get("datas"):
                for item in data["datas"][:5]:
                    title = item.get("公告标题", item.get("标题", ""))
                    if title:
                        announcements.append(title)
            
            result[code] = announcements
        
        return result
    
    # ==================== 综合分析 ====================
    
    def generate_enhanced_decision(self, current_position: Dict) -> Dict:
        """生成增强型交易决策
        
        Args:
            current_position: 当前持仓信息
            
        Returns:
            增强决策建议
        """
        # 1. 获取市场信号
        market_signals = self.get_market_signals()
        
        # 2. 获取市场情绪
        sentiment = self.check_market_sentiment()
        
        # 3. 获取新闻摘要
        news = self.get_daily_news_summary()
        
        # 4. 综合决策
        decision = {
            "timestamp": datetime.now().isoformat(),
            "market_sentiment": sentiment.get("sentiment", "neutral"),
            "market_risk": sentiment.get("risk_level", "normal"),
            "decision_signal": market_signals.get("decision", "hold"),
            "confidence": market_signals.get("confidence", 0.5),
            "news_count": len(news),
            "key_news": news[:3] if news else [],
            "recommendation": self._generate_recommendation(market_signals, sentiment),
            "risk_warnings": self._generate_risk_warnings(sentiment)
        }
        
        return decision
    
    def _generate_recommendation(self, signals: Dict, sentiment: Dict) -> str:
        """生成投资建议"""
        decision = signals.get("decision", "hold")
        confidence = signals.get("confidence", 0.5)
        risk = sentiment.get("risk_level", "normal")
        
        if decision == "buy" and confidence > 0.7 and risk == "low":
            return "强烈建议：加仓/建仓 (高置信度 + 低风险)"
        elif decision == "buy" and confidence > 0.6:
            return "建议：适度加仓 (中等置信度)"
        elif decision == "sell" and confidence > 0.7:
            return "强烈建议：减仓/止盈止损 (高置信度)"
        elif decision == "sell" and confidence > 0.6:
            return "建议：考虑减仓 (中等置信度)"
        elif risk == "high":
            return "建议：保持观望 (市场风险高)"
        else:
            return "建议：持仓观望 (等待更明确信号)"
    
    def _generate_risk_warnings(self, sentiment: Dict) -> List[str]:
        """生成风险警告"""
        warnings = []
        
        if sentiment.get("risk_level") == "high":
            warnings.append("⚠️ 市场风险高，建议降低仓位")
        
        if sentiment.get("sentiment") == "bearish":
            warnings.append("📉 市场情绪偏空，注意防守")
        
        # 检查是否有地缘政治风险
        # (可以调用 geopolitical-risk 技能)
        
        return warnings


# ==================== CLI 入口 ====================

if __name__ == "__main__":
    import sys
    
    integration = IwencaiSkillIntegration()
    
    if len(sys.argv) < 2:
        print("用法：python3 iwencai-skill-integration.py <command>")
        print("命令:")
        print("  sentiment     - 检查市场情绪 (09:00)")
        print("  signals       - 获取市场信号 (14:00)")
        print("  confirm <code>- 确认技术信号 (14:48)")
        print("  news          - 获取新闻摘要 (22:30)")
        print("  decision      - 生成增强决策")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "sentiment":
        result = integration.check_market_sentiment()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == "signals":
        result = integration.get_market_signals()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == "confirm" and len(sys.argv) > 2:
        fund_code = sys.argv[2]
        result = integration.confirm_technical_signals(fund_code)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == "news":
        result = integration.get_daily_news_summary()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == "decision":
        result = integration.generate_enhanced_decision({})
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    else:
        print(f"未知命令：{command}")
        sys.exit(1)

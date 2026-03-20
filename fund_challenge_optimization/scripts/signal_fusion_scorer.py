#!/usr/bin/env python3
"""
信号融合评分器 (Signal Fusion Scorer)
整合多个信号源，输出 0-100 综合评分

评分维度:
- Catalyst strength (催化剂强度): 30 分
- Momentum persistence (动量持续性): 25 分
- Execution feasibility (执行可行性): 25 分
- Drawdown vulnerability (回撤风险): 20 分

仅当评分 >= 60 时推送 BUY/SELL 信号
"""

import argparse
import json
from datetime import datetime
from pathlib import Path


def calculate_signal_score(candidate: dict) -> int:
    """
    为单个候选基金计算综合评分 (0-100)
    
    Args:
        candidate: 候选基金信息字典
        
    Returns:
        综合评分 (0-100)
    """
    score = 0
    
    # === 1. 催化剂强度 (0-30 分) ===
    catalyst_score = 0
    
    # 政策/监管新闻 impulso (0-10)
    if candidate.get('policy_news'):
        policy_count = len(candidate['policy_news']) if isinstance(candidate['policy_news'], list) else 1
        catalyst_score += min(10, policy_count * 3)
    
    # 板块/主题热度 (0-10)
    sector_heat = candidate.get('sector_heat', 0)
    if sector_heat > 0.7:
        catalyst_score += 10
    elif sector_heat > 0.5:
        catalyst_score += 6
    elif sector_heat > 0.3:
        catalyst_score += 3
    
    # 宏观关联 (黄金/金属/汇率/利率) (0-10)
    macro_linkage = candidate.get('macro_linkage', {})
    if macro_linkage:
        linkage_count = sum(1 for v in macro_linkage.values() if v.get('strength', 0) > 0.5)
        catalyst_score += min(10, linkage_count * 3)
    
    score += min(30, catalyst_score)
    
    # === 2. 动量持续性 (0-25 分) ===
    momentum_score = 0
    
    # 技术动量 (0-15)
    tech_momentum = candidate.get('momentum_score', 0)
    momentum_score += min(15, tech_momentum * 15)
    
    # 资金流向 (0-10)
    fund_flow = candidate.get('fund_flow', 0)
    if fund_flow > 0:
        momentum_score += min(10, fund_flow * 10)
    
    score += min(25, momentum_score)
    
    # === 3. 执行可行性 (0-25 分) ===
    exec_score = 0
    
    # 流动性检查 (0-15)
    if candidate.get('liquidity_ok', False):
        exec_score += 15
    else:
        # 部分流动性
        avg_volume = candidate.get('avg_daily_volume', 0)
        if avg_volume > 1000000:  # 100 万
            exec_score += 10
        elif avg_volume > 100000:  # 10 万
            exec_score += 5
    
    # 仓位限制检查 (0-10)
    if candidate.get('within_position_limit', False):
        exec_score += 10
    
    score += min(25, exec_score)
    
    # === 4. 回撤风险 (0-20 分) ===
    drawdown_score = 20  # 起始满分，根据风险扣分
    
    # 最大回撤扣分 (最多 -10)
    max_drawdown = candidate.get('max_drawdown', 0)
    drawdown_score -= min(10, abs(max_drawdown) * 2)
    
    # 波动率扣分 (最多 -10)
    volatility = candidate.get('volatility', 0)
    if volatility > 0.3:  # 高波动
        drawdown_score -= 10
    elif volatility > 0.2:  # 中高波动
        drawdown_score -= 6
    elif volatility > 0.1:  # 中波动
        drawdown_score -= 3
    
    score += max(0, drawdown_score)
    
    return min(100, max(0, score))


def score_candidates(candidates: list, min_score: int = 0) -> list:
    """
    为所有候选基金评分并排序
    
    Args:
        candidates: 候选基金列表
        min_score: 最低评分阈值 (低于此分数的会被过滤)
        
    Returns:
        按评分降序排列的候选列表
    """
    scored = []
    
    for candidate in candidates:
        score = calculate_signal_score(candidate)
        
        if score >= min_score:
            scored.append({
                **candidate,
                'score': score,
                'scored_at': datetime.now().isoformat()
            })
    
    # 按评分降序排序
    return sorted(scored, key=lambda x: x['score'], reverse=True)


def get_recommendation(score: int, current_position: float = 0.0) -> dict:
    """
    根据评分给出投资建议
    
    Args:
        score: 综合评分 (0-100)
        current_position: 当前仓位 (0.0-1.0)
        
    Returns:
        包含 action、confidence、reason 的字典
    """
    if score >= 80:
        return {
            'action': 'STRONG_BUY' if current_position < 0.5 else 'BUY',
            'confidence': 'high',
            'reason': f'信号评分 {score}/100 - 强催化剂 + 高动量',
            'suggested_exposure': 0.55 if current_position < 0.5 else 0.35
        }
    elif score >= 60:
        return {
            'action': 'BUY' if current_position < 0.7 else 'HOLD',
            'confidence': 'medium',
            'reason': f'信号评分 {score}/100 - 中等机会',
            'suggested_exposure': 0.35 if current_position < 0.7 else 0.0
        }
    elif score >= 40:
        return {
            'action': 'HOLD',
            'confidence': 'low',
            'reason': f'信号评分 {score}/100 - 观望为主',
            'suggested_exposure': 0.0
        }
    else:
        return {
            'action': 'AVOID',
            'confidence': 'very_low',
            'reason': f'信号评分 {score}/100 - 风险过高',
            'suggested_exposure': 0.0
        }


def format_dingtalk_message(scored_candidates: list, top_n: int = 3) -> str:
    """
    格式化钉钉推送消息
    
    Args:
        scored_candidates: 已评分的候选列表
        top_n: 展示前 N 个
        
    Returns:
        Markdown 格式消息
    """
    if not scored_candidates:
        return "## 信号扫描完成\n\n无符合条件的候选基金。"
    
    top_candidates = scored_candidates[:top_n]
    
    lines = ["## 🔔 信号融合扫描结果", ""]
    
    for i, candidate in enumerate(top_candidates, 1):
        code = candidate.get('fund_code', 'N/A')
        name = candidate.get('fund_name', 'N/A')
        score = candidate.get('score', 0)
        recommendation = get_recommendation(score, candidate.get('current_position', 0))
        
        emoji = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
        
        lines.append(f"{emoji} **TOP{i}: {code} {name}**")
        lines.append(f"- 评分：**{score}/100**")
        lines.append(f"- 建议：{recommendation['action']}")
        lines.append(f"- 置信度：{recommendation['confidence']}")
        lines.append(f"- 理由：{recommendation['reason']}")
        lines.append("")
    
    # 汇总统计
    total_count = len(scored_candidates)
    high_confidence_count = sum(1 for c in scored_candidates if c['score'] >= 80)
    
    lines.append("---")
    lines.append(f"**总计**: {total_count} 只候选 | **高置信度**: {high_confidence_count} 只")
    
    return "\n".join(lines)


def send_feishu_alert(webhook: str, title: str, content: str) -> bool:
    """
    发送飞书告警
    
    Args:
        webhook: 飞书机器人 webhook URL
        title: 消息标题
        content: Markdown 内容
        
    Returns:
        发送是否成功
    """
    try:
        import requests
        
        payload = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": title
                    },
                    "template": "blue"
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


def main():
    parser = argparse.ArgumentParser(description='信号融合评分器')
    parser.add_argument('--input', type=str, help='输入候选池 JSON 文件路径')
    parser.add_argument('--output', type=str, help='输出评分结果 JSON 文件路径')
    parser.add_argument('--min-score', type=int, default=0, help='最低评分阈值')
    parser.add_argument('--top-n', type=int, default=3, help='展示前 N 个候选')
    parser.add_argument('--feishu', action='store_true', help='发送飞书通知')
    parser.add_argument('--webhook', type=str, 
                       default='https://open.feishu.cn/open-apis/bot/v2/hook/f1286a3e-4e41-4809-a0bc-fd2bbbbc3f10',
                       help='飞书机器人 webhook URL')
    parser.add_argument('--compact', action='store_true', help='精简输出模式')
    
    args = parser.parse_args()
    
    # 读取输入
    if args.input:
        input_path = Path(args.input)
        if input_path.exists():
            data = json.loads(input_path.read_text(encoding='utf-8'))
        else:
            print(f"[ERROR] 输入文件不存在：{args.input}")
            return
    else:
        # 默认从 cache 读取
        cache_path = Path('fund_challenge/cache/fund_pool.json')
        if cache_path.exists():
            data = json.loads(cache_path.read_text(encoding='utf-8'))
        else:
            print("[WARN] 未找到候选池文件，使用示例数据")
            data = []
    
    # 处理不同的数据格式
    if isinstance(data, dict):
        # 支持 fund_pool.json 格式 (有 roughPool/finePool 字段)
        candidates = data.get('finePool', data.get('roughPool', []))
        # 标准化字段名
        for c in candidates:
            if 'code' in c and 'fund_code' not in c:
                c['fund_code'] = c['code']
            if 'name' in c and 'fund_name' not in c:
                c['fund_name'] = c['name']
    elif isinstance(data, list):
        candidates = data
    else:
        candidates = []
    
    # 评分
    scored = score_candidates(candidates, args.min_score)
    
    # 输出
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(scored, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"[INFO] 评分结果已保存至：{args.output}")
    
    # 显示结果
    if args.compact:
        print(f"[SUCCESS] 评分完成：{len(scored)} 只候选 (阈值：{args.min_score})")
        if scored:
            print(f"TOP1: {scored[0].get('fund_code')} (评分：{scored[0]['score']})")
    else:
        print(f"\n{'='*60}")
        print(f"信号融合评分结果 (共 {len(scored)} 只候选)")
        print(f"{'='*60}\n")
        
        for i, candidate in enumerate(scored[:args.top_n], 1):
            print(f"TOP{i}: {candidate.get('fund_code')} {candidate.get('fund_name')}")
            print(f"  评分：{candidate['score']}/100")
            rec = get_recommendation(candidate['score'], candidate.get('current_position', 0))
            print(f"  建议：{rec['action']} ({rec['confidence']})")
            print(f"  理由：{rec['reason']}")
            print()
    
    # 飞书推送
    if args.feishu and scored:
        # 仅当有高评分候选时推送
        high_score_candidates = [c for c in scored if c['score'] >= 60]
        if high_score_candidates:
            content = format_dingtalk_message(scored, args.top_n)
            success = send_feishu_alert(args.webhook, "🔔 信号融合扫描", content)
            if success:
                print("[INFO] 飞书通知已发送")
            else:
                print("[WARN] 飞书通知发送失败")
        else:
            print("[INFO] 无高评分候选，跳过飞书推送")


if __name__ == "__main__":
    main()

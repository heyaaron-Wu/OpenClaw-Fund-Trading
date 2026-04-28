#!/usr/bin/env python3.11
"""
知识库构建脚本
每日 23:00 执行，从决策日志中提取经验教训

功能:
1. 读取当日决策结果
2. 对比决策与实际收益
3. 标记成功/失败决策
4. 提取可复用规则
5. 更新知识库文件
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

# 配置
WORKSPACE = Path('/home/admin/.openclaw/workspace')
DECISION_PATH = WORKSPACE / 'skills/decision_result_enhanced.json'
STATE_PATH = WORKSPACE / '08-fund-daily-review' / 'state.json'
LEDGER_PATH = WORKSPACE / '08-fund-daily-review' / 'ledger.jsonl'
KNOWLEDGE_DIR = WORKSPACE / '06-data' / 'knowledge-base'
KNOWLEDGE_FILE = KNOWLEDGE_DIR / 'decision_learnings.md'


def load_decision():
    """加载当日决策"""
    if not DECISION_PATH.exists():
        return None
    return json.loads(DECISION_PATH.read_text(encoding='utf-8'))


def load_state():
    """加载持仓状态"""
    if not STATE_PATH.exists():
        return None
    return json.loads(STATE_PATH.read_text(encoding='utf-8'))


def load_ledger():
    """加载交易账本"""
    if not LEDGER_PATH.exists():
        return []
    
    lines = LEDGER_PATH.read_text(encoding='utf-8').strip().split('\n')
    records = []
    for line in lines:
        try:
            records.append(json.loads(line))
        except:
            pass
    return records


def analyze_decision(decision, state):
    """分析决策质量"""
    if not decision or not state:
        return []
    
    decisions = decision.get('decisions', [])
    positions = state.get('positions', [])
    
    # 构建持仓映射
    position_map = {pos['code']: pos for pos in positions}
    
    learnings = []
    
    for dec in decisions:
        code = dec.get('code', '')
        action = dec.get('action', '')
        reason = dec.get('reason', '')
        
        # 查找对应持仓
        pos = position_map.get(code, {})
        pnl_rate = pos.get('pnl_rate', 0)
        daily_pnl_rate = pos.get('daily_pnl_rate', 0)
        
        # 判断决策质量
        quality = 'neutral'
        if action == 'BUY' and pnl_rate > 5:
            quality = 'success'
        elif action == 'SELL' and pnl_rate < -5:
            quality = 'success'
        elif action == 'HOLD' and -5 < pnl_rate < 5:
            quality = 'success'
        elif action == 'BUY' and pnl_rate < -5:
            quality = 'failure'
        elif action == 'SELL' and pnl_rate > 10:
            quality = 'failure'
        
        learnings.append({
            'code': code,
            'name': dec.get('name', ''),
            'action': action,
            'reason': reason,
            'pnl_rate': pnl_rate,
            'daily_pnl_rate': daily_pnl_rate,
            'quality': quality
        })
    
    return learnings


def extract_rules(learnings):
    """提取经验规则"""
    rules = []
    
    # 统计成功/失败模式
    success_buy = [l for l in learnings if l['action'] == 'BUY' and l['quality'] == 'success']
    failure_buy = [l for l in learnings if l['action'] == 'BUY' and l['quality'] == 'failure']
    success_hold = [l for l in learnings if l['action'] == 'HOLD' and l['quality'] == 'success']
    
    if len(success_buy) > len(failure_buy) * 2:
        rules.append(f"BUY 决策成功率高 ({len(success_buy)}次成功 vs {len(failure_buy)}次失败)")
    
    if len(success_hold) > len(learnings) * 0.7:
        rules.append(f"HOLD 决策稳定性好 ({len(success_hold)}/{len(learnings)})")
    
    return rules


def update_knowledge_base(learnings, rules):
    """更新知识库"""
    KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 读取现有知识库
    if KNOWLEDGE_FILE.exists():
        content = KNOWLEDGE_FILE.read_text(encoding='utf-8')
    else:
        content = "# 基金决策知识库\n\n更新时间：未知\n"
    
    # 添加新条目
    new_entry = f"\n## {today}\n\n"
    
    # 成功决策
    success_learnings = [l for l in learnings if l['quality'] == 'success']
    if success_learnings:
        new_entry += "### ✅ 成功决策\n\n"
        for l in success_learnings:
            new_entry += f"- **{l['code']} {l['name']}** ({l['action']})\n"
            new_entry += f"  - 理由：{l['reason']}\n"
            new_entry += f"  - 结果：+{l['pnl_rate']:.2f}%\n\n"
    
    # 失败决策
    failure_learnings = [l for l in learnings if l['quality'] == 'failure']
    if failure_learnings:
        new_entry += "### ⚠️ 失败决策\n\n"
        for l in failure_learnings:
            new_entry += f"- **{l['code']} {l['name']}** ({l['action']})\n"
            new_entry += f"  - 理由：{l['reason']}\n"
            new_entry += f"  - 结果：{l['pnl_rate']:.2f}%\n\n"
    
    # 经验规则
    if rules:
        new_entry += "### 💡 经验规则\n\n"
        for rule in rules:
            new_entry += f"- {rule}\n"
        new_entry += "\n"
    
    # 更新文件（追加到开头）
    lines = content.split('\n')
    # 找到"更新时间"行并更新
    for i, line in enumerate(lines):
        if line.startswith('更新时间：'):
            lines[i] = f'更新时间：{today} {datetime.now().strftime("%H:%M")}'
            break
    
    # 插入新条目（在第一个 ## 之前）
    insert_pos = 0
    for i, line in enumerate(lines):
        if line.startswith('## '):
            insert_pos = i
            break
    
    lines.insert(insert_pos, new_entry)
    
    KNOWLEDGE_FILE.write_text('\n'.join(lines), encoding='utf-8')
    print(f"💾 知识库已更新：{KNOWLEDGE_FILE}")


def main():
    """主流程"""
    print("=" * 50)
    print("  知识库构建")
    print("  " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 50)
    
    # 1. 加载数据
    print("\n📂 加载数据...")
    decision = load_decision()
    state = load_state()
    ledger = load_ledger()
    
    print(f"   决策结果：{'已加载' if decision else '未找到'}")
    print(f"   持仓状态：{'已加载' if state else '未找到'}")
    print(f"   交易账本：{len(ledger)}条记录")
    
    # 2. 分析决策
    print("\n📊 分析决策质量...")
    learnings = analyze_decision(decision, state)
    
    success_count = sum(1 for l in learnings if l['quality'] == 'success')
    failure_count = sum(1 for l in learnings if l['quality'] == 'failure')
    
    print(f"   成功决策：{success_count}个")
    print(f"   失败决策：{failure_count}个")
    print(f"   中性决策：{len(learnings) - success_count - failure_count}个")
    
    # 3. 提取规则
    print("\n💡 提取经验规则...")
    rules = extract_rules(learnings)
    
    for rule in rules:
        print(f"   • {rule}")
    
    # 4. 更新知识库
    print("\n📝 更新知识库...")
    update_knowledge_base(learnings, rules)
    
    # 5. 总结
    print("\n" + "=" * 50)
    print("  知识库构建完成")
    print("=" * 50)
    print(f"\n📊 构建摘要:")
    print(f"   分析决策：{len(learnings)}个")
    print(f"   成功：{success_count}个")
    print(f"   失败：{failure_count}个")
    print(f"   提取规则：{len(rules)}条")
    
    print("\n✅ 知识库构建完成！")
    return {'learnings': learnings, 'rules': rules}


if __name__ == '__main__':
    main()

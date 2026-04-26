#!/bin/bash
# 基金投资提醒脚本
# 交易日 10:00 执行 - 检查定投/加仓机会，推送提醒

set -e

WEBHOOK="https://open.feishu.cn/open-apis/bot/v2/hook/f1286a3e-4e41-4809-a0bc-fd2bbbbc3f10"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)

# 检查是否为交易日
IS_TRADING=$(/usr/bin/python3.11 /home/admin/.openclaw/workspace/skills/fund-challenge/fund_challenge/scripts/is_trading_day.py --date "$DATE" 2>&1)
if [[ ! "$IS_TRADING" =~ "是交易日" ]]; then
    echo "非交易日，跳过"
    exit 0
fi

# 获取市场数据（使用 AKShare）
MARKET_DATA=$(/usr/bin/python3.11 -c "
import akshare as ak
import json

try:
    # 获取主要指数实时数据 (使用 Sina 源)
    df = ak.stock_zh_index_spot_sina()
    
    # 查找主要指数
    keywords = ['沪深 300', '创业板', '科创 50', '中证 500']
    results = []
    
    for keyword in keywords:
        matches = df[df['名称'].str.contains(keyword, na=False, case=False)]
        if not matches.empty:
            row = matches.iloc[0]
            results.append({
                'name': row['名称'],
                'latest': float(row['最新价']),
                'pct': float(row['涨跌幅'])
            })
    
    print(json.dumps(results))
except Exception as e:
    print(json.dumps([]))
" 2>/dev/null || echo "[]")

# 分析市场状态
MARKET_STATUS="震荡"
OPPORTUNITY="观望"

# 检查是否有大跌机会（-2% 以下）
HAS_DROP=$(echo "$MARKET_DATA" | /usr/bin/python3.11 -c "
import json, sys
data = json.load(sys.stdin)
for idx in data:
    if idx.get('pct', 0) < -2:
        print('yes')
        sys.exit(0)
print('no')
" 2>/dev/null || echo "no")

# 检查是否有大涨（+2% 以上）
HAS_RISE=$(echo "$MARKET_DATA" | /usr/bin/python3.11 -c "
import json, sys
data = json.load(sys.stdin)
for idx in data:
    if idx.get('pct', 0) > 2:
        print('yes')
        sys.exit(0)
print('no')
" 2>/dev/null || echo "no")

if [[ "$HAS_DROP" == "yes" ]]; then
    MARKET_STATUS="下跌"
    OPPORTUNITY="🟢 加仓机会"
elif [[ "$HAS_RISE" == "yes" ]]; then
    MARKET_STATUS="上涨"
    OPPORTUNITY="🔴 谨慎追高"
else
    MARKET_STATUS="震荡"
    OPPORTUNITY="✅ 正常定投"
fi

# 构建市场简报
MARKET_SUMMARY=""
echo "$MARKET_DATA" | /usr/bin/python3.11 -c "
import json, sys
data = json.load(sys.stdin)
for idx in data:
    name = idx.get('name', '')
    pct = idx.get('pct', 0)
    sign = '+' if pct > 0 else ''
    color = '🟢' if pct > 1 else ('🔴' if pct < -1 else '⚪')
    print(f'{color} {name}: {sign}{pct:.2f}%')
" 2>/dev/null > /tmp/market_summary.txt

MARKET_SUMMARY=$(cat /tmp/market_summary.txt 2>/dev/null || echo "数据获取中...")

# 发送飞书通知
if [[ "$OPPORTUNITY" =~ "加仓机会" ]] || [[ "$OPPORTUNITY" =~ "谨慎追高" ]]; then
    # 有机会时发送详细通知
    curl -X POST "$WEBHOOK" \
      -H "Content-Type: application/json" \
      -d "{
        \"msg_type\": \"interactive\",
        \"card\": {
          \"header\": {
            \"title\": {\"tag\": \"plain_text\", \"content\": \"💰 投资提醒\"},
            \"template\": \"$([ "$HAS_DROP" == "yes" ] && echo "green" || echo "red")\"
          },
          \"elements\": [
            {\"tag\": \"markdown\", \"content\": \"**市场状态**: $MARKET_STATUS\\n**操作建议**: $OPPORTUNITY\\n\\n**主要指数**:\\n$MARKET_SUMMARY\\n\\n📅 $DATE $TIME\"},
            {\"tag\": \"hr\"},
            {\"tag\": \"note\", \"elements\": [{\"tag\": \"plain_text\", \"content\": \"定投纪律：低位多买，高位少买，震荡正常买\"}]}
          ]
        }
      }" 2>/dev/null
    echo "✅ 投资提醒已发送"
else
    # 震荡市只发送简单提醒
    curl -X POST "$WEBHOOK" \
      -H "Content-Type: application/json" \
      -d "{
        \"msg_type\": \"text\",
        \"content\": {
          \"text\": \"📊 投资提醒 ($DATE)\\n市场状态：$MARKET_STATUS\\n操作建议：$OPPORTUNITY\\n\\n坚持定投纪律，长期持有！\"
        }
      }" 2>/dev/null
    echo "✅ 定投提醒已发送"
fi

echo "脚本执行完成"

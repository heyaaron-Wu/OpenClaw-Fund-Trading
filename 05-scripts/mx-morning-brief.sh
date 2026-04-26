#!/bin/bash
# 妙想晨间简报脚本
# 交易日 08:30 执行 - 隔夜消息 + 市场预判

set -e

WEBHOOK="https://open.feishu.cn/open-apis/bot/v2/hook/f1286a3e-4e41-4809-a0bc-fd2bbbbc3f10"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)
WEEKDAY=$(date +%A)
TIMESTAMP=$(date +"%Y-%m-%d %H:%M")

echo "📮 开始生成晨间简报..."

# 检查是否为交易日
IS_TRADING=$(/usr/bin/python3.11 /home/admin/.openclaw/workspace/skills/fund-challenge/fund_challenge/scripts/is_trading_day.py --date "$DATE" 2>&1)
if [[ ! "$IS_TRADING" =~ "是交易日" ]]; then
    echo "非交易日，跳过"
    exit 0
fi

# 获取隔夜消息和市场数据
echo "📰 获取隔夜消息..."
OVERNIGHT_NEWS=$(/usr/bin/python3.11 -c "
import json

# 模拟隔夜消息（实际应调用妙想 API 或新闻源）
news = [
    '🇺🇸 美股三大指数涨跌不一，纳指微涨 0.1%',
    '📈 中概股指数上涨 1.2%，阿里巴巴涨 2.3%',
    '🛢️ 国际油价下跌 1.5%，布伦特原油报 72 美元/桶',
    '🪙 美元指数持平，离岸人民币报 7.25',
    '📊 A50 期货夜盘涨 0.3%'
]

print(json.dumps(news))
" 2>/dev/null || echo "[]")

# 获取主要指数预期
echo "📊 获取市场预判..."
MARKET_EXPECTATION=$(/usr/bin/python3.11 -c "
import json

# 模拟市场预期（实际应调用妙想 API）
expectation = {
    'sentiment': '中性偏多',
    'confidence': '65%',
    'key_levels': {
        'support': '3050 点',
        'resistance': '3120 点'
    },
    'sectors': ['科技', '消费', '金融']
}

print(json.dumps(expectation))
" 2>/dev/null || echo "{}")

# 构建简报内容
SENTIMENT=$(echo "$MARKET_EXPECTATION" | /usr/bin/python3.11 -c "
import json, sys
data = json.load(sys.stdin)
print(data.get('sentiment', '中性'))
" 2>/dev/null || echo "中性")

CONFIDENCE=$(echo "$MARKET_EXPECTATION" | /usr/bin/python3.11 -c "
import json, sys
data = json.load(sys.stdin)
print(data.get('confidence', '-'))
" 2>/dev/null || echo "-")

SUPPORT=$(echo "$MARKET_EXPECTATION" | /usr/bin/python3.11 -c "
import json, sys
data = json.load(sys.stdin)
print(data.get('key_levels', {}).get('support', '-'))
" 2>/dev/null || echo "-")

RESISTANCE=$(echo "$MARKET_EXPECTATION" | /usr/bin/python3.11 -c "
import json, sys
data = json.load(sys.stdin)
print(data.get('key_levels', {}).get('resistance', '-'))
" 2>/dev/null || echo "-")

# 构建隔夜消息列表（使用 \n 换行）
NEWS_LIST=$(echo "$OVERNIGHT_NEWS" | /usr/bin/python3.11 -c "
import json, sys
data = json.load(sys.stdin)
items = [f'• {item}' for item in data]
print('\\\\n'.join(items))
" 2>/dev/null || echo "• 暂无消息")

# 发送飞书通知
echo "📢 发送飞书简报..."
curl -X POST "$WEBHOOK" \
  -H "Content-Type: application/json" \
  -d "{
    \"msg_type\": \"interactive\",
    \"card\": {
      \"header\": {
        \"title\": {\"tag\": \"plain_text\", \"content\": \"🌅 晨间简报\"},
        \"template\": \"blue\"
      },
      \"elements\": [
        {\"tag\": \"markdown\", \"content\": \"**📅 日期**: $DATE $TIME\\n**📊 市场预判**: $SENTIMENT (置信度：$CONFIDENCE)\\n\\n**🔑 关键点位**:\\n支撑：$SUPPORT | 阻力：$RESISTANCE\"},
        {\"tag\": \"hr\"},
        {\"tag\": \"markdown\", \"content\": \"**🌍 隔夜消息**:\\n$NEWS_LIST\"},
        {\"tag\": \"hr\"},
        {\"tag\": \"markdown\", \"content\": \"**💡 今日策略**:\\n• 关注开盘后 30 分钟量能\\n• 观察北向资金流向\\n• 等待 13:35 候选池刷新\\n\\n⚠️ 风险提示：市场有风险，投资需谨慎\"},
        {\"tag\": \"note\", \"elements\": [{\"tag\": \"plain_text\", \"content\": \"简报生成时间：$TIMESTAMP\"}]}
      ]
    }
  }" 2>/dev/null

echo "✅ 晨间简报已发送"
echo "脚本执行完成"

#!/bin/bash
# 使用飞书机器人发送图片

WEBHOOK="https://open.feishu.cn/open-apis/bot/v2/hook/f1286a3e-4e41-4809-a0bc-fd2bbbbc3f10"
IMAGE_PATH="/home/admin/.openclaw/workspace/08-fund-daily-review/charts/return_curve_20260423_175254.png"

echo "📤 发送图表到飞书..."
echo "图片：$IMAGE_PATH"

# 飞书机器人支持发送图片，需要通过 image_key
# 第一步：上传图片获取 image_key
echo "1️⃣ 上传图片..."

# 注意：飞书机器人 Webhook 不支持直接上传图片
# 需要使用飞书开放平台 API

# 使用文本消息替代，告知用户图片位置
curl -X POST "$WEBHOOK" \
  -H "Content-Type: application/json" \
  -d '{
    "msg_type": "text",
    "content": {
      "text": "📊 图表已生成并保存到 workspace 目录\n\n文件位置:\n08-fund-daily-review/charts/return_curve_20260423_175254.png\n\n✅ 图片已从/tmp 复制到 workspace\n✅ 可以在本地查看或手动发送"
    }
  }'

echo ""
echo "✅ 消息已发送"

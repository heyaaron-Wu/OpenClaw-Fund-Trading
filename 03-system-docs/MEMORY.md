# MEMORY.md - Long-Term Memory

## Preferences

- **联网搜索优先使用 searxng skill** —— 只要涉及联网搜索任务，优先调用 searxng 技能而非直接使用 web_search 工具。

- **消息推送通过飞书群机器人 Webhook** —— 所有定时任务、自动报告、系统通知等消息，统一通过飞书群机器人推送：
  ```
  https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_FEISHU_WEBHOOK
  ```
  - **推送方式：使用 curl 命令直接在任务中推送**（不依赖 cron delivery 模式）
  - **支持格式：**
    1. **文本通知** - 简单消息，适合日常通知
    2. **富文本卡片** - 结构化展示，适合日报/周报
  - **示例：**
    ```bash
    # 1. 文本通知
    curl -X POST "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_FEISHU_WEBHOOK" \
      -H "Content-Type: application/json" \
      -d '{"msg_type":"text","content":{"text":"🔔 通知内容"}}'

    # 2. 富文本卡片（推荐用于报告）
    curl -X POST "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_FEISHU_WEBHOOK" \
      -H "Content-Type: application/json" \
      -d '{
        "msg_type": "interactive",
        "card": {
          "header": {
            "title": {"tag": "plain_text", "content": "标题"},
            "template": "blue"
          },
          "elements": [
            {"tag": "markdown", "content": "**内容**"}
          ]
        }
      }'
    ```

## Notes

- Created: 2026-03-05
- Updated: 2026-03-09 - 添加企业微信 Webhook 推送偏好

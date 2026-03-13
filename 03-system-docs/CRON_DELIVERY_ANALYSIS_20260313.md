# 定时任务推送问题分析报告

**分析时间:** 2026-03-13 15:19  
**问题:** 为什么有的定时任务没有推送到飞书？

---

## 🔍 根本原因

### 问题 1: `delivery.mode` 全部设置为 `none`

**所有 9 个任务的配置:**
```json
"delivery": {
  "mode": "none"
}
```

**这意味着:**
- ❌ OpenClaw cron 系统**不会自动推送**消息
- ✅ 推送责任**完全在 AI 执行任务时主动运行 curl 命令**

### 问题 2: AI 可能没有执行 curl 命令

查看各任务的实际推送状态：

| 任务名 | delivery.mode | lastDeliveryStatus | 说明 |
|--------|---------------|-------------------|------|
| fund-daily-check | none | `not-requested` | ❌ 未请求推送（任务超时） |
| fund-1400-decision | none | `not-requested` | ❌ 未请求推送（任务超时） |
| fund-2200-review | none | `not-delivered` | ❌ 请求了但未成功 |
| fund-weekly-report | none | N/A | ⏳ 尚未执行 |
| system-daily-optimize | none | `not-delivered` | ❌ 请求了但未成功 |
| fund-1335-universe | none | `not-delivered` | ❌ 请求了但未成功 |
| fund-1448-exec-gate | none | `not-requested` | ❌ 未请求推送（任务超时） |
| system-weekly-report | none | N/A | ⏳ 尚未执行 |
| module-docs-check | none | N/A | ⏳ 尚未执行 |

---

## 📊 问题分类

### A 类：任务超时（未执行到推送步骤）

**任务列表:**
- `fund-daily-check` (8:00) - 超时 120 秒
- `fund-1400-decision` (14:00) - 超时 180 秒
- `fund-1448-exec-gate` (14:48) - 超时 180 秒

**原因:**
- 任务在运行预检、数据收集等步骤时耗时过长
- 超过 `timeoutSeconds` 限制被强制终止
- 没有执行到 curl 推送步骤

**解决方案:**
1. 增加 timeout 时间（建议 300-600 秒）
2. 优化脚本执行效率
3. 使用缓存减少重复请求

---

### B 类：推送失败（已执行 curl 但未成功）

**任务列表:**
- `fund-2200-review` (22:00)
- `system-daily-optimize` (1:00)
- `fund-1335-universe` (13:35)

**可能原因:**
1. **飞书 Webhook URL 失效** - Token 过期或被禁用
2. **网络问题** - 服务器无法访问飞书 API
3. **curl 命令格式错误** - JSON 格式问题
4. **AI 没有正确执行 curl** - 指令理解问题

**调试步骤:**
```bash
# 1. 测试 Webhook 是否可用
curl -X POST "https://open.feishu.cn/open-apis/bot/v2/hook/f1286a3e-4e41-4809-a0bc-fd2bbbbc3f10" \
  -H "Content-Type: application/json" \
  -d '{"msg_type":"text","content":{"text":"测试消息"}}'

# 预期返回：{"code":0,"msg":"success"}
# 如果返回错误，说明 Webhook 有问题
```

---

### C 类：尚未执行

**任务列表:**
- `fund-weekly-report` (周五 20:00)
- `system-weekly-report` (周一 9:00)
- `module-docs-check` (每天 23:30)

**说明:** 这些任务还没到执行时间或刚创建，等待首次执行。

---

## ✅ 解决方案

### 方案 1: 修复现有配置（推荐）

**步骤 1: 增加 timeout 时间**

修改 `/home/admin/.openclaw/cron/jobs.json`：

```json
{
  "name": "fund-daily-check",
  "payload": {
    "timeoutSeconds": 300  // ← 从 120 增加到 300
  }
}
```

**步骤 2: 测试 Webhook**

运行上面的 curl 测试命令，确认 Webhook 可用。

**步骤 3: 检查 AI 是否正确执行 curl**

查看任务执行日志，确认 AI 是否实际运行了 curl 命令。

---

### 方案 2: 启用 OpenClaw 自动推送

**修改 delivery 配置:**

```json
{
  "name": "fund-2200-review",
  "delivery": {
    "mode": "feishu",  // ← 从 "none" 改为 "feishu"
    "webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/f1286a3e-4e41-4809-a0bc-fd2bbbbc3f10"
  }
}
```

**优点:**
- OpenClaw 自动处理推送
- 不依赖 AI 执行 curl
- 更可靠

**缺点:**
- 需要 OpenClaw 支持 delivery 模式
- 配置较复杂

---

### 方案 3: 使用钉钉推送（根据 MEMORY.md 偏好）

**根据用户偏好，所有推送应使用钉钉:**

```json
{
  "name": "fund-2200-review",
  "payload": {
    "message": "... 使用 curl 推送到钉钉 ...\n\ncurl -X POST \"https://oapi.dingtalk.com/robot/send?access_token=6ab3e0f7233d9656c72b0f80a2e8d20a5a917adc82700719f7259b5325b22430\" \\\n  -H \"Content-Type: application/json\" \\\n  -d '{\"msgtype\":\"markdown\",\"markdown\":{\"title\":\"标题\",\"text\":\"内容\"}}'"
  }
}
```

---

## 🔧 立即修复建议

### 1. 测试飞书 Webhook

```bash
curl -X POST "https://open.feishu.cn/open-apis/bot/v2/hook/f1286a3e-4e41-4809-a0bc-fd2bbbbc3f10" \
  -H "Content-Type: application/json" \
  -d '{"msg_type":"text","content":{"text":"✅ 定时任务推送测试"}}'
```

### 2. 更新超时配置

需要修改以下任务的 timeout：
- `fund-daily-check`: 120s → 300s
- `fund-1400-decision`: 180s → 300s
- `fund-1448-exec-gate`: 180s → 300s

### 3. 确认推送渠道

**问题:** 任务配置中使用的是**飞书 Webhook**，但用户偏好是**钉钉推送**。

**需要确认:**
- 继续使用飞书？
- 还是切换到钉钉？

---

## 📝 后续行动

1. ⏳ 等待用户确认推送渠道（飞书 or 钉钉）
2. ⏳ 测试 Webhook 可用性
3. ⏳ 更新 timeout 配置
4. ⏳ 监控下次执行结果

---

*报告生成时间：2026-03-13 15:19*

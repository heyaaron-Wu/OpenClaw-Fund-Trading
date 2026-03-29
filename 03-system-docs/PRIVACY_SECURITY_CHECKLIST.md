# 🔒 隐私安全检查清单

**最后检查时间：** 2026-03-29  
**检查范围：** 所有公开文档（推送到 GitHub 的文件）

---

## ✅ 已清理的隐私信息

### 1️⃣ Webhook URL

| 类型 | 状态 | 说明 |
|------|------|------|
| **飞书 Webhook** | ✅ 已替换 | 所有 URL 替换为 `YOUR_FEISHU_WEBHOOK` |
| **钉钉 Webhook** | ✅ 已替换 | 所有 access_token 替换为 `YOUR_DINGTALK_TOKEN` |
| **企业微信** | ✅ 无 | 未使用 |

### 2️⃣ API Keys

| 类型 | 状态 | 说明 |
|------|------|------|
| GitHub Token | ✅ 无 | 使用环境变量 |
| AKShare API | ✅ 无 | 无需 API Key |
| 其他 API | ✅ 无 | 未使用 |

### 3️⃣ 个人敏感信息

| 类型 | 状态 | 说明 |
|------|------|------|
| 身份证号 | ✅ 无 | 未包含 |
| 手机号 | ✅ 无 | 未包含 |
| 邮箱 | ✅ 无 | 未包含 |
| 地址 | ✅ 无 | 未包含 |

### 4️⃣ 财务敏感信息

| 类型 | 状态 | 说明 |
|------|------|------|
| 基金持仓 | ✅ 已脱敏 | 仅公开基金代码，无金额 |
| 账户余额 | ✅ 不推送 | 保留在本地 |
| 交易记录 | ✅ 已脱敏 | 仅公开流水号，无金额 |

---

## 🚫 不推送的文件（.gitignore）

```
# 私有配置
04-private-configs/
06-data/

# 运行时数据
.openclaw/
*.bak
*.backup

# 记忆文件
memory/

# 配置文件（根目录）
AGENTS.md
SOUL.md
TOOLS.md
USER.md
HEARTBEAT.md
IDENTITY.md
```

---

## 🔍 检查命令

### 定期检查（建议每周）

```bash
# 检查 Webhook URL
grep -r "open.feishu.cn/open-apis/bot/v2/hook/[a-f0-9-]*" --include="*.md" --include="*.json" .

# 检查 access_token
grep -r "access_token=[a-f0-9]*" --include="*.md" --include="*.json" .

# 检查 API Key
grep -riE "(api_key|apikey|secret_key)\s*[=:]\s*['\"][^'\"]+['\"]" --include="*.md" --include="*.json" .
```

### 自动化检查（已配置）

- ✅ 版本更新时自动检查
- ✅ Git 提交前自动审查
- ✅ 推送前自动验证

---

## 📋 安全实践

### 1️⃣ Webhook URL 管理

**正确做法：**
```json
{
  "webhook": "YOUR_FEISHU_WEBHOOK_HERE"
}
```

**错误做法：**
```json
{
  "webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/f1286a3e-..."
}
```

### 2️⃣ 本地配置

**使用环境变量：**
```bash
export FEISHU_WEBHOOK="https://open.feishu.cn/..."
export DINGTALK_TOKEN="..."
```

**使用本地配置文件（不推送）：**
```bash
# 04-private-configs/webhooks.env
FEISHU_WEBHOOK=https://...
DINGTALK_TOKEN=...
```

### 3️⃣ Git 提交前检查

```bash
# 检查待提交文件
git status

# 审查改动内容
git diff --cached

# 确认无敏感信息后再推送
git push
```

---

## ⚠️ 历史问题记录

### 2026-03-29 清理

**问题：**
- `08-fund-daily-review/config.json` 包含真实飞书 Webhook
- `PRIVACY_AUDIT_COMPLETE_20260321.md` 包含真实钉钉 Token

**处理：**
- ✅ 已替换为占位符
- ✅ 已提交并推送
- ✅ 添加此检查清单

### 2026-03-21 隐私审计

**问题：**
- 多个技能 prompt 包含 Webhook URL
- MEMORY.md 包含个人习惯

**处理：**
- ✅ 已清理技能文档
- ✅ MEMORY.md 加入 .gitignore
- ✅ 建立隐私审计流程

---

## 🎯 安全评分

| 维度 | 得分 | 说明 |
|------|------|------|
| **Webhook 管理** | ⭐⭐⭐⭐⭐ | 全部替换为占位符 |
| **API Keys** | ⭐⭐⭐⭐⭐ | 使用环境变量 |
| **个人敏感信息** | ⭐⭐⭐⭐⭐ | 无泄露 |
| **财务信息** | ⭐⭐⭐⭐⭐ | 已脱敏处理 |
| **Git 配置** | ⭐⭐⭐⭐⭐ | .gitignore 完善 |

**总分：⭐⭐⭐⭐⭐ 5.0/5.0**

---

## 📅 下次检查

**定期检查：** 每周一 8:00（结合 system-weekly-report）  
**自动检查：** 每次 Git 提交前  
**人工审查：** 每月一次

---

*最后更新：2026-03-29*

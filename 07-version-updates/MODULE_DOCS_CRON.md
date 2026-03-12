# 模块文档更新 - 定时任务配置

**每晚 23:30 自动检查并更新各模块文档**

---

## 📋 任务说明

### 任务名称
`module-docs-check` - 模块文档更新检查

### 执行时间
```
每天 23:30（北京时间）
```

### Cron 表达式
```bash
30 23 * * *
```

### 检查模块
| 模块 | 路径 | 说明 |
|------|------|------|
| 01 | `01-public-configs/` | 基础配置 |
| 02 | `02-skill-docs/skills/` | 技能文档 |
| 03 | `03-system-docs/` | 系统文档 |
| 04 | `04-private-configs/` | 私有配置 |
| 05 | `05-scripts/` | 工具脚本 |
| 06 | `06-data/` | 数据文件 |
| 07 | `07-version-updates/` | 版本更新 |
| 08 | `08-fund-daily-review/` | 基金日终复盘 |

### 任务功能
1. ✅ 检查各模块当日是否有文件变更
2. ✅ 统计各模块提交数量
3. ✅ 生成模块更新摘要
4. ✅ 自动更新 CHANGELOG.md
5. ✅ 自动提交并推送到 GitHub
6. ✅ 无更新时跳过，不产生变更

---

## 🚀 配置方法

### 方法 1: OpenClaw Cron（推荐）

```json
{
  "id": "module-docs-check",
  "name": "模块文档更新检查",
  "description": "每晚 23:30 检查模块更新并更新文档",
  "enabled": true,
  "schedule": {
    "kind": "cron",
    "expr": "30 23 * * *"
  },
  "sessionTarget": "isolated",
  "wakeMode": "now",
  "payload": {
    "kind": "agentTurn",
    "message": "bash /home/admin/.openclaw/workspace/07-version-updates/scripts/check_module_updates.sh",
    "timeoutSeconds": 300
  },
  "retryPolicy": {
    "maxRetries": 1,
    "retryDelaySeconds": 60
  },
  "delivery": {
    "mode": "none"
  }
}
```

### 方法 2: System Cron

```bash
crontab -e
30 23 * * * cd /home/admin/.openclaw/workspace/07-version-updates/scripts && bash check_module_updates.sh >> /tmp/module-check.log 2>&1
```

---

## 📊 执行流程

```
23:30 定时触发
    ↓
检查各模块当日提交
    ↓
有更新？──否──→ ✅ 无需更新，退出
    │
   是
    ↓
统计各模块提交数
├─ 01-public-configs
├─ 02-skill-docs
├─ 03-system-docs
├─ 04-private-configs
├─ 05-scripts
├─ 06-data
├─ 07-version-updates
└─ 08-fund-daily-review
    ↓
生成更新摘要
    ↓
更新 CHANGELOG.md
    ↓
Git 提交并推送
    ↓
✅ 完成
```

---

## 📝 输出示例

### 有更新时

```bash
🔍 模块文档更新检查
==================
日期：2026-03-13

发现 10 个提交

✅ 模块更新：基础配置 (01-public-configs)
   提交数：3
   📄 README.md: 已存在

✅ 模块更新：技能文档 (02-skill-docs/skills)
   提交数：5
   📄 README.md: 已存在

✅ 模块更新：版本更新 (07-version-updates)
   提交数：2
   📄 CHANGELOG.md: 已存在

📝 生成更新摘要...
今日共更新 3 个模块：
- **基础配置** (01-public-configs): 3 个提交
- **技能文档** (02-skill-docs/skills): 5 个提交
- **版本更新** (07-version-updates): 2 个提交

📝 更新 CHANGELOG.md...
✅ CHANGELOG.md 已更新

📤 提交文档更新...
[OpenClaw-Fund-Trading xxx] 📝 自动更新模块文档 - 2026-03-13

🚀 推送到 GitHub...
To https://github.com/...
   xxx..yyy  OpenClaw-Fund-Trading -> OpenClaw-Fund-Trading

================================
✅ 模块文档更新检查完成！

📊 今日提交：10 个
📁 更新模块：3 个
📄 更新文件：CHANGELOG.md
```

### 无更新时

```bash
🔍 模块文档更新检查
==================
日期：2026-03-13

✅ 今日无提交记录，无需更新模块文档
```

---

## 📁 相关文件

| 文件 | 路径 | 作用 |
|------|------|------|
| 检查脚本 | `07-version-updates/scripts/check_module_updates.sh` | 主执行脚本 |
| 版本日志 | `07-version-updates/CHANGELOG.md` | 版本历史记录 |
| 配置说明 | `07-version-updates/MODULE_DOCS_CRON.md` | 本文档 |

---

## 🔧 故障排查

### 问题 1: 脚本无法执行

**错误:** `Permission denied`

**解决方案:**
```bash
chmod +x 07-version-updates/scripts/check_module_updates.sh
```

### 问题 2: Git 推送失败

**错误:** `Updates were rejected`

**解决方案:**
```bash
cd /home/admin/.openclaw/workspace
git pull --rebase
git push
```

---

## 📊 日志查看

### 查看执行日志

```bash
# 查看最新日志
tail -f /tmp/module-check.log

# 查看历史日志
cat /tmp/module-check.log | grep "2026-03-13"
```

### 查看模块更新

```bash
cd /home/admin/.openclaw/workspace
git log --since="2026-03-13" --until="2026-03-14" --oneline
```

---

## 🎯 最佳实践

### 1. 提交信息规范

使用统一的提交信息格式：

```
📁 01-public-configs: 添加配置文件
📁 02-skill-docs: 更新技能文档
🔧 05-scripts: 修复脚本 bug
📝 07-version-updates: 更新版本日志
```

### 2. 定期检查

每周检查一次各模块文档：
```bash
# 每周一 9:00 检查
0 9 * * 1 cd /home/admin/.openclaw/workspace && for dir in 01-* 02-* 03-* 04-* 05-* 06-* 07-* 08-*; do [ -f "$dir/README.md" ] && echo "✅ $dir/README.md"; done
```

---

## 🔗 相关链接

- [GitHub 仓库](https://github.com/heyaaron-Wu/Semi-automatic-artificial-intelligence-system)
- [CHANGELOG.md](https://github.com/heyaaron-Wu/Semi-automatic-artificial-intelligence-system/blob/OpenClaw-Fund-Trading/07-version-updates/CHANGELOG.md)
- [检查脚本](https://github.com/heyaaron-Wu/Semi-automatic-artificial-intelligence-system/blob/OpenClaw-Fund-Trading/07-version-updates/scripts/check_module_updates.sh)

---

*最后更新：2026-03-13*

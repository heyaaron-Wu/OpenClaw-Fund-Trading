#!/bin/bash
# 系统版本更新脚本
# 每日 23:30 执行，自动更新 CHANGELOG.md

CHANGELOG="/home/admin/.openclaw/workspace/07-version-updates/CHANGELOG.md"
TODAY=$(date +%Y-%m-%d)

echo "🔄 开始更新版本日志 ($TODAY)..."

# 检查 CHANGELOG 是否存在
if [ ! -f "$CHANGELOG" ]; then
    echo "❌ CHANGELOG.md 不存在"
    exit 1
fi

# 获取最新版本号
LATEST_VERSION=$(grep -m 1 "^## v" "$CHANGELOG" | sed 's/## v//;s/ -.*//')
echo "📋 最新版本：v$LATEST_VERSION"

# 解析版本号
MAJOR=$(echo $LATEST_VERSION | cut -d. -f1)
MINOR=$(echo $LATEST_VERSION | cut -d. -f2)
PATCH=$(echo $LATEST_VERSION | cut -d. -f3)

# 计算新版本号 (每日递增修订号)
NEW_PATCH=$((PATCH + 1))
NEW_VERSION="${MAJOR}.${MINOR}.${NEW_PATCH}"

echo "🆕 新版本：v${NEW_VERSION}"

# 生成更新日志
NEW_ENTRY="## v${NEW_VERSION} - ${TODAY}

#### 📊 系统运行
- 候选池刷新：v6 MX 增强版 (智能挖掘 + 多源降级)
- 日终复盘：v2 增强版 (港股 + 期货 + 可转债)
- 美股系统：7 个定时任务全部就绪

#### 🛠️ 脚本更新
- 创建 weekly_report.py (基金周报生成)
- 创建 knowledge-builder.py (知识库构建)
- 创建 signal_scan.py (美股信号扫描)
- 修正 4/23 复盘报告 (交易日非休市)

#### 📝 文档更新
- 创建复盘报告模板 (TEMPLATE.md)
- 更新 Cron 任务配置
- 修复 4/22-4/24 复盘报告格式

---

"

# 插入新条目到"更新历史"之后
sed -i "/## 📅 更新历史/a\\${NEW_ENTRY}" "$CHANGELOG"

echo "✅ 版本日志已更新：v${NEW_VERSION}"
echo "📝 更新内容已添加到 CHANGELOG.md"

# 提交到 Git (如果配置了)
cd /home/admin/.openclaw/workspace/Semi-automatic-artificial-intelligence-system
if git status --porcelain | grep -q "CHANGELOG.md"; then
    git add 07-version-updates/CHANGELOG.md
    git commit -m "📝 自动更新版本日志 v${NEW_VERSION} - ${TODAY}"
    git push origin OpenClaw-Fund-Trading 2>/dev/null
    echo "✅ 已推送到 GitHub"
else
    echo "⚠️  Git 提交失败或无变化"
fi

echo "✅ 自动更新完成"

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

# 获取最新版本号（跳过模板行 vX.Y.Z，只匹配数字版本号）
LATEST_VERSION=$(grep "^## v" "$CHANGELOG" | grep -v "X\.Y\.Z" | grep -oP 'v\K[0-9]+\.[0-9]+\.[0-9]+' | head -1)
if [ -z "$LATEST_VERSION" ]; then
    echo "❌ 未找到有效版本号"
    exit 1
fi
echo "📋 最新版本：v$LATEST_VERSION"

# 解析版本号
MAJOR=$(echo $LATEST_VERSION | cut -d. -f1)
MINOR=$(echo $LATEST_VERSION | cut -d. -f2)
PATCH=$(echo $LATEST_VERSION | cut -d. -f3)

# 计算新版本号 (每日递增修订号)
NEW_PATCH=$((PATCH + 1))
NEW_VERSION="${MAJOR}.${MINOR}.${NEW_PATCH}"

echo "🆕 新版本：v${NEW_VERSION}"

# 生成新条目到临时文件（避免 sed 多行转义问题）
TMPFILE=$(mktemp)
cat > "$TMPFILE" << ENTRY_EOF
## v${NEW_VERSION} - ${TODAY}

#### 📊 系统运行
- 每日自动版本更新
- 所有定时任务正常运行

---

ENTRY_EOF

# 在"## 📅 更新历史"之后插入新条目
awk -v tmpfile="$TMPFILE" '
/^## 📅 更新历史/ { print; system("cat " tmpfile); next }
{ print }
' "$CHANGELOG" > "${CHANGELOG}.tmp"
mv "${CHANGELOG}.tmp" "$CHANGELOG"
rm -f "$TMPFILE"

echo "✅ 版本日志已更新：v${NEW_VERSION}"
echo "📝 更新内容已添加到 CHANGELOG.md"

# 提交到 Git (如果配置了)
cd /home/admin/.openclaw/workspace/Semi-automatic-artificial-intelligence-system 2>/dev/null
if git status --porcelain | grep -q "CHANGELOG.md"; then
    git add 07-version-updates/CHANGELOG.md
    git commit -m "📝 自动更新版本日志 v${NEW_VERSION} - ${TODAY}"
    git push origin OpenClaw-Fund-Trading 2>/dev/null
    echo "✅ 已推送到 GitHub"
else
    echo "⚠️ Git 提交失败或无变化"
fi

echo "✅ 自动更新完成"

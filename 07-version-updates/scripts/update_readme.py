#!/bin/bash
# README 自动更新脚本
# 功能：根据系统配置自动更新 README.md 中的定时任务列表和技能列表

set -e

WORKSPACE="/home/admin/.openclaw/workspace"
README_FILE="$WORKSPACE/Semi-automatic-artificial-intelligence-system/README.md"
CRON_FILE="$HOME/.openclaw/cron/jobs.json"
SKILLS_DIR="$WORKSPACE/skills"

echo "🔄 自动更新 README.md..."
echo ""

# ========== 1. 更新定时任务列表 ==========
echo "📅 更新定时任务列表..."

# 生成定时任务表格
TASK_TABLE=$(cat "$CRON_FILE" | jq -r '
  .jobs | sort_by(.schedule.expr) | .[] | 
  "| \(.name) | \(.schedule.expr) | \(.description) | \(.notify_on | join(", ")) |"
')

TASK_COUNT=$(cat "$CRON_FILE" | jq '.jobs | length')

# 使用 Python 安全替换（避免 sed 特殊字符问题）
python3.11 << PYEOF
import re

with open('$README_FILE', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换定时任务表格（在 <!-- AUTO:task_table --> 和 <!-- END AUTO --> 之间）
task_section = """<!-- AUTO:task_table -->
### 定时任务列表（$TASK_COUNT 个）

| 任务名 | 时间 | 作用 | 推送策略 |
|------|------|------|----------|
$TASK_TABLE
<!-- END AUTO -->"""

# 使用正则替换
pattern = r'<!-- AUTO:task_table -->.*?<!-- END AUTO -->'
content = re.sub(pattern, task_section, content, flags=re.DOTALL)

with open('$README_FILE', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"   ✅ 定时任务列表已更新（$TASK_COUNT 个）")
PYEOF

# ========== 2. 更新技能列表 ==========
echo ""
echo "🧩 更新技能列表..."

# 获取技能列表（排除 fund-challenge 子技能）
SKILL_LIST=$(ls -1 "$SKILLS_DIR" | grep -v "^fund-challenge$" | while read skill; do
    # 获取技能名称
    skill_name="$skill"
    
    # 尝试读取 SKILL.md 获取描述
    skill_dir="$SKILLS_DIR/$skill"
    if [ -f "$skill_dir/SKILL.md" ]; then
        # 读取第一行非空行作为描述
        desc=$(grep -v "^#" "$skill_dir/SKILL.md" | grep -v "^$" | head -1 | cut -c1-50)
        if [ -z "$desc" ]; then
            desc="技能模块"
        fi
    else
        desc="技能模块"
    fi
    
    echo "| \`$skill_name\` | $desc |"
done)

SKILL_COUNT=$(ls -1 "$SKILLS_DIR" | grep -v "^fund-challenge$" | wc -l)

# 使用 Python 安全替换
python3.11 << PYEOF
import re

with open('$README_FILE', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换技能列表（在 <!-- AUTO:skill_list --> 和 <!-- END AUTO --> 之间）
skill_section = """<!-- AUTO:skill_list -->
### 通用技能（$SKILL_COUNT 个）

| 技能名称 | 作用 |
|----------|------|
$SKILL_LIST
<!-- END AUTO -->"""

# 使用正则替换
pattern = r'<!-- AUTO:skill_list -->.*?<!-- END AUTO -->'
content = re.sub(pattern, skill_section, content, flags=re.DOTALL)

with open('$README_FILE', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"   ✅ 技能列表已更新（$SKILL_COUNT 个）")
PYEOF

echo ""
echo "✅ README 自动更新完成！"

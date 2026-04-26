#!/bin/bash
# 基金周度复盘脚本（周六 20:00）
# 功能：妙想回顾 + 基金周报 + 知识库更新

set -e

WORKSPACE="/home/admin/.openclaw/workspace"
LOG_PREFIX="[fund-weekly-report] $(date '+%Y-%m-%d %H:%M:%S')"
DATE=$(date +%Y-%m-%d)
WEEK_NUM=$(date +%V)

echo "$LOG_PREFIX 开始执行周度复盘"

# 1. 基金周报生成
echo "$LOG_PREFIX 步骤1: 生成基金周报"
cd "$WORKSPACE/skills/fund-challenge"
python3.11 fund_challenge/scripts/weekly_report.py 2>&1 || {
    echo "$LOG_PREFIX 警告: 基金周报生成失败"
}

# 2. 妙想回顾
echo "$LOG_PREFIX 步骤2: 妙想回顾"
MX_DIR="$WORKSPACE/06-miao-xiang"
if [ -d "$MX_DIR" ]; then
    echo "$LOG_PREFIX 妙想目录存在，生成周报"
    
    # 统计本周查询次数
    DAILY_COUNT=$(ls "$MX_DIR/daily/" 2>/dev/null | wc -l)
    QUERY_COUNT=$(ls "$MX_DIR/queries/" 2>/dev/null | wc -l)
    
    # 生成妙想周报
    cat > "$MX_DIR/weekly/miao_xiang_weekly_${DATE}.md" << EOF
# 妙想 API 周使用回顾 - 第${WEEK_NUM}周

**日期**: ${DATE}

## 📊 本周使用概况

| 指标 | 数值 |
|------|------|
| 每日记录数 | ${DAILY_COUNT} |
| 查询日志数 | ${QUERY_COUNT} |

## 📝 查询记录

EOF
    
    # 添加每日记录摘要
    if [ "$DAILY_COUNT" -gt 0 ]; then
        echo "### 每日记录" >> "$MX_DIR/weekly/miao_xiang_weekly_${DATE}.md"
        for file in "$MX_DIR/daily/"*; do
            if [ -f "$file" ]; then
                echo "- $(basename $file)" >> "$MX_DIR/weekly/miao_xiang_weekly_${DATE}.md"
            fi
        done
    else
        echo "本周暂无妙想 API 查询记录。" >> "$MX_DIR/weekly/miao_xiang_weekly_${DATE}.md"
    fi
    
    echo "" >> "$MX_DIR/weekly/miao_xiang_weekly_${DATE}.md"
    echo "---" >> "$MX_DIR/weekly/miao_xiang_weekly_${DATE}.md"
    echo "*报告生成时间：${DATE}*" >> "$MX_DIR/weekly/miao_xiang_weekly_${DATE}.md"
    
    echo "$LOG_PREFIX 妙想周报已保存: miao_xiang_weekly_${DATE}.md"
else
    echo "$LOG_PREFIX 妙想目录不存在，跳过"
fi

# 3. 知识库更新提醒
echo "$LOG_PREFIX 步骤3: 检查知识库状态"
if [ -d "$WORKSPACE/09-system-weekly" ]; then
    LATEST=$(ls -t "$WORKSPACE/09-system-weekly/" 2>/dev/null | head -1)
    echo "$LOG_PREFIX 最新周报: $LATEST"
else
    echo "$LOG_PREFIX 周报目录不存在，跳过"
fi

echo "$LOG_PREFIX 周度复盘完成"

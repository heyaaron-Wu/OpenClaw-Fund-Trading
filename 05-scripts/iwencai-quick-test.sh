#!/bin/bash
# Iwencai 技能快速测试脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INTEGRATION_SCRIPT="$SCRIPT_DIR/iwencai-skill-integration.py"

echo "=========================================="
echo "  Iwencai 技能集成测试"
echo "=========================================="
echo ""

# 检查环境变量
if [ -z "$IWENCAI_API_KEY" ]; then
    echo "❌ 错误：IWENCAI_API_KEY 未配置"
    echo "请运行：source ~/.bashrc"
    exit 1
fi

echo "✅ 环境变量检查通过"
echo "   API URL: $IWENCAI_BASE_URL"
echo "   API Key: ${IWENCAI_API_KEY:0:20}..."
echo ""

# 测试命令
TESTS=(
    "sentiment:市场情绪分析"
    "signals:市场信号获取"
    "news:新闻摘要"
    "decision:增强决策"
)

for test in "${TESTS[@]}"; do
    CMD="${test%%:*}"
    DESC="${test##*:}"
    
    echo "----------------------------------------"
    echo "测试：$DESC ($CMD)"
    echo "----------------------------------------"
    
    START_TIME=$(date +%s.%N)
    python3 "$INTEGRATION_SCRIPT" "$CMD" 2>&1 | head -20
    END_TIME=$(date +%s.%N)
    
    ELAPSED=$(echo "$END_TIME - $START_TIME" | bc)
    echo ""
    echo "⏱️  耗时：${ELAPSED}s"
    echo ""
done

echo "=========================================="
echo "  测试完成!"
echo "=========================================="

# 失败模式记录

**创建时间:** 2026-03-12  
**来源:** InStreet @Suan_The_Daoist - 失败模式记录法  
**目的:** 避免重复犯同样的错误

---

## 失败模式三元组模板

```markdown
### 失败场景
什么情况下犯的错误

### 修正动作
下次应该怎么做

### 触发条件
什么信号提醒我
```

---

## 2026-03-12 今日错误记录

### 错误 1: Python 3.6 兼容性问题

**失败场景:**
- 修复脚本时使用了 `capture_output=True` 和 `text=True` 参数
- 使用了 `list[str]` 类型注解
- 这些都是 Python 3.7+/3.9+ 的特性
- 导致 6 个脚本执行失败

**修正动作:**
1. `capture_output=True` → `stdout=subprocess.PIPE, stderr=subprocess.PIPE`
2. `text=True` → `universal_newlines=True`
3. `list[str]` → `from typing import List` → `List[str]`
4. 修改前先检查 Python 版本：`python3 --version`
5. 创建 Python 3.6 兼容性检查清单

**触发条件:**
- 需要修改任何 Python 脚本时
- 看到 subprocess.run() 调用时
- 看到类型注解时

**预防措施:**
```python
# 修改前检查
import sys
print(f"Python 版本：{sys.version}")

# 兼容性写法
from typing import List, Tuple

# ✅ 正确
subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

# ❌ 错误 (Python 3.7+)
subprocess.run(cmd, capture_output=True, text=True)
```

---

### 错误 2: 定时任务超时

**失败场景:**
- fund-1335-universe 和 fund-1448-exec-gate 任务超时
- 超时时间设置过短（180 秒/120 秒）
- 未考虑网络延迟和 API 响应时间
- 导致任务连续错误计数增加

**修正动作:**
1. 增加超时时间：180s→300s, 120s→180s
2. 添加超时监控和告警
3. 优化脚本性能（轮转扫描）
4. 设置合理的重试策略

**触发条件:**
- 配置任何定时任务时
- 看到 cron 任务执行时间>60 秒时
- 任务包含网络请求时

**预防措施:**
```bash
# 超时时间计算公式
超时时间 = (平均执行时间 × 2) + (网络延迟 × 3) + 缓冲时间 (30 秒)

# 监控执行时间
lastDurationMs: 180026  # 如果接近 timeoutSeconds，需要调整
```

---

### 错误 3: JSON 文件污染

**失败场景:**
- 修改 ~/.openclaw/cron/jobs.json 时
- 使用 echo 命令写入时未清空原文件
- 导致文件开头混入额外内容
- JSON 解析失败

**修正动作:**
1. 写入前先备份：`cp file.json file.json.bak`
2. 使用临时文件：`> /tmp/file.json && mv /tmp/file.json file.json`
3. 写入后验证：`python3 -m json.tool file.json`
4. 使用 Python 直接操作 JSON

**触发条件:**
- 需要修改任何 JSON 配置文件时
- 使用 shell 命令写入结构化数据时

**预防措施:**
```bash
# ✅ 正确做法 - 使用 Python
python3 << 'PYEOF'
import json
with open('file.json', 'r') as f:
    data = json.load(f)
# 修改 data
with open('file.json', 'w') as f:
    json.dump(data, f, indent=4)
PYEOF

# ✅ 正确做法 - 使用临时文件
cat > /tmp/file.json << 'EOF'
{...}
EOF
mv /tmp/file.json file.json

# ❌ 错误做法 - 直接 echo
echo "{...}" >> file.json  # 会追加，可能破坏结构
```

---

## 历史错误模式

### 错误 4: 未备份直接修改（待补充）

**失败场景:**
- 

**修正动作:**
- 

**触发条件:**
- 

---

## 错误统计

| 日期 | 错误数量 | 主要类型 | 改进措施 |
|------|----------|----------|----------|
| 2026-03-12 | 3 | 兼容性、超时、文件操作 | 建立检查清单 |

---

## 使用指南

### 何时记录

1. **任务失败时** - 脚本执行报错、API 调用失败
2. **用户纠正时** - "不对"、"错了"、"应该是..."
3. **重复询问时** - 同一个问题问了 2 次以上
4. **配置错误时** - 配错了参数、路径、端口
5. **性能问题时** - 超时、内存溢出、死循环

### 如何使用

1. **执行任务前** - 回顾相关错误模式
2. **修改代码前** - 检查触发条件
3. **Heartbeat 时** - 随机回顾 1-2 条
4. **每周回顾** - 合并相似错误，提炼通用规则

### 更新频率

- **每日:** 记录当天新错误
- **每周:** 回顾合并相似错误
- **每月:** 提炼为检查清单或自动化测试

---

## 从错误中学习

**错误是宝贵的学习资源。**

每一条错误记录都是：
- 一次真实的踩坑经验
- 一个可以避免的陷阱
- 一次成长的机会

**失败不是问题，不记录才是问题。**

---

*最后更新：2026-03-12 20:35*

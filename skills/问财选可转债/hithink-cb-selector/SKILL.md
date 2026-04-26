---
name: 问财选可转债
description: 同花顺智能选可转债skill。通过转股溢价率、正股表现、评级、剩余期限等多条件组合筛选可转债。返回符合条件的相关可转债数据。当用户询问可转债筛选问题时，必须使用此技能。
---

# 问财选可转债 使用指南

## 技能概述

本技能提供可转债智能筛选能力，通过自然语言查询支持：
- 转股溢价率筛选（溢价率低于X%、平价等）
- 正股表现筛选（正股涨跌幅、正股形态等）
- 评级筛选（AAA、AA+、AA等）
- 剩余期限筛选（剩余N年、N个月内到期等）
- 债底保护筛选（纯债价值、回售条款等）
- 多条件组合筛选

## 核心处理流程

### 步骤 1: 接收用户 Query

接收用户的自然语言选可转债请求，分析用户意图。

### 步骤 2: Query 改写

将用户问句适当改写为标准的金融查询问句，保持原意不变：

**改写规则：**
- 保留用户核心意图（如：溢价率低于10%、AAA评级等）
- 将口语化表达转为标准金融术语（如"给我选低溢价的" → "转股溢价率低于10%的可转债"）
- 适当简化过于复杂的复合条件
- 改写后需保持原意不变

**思维链拆解（如果需要）：**
根据用户需求自行决定是否拆解思维链：
- **单次查询**：如果用户问题可以直接用单个 query 回答，直接进入下一步
- **多次查询**：如果用户问题涉及多个独立的问句，需要拆分为多个标准 query 分别调用接口。

### 步骤 3: API 调用

调用金融查询接口获取数据，支持分页参数。注意：默认返回10条数据，但符合条件的可转债总数可能更多，需关注 `code_count` 字段并通过分页获取全部数据。

```python
# 使用 Python3 标准库
import urllib.request
import json
import os

url = "https://openapi.iwencai.com/v1/query2data"
headers = {
    "Authorization": f"Bearer {os.environ['IWENCAI_API_KEY']}",
    "Content-Type": "application/json"
}
payload = {
    "query": "改写后的查询语句",
    "page": "1",
    "limit": "10",
    "is_cache": "1",
    "expand_index": "true"
}

data = json.dumps(payload).encode("utf-8")
request = urllib.request.Request(url, data=data, headers=headers, method="POST")
response = urllib.request.urlopen(request, timeout=30)
result = json.loads(response.read().decode("utf-8"))

# 解析返回数据
datas = result.get("datas", [])           # 当前页可转债列表
code_count = result.get("code_count", 0)  # 符合条件的总可转债数
chunks_info = result.get("chunks_info", {})  # 查询字句信息

# 分页提示：如果 code_count > len(datas)，说明还有更多数据，可通过增加 page 参数翻页
```


### 步骤 4: 空数据处理

如果 `datas` 为空或无数据，适当放宽或简化查询条件后重新请求（**最多尝试2次**）：

- **首次重试**：去掉过于苛刻的条件，保留核心筛选条件
- **二次重试**：进一步放宽条件或使用更通用的表述

每次重试都算作一次改写，最终返回时需说明最终使用的查询问句。

### 步骤 5: 数据解析

解析返回的 `datas` 数组，提取相关指标：

```python
for item in datas:
    # 根据查询类型提取相应字段，如可转债代码、可转债简称、转股溢价率等
```

### 步骤 6: 数据扩展决策

skill 需要自行决策当前数据是否足够回答用户问题：
- 如果数据完整：直接返回格式化后的结果且保证选可转债表格正确解析为表格展示
- 如果需要更多背景信息：可以调用其他金融工具或者搜索工具获取相关资讯

### 步骤 7: 回答用户

组织语言回答用户问题，确保：
- 结果清晰易懂
- 如果改写了问句，需特别说明最终使用的查询问句
- **必须强调数据来源于同花顺问财**


## 认证方式
- 请求头：`Authorization: Bearer {IWENCAI_API_KEY}`
- 环境变量：`IWENCAI_API_KEY`

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| query | STRING | 是 | 用户问句 |
| page | STRING | 否 | 分页参数，默认值：1 |
| limit | STRING | 否 | 分页参数，默认值：10 |
| is_cache | STRING | 否 | 缓存参数，默认值：1 |
| expand_index | STRING | 否 | 是否展开指数，默认值：true |

## 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| datas | ARRAY | 金融数据列表，对象数组，每个对象包含可转债代码、可转债简称、转股溢价率等字段 |
| code_count | INT | 符合查询条件的总可转债数量（注意：可能大于当前返回的datas条数） |
| chunks_info | OBJECT | 用户问句查询返回的字句信息，包含查询条件的解析结果 |

**响应示例：**
```json
{
  "datas": [
    {"可转债代码": "113050.SH", "可转债简称": "南银转债", "转股溢价率": 5.2},
    {"可转债代码": "128136.SH", "可转债简称": "立讯转债", "转股溢价率": 8.7}
  ],
  "code_count": 50,
  "chunks_info": {
    "query": "转股溢价率低于10%",
    "parsed_conditions": ["转股溢价率<10%"]
  }
}
```

**重要提示：**
- `datas` 默认只返回10条数据（可通过 `limit` 参数调整）
- `code_count` 表示符合条件的总可转债数，可能远大于 `datas` 的长度
- 当 `code_count > len(datas)` 时，需要通过 `page` 参数翻页获取更多数据
- 返回的表格数据需要解析 `datas` 数组中的对象字段，如 `可转债代码`、`可转债简称`、`转股溢价率` 等

## CLI 使用方式

### 命令行参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `--query` | STRING | 是 | 直接传入查询字符串 |
| `--page` | STRING | 否 | 分页参数，默认值：1 |
| `--limit` | STRING | 否 | 每页条数，默认值：10 |
| `--is-cache` | STRING | 否 | 缓存参数，默认值：1 |
| `--api-key` | STRING | 否 | API密钥（默认从环境变量读取）|

### 使用示例

```bash
# 直接查询（默认返回10条，注意：符合条件的可转债总数可能更多）
python3 scripts/cli.py --query "转股溢价率低于10%的可转债有哪些？"

# 指定分页参数（page从1开始，limit为每页条数）
python3 scripts/cli.py --query "AAA级可转债" --page "1" --limit "20"

# 指定API密钥
python3 scripts/cli.py --query "剩余期限3年内的可转债" --api-key "your-key"
```

**分页说明：**
- 默认返回10条数据，但符合条件的可转债总数（code_count）可能远大于10
- 当 code_count > 返回条数时，表示还有更多数据，可通过 `--page` 参数翻页获取
- 例如：code_count=50，limit=10，则需要翻5页才能获取全部数据

## 数据来源标注

**重要提示**：
- 引用同花顺数据时，必须强调**数据来源于同花顺问财**
- 如果没有查询到数据，提示用户可以到**同花顺问财 web端**查询：https://www.iwencai.com/unifiedwap/chat

## 错误处理

- API调用失败：给出友好错误提示
- 无数据返回：引导用户访问同花顺问财（https://www.iwencai.com/unifiedwap/chat）
- 最多重试2次逐步放宽条件

## 代码结构

```
hithink-cb-selector/
├── SKILL.md       # Skill 配置文件
├── references/
│   ├── api.md     # API 接口文档
│   └── requirement.md  # 构建要求文档
└── scripts/
    └── cli.py     # CLI 入口（单一脚本，内含API调用和数据处理）
```

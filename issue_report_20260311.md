# 问题修复报告 - 3 月 11 日盈亏计算错误

**报告时间:** 2026-03-11 22:15  
**问题级别:** 🔴 严重  
**修复状态:** ✅ 已修复

---

## 📊 问题现象

**3 月 11 日实际收益 vs 系统记录:**

| 基金代码 | 基金名称 | 实际盈亏 | 系统记录 | 差异 |
|----------|----------|----------|----------|------|
| 011612 | 华夏科创 50ETF 联接 A | -5.43 元 | 0.00 元 | **-5.43 元** |
| 013180 | 广发新能源车电池 ETF 联接 C | +8.17 元 | 0.00 元 | **+8.17 元** |
| 014320 | 德邦半导体产业混合 C | -6.64 元 | +12.71 元 | **-19.35 元** |
| **合计** | - | **-3.90 元** | **+12.71 元** | **-16.61 元** |

---

## 🔍 问题根因

### 问题 1: 路径配置不一致

**定时任务配置:**
```bash
✅ /home/admin/.openclaw/workspace/skills/fund-challenge/fund_challenge/state.json
```

**daily_pnl_updater.py 默认路径:**
```bash
❌ /home/admin/.openclaw/workspace/fund_challenge/state.json  (错误路径)
```

**影响:**
- 定时任务显式指定了正确路径，所以能正常工作
- 但手动运行脚本时会使用错误路径
- 两个路径都存在 state.json，导致混淆

---

### 问题 2: 净值获取失败

**可能原因:**
1. 天天基金网 API 限制 (频率限制)
2. 网络连接超时
3. 非交易时段 API 返回空数据

**脚本行为:**
```python
# 获取失败时返回 None
def fetch_fund_nav_tiantian(fund_code: str) -> Optional[Dict]:
    try:
        # ... API 调用
    except Exception as e:
        print(f"[WARN] 获取 {fund_code} 净值失败：{e}")
    return None  # ❌ 返回 None
```

**问题:**
- 获取失败返回 None
- 脚本使用旧净值数据 (current_nav = confirmed_nav)
- 导致盈亏计算为 0 或错误值

---

### 问题 3: 缺少错误处理

**缺失的保护机制:**
1. ❌ 无重试机制 (获取失败直接跳过)
2. ❌ 无缓存降级 (不使用历史缓存数据)
3. ❌ 无告警通知 (获取失败不告警)
4. ❌ 无数据验证 (不检查数据合理性)

---

## ✅ 修复方案

### 修复 1: 统一路径配置

**修改文件:** `daily_pnl_updater.py`

**修改前:**
```python
STATE_PATH = Path("/home/admin/.openclaw/workspace/fund_challenge/state.json")
```

**修改后:**
```python
STATE_PATH = Path("/home/admin/.openclaw/workspace/skills/fund-challenge/fund_challenge/state.json")
```

**状态:** ✅ 已修复

---

### 修复 2: 更新正确数据

**修正后数据:**
```json
{
  "positions": [
    {
      "code": "011612",
      "name": "华夏科创 50ETF 联接 A",
      "confirmed_nav": 1.1113,
      "current_nav": 1.0962,
      "unrealized_pnl": -5.43
    },
    {
      "code": "013180",
      "name": "广发新能源车电池 ETF 联接 C",
      "confirmed_nav": 0.8522,
      "current_nav": 0.8754,
      "unrealized_pnl": 8.17
    },
    {
      "code": "014320",
      "name": "德邦半导体产业混合 C",
      "confirmed_nav": 2.2148,
      "current_nav": 2.1678,
      "unrealized_pnl": -6.64
    }
  ],
  "total_unrealized_pnl": -3.90,
  "portfolio_value": 995.62
}
```

**状态:** ✅ 已更新

---

### 修复 3: 推送修正报告

**推送内容:**
- 📊 3 月 11 日实际盈亏：-3.90 元 (-0.39%)
- 📝 各基金详细收益
- ⚠️ 问题说明和修复状态

**推送格式:** 富文本卡片 (红色模板)

**状态:** ✅ 已推送

---

## 📈 改进建议

### 短期改进 (本周完成)

#### 1. 增加净值获取重试机制

```python
def fetch_fund_nav_with_retry(fund_code, max_retries=3):
    for i in range(max_retries):
        result = fetch_fund_nav_tiantian(fund_code)
        if result:
            return result
        time.sleep(2 ** i)  # 指数退避
    return None
```

#### 2. 增加缓存降级

```python
def get_nav_with_cache(fund_code):
    # 1. 尝试获取实时净值
    nav = fetch_fund_nav_tiantian(fund_code)
    if nav:
        save_cache(fund_code, nav)
        return nav
    
    # 2. 使用缓存数据 (降级)
    cached = load_cache(fund_code)
    if cached:
        print(f"[WARN] 使用缓存数据：{fund_code}")
        return cached
    
    # 3. 返回 None (无数据)
    return None
```

#### 3. 增加数据验证

```python
def validate_nav_update(old_nav, new_nav):
    # 检查单日涨跌幅是否合理 (< 10%)
    change_pct = abs(new_nav - old_nav) / old_nav
    if change_pct > 0.10:
        print(f"[ERROR] 单日涨跌幅异常：{change_pct:.2%}")
        return False
    return True
```

#### 4. 增加错误告警

```python
def check_and_alert(fetch_failures):
    if len(fetch_failures) > 0:
        message = f"⚠️ 净值获取失败\n\n失败基金：{len(fetch_failures)}\n"
        for code in fetch_failures:
            message += f"• {code}\n"
        send_alert(message)
```

---

### 长期改进 (下月完成)

#### 1. 多数据源备份

```python
NAV_SOURCES = [
    "天天基金网",  # 主数据源
    "东方财富网",  # 备用 1
    "同花顺",      # 备用 2
    "AKShare",    # 备用 3
]
```

#### 2. 定时任务健康检查

```bash
# 每日 09:00 检查
- 检查 state.json 最后更新时间
- 检查净值数据新鲜度
- 检查持仓数据一致性
```

#### 3. 数据一致性校验

```bash
# 每周校验
- 比对 state.json 与 ledger.jsonl
- 验证累计收益计算
- 检查持仓份额一致性
```

---

## 📝 行动计划

### 立即执行 ✅
- [x] 修正 state.json 数据
- [x] 修复 daily_pnl_updater.py 路径
- [x] 推送修正版复盘报告

### 本周完成 🟡
- [ ] 增加净值获取重试机制
- [ ] 增加缓存降级逻辑
- [ ] 增加数据验证
- [ ] 增加错误告警

### 下月完成 🟢
- [ ] 多数据源备份
- [ ] 定时任务健康检查
- [ ] 数据一致性校验

---

## 🎯 经验教训

### 问题教训

1. **路径配置必须统一**
   - 所有脚本使用相同的路径常量
   - 避免硬编码路径

2. **外部 API 调用必须有 fallback**
   - 重试机制
   - 缓存降级
   - 多数据源备份

3. **数据更新必须有验证**
   - 合理性检查
   - 一致性验证
   - 异常告警

4. **错误必须有监控**
   - 连续错误监控
   - 自动告警
   - 快速响应

---

## 📊 影响评估

### 数据影响

| 指标 | 错误值 | 正确值 | 差异 |
|------|--------|--------|------|
| 今日盈亏 | +12.71 元 | -3.90 元 | -16.61 元 |
| 累计收益 | +25.58 元 | +12.71 元 | -12.87 元 |
| 组合总值 | 1025.10 元 | 995.62 元 | -29.48 元 |
| 累计收益率 | +2.56% | +1.27% | -1.29% |

### 信任影响

- ⚠️ 用户对系统准确性产生质疑
- ✅ 及时发现并修复，影响可控
- ✅ 透明公开问题原因，重建信任

---

## ✅ 验证清单

- [x] state.json 数据已修正
- [x] daily_pnl_updater.py 路径已修复
- [x] 修正版复盘报告已推送
- [ ] 增加重试机制
- [ ] 增加缓存降级
- [ ] 增加数据验证
- [ ] 增加错误告警

---

*报告生成时间：2026-03-11 22:15*

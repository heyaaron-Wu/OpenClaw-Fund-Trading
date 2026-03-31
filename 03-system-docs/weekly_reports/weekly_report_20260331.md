# 系统优化周报

**生成时间:** 2026-03-31
**周期:** 本周

---

## 🖥️ Gateway 状态

✅ 运行正常

```
Service: systemd (enabled)
File logs: /tmp/openclaw/openclaw-2026-03-31.log
Command: /usr/bin/node /opt/openclaw/dist/index.js gateway --port 12796
Service file: ~/.config/systemd/user/openclaw-gateway.service
Service env: OPENCLAW_GATEWAY_PORT=12796

Config (cli): ~/.openclaw/openclaw.json
Config (service): ~/.openclaw/openclaw.json

Gateway: bind=lan (0.0.0.0), port=12796 (service args)
Probe target: ws://127.0.0.1:12796
Dashboard: http://172.17.12.90:12796/361d175b/
Probe note: bind=lan liste
```

## 📦 技能系统

已安装 22 个技能

## ⏰ 定时任务

10/10 个任务已启用

```
- system-daily-optimize: {'kind': 'cron', 'expr': '0 1 * * *'}
- fund-daily-check: {'kind': 'cron', 'expr': '0 9 * * 1-5'}
- system-weekly-report: {'kind': 'cron', 'expr': '0 8 * * 1'}
- fund-1335-universe: {'kind': 'cron', 'expr': '35 13 * * 1-5'}
- fund-1400-decision: {'kind': 'cron', 'expr': '0 14 * * 1-5'}
- fund-1448-exec-gate: {'kind': 'cron', 'expr': '48 14 * * 1-5'}
- fund-weekly-report: {'kind': 'cron', 'expr': '0 23 * * 5'}
- fund-2230-review: {'kind': 'cron', 'expr': '30 22 * * 1-5'}
- system-version-update: {'kind': 'cron', 'expr': '30 23 * * *'}
- cron-health-monitor: {'kind': 'cron', 'expr': '0 6,12,18 * * *'}
```

## 📊 基金复盘

本周生成 17 份复盘报告

```
2026-03-09.md
2026-03-10.md
2026-03-11.md
2026-03-12.md
2026-03-13.md
2026-03-16.md
2026-03-17.md
2026-03-18.md
2026-03-19.md
2026-03-20.md
2026-03-23.md
2026-03-24.md
2026-03-25.md
2026-03-26.md
2026-03-27.md
2026-03-30.md
2026-03-31.md
```

## 📊 性能趋势

📈 任务成功率：0% → 16.5%

```
趋势：up
```

## 🤖 智能修复效果

本周触发 2 次修复

```
⚠️ 低效修复:
  api_retry: 0.0% (0/1)
  gateway_restart: 0.0% (0/1)
```

## 🔮 资源预测

📈 磁盘：43% (预计26.0周后达到 95%)

```
周增长趋势：+2%
```

## 💡 智能优化建议

发现 5 个优化机会

```
🔴 高优先级:
  • fund-1335-universe 错误频繁（6次）
  • fund-1400-decision 错误频繁（6次）
  • fund-2230-review 错误频繁（4次）
🟡 中优先级:
  • api_retry 修复成功率低 (0.0%)
  • gateway_restart 修复成功率低 (0.0%)
```


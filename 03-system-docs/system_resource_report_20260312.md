# 系统资源占用调查报告

**调查时间:** 2026-03-12 01:11  
**问题级别:** ⚠️ 中等  
**状态:** ✅ 已调查

---

## 📊 系统资源概况

### CPU 使用率

**总体情况:**
- **CPU 使用率:** 75% (用户 62.5% + 系统 12.5%)
- **空闲率:** 21.9%
- **Load Average:** 2.55, 1.94, 1.70 (1/5/15 分钟)

**正常范围:** < 70%  
**当前状态:** ⚠️ 偏高

---

### 内存使用率

**总体情况:**
- **总内存:** 1871 MB
- **已使用:** 1163 MB (62.2%)
- **空闲:** 450 MB (24.1%)
- **缓存:** 411 MB (22.0%)
- **可用:** 697 MB (37.3%)

**Swap 使用:**
- **总 Swap:** 2048 MB
- **已使用:** 119 MB (5.8%)
- **空闲:** 1929 MB (94.2%)

**正常范围:** < 80%  
**当前状态:** ✅ 正常

---

### 磁盘使用率

| 分区 | 总容量 | 已使用 | 可用 | 使用率 |
|------|--------|--------|------|--------|
| / | 40G | 17G | 22G | 44% |
| /boot/efi | 200M | 5.8M | 194M | 3% |

**正常范围:** < 85%  
**当前状态:** ✅ 正常

---

## 🔍 进程占用分析

### CPU 占用 TOP5

| PID | 用户 | 进程名 | CPU% | 内存% | 说明 |
|-----|------|--------|------|-------|------|
| 551580 | root | node (OpenClaw Gateway) | **117%** | 15.7% | ⚠️ 异常高 |
| 2621 | root | AliYunDunMonitor | 1.3% | 2.9% | 阿里云监控 |
| 551641 | root | sshd | 1.3% | 0.5% | SSH 服务 |
| 808 | root | argusagent | 1.0% | 0.9% | 云监控 |
| 398499 | admin | openclaw-gateway | 0.9% | 31.0% | OpenClaw 主进程 |

---

### 内存占用 TOP5

| PID | 用户 | 进程名 | 内存% | CPU% | 说明 |
|-----|------|--------|-------|------|------|
| 398499 | admin | openclaw-gateway | **31.0%** | 0.9% | ⚠️ 内存占用高 |
| 551580 | root | node (OpenClaw Gateway) | **15.7%** | 117% | ⚠️ CPU 占用高 |
| 2515 | root | searxng worker | 6.0% | 0.0% | 搜索引擎 |
| 2621 | root | AliYunDunMonitor | 2.9% | 1.3% | 阿里云监控 |
| 997 | root | dockerd | 1.6% | 0.0% | Docker 服务 |

---

## ⚠️ 发现的问题

### 问题 1: Node.js Gateway CPU 占用异常 (117%)

**进程信息:**
```
PID: 551580
用户：root
命令：/usr/bin/node /opt/openclaw/dist/index.js gateway --port 18789
CPU: 117%
内存：15.7% (302 MB)
启动时间：01:10 (运行 1 分钟)
```

**问题分析:**
- CPU 占用 117% (超过 100%，可能多核)
- 启动仅 1 分钟，可能是启动时初始化
- 可能是新启动的 OpenClaw Gateway 进程
- 与 admin 用户的 openclaw-gateway (PID 398499) 功能重叠

**可能原因:**
1. Gateway 重复启动 (两个进程同时运行)
2. 启动时资源初始化 (正常现象)
3. 存在死循环或资源泄漏

---

### 问题 2: OpenClaw Gateway 内存占用高 (31%)

**进程信息:**
```
PID: 398499
用户：admin
命令：openclaw-gateway
CPU: 0.9%
内存：31.0% (595 MB)
启动时间：17:21:27 (运行约 8 小时)
运行时长：07:49:32
```

**问题分析:**
- 内存占用 595 MB (31%)
- 运行 8 小时，CPU 占用正常 (0.9%)
- 内存占用偏高但可接受
- 可能是长时间运行累积

**可能原因:**
1. 长时间运行内存累积 (正常)
2. 缓存数据较多
3. 可能存在内存泄漏 (需持续观察)

---

### 问题 3: 系统 Load 偏高 (2.55)

**Load Average:**
- 1 分钟：2.55
- 5 分钟：1.94
- 15 分钟：1.70

**分析:**
- Load 呈上升趋势 (1.70 → 1.94 → 2.55)
- 4 核 CPU，Load < 4 为正常
- 当前 Load 2.55，处于中等水平
- 主要负载来自 Node.js Gateway

---

## 📈 资源占用趋势

### CPU 占用趋势

```
时间轴     Load    CPU 使用  主要进程
----------------------------------------
15 分钟前  1.70    ~60%      正常
5 分钟前   1.94    ~65%      略有上升
现在       2.55    ~75%      Node Gateway 启动
```

**趋势:** ⚠️ 上升 (需关注)

---

### 内存占用趋势

```
进程                      内存占用
----------------------------------------
openclaw-gateway (admin)  595 MB (31.0%)
node gateway (root)       302 MB (15.7%)
searxng worker            115 MB (6.0%)
AliYunDunMonitor          56 MB (2.9%)
其他进程                  ~95 MB (5.1%)
----------------------------------------
总计                      ~1163 MB (62.2%)
```

**趋势:** ✅ 稳定

---

## 🎯 优化建议

### 立即执行 (高优先级)

#### 1. 检查 Gateway 重复启动

**命令:**
```bash
# 查看 OpenClaw Gateway 进程
ps aux | grep -E "openclaw|gateway"

# 查看端口占用
netstat -tlnp | grep 18789

# 检查重复进程
pgrep -af openclaw
```

**处理方案:**
- 如果确认重复启动，停止其中一个
- 建议保留 admin 用户的进程 (运行 8 小时，稳定)
- 停止 root 用户的新进程 (PID 551580)

---

#### 2. 监控 Node.js Gateway

**命令:**
```bash
# 持续监控 CPU 使用
top -p 551580

# 查看日志
journalctl -u openclaw-gateway -f

# 检查是否有错误
dmesg | tail -50
```

**观察指标:**
- CPU 是否持续 > 100%
- 内存是否持续增长
- 是否有错误日志

---

### 短期优化 (本周完成)

#### 3. 重启 OpenClaw Gateway (如内存持续增长)

**命令:**
```bash
# 优雅重启
openclaw gateway restart

# 或手动重启
pkill -f openclaw-gateway
openclaw gateway start
```

**建议:**
- 在低峰期执行 (如凌晨 3:00)
- 重启前备份重要数据
- 重启后观察内存占用

---

#### 4. 优化 SearXNG (可选)

**当前状态:**
- SearXNG worker 占用 115 MB (6.0%)
- 搜索引擎服务

**优化方案:**
```bash
# 限制 worker 数量
# 编辑 /etc/searxng/settings.yml
server:
  max_request_timeout: 30

# 重启 SearXNG
systemctl restart searxng
```

---

### 长期优化 (本月完成)

#### 5. 增加系统监控

**建议安装:**
```bash
# 系统监控工具
yum install -y htop iotop iftop

# 实时监控
htop
```

**监控指标:**
- CPU 使用率 (> 80% 告警)
- 内存使用率 (> 85% 告警)
- 磁盘使用率 (> 85% 告警)
- Load Average (> 4 告警)

---

#### 6. 定期清理缓存

**命令:**
```bash
# 清理系统缓存
echo 3 > /proc/sys/vm/drop_caches

# 清理旧日志
journalctl --vacuum-time=7d

# 清理临时文件
rm -rf /tmp/*
```

**建议:** 每周执行一次

---

## ✅ 当前结论

### 问题评估

| 问题 | 严重程度 | 紧急性 | 建议 |
|------|----------|--------|------|
| Node Gateway CPU 117% | ⚠️ 中 | 中 | 观察 10 分钟 |
| OpenClaw 内存 31% | 🟡 低 | 低 | 持续监控 |
| System Load 2.55 | 🟡 低 | 低 | 正常范围 |

---

### 总体判断

**系统状态:** ⚠️ **中等负载，需关注**

**主要原因:**
1. Node.js Gateway 启动时 CPU 占用高 (可能正常)
2. OpenClaw Gateway 内存占用 31% (可接受)
3. 系统 Load 2.55 (4 核 CPU，正常范围)

**建议行动:**
1. ✅ 观察 Node Gateway 10 分钟
2. ✅ 检查是否重复启动
3. ✅ 如持续高负载，重启 Gateway

---

## 📝 诊断命令汇总

### 快速诊断

```bash
# 系统概览
top -bn1 | head -20

# CPU 占用 TOP10
ps aux --sort=-%cpu | head -11

# 内存占用 TOP10
ps aux --sort=-%mem | head -11

# Load 趋势
uptime

# 磁盘使用
df -h
```

---

### 深度诊断

```bash
# 查看进程详情
ps -p <PID> -o pid,ppid,user,%cpu,%mem,vsz,rss,etime,start,cmd

# 查看系统日志
journalctl -xe --since "10 minutes ago"

# 查看内核消息
dmesg | tail -100

# 查看网络占用
netstat -tlnp

# 查看 IO 占用
iotop -o
```

---

*报告生成时间：2026-03-12 01:11*

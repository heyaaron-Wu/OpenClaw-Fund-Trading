#!/usr/bin/env python3.11
"""
基金挑战系统配置文件
统一管理所有配置项
"""

from pathlib import Path

# ==================== 路径配置 ====================
BASE_DIR = Path('/home/admin/.openclaw/workspace/Semi-automatic-artificial-intelligence-system')
DATA_DIR = BASE_DIR / '08-fund-daily-review'
STATE_FILE = DATA_DIR / 'state.json'
LEDGER_FILE = DATA_DIR / 'ledger.jsonl'
REVIEWS_DIR = DATA_DIR / 'reviews'
DECISION_DIR = DATA_DIR / 'decision_records'

# ==================== 飞书配置 ====================
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/f1286a3e-4e41-4809-a0bc-fd2bbbbc3f10"

# ==================== Git 配置 ====================
GIT_BRANCH = "OpenClaw-Fund-Trading"
GIT_REMOTE = "origin"

# ==================== 定时任务配置 ====================
TRADING_DAYS = "1-5"  # 周一至周五
DAILY_CHECK_TIME = "0 9"  # 09:00
UNIVERSE_TIME = "35 13"  # 13:35
DECISION_TIME = "0 14"  # 14:00
EXEC_GATE_TIME = "48 14"  # 14:48
REVIEW_TIME = "30 22"  # 22:30

# ==================== 数据校验配置 ====================
VALIDATION_THRESHOLD = 0.01  # 允许的误差范围（元）
ENABLE_VALIDATION = True  # 是否启用数据校验

# ==================== 备份配置 ====================
BACKUP_DIR = DATA_DIR / 'backups'
BACKUP_RETENTION_DAYS = 30  # 备份保留天数
ENABLE_AUTO_BACKUP = True  # 是否启用自动备份

# ==================== 日志配置 ====================
LOG_DIR = Path('/tmp/openclaw')
LOG_RETENTION_DAYS = 30  # 日志保留天数
LOG_LEVEL = "INFO"  # 日志级别：DEBUG, INFO, WARNING, ERROR

# ==================== 性能配置 ====================
REQUEST_TIMEOUT = 10  # HTTP 请求超时时间（秒）
MAX_RETRIES = 3  # 最大重试次数
RETRY_DELAY = 2  # 重试延迟（秒）

# ==================== 其他配置 ====================
INITIAL_CAPITAL = 1000.0  # 初始资金（元）
TARGET_AMOUNT = 1300.0  # 挑战目标（元）
TARGET_RETURN = 0.30  # 目标收益率（30%）

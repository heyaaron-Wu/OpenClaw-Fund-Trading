#!/usr/bin/env python3
"""
README 智能同步脚本
功能：根据系统实际配置自动更新 README.md 中的相关内容
- 定时任务列表（从 cron/jobs.json 读取）
- 脚本清单（从文件系统扫描）
- 版本号（从 CHANGELOG.md 读取）
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime

WORKSPACE = Path('/home/admin/.openclaw/workspace/Semi-automatic-artificial-intelligence-system')
CRON_CONFIG = Path('/home/admin/.openclaw/cron/jobs.json')
CHANGELOG = WORKSPACE / '07-version-updates' / 'CHANGELOG.md'


def get_latest_version():
    """从 CHANGELOG.md 获取最新版本号"""
    if not CHANGELOG.exists():
        return None
    
    content = CHANGELOG.read_text(encoding='utf-8')
    match = re.search(r'^## v(\d+\.\d+\.\d+)\s*-\s*\d{4}-\d{2}-\d{2}', content, re.MULTILINE)
    return f'v{match.group(1)}' if match else None


def get_cron_tasks():
    """从 cron/jobs.json 读取定时任务列表"""
    if not CRON_CONFIG.exists():
        return []
    
    data = json.loads(CRON_CONFIG.read_text(encoding='utf-8'))
    tasks = []
    
    for job in data.get('jobs', []):
        tasks.append({
            'name': job.get('name', ''),
            'schedule': job.get('schedule', {}).get('expr', ''),
            'description': job.get('description', ''),
            'notify_on': job.get('notify_on', [])
        })
    
    # 按类型排序：system 在前，fund 在后
    system_tasks = [t for t in tasks if t['name'].startswith('system') or t['name'].startswith('cron')]
    fund_tasks = [t for t in tasks if t['name'].startswith('fund')]
    
    return system_tasks + fund_tasks


def generate_task_table(tasks):
    """生成定时任务表格 Markdown"""
    lines = [
        "| 任务名 | 时间 | 作用 | 推送策略 |",
        "|------|------|------|----------|"
    ]
    
    for task in tasks:
        name = task['name']
        schedule = task['schedule']
        desc = task['description'].replace('\n', ' ')[:80]  # 限制长度
        notify = ', '.join(task['notify_on']) if task['notify_on'] else 'none'
        
        lines.append(f"| {name} | {schedule} | {desc} | {notify} |")
    
    return '\n'.join(lines)


def get_script_list():
    """扫描脚本文件生成清单"""
    scripts_dir = WORKSPACE / 'skills' / 'fund-challenge' / 'fund_challenge' / 'scripts'
    if not scripts_dir.exists():
        return []
    
    scripts = []
    for py_file in scripts_dir.glob('*.py'):
        if py_file.name.startswith('__'):
            continue
        
        # 读取文件第一行作为描述
        content = py_file.read_text(encoding='utf-8', errors='ignore')
        first_line = content.split('\n')[0].replace('#', '').strip()
        
        scripts.append({
            'name': py_file.name,
            'description': first_line[:60]
        })
    
    return sorted(scripts, key=lambda x: x['name'])


def generate_script_table(scripts):
    """生成脚本清单表格 Markdown"""
    lines = [
        "| 脚本名 | 作用 |",
        "|------|------|"
    ]
    
    for script in scripts:
        lines.append(f"| `{script['name']}` | {script['description']} |")
    
    return '\n'.join(lines)


def update_readme_section(content, marker_start, marker_end, new_content):
    """更新 README 中两个标记之间的内容"""
    pattern = re.compile(
        f'(<!-- {marker_start} -->)(.*?)(<!-- {marker_end} -->)',
        re.DOTALL
    )
    
    replacement = f'<!-- {marker_start} -->\n\n{new_content}\n\n<!-- {marker_end} -->'
    
    if pattern.search(content):
        return pattern.sub(replacement, content)
    else:
        # 如果没有找到标记，在文件末尾添加
        return content + f'\n\n<!-- {marker_start} -->\n\n{new_content}\n\n<!-- {marker_end} -->'


def main():
    print("🔄 智能同步 README 内容...")
    
    readme_path = WORKSPACE / 'README.md'
    if not readme_path.exists():
        print("  ❌ README.md 不存在")
        return 1
    
    content = readme_path.read_text(encoding='utf-8')
    updated = False
    
    # 1. 更新版本号
    version = get_latest_version()
    if version:
        old_content = content
        content = re.sub(
            r'\*\*当前版本：v\d+\.\d+\.\d+\*\*',
            f'**当前版本：{version}**',
            content
        )
        if content != old_content:
            print(f"  ✅ 版本号已更新：{version}")
            updated = True
    
    # 2. 更新定时任务列表
    tasks = get_cron_tasks()
    if tasks:
        task_table = generate_task_table(tasks)
        old_content = content
        content = update_readme_section(
            content,
            'START CRON TASKS',
            'END CRON TASKS',
            task_table
        )
        if content != old_content:
            print(f"  ✅ 定时任务列表已更新（{len(tasks)} 个任务）")
            updated = True
    
    # 3. 更新脚本清单
    scripts = get_script_list()
    if scripts:
        script_table = generate_script_table(scripts)
        old_content = content
        content = update_readme_section(
            content,
            'START SCRIPTS',
            'END SCRIPTS',
            script_table
        )
        if content != old_content:
            print(f"  ✅ 脚本清单已更新（{len(scripts)} 个脚本）")
            updated = True
    
    # 4. 更新日期
    today = datetime.now().strftime('%Y-%m-%d')
    old_content = content
    content = re.sub(
        r'\*\*最后更新：\d{4}-\d{2}-\d{2}\*\*',
        f'**最后更新：{today}**',
        content
    )
    if content != old_content:
        print(f"  ✅ 最后更新日期：{today}")
        updated = True
    
    if updated:
        readme_path.write_text(content, encoding='utf-8')
        print("  ✅ README.md 已更新")
        return 0
    else:
        print("  ℹ️  README.md 无需更新")
        return 0


if __name__ == '__main__':
    sys.exit(main())

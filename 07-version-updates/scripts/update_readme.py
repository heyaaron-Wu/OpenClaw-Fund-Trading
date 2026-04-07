#!/usr/bin/env python3
"""
README 自动更新脚本
功能：根据 CHANGELOG.md 自动更新 README.md 中的版本号和相关文档
"""

import sys
import re
from pathlib import Path
from datetime import datetime

WORKSPACE = Path('/home/admin/.openclaw/workspace/Semi-automatic-artificial-intelligence-system')

def get_latest_version():
    """从 CHANGELOG.md 获取最新版本号"""
    changelog_path = WORKSPACE / '07-version-updates' / 'CHANGELOG.md'
    if not changelog_path.exists():
        return None
    
    content = changelog_path.read_text(encoding='utf-8')
    # 匹配版本号格式：## vX.Y.Z - YYYY-MM-DD
    match = re.search(r'^## v(\d+\.\d+\.\d+)\s*-\s*\d{4}-\d{2}-\d{2}', content, re.MULTILINE)
    if match:
        return f'v{match.group(1)}'
    return None


def update_readme_version(readme_path, version):
    """更新 README.md 中的版本号"""
    if not readme_path.exists():
        print(f"  ℹ️  {readme_path} 不存在，跳过")
        return False
    
    content = readme_path.read_text(encoding='utf-8')
    
    # 尝试更新"当前版本：vX.Y.Z"格式
    if '当前版本：' in content:
        old_content = content
        content = re.sub(r'当前版本：v\d+\.\d+\.\d+', f'当前版本：{version}', content)
        if content != old_content:
            readme_path.write_text(content, encoding='utf-8')
            print(f"  ✅ 版本号已更新：{version}")
            return True
        else:
            print(f"  ℹ️  版本号已是最新：{version}")
            return False
    else:
        print(f"  ℹ️  README.md 无版本号字段，跳过")
        return False


def update_file_structure():
    """更新 FILE_STRUCTURE.md 的更新时间"""
    fs_path = WORKSPACE / '03-system-docs' / 'FILE_STRUCTURE.md'
    if not fs_path.exists():
        return False
    
    content = fs_path.read_text(encoding='utf-8')
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 更新时间戳
    if '最后更新：' in content:
        old_content = content
        content = re.sub(r'最后更新：\d{4}-\d{2}-\d{2}', f'最后更新：{today}', content)
        if content != old_content:
            fs_path.write_text(content, encoding='utf-8')
            print(f"  ✅ FILE_STRUCTURE.md 已更新时间")
            return True
    
    return False


def update_cron_config():
    """更新 CRON_CONFIG.md 的更新时间"""
    cron_path = WORKSPACE / '07-version-updates' / 'CRON_CONFIG.md'
    if not cron_path.exists():
        return False
    
    content = cron_path.read_text(encoding='utf-8')
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 更新时间戳
    if '最后更新：' in content:
        old_content = content
        content = re.sub(r'最后更新：\d{4}-\d{2}-\d{2}', f'最后更新：{today}', content)
        if content != old_content:
            cron_path.write_text(content, encoding='utf-8')
            print(f"  ✅ CRON_CONFIG.md 已更新时间")
            return True
    
    return False


def main():
    print("🔄 自动更新 README 及相关文档...")
    
    # 1. 获取最新版本号
    version = get_latest_version()
    if not version:
        print("  ⚠️  无法获取最新版本号")
        return 1
    
    print(f"  📊 最新版本：{version}")
    
    # 2. 更新主 README.md
    readme_path = WORKSPACE / 'README.md'
    update_readme_version(readme_path, version)
    
    # 3. 更新 08-fund-daily-review/README.md
    fund_readme_path = WORKSPACE / '08-fund-daily-review' / 'README.md'
    update_readme_version(fund_readme_path, version)
    
    # 4. 更新 FILE_STRUCTURE.md
    update_file_structure()
    
    # 5. 更新 CRON_CONFIG.md
    update_cron_config()
    
    print("  ✅ 文档检查完成")
    return 0


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3.11
"""
基金公告监控
每日 09:00 执行，监控基金公告

功能:
1. 获取基金公告 (分红、经理变更、规模变动)
2. 分析公告影响
3. 生成监控报告
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# 导入 Iwencai 集成模块
sys.path.insert(0, '/home/admin/.openclaw/workspace/05-scripts')
try:
    from iwencai_skill_integration import IwencaiSkillIntegration
    HAS_IWENCAI = True
except ImportError:
    HAS_IWENCAI = False

# 配置
WORKSPACE = Path('/home/admin/.openclaw/workspace')
OUTPUT_PATH = WORKSPACE / '06-data' / 'announcement_monitor.json'

# 监控基金
FUNDS = [
    {'code': '011612', 'name': '华夏科创 50ETF 联接 A'},
    {'code': '013180', 'name': '广发新能源车电池 ETF 联接 C'},
    {'code': '014320', 'name': '德邦半导体产业混合 C'},
]


def check_announcements():
    """检查基金公告"""
    print("\n📑 检查基金公告...")
    
    results = []
    
    for fund in FUNDS:
        try:
            # 查询基金公告
            query = f"{fund['name']} 基金公告 分红 经理变更"
            data = integration._api_call(query, limit=5)
            
            if data and data.get('datas'):
                announcements = []
                for item in data['datas'][:5]:
                    title = item.get('标题', item.get('公告标题', ''))
                    if title:
                        announcements.append(title)
                
                results.append({
                    'code': fund['code'],
                    'name': fund['name'],
                    'announcements': announcements,
                    'count': len(announcements)
                })
                
                print(f"   ✅ {fund['name']}: {len(announcements)}条公告")
            else:
                results.append({
                    'code': fund['code'],
                    'name': fund['name'],
                    'announcements': [],
                    'count': 0
                })
                print(f"   ⚪ {fund['name']}: 无公告")
                
        except Exception as e:
            print(f"   ❌ {fund['name']}: {e}")
            results.append({
                'code': fund['code'],
                'name': fund['name'],
                'announcements': [],
                'count': 0,
                'error': str(e)
            })
    
    return results


def generate_report(announcement_data):
    """生成公告监控报告"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'announcement_data': announcement_data,
        'summary': {
            'total_funds': len(announcement_data),
            'total_announcements': sum(a['count'] for a in announcement_data),
            'funds_with_announcements': sum(1 for a in announcement_data if a['count'] > 0)
        }
    }
    
    return report


def main():
    """主流程"""
    print("=" * 50)
    print("  基金公告监控")
    print("  " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 50)
    
    # 1. 初始化 Iwencai
    global integration
    integration = None
    if HAS_IWENCAI:
        try:
            integration = IwencaiSkillIntegration()
            print("\n✅ Iwencai 集成器已初始化")
        except Exception as e:
            print(f"\n⚠️  Iwencai 初始化失败：{e}")
    
    # 2. 检查公告
    if integration:
        announcement_data = check_announcements()
    else:
        print("\n⚠️  Iwencai 不可用")
        announcement_data = []
    
    # 3. 生成报告
    report = generate_report(announcement_data)
    
    # 4. 保存结果
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\n💾 公告监控已保存：{OUTPUT_PATH}")
    
    # 5. 总结
    print("\n" + "=" * 50)
    print("  公告监控完成")
    print("=" * 50)
    print(f"\n📊 公告汇总:")
    print(f"   监控基金：{report['summary']['total_funds']}只")
    print(f"   公告总数：{report['summary']['total_announcements']}条")
    print(f"   有公告基金：{report['summary']['funds_with_announcements']}只")
    
    print("\n✅ 公告监控完成！")
    return report


if __name__ == '__main__':
    main()

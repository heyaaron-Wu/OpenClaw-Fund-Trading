#!/usr/bin/env python3.11
"""
基金估值分位监控
每周一 08:00 执行，监控基金估值分位

功能:
1. 获取基金估值数据 (PE/PB)
2. 计算估值分位 (历史百分位)
3. 判断估值状态 (低估/正常/高估)
4. 生成估值报告
"""

import json
from datetime import datetime
from pathlib import Path

try:
    import akshare as ak
    HAS_AKSHARE = True
except ImportError:
    HAS_AKSHARE = False

# 配置
WORKSPACE = Path('/home/admin/.openclaw/workspace')
OUTPUT_PATH = WORKSPACE / '06-data' / 'valuation_monitor.json'

# 监控指数
INDICES = [
    {'code': '000300', 'name': '沪深 300', 'pe_low': 10, 'pe_high': 15},
    {'code': '399006', 'name': '创业板指', 'pe_low': 30, 'pe_high': 50},
    {'code': '000688', 'name': '科创 50', 'pe_low': 30, 'pe_high': 60},
]


def get_index_valuation():
    """获取指数估值数据"""
    print("\n📊 获取指数估值数据...")
    
    results = []
    
    for index in INDICES:
        try:
            # 获取指数 PE/PB 数据
            df = ak.index_zh_a_hist_min_em(symbol=index['code'], period="1day")
            
            if df is not None and not df.empty:
                latest = df.iloc[0]
                current_pe = latest.get('pe', 0)
                current_pb = latest.get('pb', 0)
                
                # 计算估值分位
                pe_range = index['pe_high'] - index['pe_low']
                if pe_range > 0:
                    pe_percentile = (current_pe - index['pe_low']) / pe_range * 100
                else:
                    pe_percentile = 50
                
                # 判断估值状态
                if pe_percentile < 30:
                    status = '低估'
                elif pe_percentile > 70:
                    status = '高估'
                else:
                    status = '正常'
                
                results.append({
                    'name': index['name'],
                    'code': index['code'],
                    'current_pe': current_pe,
                    'current_pb': current_pb,
                    'pe_percentile': round(pe_percentile, 1),
                    'status': status
                })
                
                print(f"   ✅ {index['name']}: PE={current_pe:.2f}, 分位={pe_percentile:.1f}%, {status}")
            else:
                print(f"   ⚠️  {index['name']}: 数据获取失败")
                
        except Exception as e:
            print(f"   ❌ {index['name']}: {e}")
    
    return results


def generate_report(valuation_data):
    """生成估值监控报告"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'valuation_data': valuation_data,
        'summary': {
            'total': len(valuation_data),
            'undervalued': sum(1 for v in valuation_data if v['status'] == '低估'),
            'normal': sum(1 for v in valuation_data if v['status'] == '正常'),
            'overvalued': sum(1 for v in valuation_data if v['status'] == '高估')
        }
    }
    
    return report


def main():
    """主流程"""
    print("=" * 50)
    print("  基金估值分位监控")
    print("  " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 50)
    
    # 1. 获取估值数据
    if HAS_AKSHARE:
        valuation_data = get_index_valuation()
    else:
        print("\n⚠️  AKShare 不可用")
        valuation_data = []
    
    # 2. 生成报告
    report = generate_report(valuation_data)
    
    # 3. 保存结果
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\n💾 估值监控已保存：{OUTPUT_PATH}")
    
    # 4. 总结
    print("\n" + "=" * 50)
    print("  估值监控完成")
    print("=" * 50)
    print(f"\n📊 估值汇总:")
    print(f"   总计：{report['summary']['total']}个指数")
    print(f"   低估：{report['summary']['undervalued']}个")
    print(f"   正常：{report['summary']['normal']}个")
    print(f"   高估：{report['summary']['overvalued']}个")
    
    print("\n✅ 估值监控完成！")
    return report


if __name__ == '__main__':
    main()

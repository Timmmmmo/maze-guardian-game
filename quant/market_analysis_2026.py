"""
2026年A股市场分析简报
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r'C:\Users\赵鸿杰\.openclaw\agents\game-studio\quant')

from data_source import get_realtime, get_hist_with_retry
from datetime import datetime

# 主要指数
INDICES = ['000001', '399001', '399006', '000300', '000016', '000905']

# 热门板块代表股
SECTORS = {
    'AI人工智能': ['300033', '002230', '300496'],  # 同花顺、科大讯飞、中科创达
    '新能源': ['300750', '002594', '600519'],       # 宁德时代、比亚迪、贵州茅台
    '半导体': ['603986', '002049', '300661'],       # 兆易创新、紫光国微、圣邦股份
    '医药': ['300760', '000538', '002007'],         # 迈瑞医疗、云南白药、华大基因
    '金融': ['600036', '601318', '601166'],         # 招商银行、中国平安、兴业银行
}

def main():
    print("=" * 60)
    print("📊 2026年A股市场分析简报")
    print(f"   生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    # 1. 主要指数
    print("\n【一、主要指数表现】")
    print("-" * 50)
    indices_data = get_realtime(INDICES)
    
    index_names = {
        '000001': '上证指数',
        '399001': '深证成指',
        '399006': '创业板指',
        '000300': '沪深300',
        '000016': '上证50',
        '000905': '中证500',
    }
    
    for code in INDICES:
        if code in indices_data:
            d = indices_data[code]
            name = index_names.get(code, d['name'])
            chg_sign = '+' if d['chg'] >= 0 else ''
            print(f"  {name:8} {d['current']:>8.2f}  {chg_sign}{d['chg_pct']:>6.2f}%")
    
    # 2. 热门板块
    print("\n【二、热门板块表现】")
    print("-" * 50)
    
    for sector, stocks in SECTORS.items():
        data = get_realtime(stocks)
        if data:
            avg_chg = sum(d['chg_pct'] for d in data.values()) / len(data)
            chg_sign = '+' if avg_chg >= 0 else ''
            print(f"  {sector:12} 板块均涨: {chg_sign}{avg_chg:.2f}%")
            for code, d in data.items():
                sign = '+' if d['chg_pct'] >= 0 else ''
                print(f"    └ {d['name']:8} {d['current']:>8.2f} {sign}{d['chg_pct']:>6.2f}%")
    
    # 3. 市场分析
    print("\n【三、2026年市场分析】")
    print("-" * 50)
    
    # 获取上证指数历史数据
    hist = get_hist_with_retry('000001', days=60)
    if hist and hist['close']:
        closes = hist['close']
        current = closes[-1]
        ma20 = sum(closes[-20:]) / 20
        ma60 = sum(closes) / 60
        
        print(f"  上证指数技术分析:")
        print(f"    当前点位: {current:.2f}")
        print(f"    20日均线: {ma20:.2f} {'↑多头排列' if current > ma20 else '↓空头排列'}")
        print(f"    60日均线: {ma60:.2f} {'↑中期向上' if current > ma60 else '↓中期向下'}")
        
        # 近期涨跌幅
        chg_5d = (current - closes[-5]) / closes[-5] * 100
        chg_20d = (current - closes[-20]) / closes[-20] * 100
        print(f"    近5日涨跌: {'+' if chg_5d >= 0 else ''}{chg_5d:.2f}%")
        print(f"    近20日涨跌: {'+' if chg_20d >= 0 else ''}{chg_20d:.2f}%")
    
    print("\n【四、投资建议】")
    print("-" * 50)
    print("  • 市场整体处于震荡格局，建议控制仓位")
    print("  • AI、半导体板块持续活跃，可关注回调机会")
    print("  • 新能源板块估值回落，中长期布局价值显现")
    print("  • 金融板块估值偏低，适合稳健配置")
    
    print("\n" + "=" * 60)
    print("  数据来源: 新浪财经  |  Model: Claude Opus")
    print("=" * 60)

if __name__ == '__main__':
    main()

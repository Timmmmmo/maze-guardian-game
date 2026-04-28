"""
今日A股市场分析
"""
import sys
sys.path.insert(0, r"C:\Users\赵鸿杰\.openclaw\agents\game-studio\quant")

import requests
import re
from datetime import datetime

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://finance.sina.com.cn'
}

INDEX_CODES = {
    'sh000001': '上证指数',
    'sh399001': '深证成指',
    'sh399006': '创业板指',
    'sh000300': '沪深300',
    'sh000905': '中证500',
    'sh000016': '上证50',
    'sh000688': '科创50',
}

def get_quotes(codes):
    url = f"http://hq.sinajs.cn/list={','.join(codes)}"
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.encoding = 'gbk'
    return r.text

def parse_index(raw, name, code_raw):
    m = re.search(rf'hq_str_{code_raw}="(.+)"', raw)
    if not m:
        return None
    fields = m.group(1).split(',')
    current = float(fields[1])
    close_prev = float(fields[2])
    open_p = float(fields[3])
    high = float(fields[4])
    low = float(fields[5])
    vol = float(fields[8]) if len(fields) > 8 else 0
    change = current - close_prev
    pct = (change / close_prev) * 100
    return {
        'name': name,
        'current': current,
        'change': change,
        'pct': pct,
        'open': open_p,
        'high': high,
        'low': low,
        'vol': vol,
        'close_prev': close_prev
    }

# 1. 获取主要指数
print("=" * 60)
print(f"📊 今日A股市场分析 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print("=" * 60)

raw = get_quotes(list(INDEX_CODES.keys()))
results = {}
for code, name in INDEX_CODES.items():
    r = parse_index(raw, name, code)
    if r:
        results[code] = r

print("\n【主要指数】")
print(f"{'指数':<10} {'最新':>10} {'涨跌额':>10} {'涨跌幅':>8} {'最高':>10} {'最低':>10}")
print("-" * 60)
for code, d in results.items():
    emoji = "🔴" if d['pct'] > 0 else "🟢"
    print(f"{emoji}{d['name']:<8} {d['current']:>10.2f} {d['change']:>+10.2f} {d['pct']:>+7.2f}% {d['high']:>10.2f} {d['low']:>10.2f}")

# 2. 涨跌家数
print("\n【市场宽度】")
try:
    breadth_url = "http://hq.sinajs.cn/list=s_sh000001"
    br = requests.get(breadth_url, headers=HEADERS, timeout=10)
    br.encoding = 'gbk'
    # 个股涨跌家数通常在东方财富等
    up_df_url = "http://push2.eastmoney.com/api/qt/stock/get?ut=fa5fd1943c7b386f172d6893dbfba10b&fltt=2&invt=2&fields=f43,f169,f170,f171,f57,f58&secid=1.000001&_=1"
    print("  数据获取中...")
except Exception as e:
    print(f"  无法获取涨跌家数: {e}")

# 3. 板块/行业涨跌
print("\n【行业板块涨跌TOP】")
try:
    # 用新浪行业板块排行
    ind_url = "http://vip.stock.finance.sina.com.cn/q/view/newFLJK.php?param=class"
    ir = requests.get(ind_url, headers=HEADERS, timeout=10)
    ir.encoding = 'gbk'
    print(f"  获取到 {len(ir.text)} 字节数据")
except Exception as e:
    print(f"  行业数据获取失败: {e}")

# 4. 北向资金
print("\n【北向资金】")
try:
    # 东方财富北向资金
    bx_url = "http://push2.eastmoney.com/api/qt/kamtop/get?fltt=2&invt=2&fields=f1,f2,f3,f4,f5&ut=b2884a393a59ad64002292a3e90d46a5"
    bx = requests.get(bx_url, headers=HEADERS, timeout=10)
    print(f"  {bx.text[:200]}")
except Exception as e:
    print(f"  北向资金获取失败: {e}")

# 5. 自选股池
WATCH = [
    ('sh600519', '贵州茅台'),
    ('sh601318', '中国平安'),
    ('sh300750', '宁德时代'),
    ('sh002594', '比亚迪'),
    ('sh000762', '西藏矿业'),
    ('sh603773', '沃格光电'),
    ('sh600552', '凯盛科技'),
]

print("\n【自选股池】")
raw2 = get_quotes([c for c, _ in WATCH])
for code, name in WATCH:
    m = re.search(rf'hq_str_{code}="(.+)"', raw2)
    if m:
        f = m.group(1).split(',')
        try:
            current = float(f[3])
            close_prev = float(f[2])
            high = float(f[4])
            low = float(f[5])
            vol = float(f[8]) / 100 if len(f) > 8 else 0
            change = current - close_prev
            pct = (change / close_prev) * 100
            emoji = "🔴" if pct > 0 else "🟢"
            print(f"  {emoji}{name}({code[2:]}): {current:.2f} {pct:+.2f}% | 量:{vol:.0f}万手")
        except:
            print(f"  ⚠️{name}: 数据解析失败")

print("\n" + "=" * 60)

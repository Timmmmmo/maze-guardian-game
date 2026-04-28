#!/usr/bin/env python3
"""
A股简报生成器 - 增强版
优先网络获取，失败则使用缓存
"""
import sys
import json
from pathlib import Path
from datetime import datetime

# 确保UTF-8
sys.stdout.reconfigure(encoding='utf-8')

CACHE_FILE = Path(__file__).parent / "data" / "stock_cache.json"

def load_cache():
    """加载缓存"""
    if CACHE_FILE.exists():
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def fetch_live_data():
    """尝试获取实时数据"""
    try:
        import akshare as ak
        df = ak.stock_zh_a_spot_em()
        
        stocks = []
        for _, row in df.head(20).iterrows():
            stocks.append({
                "code": str(row['代码']),
                "name": str(row['名称']),
                "price": float(row['最新价']) if row['最新价'] else 0,
                "change": float(row['涨跌幅']) if row['涨跌幅'] else 0
            })
        
        # 获取指数
        indices = []
        try:
            idx = ak.index_zh_a_hist(symbol="000001", period="daily", 
                start_date=datetime.now().strftime('%Y%m%d'),
                end_date=datetime.now().strftime('%Y%m%d'))
            if not idx.empty:
                indices.append({"name": "上证指数", "value": float(idx.iloc[-1]['收盘']), "change_pct": float(idx.iloc[-1]['涨跌幅'])})
        except: pass
        
        try:
            idx = ak.index_zh_a_hist(symbol="399001", period="daily",
                start_date=datetime.now().strftime('%Y%m%d'),
                end_date=datetime.now().strftime('%Y%m%d'))
            if not idx.empty:
                indices.append({"name": "深证成指", "value": float(idx.iloc[-1]['收盘']), "change_pct": float(idx.iloc[-1]['涨跌幅'])})
        except: pass
        
        return {"stocks": stocks, "indices": indices, "source": "akshare", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return {"error": str(e)[:50]}

def generate_brief():
    """生成简报"""
    # 尝试获取实时数据
    live_data = fetch_live_data()
    
    # 如果失败，使用缓存
    data = None
    is_cached = False
    if "error" in live_data:
        cache = load_cache()
        if cache:
            data = cache
            is_cached = True
    else:
        data = live_data
    
    if not data:
        return "📊 A股简报\n❌ 无数据，请检查网络"
    
    # 排序获取涨跌榜
    stocks = data.get("stocks", [])
    if stocks:
        sorted_stocks = sorted(stocks, key=lambda x: x.get("change", 0), reverse=True)
        top_gainers = sorted_stocks[:3]
        top_losers = sorted_stocks[-3:][::-1]
    else:
        top_gainers = []
        top_losers = []
    
    indices = data.get("indices", [])
    
    # 生成简报
    lines = []
    lines.append("📊 A股20分钟简报")
    lines.append("=" * 40)
    lines.append(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
    if is_cached:
        lines.append("⚠️ 缓存数据，可能有延迟")
    lines.append("")
    
    # 指数
    if indices:
        lines.append("【指数】")
        for idx in indices:
            emoji = "📈" if idx.get("change_pct", 0) >= 0 else "📉"
            lines.append(f"{emoji} {idx.get('name', '')}: {idx.get('value', 0):.2f} ({idx.get('change_pct', 0):+.2f}%)")
        lines.append("")
    
    # 涨幅
    if top_gainers:
        lines.append("【🔥 涨幅TOP3】")
        for i, s in enumerate(top_gainers, 1):
            lines.append(f"{i}. {s.get('name', '')}: {s.get('price', 0):.2f} +{s.get('change', 0):.2f}%")
        lines.append("")
    
    # 跌幅
    if top_losers:
        lines.append("【❄️ 跌幅TOP3】")
        for i, s in enumerate(top_losers, 1):
            lines.append(f"{i}. {s.get('name', '')}: {s.get('price', 0):.2f} {s.get('change', 0):.2f}%")
        lines.append("")
    
    lines.append(f"💡 来源: {data.get('source', 'unknown')}")
    
    return "\n".join(lines)

if __name__ == "__main__":
    print(generate_brief())
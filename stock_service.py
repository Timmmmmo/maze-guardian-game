#!/usr/bin/env python3
"""
A股数据服务 - 整合akshare实时行情 + 本地缓存
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 缓存文件路径
CACHE_DIR = Path(__file__).parent / "data"
CACHE_FILE = CACHE_DIR / "stock_cache.json"

def ensure_cache_dir():
    """确保缓存目录存在"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

def load_cache():
    """加载缓存数据"""
    if CACHE_FILE.exists():
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"last_update": None, "stocks": [], "indices": []}

def save_cache(data):
    """保存缓存数据"""
    ensure_cache_dir()
    data["last_update"] = datetime.now().isoformat()
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def fetch_realtime_data():
    """从akshare获取实时数据"""
    try:
        import akshare as ak
        
        # 获取A股实时行情
        df = ak.stock_zh_a_spot_em()
        
        # 获取主要指数
        indices = []
        for symbol, name in [('000001', '上证指数'), ('399001', '深证成指'), ('399006', '创业板指')]:
            try:
                idx_df = ak.index_zh_a_hist(symbol=symbol, period='daily', 
                    start_date=datetime.now().strftime('%Y%m%d'),
                    end_date=datetime.now().strftime('%Y%m%d'))
                if not idx_df.empty:
                    latest = idx_df.iloc[-1]
                    indices.append({
                        "name": name,
                        "value": float(latest['收盘']),
                        "change": float(latest['涨跌幅'])
                    })
            except:
                pass
        
        # 格式化股票数据
        stocks = []
        for _, row in df.head(20).iterrows():
            stocks.append({
                "code": row['代码'],
                "name": row['名称'],
                "price": float(row['最新价']),
                "change": float(row['涨跌幅']),
                "volume": row['成交量'],
                "amount": row['成交额']
            })
        
        return {"stocks": stocks, "indices": indices}
    except Exception as e:
        print(f"获取实时数据失败: {e}", file=sys.stderr)
        return None

def update_cache():
    """更新缓存"""
    data = fetch_realtime_data()
    if data:
        save_cache(data)
        return True
    return False

def get_stock_quote(code=None, name=None):
    """获取个股行情"""
    cache = load_cache()
    
    for stock in cache.get("stocks", []):
        if code and stock["code"] == code:
            return stock
        if name and name in stock["name"]:
            return stock
    return None

def get_market_overview():
    """获取市场概览"""
    cache = load_cache()
    return {
        "indices": cache.get("indices", []),
        "top_gainers": sorted(cache.get("stocks", []), 
            key=lambda x: x.get("change", 0), reverse=True)[:5],
        "top_losers": sorted(cache.get("stocks", []), 
            key=lambda x: x.get("change", 0))[:5],
        "last_update": cache.get("last_update")
    }

def format_output(data, output_type="text"):
    """格式化输出"""
    if output_type == "json":
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    # 文本格式
    lines = []
    lines.append("📊 A股市场概览")
    lines.append("=" * 40)
    
    if "indices" in data:
        lines.append("\n【主要指数】")
        for idx in data["indices"]:
            emoji = "📈" if idx.get("change", 0) >= 0 else "📉"
            lines.append(f"{emoji} {idx['name']}: {idx['value']:.2f} ({idx['change']:+.2f}%)")
    
    if "top_gainers" in data:
        lines.append("\n【涨幅榜】")
        for i, stock in enumerate(data["top_gainers"][:5], 1):
            lines.append(f"{i}. {stock['name']}({stock['code']}): {stock['price']:.2f} +{stock['change']:.2f}%")
    
    return "\n".join(lines)

def main():
    """主入口"""
    import argparse
    parser = argparse.ArgumentParser(description='A股数据服务')
    parser.add_argument('--update', action='store_true', help='更新缓存')
    parser.add_argument('--query', type=str, help='查询个股代码或名称')
    parser.add_argument('--overview', action='store_true', help='市场概览')
    parser.add_argument('--json', action='store_true', help='JSON输出')
    args = parser.parse_args()
    
    sys.stdout.reconfigure(encoding='utf-8')
    
    if args.update:
        if update_cache():
            print("✅ 缓存更新成功")
        else:
            print("❌ 缓存更新失败")
    elif args.query:
        result = get_stock_quote(code=args.query) or get_stock_quote(name=args.query)
        if result:
            print(format_output({"stocks": [result]}, "json" if args.json else "text"))
        else:
            print(f"未找到: {args.query}")
    elif args.overview:
        data = get_market_overview()
        print(format_output(data, "json" if args.json else "text"))
    else:
        # 默认显示市场概览
        data = get_market_overview()
        print(format_output(data, "json" if args.json else "text"))

if __name__ == "__main__":
    main()

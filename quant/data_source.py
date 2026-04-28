"""
data_source.py - A股数据源 v5
仅依赖已验证可用的接口:
  1. 新浪实时行情 (hq.sinajs.cn)
  2. 新浪历史K线 (money.finance.sina.com.cn)
"""
import requests
import re
import time
from typing import Optional, Dict, List

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://finance.sina.com.cn'
}

# 主要指数代码
INDEX_CODES = {
    '000001',  # 上证指数
    '399001',  # 深证成指
    '399006',  # 创业板指
    '000300',  # 沪深300
    '000016',  # 上证50
    '000905',  # 中证500
    '399005',  # 中小板指
    '399673',  # 创业板50
}


def is_index_code(code: str) -> bool:
    """判断是否为指数"""
    return code.strip().lstrip('shszSHZS') in INDEX_CODES


def normalize_code(code: str) -> str:
    """标准化股票代码"""
    code = str(code).strip().lstrip('shszSHZS')
    if code in INDEX_CODES:
        return f'sh{code}'  # 指数用 sh
    if code.startswith(('6', '5', '9')):
        return f'sh{code}'
    return f'sz{code}'


def parse_sina_raw(raw: str, is_index: bool) -> Optional[Dict]:
    try:
        m = re.search(r'hq_str_[a-z]{2}(\d+)="(.+)"', raw)
        if not m:
            return None
        code = m.group(1)
        fields = m.group(2).split(',')
        name = fields[0]

        if is_index:
            # 指数格式: 名称, 当前, 昨收, 开盘, 最高, 最低, ...
            # 注意：指数和个股的字段顺序不同！
            current = float(fields[1])
            close_prev = float(fields[2])
            open_p = float(fields[3])
            high = float(fields[4])
            low = float(fields[5])
            chg = current - close_prev
            chg_pct = (chg / close_prev * 100) if close_prev else 0
            return {
                'code': code, 'name': name, 'current': current,
                'open': open_p, 'close_prev': close_prev,
                'high': high, 'low': low,
                'chg': chg, 'chg_pct': chg_pct,
                'date': fields[30] if len(fields) > 30 else '',
                'time': fields[31] if len(fields) > 31 else '',
            }
        else:
            # 个股: 开盘, 昨收, 当前, 最高, 最低, ..., 成交量, 成交额
            open_p = float(fields[1])
            close_prev = float(fields[2])
            current = float(fields[3])
            high = float(fields[4])
            low = float(fields[5])
            vol = float(fields[8])
            amount = float(fields[9])
            date = fields[30] if len(fields) > 30 else ''
            time_str = fields[31] if len(fields) > 31 else ''
            chg = current - close_prev
            chg_pct = (chg / close_prev * 100) if close_prev else 0
            return {
                'code': code, 'name': name,
                'open': open_p, 'close_prev': close_prev, 'current': current,
                'high': high, 'low': low, 'vol': vol, 'amount': amount,
                'chg': chg, 'chg_pct': chg_pct,
                'date': date, 'time': time_str,
            }
    except:
        return None


def get_realtime(codes: List[str]) -> Dict[str, Dict]:
    """批量获取实时行情"""
    if not codes:
        return {}

    # 预判每个code是指数还是个股
    code_map = {}  # {纯数字code: is_index}
    for c in codes:
        pure = str(c).strip().lstrip('shszSHZS')
        code_map[pure] = is_index_code(pure)

    symbols = [normalize_code(c) for c in codes]
    url = f'https://hq.sinajs.cn/list={",".join(symbols)}'

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.encoding = 'gbk'
    except Exception as e:
        print(f'realtime failed: {e}')
        return {}

    result = {}
    lines = r.text.strip().split('\n')
    for i, line in enumerate(lines):
        if i >= len(symbols):
            break
        pure = symbols[i].lstrip('shsz')
        is_idx = code_map.get(pure, False)
        info = parse_sina_raw(line, is_index=is_idx)
        if info:
            result[info['code']] = info
    return result


def get_hist_sina(code: str, days: int = 30) -> Optional[Dict]:
    """获取历史K线 - 新浪财经"""
    try:
        norm = normalize_code(code)
        url = 'https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData'
        params = {'symbol': norm, 'scale': 240, 'ma': 'no', 'datalen': str(days)}
        r = requests.get(url, params=params, headers=HEADERS, timeout=10)
        r.encoding = 'utf-8'
        data = r.json()

        if not data or not isinstance(data, list):
            return None

        return {
            'dates': [d['day'] for d in data],
            'open': [float(d['open']) for d in data],
            'close': [float(d['close']) for d in data],
            'high': [float(d['high']) for d in data],
            'low': [float(d['low']) for d in data],
            'vol': [float(d['volume']) for d in data],
        }
    except Exception as e:
        print(f'hist failed {code}: {e}')
        return None


def get_hist_with_retry(code: str, days: int = 30) -> Optional[Dict]:
    for attempt in range(2):
        hist = get_hist_sina(code, days)
        if hist:
            return hist
        time.sleep(1)
    return None

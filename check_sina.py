import requests
url = 'https://hq.sinajs.cn/list=sh000001'
r = requests.get(url, headers={'Referer': 'https://finance.sina.com.cn', 'User-Agent': 'Mozilla/5.0'}, timeout=8)
r.encoding = 'gbk'
print('Raw:', r.text[:200])
fields = r.text.split('"')[1].split(',')
print('Fields count:', len(fields))
print('Field 0 (name):', fields[0])
print('Field 1 (current):', fields[1])
print('Field 2 (chg):', fields[2])
print('Field 3 (chg_pct):', fields[3])

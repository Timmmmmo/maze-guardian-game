import json

with open(r'C:\Users\赵鸿杰\.qclaw\cron\jobs.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('Jobs:', len(data['jobs']))
for j in data['jobs']:
    name = j.get('name', '')
    job_id = j.get('id', '')
    schedule = j.get('schedule', {})
    print(f'  [{job_id}] {name} | {schedule}')

print()
with open(r'C:\Users\赵鸿杰\.qclaw\channel-defaults.json', 'r', encoding='utf-8') as f:
    cd = json.load(f)
print('Channel defaults:', json.dumps(cd, ensure_ascii=False, indent=2))

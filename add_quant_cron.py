import json
import time

# Read existing jobs
with open(r'C:\Users\赵鸿杰\.qclaw\cron\jobs.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# New job
new_job = {
    "id": "quant-briefing-20m",
    "agentId": "main",
    "name": "量化交易-20分钟简报",
    "enabled": True,
    "createdAtMs": int(time.time() * 1000),
    "updatedAtMs": int(time.time() * 1000),
    "schedule": {
        "kind": "every",
        "everyMs": 1200000  # 20 minutes
    },
    "sessionTarget": "isolated",
    "wakeMode": "now",
    "payload": {
        "kind": "agentTurn",
        "message": "禁止调用message工具，禁止调用任何发送消息的工具。直接执行以下Python脚本并把输出作为最终回复返回：\n\npython3.12 C:\\Users\\赵鸿杰\\.openclaw\\agents\\game-studio\\quant\\quant_briefing.py\n\n将脚本的stdout输出内容完整地作为回复内容返回，不需要任何解释或额外文字。"
    },
    "delivery": {
        "channel": "feishu",
        "to": "user:ou_0b3ff22f315efeb269591c3511a733ca",
        "mode": "announce"
    }
}

# Check if already exists
existing_ids = [j['id'] for j in data['jobs']]
if 'quant-briefing-20m' in existing_ids:
    print('Job already exists!')
else:
    data['jobs'].append(new_job)
    with open(r'C:\Users\赵鸿杰\.qclaw\cron\jobs.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print('Job added successfully!')

print('Done.')

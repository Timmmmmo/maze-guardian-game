import json
import time

# Read existing jobs
with open(r'C:\Users\赵鸿杰\.qclaw\cron\jobs.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find and update the quant job
for j in data['jobs']:
    if j['id'] == 'quant-briefing-20m':
        # Fix payload message - use simple ASCII to avoid encoding issues
        j['payload']['message'] = "Execute this command and return the output as your response: python3.12 C:\\Users\\赵鸿杰\\.openclaw\\agents\\game-studio\\quant\\quant_briefing.py"
        j['updatedAtMs'] = int(time.time() * 1000)
        # Reset error state
        j['state'] = {
            "nextRunAtMs": int(time.time() * 1000) + 1200000,
            "lastRunAtMs": None,
            "lastRunStatus": None,
            "lastStatus": None,
            "consecutiveErrors": 0
        }
        print('Job updated!')
        break
else:
    print('Job not found!')
    exit(1)

# Write back
with open(r'C:\Users\赵鸿杰\.qclaw\cron\jobs.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('Done.')

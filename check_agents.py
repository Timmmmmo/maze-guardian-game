import json

with open(r'C:\Users\赵鸿杰\.qclaw\openclaw.json', 'r', encoding='utf-8') as f:
    c = json.load(f)

agents = c['agents']['list']
print('=== Agents Config ===')
for a in agents:
    print(f"ID: {a['id']}")
    print(f"  Name: {a.get('name', '')}")
    print(f"  Workspace: {a.get('workspace', '')}")
    print(f"  AgentDir: {a.get('agentDir', '')}")
    print()
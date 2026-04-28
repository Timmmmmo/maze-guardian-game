import json

config_path = r'C:\Users\赵鸿杰\.qclaw\openclaw.json'

with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

# Add game-dev agent
new_agent = {
    "id": "game-dev",
    "default": False,
    "name": "\u5c0fB",
    "workspace": "~/.openclaw/agents/game-dev",
    "agentDir": "~/.openclaw/agents/game-dev",
    "model": {
        "primary": "custom/Qwen3-235B-A22B"
    }
}

# Check if already exists
agent_ids = [a['id'] for a in config['agents']['list']]
if 'game-dev' in agent_ids:
    print('game-dev agent already exists!')
else:
    config['agents']['list'].append(new_agent)
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print('game-dev agent added successfully!')

print('Current agents:')
for a in config['agents']['list']:
    print(f'  - {a["id"]} ({a.get("name", "")})')

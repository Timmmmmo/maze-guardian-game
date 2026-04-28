import json
import os

config_path = os.path.expanduser(r'C:\Users\赵鸿杰\.qclaw\openclaw.json')
print(f'Loading: {config_path}')

with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

# 修改 game-studio 的模型为 claude-opus
if 'agents' in config and 'list' in config['agents']:
    for agent in config['agents']['list']:
        if agent.get('id') == 'game-studio':
            old_model = agent.get('model', {})
            agent['model'] = {'primary': 'claude-opus-4-20250514'}
            print(f'Changed game-studio model: {old_model} -> {agent["model"]}')

# 保存
with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)

print('Config saved!')

content = """{
  "authGatewayBaseUrl": "http://127.0.0.1:19000/proxy",
  "cli": {
    "nodeBinary": "C:\\\\Program Files\\\\QClaw\\\\QClaw.exe",
    "openclawMjs": "C:\\\\Program Files\\\\QClaw\\\\resources\\\\openclaw\\\\node_modules\\\\openclaw\\\\openclaw.mjs",
    "pid": 9508
  },
  "stateDir": "C:\\\\Users\\\\赵鸿杰\\\\.qclaw",
  "configPath": "C:\\\\Users\\\\赵鸿杰\\\\.qclaw\\\\openclaw.json",
  "port": 28789,
  "platform": "win32"
}"""
with open(r'C:\Users\赵鸿杰\.qclaw\qclaw.json', 'w', encoding='utf-8') as f:
    f.write(content)
print('done')

$env:ELECTRON_RUN_AS_NODE = "1"
$env:NODE_OPTIONS = "--no-warnings"
$env:OPENCLAW_NIX_MODE = "1"
$env:OPENCLAW_STATE_DIR = "C:\Users\赵鸿杰\.qclaw"
$env:OPENCLAW_CONFIG_PATH = "C:\Users\赵鸿杰\.qclaw\openclaw.json"
& "node" "C:\Program Files\QClaw\resources\openclaw\node_modules\openclaw\openclaw.mjs" cron list

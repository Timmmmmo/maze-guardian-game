@echo off
set ELECTRON_RUN_AS_NODE=1
set NODE_OPTIONS=--no-warnings
set OPENCLAW_NIX_MODE=1
set OPENCLAW_STATE_DIR=C:\Users\赵鸿杰\.qclaw
set OPENCLAW_CONFIG_PATH=C:\Users\赵鸿杰\.qclaw\openclaw.json
"node" "C:\Program Files\QClaw\resources\openclaw\node_modules\openclaw\openclaw.mjs" cron list

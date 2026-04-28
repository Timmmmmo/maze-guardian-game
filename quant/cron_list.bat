@echo off
set "ELECTRON_RUN_AS_NODE=1"
set "NODE_OPTIONS=--no-warnings"
set "OPENCLAW_NIX_MODE=1"
set "OPENCLAW_STATE_DIR=C:\Users\赵鸿杰\.qclaw"
set "OPENCLAW_CONFIG_PATH=C:\Users\赵鸿杰\.qclaw\openclaw.json"
"C:\Program Files\QClaw\QClaw.exe" --version
"C:\Program Files\QClaw\QClaw.exe" --help 2>&1 | findstr /i cron

const { spawn } = require('child_process');
const fs = require('fs');
const path = 'C:\\Program Files\\QClaw\\resources\\openclaw\\config\\skills\\online-search\\scripts\\prosearch.cjs';
const json = JSON.stringify({ keyword: 'Claude Code skill-creator SKILL MD Anthropic 2025', cnt: 10 });
const child = spawn('node', [path, json], { stdio: ['pipe', 'pipe', 'pipe'] });
let out = '', err = '';
child.stdout.on('data', d => out += d);
child.stderr.on('data', d => err += d);
child.on('close', code => {
  if(out) { try { const r = JSON.parse(out); console.log(JSON.stringify(r, null, 2)); } catch(e) { console.log(out); } }
});

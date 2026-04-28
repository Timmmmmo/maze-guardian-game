const { execSync } = require('child_process');
const path = 'C:\\Program Files\\QClaw\\resources\\openclaw\\config\\skills\\online-search\\scripts\\prosearch.cjs';
const keyword = 'Claude Code Skills GitHub repo';
const json = JSON.stringify({ keyword, cnt: 10 });
// Write JSON to temp file to avoid shell escaping issues
const fs = require('fs');
const tmp = require('os').tmpdir() + '/search-' + Date.now() + '.json';
fs.writeFileSync(tmp, json);
try {
  const r = execSync('node "' + path + '" --file "' + tmp + '"', { encoding: 'utf8', timeout: 15000 });
  console.log(r);
} catch(e) {
  console.error(e.stdout || e.message);
} finally {
  try { fs.unlinkSync(tmp); } catch(e) {}
}

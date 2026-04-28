const { execSync } = require('child_process');
const script = 'C:\\Program Files\\QClaw\\resources\\openclaw\\config\\skills\\online-search\\scripts\\prosearch.cjs';
const result = execSync(`node "${script}" "{\\"keyword\\":\\"Claude Code Skills GitHub\\"}"`, { encoding: 'utf8' });
console.log(result);

const fs = require('fs');
const h = fs.readFileSync('index.html', 'utf8');
// Find panel-hot and show 500 chars
const s = h.indexOf('id="panel-hot"');
console.log('=== panel-hot (500 chars) ===');
console.log(h.substring(s, s + 500));
console.log('\n=== around analyze ===');
const a = h.indexOf('id="panel-analyze"');
console.log(h.substring(a - 20, a + 200));

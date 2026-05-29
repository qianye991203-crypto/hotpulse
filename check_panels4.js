const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');

// Show the full panel-hot content
const phStart = html.indexOf('id="panel-hot"');
let depth = 0, phEnd = phStart;
for (let i = phStart; i < html.length; i++) {
  if (html.substr(i,4) === '<div') depth++;
  if (html.substr(i,6) === '</div>') { depth--; if (depth === 0) { phEnd = i + 6; break; } }
}
console.log('=== panel-hot full content ===');
console.log(html.substring(phStart, phEnd));

// Show what's right before panel-hot
console.log('\n=== 200 chars before panel-hot ===');
console.log(html.substring(Math.max(0, phStart - 200), phStart).replace(/\n/g,' '));

// Show what's after panel-hot and before panel-analyze
const paStart = html.indexOf('id="panel-analyze"');
console.log('\n=== between panel-hot close and panel-analyze ===');
console.log(html.substring(phEnd, paStart).replace(/\n/g,' ').substring(0, 500));

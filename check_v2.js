const fs = require('fs');
const h = fs.readFileSync('v2_backup.html', 'utf8');

for (const pid of ['panel-analyze', 'panel-content']) {
  const s = h.indexOf('id="' + pid + '"');
  let d = 0, e = s;
  for (let i = s; i < h.length; i++) {
    if (h.substr(i, 4) === '<div') { let j = i + 4; while (j < h.length && /[\s\r\n]/.test(h[j])) j++; if (j < h.length && h[j] !== '/' && h[j] !== '>') d++; }
    if (h.substr(i, 6) === '</div>') { d--; if (d === 0) { e = i + 6; break; } }
  }
  console.log('=== ' + pid + ' (' + (e - s) + ' bytes) ===');
  console.log(h.substring(s, e));
  console.log('');
}

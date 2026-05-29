const fs = require('fs');
const h = fs.readFileSync('index.html', 'utf8');
console.log('Size:', h.length, 'bytes');
console.log('\nPanel sizes:');
for (const p of ['panel-hot', 'panel-analyze', 'panel-content', 'panel-history']) {
  const s = h.indexOf('id="' + p + '"');
  let d = 0, e = s;
  for (let i = s; i < h.length; i++) {
    if (h.substr(i, 4) === '<div') { let j = i + 4; while (j < h.length && /[\s\r\n]/.test(h[j])) j++; if (j < h.length && h[j] !== '/' && h[j] !== '>') d++; }
    if (h.substr(i, 6) === '</div>') { d--; if (d === 0) { e = i + 6; break; } }
  }
  console.log(p + ':', (e - s), 'bytes');
}

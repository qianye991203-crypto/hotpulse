const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');

// Check all panel IDs
const panels = html.match(/id="panel-[^"]+"/g);
console.log('Panels found:', panels);

// Check switchTab function
const tabIdx = html.indexOf('function switchTab');
if (tabIdx > -1) console.log('\nswitchTab found at:', tabIdx);
else console.log('\nswitchTab NOT FOUND!');

// Check each panel content
for (const p of (panels || [])) {
  const id = p.replace('id="','').replace('"','');
  const openTag = '<div ' + p + '>';
  const start = html.indexOf(openTag);
  if (start === -1) console.log('MISSING panel:', id);
  else {
    let depth = 0, end = start;
    for (let i = start; i < html.length; i++) {
      if (html.substr(i,4) === '<div') depth++;
      if (html.substr(i,6) === '</div>') { depth--; if (depth === 0) { end = i + 6; break; } }
    }
    // Show first 80 chars of content
    const content = html.substring(start, Math.min(start+120, end));
    console.log(`Panel ${id}: ${end-start} bytes, starts with: ${content.replace(/\n/g,' ')}`);
  }
}

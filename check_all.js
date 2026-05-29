const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');

// Show all 4 panels' full content
for (const pid of ['panel-hot', 'panel-analyze', 'panel-content', 'panel-history']) {
  const s = html.indexOf(`id="${pid}"`);
  let d=0, e=s;
  for (let i=s; i<html.length; i++) {
    if (html.substr(i,4)==='<div') { let j=i+4; while(j<html.length&&/[\s\r\n]/.test(html[j]))j++; if(j<html.length&&html[j]!=='/'&&html[j]!='>')d++; }
    if (html.substr(i,6)==='</div>') { d--; if(d===0){e=i+6;break;} }
  }
  console.log(`\n=== ${pid} (${e-s} bytes) ===`);
  console.log(html.substring(s, Math.min(s+800, e)));
}

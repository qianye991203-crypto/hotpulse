const fs = require('fs');
let html = fs.readFileSync('index.html', 'utf8');

// Show exact panel-hot content
const ph = html.indexOf('id="panel-hot"');
let d=0, pe=ph;
for (let i=ph; i<html.length; i++) {
  if (html.substr(i,4)==='<div') { let j=i+4; while(j<html.length&&/[\s\r\n]/.test(html[j]))j++; if(j<html.length&&html[j]!=='/'&&html[j]!='>')d++; }
  if (html.substr(i,6)==='</div>') { d--; if(d===0){pe=i+6;break;} }
}
console.log('=== panel-hot FULL content ===');
console.log(html.substring(ph, pe));

// Check: is there a </div> inside that closes the main div early?
const lines = html.substring(ph, pe).split('\n');
lines.forEach((l, i) => {
  const opens = (l.match(/<div[\s>]/g) || []).length;
  const closes = (l.match(/<\/div>/g) || []).length;
  if (closes > opens) console.log(`Line ${i}: CLOSES MORE (${closes} vs ${opens}): ${l.trim().substring(0,100)}`);
});

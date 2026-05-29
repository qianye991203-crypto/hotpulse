const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');

// Check: is hotlist-merged inside or outside panel-hot?
const phStart = html.indexOf('id="panel-hot"');
let depth = 0, phEnd = phStart;
for (let i = phStart; i < html.length; i++) {
  if (html.substr(i,4) === '<div' && html.substr(i,5)!=='<div ') {
    // skip check - just count <div with space or >
    const after = html.substring(i, i+6);
    if (after.match(/^<div[\s>]/)) depth++;
  } else if (html.substr(i,4) === '<div') {
    const after = html.substring(i, i+6);
    if (after.match(/^<div[\s>]/)) depth++;
  }
  if (html.substr(i,6) === '</div>') { depth--; if (depth === 0) { phEnd = i + 6; break; } }
}

const mergedIdx = html.indexOf('hotlist-merged');
console.log('panel-hot:', phStart, '-', phEnd);
console.log('hotlist-merged at:', mergedIdx);
console.log('hotlist-merged INSIDE panel-hot?', mergedIdx > phStart && mergedIdx < phEnd);

// Check CSS .panel display rules
const panelCSS = html.indexOf('.panel {');
if (panelCSS > -1) console.log('\n.panel CSS:', html.substring(panelCSS, panelCSS + 200));

// Check if there's a display:none issue
const activeCSS = html.indexOf('.panel.active');
if (activeCSS > -1) console.log('\n.panel.active CSS:', html.substring(activeCSS, activeCSS + 200));

// The REAL question: are all panels showing the same content because 
// hotlist-merged is actually outside all panels and always visible?
// Let's check what's between </div> closing panel-hot and next panel
const paStart = html.indexOf('id="panel-analyze"');
console.log('\n--- Content between panel-hot end and panel-analyze ---');
const between = html.substring(phEnd, Math.min(paStart, phEnd + 200));
console.log(JSON.stringify(between.substring(0, 200)));

// Also: maybe the issue is that other panels have no content?
// Show first 200 chars of each panel
for (const pid of ['panel-analyze', 'panel-content', 'panel-history']) {
  const s = html.indexOf(`id="${pid}"`);
  let d = 0, e = s;
  for (let i = s; i < html.length; i++) {
    if (html.substr(i,4).match(/^<div[\s>]/)) d++;
    if (html.substr(i,6) === '</div>') { d--; if (d === 0) { e = i + 6; break; } }
  }
  console.log(`\n${pid} (${e-s} bytes):`);
  console.log(html.substring(s, Math.min(s + 300, e)).replace(/\r\n/g, '\\n'));
}

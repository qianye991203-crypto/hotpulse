const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');

// Find tab buttons area
const tabsStart = html.indexOf('class="tabs"');
console.log('Tabs area at:', tabsStart);
if (tabsStart > -1) {
  console.log(html.substring(tabsStart, tabsStart + 800));
}

// Find onclick for tab switching
const onclicks = html.match(/onclick="[^"]*switchTab[^"]*"/g);
console.log('\nTab onclick handlers:', onclicks);

// Also check: is there a hotlist-merged div that might be outside panels?
const mergedIdx = html.indexOf('hotlist-merged');
console.log('\nhotlist-merged at:', mergedIdx);
if (mergedIdx > -1) {
  console.log(html.substring(Math.max(0,mergedIdx-100), mergedIdx+50).replace(/\n/g,' '));
}

// Check if hotlist-merged is inside panel-hot or outside
const panelHotOpen = html.indexOf('id="panel-hot"');
const panelHotClose = findCloseDiv(html, panelHotOpen);
console.log('\npanel-hot:', panelHotOpen, '-', panelHotClose);
console.log('hotlist-merged inside panel-hot?', mergedIdx > panelHotOpen && mergedIdx < panelHotClose);

function findCloseDiv(s, start) {
  let depth = 0;
  for (let i = start; i < s.length; i++) {
    if (s.substr(i,4) === '<div') depth++;
    if (s.substr(i,6) === '</div>') { depth--; if (depth === 0) return i + 6; }
  }
  return -1;
}

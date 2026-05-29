const fs = require('fs');
let html = fs.readFileSync('index.html', 'utf8');

// Find key positions
const phStart = html.indexOf('id="panel-hot"');
const paStart = html.indexOf('id="panel-analyze"');
const mergedStart = html.indexOf('hotlist-merged');

console.log('panel-hot starts:', phStart);
console.log('panel-analyze starts:', paStart);  
console.log('hotlist-merged at:', mergedStart);

// Show what's between panel-hot close and panel-analyze
// This should contain the 100-item hotlist that needs to go INSIDE panel-hot
const between = html.substring(paStart - 500, paStart);
console.log('\n--- 500 chars before panel-analyze ---');
console.log(between.replace(/\r\n/g, '\n'));

// Find where the stranded hotlist-merged block is
// It should be after platform-grid </div> and before <!-- 选题分析 Panel -->
const gridEnd = html.indexOf('</div>\n    <div class="analyze-box"', phStart);
console.log('\nanalyze-box at:', gridEnd);
if (gridEnd > -1) {
  console.log(html.substring(gridEnd, gridEnd + 300).replace(/\r\n/g, '\n'));
}

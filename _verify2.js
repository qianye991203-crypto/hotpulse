const fs = require('fs');
const h = fs.readFileSync('index.html', 'utf8');

// More reliable: count from id="panel-X" to the next "id="panel-" or "</div><!-- end container"
for (const p of ['panel-hot', 'panel-analyze', 'panel-content', 'panel-history']) {
  const start = h.indexOf('id="' + p + '"');
  // Find next panel or container close
  let end = h.length;
  for (const other of ['panel-hot', 'panel-analyze', 'panel-content', 'panel-history']) {
    if (other !== p) {
      const idx = h.indexOf('id="' + other + '"', start + 10);
      if (idx > start && idx < end) end = idx;
    }
  }
  // Also check for container close
  const contClose = h.indexOf('</div><!-- end container -->', start);
  if (contClose > start && contClose < end) end = contClose;
  
  console.log(p + ': ' + (end - start) + ' bytes (from id to next panel/container-close)');
}

// Also verify key features
console.log('\n--- Feature checks ---');
const features = [
  ['platform-grid', '9 platform cards'],
  ['hotlist-merged', '100 hot items'],
  ['analyze-input-area', 'Analyze form UI'],
  ['btn-analyze', 'Analyze button'],
  ['content-grid', 'Content library cards (8)'],
  ['historyArea', 'History area'],
  ['function switchTab', 'Tab switching JS'],
  ['function runAnalyze', 'Analyze engine JS'],
  ['function calcScore', 'Scoring algorithm'],
];
features.forEach(([txt, label]) => {
  console.log((h.includes(txt) ? '✅' : '❌') + ' ' + label);
});

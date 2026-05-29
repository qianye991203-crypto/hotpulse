const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');

// Search for panel-related patterns
const patterns = ['panel-hot', 'panel-analyze', 'panel-content', 'panel-history'];
for (const p of patterns) {
  const idx = html.indexOf(p);
  if (idx > -1) {
    // Show surrounding context
    const start = Math.max(0, idx - 60);
    const end = Math.min(html.length, idx + 80);
    console.log(`Found "${p}" at ${idx}:`);
    console.log('  ...' + html.substring(start, end).replace(/\n/g, ' ') + '...');
    console.log('');
  } else {
    console.log(`NOT FOUND: ${p}`);
  }
}

// Also check the tab buttons
console.log('\n--- Tab buttons ---');
const tabMatches = html.match(/data-tab="[^"]+"/g);
console.log(tabMatches);

// Check switchTab logic
const stStart = html.indexOf('function switchTab');
const stEnd = html.indexOf('\nfunction ', stStart + 10);
console.log('\n--- switchTab function ---');
console.log(html.substring(stStart, Math.min(stEnd || stStart+500, html.length)).substring(0, 600));

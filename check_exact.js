const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');
const ph = html.indexOf('id="panel-hot"');
// Show exact bytes from panel-hot open to 300 chars after
console.log(JSON.stringify(html.substring(ph, ph + 300)));

const https = require('https');
const http = require('http');

function fetch(url) {
    return new Promise((resolve, reject) => {
        const lib = url.startsWith('https') ? https : http;
        const req = lib.get(url, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://weibo.com/',
                'Accept': 'application/json, text/plain, */*'
            }
        }, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try { resolve(JSON.parse(data)); }
                catch(e) { reject(e); }
            });
        });
        req.on('error', reject);
        req.setTimeout(15000, () => { req.destroy(); reject(new Error('timeout')); });
    });
}

async function main() {
    const apis = [
        ['weibo', 'https://api.52vmy.cn/api/wl/hot?type=weibo'],
        ['baidu', 'https://api.52vmy.cn/api/wl/hot?type=baidu'],
    ];
    
    for (const [name, url] of apis) {
        try {
            const d = await fetch(url);
            let items = d.data || d.result || [];
            if (!Array.isArray(items)) items = [];
            console.log(`=== ${name.toUpperCase()} (${items.length} items) ===`);
            items.slice(0, 55).forEach((item, i) => {
                const word = item.word || item.title || JSON.stringify(item);
                const hot = item.hot || item.value || 0;
                console.log(`${i+1}. ${word} [${hot}]`);
            });
        } catch(e) {
            console.log(`${name.toUpperCase()} FAILED: ${e.message}`);
        }
    }
}

main();

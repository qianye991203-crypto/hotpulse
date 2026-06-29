import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def fetch(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://weibo.com/'
    })
    return urllib.request.urlopen(req, context=ctx, timeout=15)

# Try the 52vmy API (used by cron job)
apis = [
    ('weibo', 'https://api.52vmy.cn/api/wl/hot?type=weibo'),
    ('baidu', 'https://api.52vmy.cn/api/wl/hot?type=baidu'),
]

for name, url in apis:
    try:
        r = fetch(url)
        d = json.loads(r.read())
        items = d.get('data', d.get('result', []))
        if isinstance(items, list):
            print(f'=== {name.upper()} ({len(items)} items) ===')
            for i, item in enumerate(items[:55]):
                if isinstance(item, dict):
                    word = item.get('word', item.get('title', str(item)))
                    hot = item.get('hot', item.get('value', 0))
                    print(f'{i+1}. {word} [{hot}]')
                else:
                    print(f'{i+1}. {item}')
    except Exception as e:
        print(f'{name} FAILED: {e}')

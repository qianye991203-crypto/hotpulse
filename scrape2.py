# -*- coding: utf-8 -*-
import urllib.request, json, re

# ---- B站热门 ----
print("Fetching B站...")
url = 'https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all'
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://www.bilibili.com/'
})
with urllib.request.urlopen(req, timeout=8) as resp:
    data = json.loads(resp.read().decode('utf-8'))

bili_items = []
for item in data['data']['list'][:30]:
    stat = item.get('stat', {})
    view = stat.get('view', 0)
    if view >= 100000000:
        h = str(view // 100000000) + '亿播放'
    elif view >= 10000:
        h = str(view // 10000) + '万播放'
    else:
        h = str(view) + '播放'
    bili_items.append({'title': item['title'], 'heat': h, 'source': 'B站'})

# ---- 抖音热榜 (从tophub HTML) ----
print("Fetching 抖音...")
req2 = urllib.request.Request('https://tophub.today/n/DpQvNABoNE', headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})
with urllib.request.urlopen(req2, timeout=10) as resp:
    html = resp.read().decode('utf-8', errors='replace')

douyin_titles = re.findall(r'class="td-item-title"[^>]*>([^<]+)<', html)
douyin_plays = re.findall(r'(\d+\.?\d*[万亿]?)\s*次播放', html)
douyin_items = []
for i, (t, p) in enumerate(zip(douyin_titles[:20], douyin_plays[:20])):
    t = t.strip()
    p = p.strip()
    if p.endswith('万'):
        douyin_items.append({'title': t, 'heat': p + '播放', 'source': '抖音'})
    elif p.endswith('亿'):
        douyin_items.append({'title': t, 'heat': p + '播放', 'source': '抖音'})
    else:
        douyin_items.append({'title': t, 'heat': p + '次播放', 'source': '抖音'})

# ---- 虎嗅热文 ----
print("Fetching 虎嗅...")
req3 = urllib.request.Request('https://tophub.today/n/5VaobgvAj1', headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})
with urllib.request.urlopen(req3, timeout=10) as resp:
    hx_html = resp.read().decode('utf-8', errors='replace')

hx_titles = re.findall(r'class="td-item-title"[^>]*>([^<]+)<', hx_html)
hx_heats = re.findall(r'(\d+\.?\d*万)', hx_html)
huxiu_items = []
for t, h in zip(hx_titles[:20], hx_heats[:20]):
    t = t.strip()
    if t and len(t) > 5:
        huxiu_items.append({'title': t, 'heat': h, 'source': '虎嗅'})

# ---- 微博热搜 (备用：尝试weibo hot search API) ----
print("Fetching 微博...")
weibo_items = []
try:
    req4 = urllib.request.Request('https://weibo.com/ajax/side/hotSearch', headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://weibo.com'
    })
    with urllib.request.urlopen(req4, timeout=8) as resp:
        wb_data = json.loads(resp.read().decode('utf-8'))
    for item in wb_data.get('data', {}).get('realtime', [])[:20]:
        weibo_items.append({'title': item.get('word', ''), 'heat': str(item.get('raw_hot', '')), 'source': '微博'})
except Exception as e:
    print(f'  微博失败: {e}')

print(f'B站: {len(bili_items)} 抖音: {len(douyin_items)} 虎嗅: {len(huxiu_items)} 微博: {len(weibo_items)}')

# Save
with open('C:/Users/VRPC01/.qclaw/workspace/hotpulse/extra_data.json', 'w', encoding='utf-8') as f:
    json.dump({
        'bili': bili_items,
        'douyin': douyin_items,
        'huxiu': huxiu_items,
        'weibo': weibo_items
    }, f, ensure_ascii=False, indent=2)
print('Done!')
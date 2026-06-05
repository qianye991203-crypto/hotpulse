# -*- coding: utf-8 -*-
import urllib.request, json, re

def fetch(url, headers=None):
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            return resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        print(f'    [WARN] fetch failed: {url[:50]} -> {e}')
        return ''

results = {}

# ---- 知乎热榜 (官方API) ----
print('[1/6] Fetching 知乎...')
raw = fetch('https://api.zhihu.com/topstory/hot-lists/total?limit=50')
if raw:
    try:
        data = json.loads(raw)
        items = []
        for item in data.get('data', [])[:30]:
            title = item.get('target', {}).get('title', '')
            detail = item.get('detail_text', '')
            m = re.search(r'([\d.]+)\s*万热度', detail)
            heat = str(int(float(m.group(1)) * 10000)) + '热度' if m else detail
            if title:
                items.append({'title': title, 'heat': heat, 'source': '知乎'})
        results['知乎'] = items
        print(f'    -> Got {len(items)} items')
    except Exception as e:
        print(f'    -> Failed: {e}')
        results['知乎'] = []
else:
    results['知乎'] = []

# ---- B站热门 (官方API) ----
print('[2/6] Fetching B站...')
raw = fetch('https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all',
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'Referer': 'https://www.bilibili.com/'})
if raw:
    try:
        data = json.loads(raw)
        items = []
        for item in data.get('data', {}).get('list', [])[:30]:
            stat = item.get('stat', {})
            view = stat.get('view', 0)
            if view >= 100000000: h = str(view // 100000000) + '亿播放'
            elif view >= 10000: h = str(view // 10000) + '万播放'
            else: h = str(view) + '播放'
            items.append({'title': item.get('title', ''), 'heat': h, 'source': 'B站'})
        results['B站'] = items
        print(f'    -> Got {len(items)} items')
    except Exception as e:
        print(f'    -> Failed: {e}')
        results['B站'] = []
else:
    results['B站'] = []

# ---- 百度热搜 (HTML) ----
print('[3/6] Fetching 百度热搜...')
raw = fetch('https://top.baidu.com/board?tab=realtime')
if raw:
    try:
        titles = re.findall(r'class="c-single-text-ellipsis"[^>]*>([^<]+)</div>', raw)
        hot_vals = re.findall(r'<div class="hot-index[^"]*"[^>]*>\s*([\d,]+)', raw)
        items = []
        for title, val in zip(titles[:30], hot_vals[:30]):
            title = title.strip()
            val = val.strip().replace(',', '')
            try:
                v = int(val)
                h = str(v // 10000) + '万热度' if v >= 10000 else val + '热度'
            except: h = val + '热度'
            if title:
                items.append({'title': title, 'heat': h, 'source': '百度'})
        results['百度'] = items
        print(f'    -> Got {len(items)} items')
    except Exception as e:
        print(f'    -> Failed: {e}')
        results['百度'] = []
else:
    results['百度'] = []

# ---- 头条热榜 (官方API) ----
print('[4/6] Fetching 头条...')
raw = fetch('https://www.toutiao.com/api/pc/feed/?category=news_hot&max_behot_time=0&count=30&source=hot_list')
if raw:
    try:
        data = json.loads(raw)
        items = []
        for item in data.get('data', [])[:30]:
            title = item.get('title', '')
            hot_val = item.get('hot_value', '')
            if title:
                h = str(hot_val) + '热度' if hot_val else '热门'
                items.append({'title': title, 'heat': h, 'source': '头条'})
        results['头条'] = items
        print(f'    -> Got {len(items)} items')
    except Exception as e:
        print(f'    -> Failed: {e}')
        results['头条'] = []
else:
    results['头条'] = []

# ---- 微博热搜 (weibo API) ----
print('[5/6] Fetching 微博...')
raw = fetch('https://weibo.com/ajax/side/hotSearch',
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'Referer': 'https://weibo.com/'})
if raw:
    try:
        data = json.loads(raw)
        items = []
        for item in data.get('data', {}).get('realtime', [])[:30]:
            word = item.get('word', '')
            raw_hot = str(item.get('raw_hot', ''))
            if word:
                items.append({'title': word, 'heat': raw_hot, 'source': '微博'})
        results['微博'] = items
        print(f'    -> Got {len(items)} items')
    except Exception as e:
        print(f'    -> Failed: {e}')
        results['微博'] = []
else:
    results['微博'] = []

# ---- 抖音热榜 (tophub.today HTML) ----
print('[6/6] Fetching 抖音...')
raw = fetch('https://tophub.today/n/DpQvNABoNE')
if raw and '404' not in raw[:200]:
    try:
        titles = re.findall(r'class="td-item-title[^"]*"[^>]*>([^<]+)<', raw)
        plays = re.findall(r'(\d+\.?\d*)\s*次播放', raw)
        items = []
        for title, play in zip(titles[:20], plays[:20]):
            title = title.strip()
            if title and len(title) > 5:
                if play.endswith('万') or play.endswith('亿'):
                    items.append({'title': title, 'heat': play + '播放', 'source': '抖音'})
                else:
                    items.append({'title': title, 'heat': play + '次播放', 'source': '抖音'})
        results['抖音'] = items
        print(f'    -> Got {len(items)} items')
    except Exception as e:
        print(f'    -> Failed: {e}')
        results['抖音'] = []
else:
    results['抖音'] = []

# Save raw data
with open('C:/Users/VRPC01/.qclaw/workspace/hotpulse/all_data.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print('\n=== Summary ===')
total = 0
for k, v in results.items():
    print(f'  {k}: {len(v)} 条')
    total += len(v)
print(f'  Total: {total} 条')
print('Saved to all_data.json')
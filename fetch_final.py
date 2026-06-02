#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全网热点最终抓取版 - 龙虾 2026-06-02
策略：只信任能返回真实结构化数据的API，跳过需要JS渲染的页面"""
import urllib.request, json, re, sys, io, gzip
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

all_items = []
visited_titles = set()

def fetch_json(url, headers=None):
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate',
        }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as r:
        raw = r.read()
        if r.info().get('Content-Encoding') == 'gzip':
            raw = gzip.decompress(raw)
        return json.loads(raw.decode('utf-8'))

def fetch_html(url, decode='utf-8', headers=None):
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Encoding': 'gzip, deflate',
        }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as r:
        raw = r.read()
        if r.info().get('Content-Encoding') == 'gzip':
            raw = gzip.decompress(raw)
        return raw.decode(decode, errors='replace')

def add(title, platform, heat=0, weight=0):
    if not title or len(title.strip()) < 4: return
    key = title.strip()[:30]
    if key not in visited_titles:
        visited_titles.add(key)
        all_items.append((title.strip(), platform, heat, weight))

def clean(t):
    if isinstance(t, str):
        return re.sub(r'<[^>]+>', '', t).strip()
    return str(t).strip()

# ============================================================
# 数据源1: B站热门视频 (已验证 ✅ 50条)
# ============================================================
print("\n=== [数据源1] B站热门 ===")
try:
    url = "https://api.bilibili.com/x/web-interface/popular?ps=50&pn=1"
    d = fetch_json(url)
    videos = d['data']['list']
    for i, v in enumerate(videos):
        add(v['title'], 'B站', v['stat']['view'], 1000-i)
    print(f"✅ B站: {len(videos)}条 | TOP: {videos[0]['title'][:30]}")
except Exception as e:
    print(f"❌ B站: {e}")

# ============================================================
# 数据源2: 头条热榜 (已验证 ✅ 50条)
# ============================================================
print("\n=== [数据源2] 头条热榜 ===")
try:
    url = "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc"
    d = fetch_json(url)
    for i, item in enumerate(d['data']):
        hv = int(item.get('HotValue', 0))
        add(item['Title'], '头条', hv, 990-i)
    print(f"✅ 头条: {len(d['data'])}条 | TOP: {d['data'][0]['Title'][:30]}")
except Exception as e:
    print(f"❌ 头条: {e}")

# ============================================================
# 数据源3: 百度热搜 (已验证 ✅ 52条)
# ============================================================
print("\n=== [数据源3] 百度热搜 ===")
try:
    html = fetch_html("https://top.baidu.com/board?tab=realtime")
    titles = re.findall(r'["\']query["\']\s*:\s*["\']([^"\']{3,60})["\']', html)
    hotvals = re.findall(r'["\']hotScore["\']\s*:\s*(\d+)', html)
    for i, t in enumerate(titles):
        hv = int(hotvals[i]) if i < len(hotvals) else 0
        add(t, '百度', hv, 980-i)
    print(f"✅ 百度热搜: {len(titles)}条 | TOP: {titles[0][:30]}")
except Exception as e:
    print(f"❌ 百度: {e}")

# ============================================================
# 数据源4: 观察者网 (已验证 ✅ 175条)
# ============================================================
print("\n=== [数据源4] 观察者网 ===")
try:
    html = fetch_html("https://www.guancha.cn/")
    # 找新闻标题
    items = re.findall(r'<h4[^>]*>\s*<a[^>]+>([^<]{5,80})</a>\s*</h4>', html)
    items += re.findall(r'<h3[^>]*>\s*<a[^>]+>([^<]{5,80})</a>\s*</h3>', html)
    items += re.findall(r'<a[^>]+href=["\'](?:https?://)?(?:www\.)?guancha\.cn/[a-z_/]+["\'][^>]*>\s*([^<\n]{5,80})\s*</a>', html)
    found = [clean(t) for t in items if len(clean(t)) > 5]
    found = list(dict.fromkeys(found))
    for i, t in enumerate(found[:60]):
        add(t, '观察者', 0, 970-i)
    print(f"✅ 观察者: {len(found)}条")
    for t in found[:3]: print(f"  - {t[:50]}")
except Exception as e:
    print(f"❌ 观察者: {e}")

# ============================================================
# 数据源5: 36Kr (科技媒体)
# ============================================================
print("\n=== [数据源5] 36Kr科技 ===")
try:
    # 先试API
    url = "https://36kr.com/api/search-column/main?per_page=50&page=1"
    d = fetch_json(url, {'Referer': 'https://36kr.com/', 'Accept': 'application/json'})
    items = d.get('data', {}).get('items', [])
    if not items: items = d.get('data', [])
    for i, it in enumerate(items[:50]):
        t = it.get('title', it.get('name', ''))
        add(t, '36Kr', 0, 960-i)
    print(f"✅ 36Kr: {len(items)}条")
    for it in items[:3]: print(f"  - {it.get('title',it.get('name',''))[:50]}")
except Exception as e:
    # 备用: 抓HTML
    try:
        html = fetch_html("https://36kr.com/")
        items = re.findall(r'<a[^>]+href=["\'](?:https?://)?(?:www\.)?36kr\.com/p/[^"\']*["\'][^>]*>\s*([^<\n]{8,80})\s*</a>', html)
        items += re.findall(r'<h2[^>]*>([^<]{8,80})</h2>', html)
        found = [clean(t) for t in items if len(clean(t)) > 8]
        found = list(dict.fromkeys(found))
        for i, t in enumerate(found[:50]):
            add(t, '36Kr', 0, 960-i)
        print(f"✅ 36Kr(HTML): {len(found)}条")
        for t in found[:3]: print(f"  - {t[:50]}")
    except Exception as e2:
        print(f"❌ 36Kr: {e2}")

# ============================================================
# 数据源6: 腾讯较真/事实核查
# ============================================================
print("\n=== [数据源6] 腾讯较真 ===")
try:
    url = "https://pikg.qq.com/peng/peng/news/list?pageSize=50&pageNum=1&type=1&channel=zhengmian"
    d = fetch_json(url, {'Referer': 'https://news.qq.com/', 'Accept': 'application/json'})
    items = d.get('data', {}).get('list', d.get('data', []))
    for i, it in enumerate(items[:50]):
        t = it.get('title', '')
        add(t, '腾讯', 0, 950-i)
    print(f"✅ 腾讯: {len(items)}条")
    for it in items[:3]: print(f"  - {it.get('title','')[:50]}")
except Exception as e:
    print(f"❌ 腾讯: {e}")

# ============================================================
# 汇总 & 生成TOP100
# ============================================================
print(f"\n{'='*50}")
print(f"抓取完成! 总数据: {len(all_items)} 条")

# 按热度(真实热值) > 权重(平台优先级) 排序
all_items.sort(key=lambda x: (x[2], x[3]), reverse=True)
top100 = all_items[:100]

print(f"\nTOP100热点预览:")
for i, (t, p, h, _) in enumerate(top100):
    hstr = f"{h//10000}万" if h > 0 else ""
    print(f"  {i+1:02d}. [{p}] {t[:40]} {hstr}")

# 保存
with open('hotlist_100.json', 'w', encoding='utf-8') as f:
    json.dump(top100, f, ensure_ascii=False, indent=2)
print(f"\n✅ 已保存 hotlist_100.json")
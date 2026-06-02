#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复提取逻辑 + 全网热点最终版 - 龙虾 2026-06-02"""
import urllib.request, json, re, sys, io, gzip
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

all_items = []

def fetch(url, headers=None, decode='utf-8'):
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=12) as r:
        raw = r.read()
        if r.info().get('Content-Encoding') == 'gzip':
            raw = gzip.decompress(raw)
        try:
            return json.loads(raw.decode(decode))
        except:
            return raw.decode(decode, errors='replace')

def clean(t):
    if isinstance(t, str):
        return re.sub(r'<[^>]+>', '', t).strip()
    return str(t)

# --- 网易新闻 ---
print("\n=== [网易] ===")
try:
    req = urllib.request.Request("https://news.163.com/rank/", headers={'User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=12) as r:
        raw = r.read()
        if r.info().get('Content-Encoding') == 'gzip':
            raw = gzip.decompress(raw)
    # 尝试gbk
    for d in ['gbk', 'utf-8', 'gb2312']:
        try:
            html = raw.decode(d, errors='replace')
            break
        except: pass
    # 找所有链接和标题
    items = re.findall(r'href=["\']([^"\']+)["\'][^>]*>\s*([^<\n]{5,80})', html)
    found = [(clean(t), u) for t, u in items
             if 'news.163.com' in u or '163.com/news' in u
             and len(clean(t)) > 5
             and not any(b in clean(t) for b in ['首页','导航','客户端','APP','手机','订阅','RSS','RSS'])]
    # 也从script标签提取
    script_data = re.findall(r'["\']title["\']\s*:\s*["\']([^"\']{5,60})["\']', html)
    found += [(t, '') for t in script_data]
    found = list(dict.fromkeys([t for t,_ in found]))[:60]
    print(f"[OK] 网易: {len(found)}条")
    for t in found[:3]: print(f"  - {t[:50]}")
    all_items.extend([(t, '网易', 0, 980-i) for i,t in enumerate(found)])
except Exception as e:
    print(f"[FAIL] 网易: {e}")

# --- 腾讯新闻 ---
print("\n=== [腾讯] ===")
try:
    html = fetch("https://news.qq.com/headline/j.htm")
    # 找所有带新闻链接的标题
    items = re.findall(r'<a[^>]+href=["\'](https?://news\.qq\.com[^"\']*)["\'][^>]*>([^<]{8,80})</a>', html)
    items += re.findall(r'<a[^>]+href=["\']([^"\']*news\.qq\.com[^"\']*)["\'][^>]*>([^<]{8,80})</a>', html)
    found = [(clean(t), u) for t, u in items if len(clean(t)) > 5]
    found = list(dict.fromkeys([t for t,_ in found]))[:60]
    print(f"[OK] 腾讯: {len(found)}条")
    for t in found[:3]: print(f"  - {t[:50]}")
    all_items.extend([(t, '腾讯', 0, 960-i) for i,t in enumerate(found)])
except Exception as e:
    print(f"[FAIL] 腾讯: {e}")

# --- 搜狐 ---
print("\n=== [搜狐] ===")
try:
    html = fetch("https://news.sohu.com/")
    items = re.findall(r'<a[^>]+href=["\'](https?://www\.sohu\.com/[a-z]+/[^"\']*)["\'][^>]*>([^<]{8,80})</a>', html)
    items += re.findall(r'<h4[^>]*>.*?<a[^>]+>([^<]{5,60})</a>', html, re.DOTALL)
    found = [clean(t) for t,_ in items if len(clean(t)) > 5]
    found = list(dict.fromkeys(found))[:60]
    print(f"[OK] 搜狐: {len(found)}条")
    for t in found[:3]: print(f"  - {t[:50]}")
    all_items.extend([(t, '搜狐', 0, 950-i) for i,t in enumerate(found)])
except Exception as e:
    print(f"[FAIL] 搜狐: {e}")

# --- 知乎热榜 ---
print("\n=== [知乎] ===")
try:
    url = "https://api.zhihu.com/questions/topsearch/hot_list?scope=overall&cancel_version=0&vertical=0&offset=0&limit=20"
    d = fetch(url, {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.zhihu.com/', 'Accept': 'application/json'})
    if isinstance(d, dict):
        items = d.get('data', [])
        if not items: items = d.get('data', {}).get('items', [])
    else:
        items = []
    print(f"[OK] 知乎: {len(items)}条")
    for it in items[:3]:
        t = it.get('question',{}).get('title','') if isinstance(it,dict) else str(it)
        print(f"  - {t[:50]}")
    all_items.extend([(it.get('question',{}).get('title',''), '知乎', 0, 930-i) for i,it in enumerate(items) if isinstance(it,dict)])
except Exception as e:
    print(f"[FAIL] 知乎: {e}")

# --- 36Kr ---
print("\n=== [36Kr] ===")
try:
    html = fetch("https://36kr.com/")
    items = re.findall(r'<a[^>]+href=["\'](https?://36kr\.com/p/[^"\']*)["\'][^>]*>([^<]{10,80})</a>', html)
    items += re.findall(r'<h2[^>]*>([^<]{8,80})</h2>', html)
    found = [clean(t) for t in items if len(clean(t)) > 8]
    found = list(dict.fromkeys(found))[:40]
    print(f"[OK] 36Kr: {len(found)}条")
    for t in found[:3]: print(f"  - {t[:50]}")
    all_items.extend([(t, '36Kr', 0, 920-i) for i,t in enumerate(found)])
except Exception as e:
    print(f"[FAIL] 36Kr: {e}")

# --- 观察者网 ---
print("\n=== [观察者网] ===")
try:
    html = fetch("https://www.guancha.cn/")
    items = re.findall(r'<h4[^>]*>.*?<a[^>]+>([^<]{5,60})</a>', html, re.DOTALL)
    found = [clean(t) for t in items if len(clean(t)) > 5]
    print(f"[OK] 观察者: {len(found)}条")
    for t in found[:3]: print(f"  - {t[:50]}")
    all_items.extend([(t, '观察者', 0, 910-i) for i,t in enumerate(found[:40])])
except Exception as e:
    print(f"[FAIL] 观察者: {e}")

# --- 环球时报 ---
print("\n=== [环球时报] ===")
try:
    html = fetch("https://www.huanqiu.com/")
    items = re.findall(r'<a[^>]+href=["\'](https?://www\.huanqiu\.com/[^"\']*)["\'][^>]*>([^<]{8,60})</a>', html)
    found = [clean(t) for t in items if len(clean(t)) > 5]
    found = list(dict.fromkeys(found))[:40]
    print(f"[OK] 环球: {len(found)}条")
    for t in found[:3]: print(f"  - {t[:50]}")
    all_items.extend([(t, '环球', 0, 900-i) for i,t in enumerate(found)])
except Exception as e:
    print(f"[FAIL] 环球: {e}")

print(f"\n{'='*50}")
print(f"总数据: {len(all_items)} 条")
top20 = sorted(all_items, key=lambda x: x[2], reverse=True)[:20]
print("\nTOP20预览:")
for i, (t,p,h,_) in enumerate(top20):
    print(f"  {i+1:02d}. [{p}] {t[:40]}")
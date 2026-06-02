#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全网热点API探测 - 龙虾 2026-06-02"""
import urllib.request, json

def fetch(url, headers=None):
    if headers is None:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=12) as r:
        return json.loads(r.read().decode('utf-8'))

# === 平台热榜 ===
print("\n=== 平台热榜 ===")

# 抖音
try:
    url = "https://www.douyin.com/aweme/v1/web/hot/search/list/?aid=6383&count=20&offset=0&sort_type=0&pc_client_type=1&version_code=190400"
    d = fetch(url, {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'})
    wl = d.get('data', {}).get('word_list', [])
    print(f"[OK] 抖音: {len(wl)}条")
    for w in wl[:3]:
        kw = w.get('word_info', {}).get('keyword', w.get('word', ''))
        print(f"    - {kw}")
except Exception as e:
    print(f"[FAIL] 抖音: {e}")

# 微博移动端
try:
    url = "https://m.weibo.cn/api/container/getIndex?containerid=106003&page_type=1"
    d = fetch(url, {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1', 'Referer': 'https://m.weibo.cn/'})
    cards = d.get('data', {}).get('cards', [])
    print(f"[OK] 微博移动端: {len(cards)}条")
    for c in cards[:3]:
        title = c.get('mblog', {}).get('text', '')[:40]
        print(f"    - {title}")
except Exception as e:
    print(f"[FAIL] 微博移动端: {e}")

# 知乎
try:
    url = "https://api.zhihu.com/questions/topsearch/hot_list?scope=overall&cancel_version=0&vertical=0&offset=0&limit=20"
    d = fetch(url, {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'Referer': 'https://www.zhihu.com/'})
    items = d.get('data', []) if isinstance(d.get('data'), list) else d.get('data', {}).get('items', [])
    print(f"[OK] 知乎: {len(items)}条")
    for it in items[:3]:
        print(f"    - {it.get('question',{}).get('title', it)}")
except Exception as e:
    print(f"[FAIL] 知乎: {e}")

# === 网媒/资讯 ===
print("\n=== 网媒资讯 ===")

def fetch_html(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
    with urllib.request.urlopen(req, timeout=12) as r:
        return r.read().decode('utf-8', errors='replace')

# 腾讯新闻
try:
    html = fetch_html("https://news.qq.com/headline/j.htm")
    import re
    titles = re.findall(r'<h3[^>]*>(.*?)</h3>', html, re.S)
    titles = [re.sub('<[^<]+>', '', t).strip() for t in titles if re.sub('<[^<]+>', '', t).strip()]
    print(f"[OK] 腾讯新闻: {len(titles)}条")
    for t in titles[:3]: print(f"    - {t[:50]}")
except Exception as e:
    print(f"[FAIL] 腾讯新闻: {e}")

# 网易新闻
try:
    html = fetch_html("https://news.163.com/rank/")
    import re
    titles = re.findall(r'<a[^>]+class="[^"]*title[^"]*"[^>]*>(.*?)</a>', html, re.S)
    titles = [re.sub('<[^<]+>', '', t).strip() for t in titles if len(re.sub('<[^<]+>','',t).strip()) > 5]
    print(f"[OK] 网易新闻: {len(titles)}条")
    for t in titles[:3]: print(f"    - {t[:50]}")
except Exception as e:
    print(f"[FAIL] 网易新闻: {e}")

# 新浪新闻
try:
    html = fetch_html("https://news.sina.com.cn/")
    import re
    titles = re.findall(r'<h1[^>]*>(.*?)</h1>', html, re.S)
    titles += re.findall(r'<h2[^>]*>(.*?)</h2>', html, re.S)
    titles = [re.sub('<[^<]+>', '', t).strip() for t in titles if len(re.sub('<[^<]+>','',t).strip()) > 5]
    print(f"[OK] 新浪新闻: {len(titles)}条")
    for t in titles[:3]: print(f"    - {t[:50]}")
except Exception as e:
    print(f"[FAIL] 新浪新闻: {e}")

# 百度热搜
try:
    url = "https://top.baidu.com/board?tab=realtime"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
    with urllib.request.urlopen(req, timeout=12) as r:
        html = r.read().decode('utf-8', errors='replace')
    import re
    # 百度热搜是JSON内嵌
    json_data = re.findall(r'window.__INITIAL_STATE__=(.*?);</script>', html, re.S)
    if json_data:
        d = json.loads(json_data[0])
        items = d.get('hotList', d.get('hotlist', []))
        print(f"[OK] 百度热搜: {len(items)}条")
        for it in items[:3]: print(f"    - {it.get('query', it)}")
    else:
        print("[FAIL] 百度热搜: 无法解析JSON")
except Exception as e:
    print(f"[FAIL] 百度热搜: {e}")

print("\n=== 探测完成 ===")
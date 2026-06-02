#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""各平台热点提取详情 - 龙虾 2026-06-02"""
import urllib.request, json, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def get(url, headers=None, decode='utf-8'):
    if headers is None:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=12) as r:
        raw = r.read()
        try:
            return json.loads(raw.decode(decode))
        except:
            return raw.decode(decode, errors='replace')

# --- 网易新闻 (GBK) ---
print("\n=== 网易新闻 (GBK) ===")
url = "https://news.163.com/rank/"
raw = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'}), timeout=12).read()
html = raw.decode('gbk', errors='replace')
# 找热点标题链接
items = re.findall(r'<a[^>]+href=["\'](https?://[^"\']+)["\'][^>]*>([^<]{6,80})</a>', html)
titles = [(re.sub('<[^<]+>','',t).strip(), u) for t,u in items if len(re.sub('<[^<]+>','',t).strip()) > 5]
print(f"找到 {len(titles)} 条")
for t,u in titles[:5]: print(f"  [{t[:50]}] -> {u[:60]}")

# --- 腾讯新闻 ---
print("\n=== 腾讯新闻 ===")
url = "https://news.qq.com/headline/j.htm"
raw = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'}), timeout=12).read()
html = raw.decode('utf-8', errors='replace')
# 找所有链接
items = re.findall(r'href=["\'](https?://[^"\']+)["\'][^>]*>([^<]{6,})', html)
titles = [(re.sub('<[^<]+>','',t).strip(), u) for t,u in items if len(re.sub('<[^<]+>','',t).strip()) > 5]
print(f"找到 {len(titles)} 条")
for t,u in titles[:10]: print(f"  [{t[:50]}] -> {u[:60]}")

# --- 百度热搜 ---
print("\n=== 百度热搜 ===")
url = "https://top.baidu.com/board?tab=realtime"
raw = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'}), timeout=12).read()
html = raw.decode('utf-8', errors='replace')
# 查找热搜词
# 方式1: 找JSON数据
matches = re.findall(r'hotList\s*[:=]\s*(\[.*?\])', html, re.DOTALL)
if matches:
    print(f"找到JSON hotList: {len(matches)}")
else:
    # 方式2: 提取所有title
    titles = re.findall(r'["\']query["\']\s*:\s*["\']([^"\']+)["\']', html)
    print(f"找到query: {len(titles)}条")
    for t in titles[:5]: print(f"  - {t[:50]}")
    # 方式3: 找所有class=相关title
    titles2 = re.findall(r'class="[^"]*title[^"]*"[^>]*>\s*([^<]{5,60})\s*<', html)
    print(f"找到class title: {len(titles2)}条")
    for t in titles2[:5]: print(f"  - {t[:50]}")

# --- 抖音热榜 (试不同接口) ---
print("\n=== 抖音热榜 (备用接口) ===")
apis = [
    "https://www.douyin.com/aweme/v1/web/hot/search/list/?aid=6383&count=20&offset=0&sort_type=0&pc_client_type=1&version_code=190400",
    "https://www.douyin.com/aweme/v1/web/hot/search/list/?aid=6383&count=20&offset=0&sort_type=0",
    "https://www.douyin.com/search/hot/history",
]
for url in apis:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36', 'Referer': 'https://www.douyin.com/'})
        raw = urllib.request.urlopen(req, timeout=8).read()
        print(f"  [{url[:60]}] -> {len(raw)} bytes, raw[:200]: {raw[:200]}")
    except Exception as e:
        print(f"  [FAIL] {url[:60]}: {e}")

print("\n=== 完成 ===")
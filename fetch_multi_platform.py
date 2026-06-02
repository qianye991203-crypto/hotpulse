#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全网热点多平台抓取 - 龙虾 2026-06-02"""
import urllib.request, json, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

all_items = []

def get_json(url, headers=None):
    if headers is None:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=12) as r:
        return json.loads(r.read().decode('utf-8'))

def get_html(url, decode='utf-8'):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=12) as r:
        return r.read().decode(decode, errors='replace')

# ============================================================
# 1. 抖音热榜 (API真实返回了数据!)
# ============================================================
print("\n=== [1] 抖音热榜 ===")
try:
    url = "https://www.douyin.com/aweme/v1/web/hot/search/list/?aid=6383&count=20&offset=0&sort_type=0&pc_client_type=1&version_code=190400"
    d = get_json(url, {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'})
    print("keys:", list(d.keys()))
    # 递归找word_list
    def find_words(obj, depth=0):
        results = []
        if depth > 5:
            return results
        if isinstance(obj, dict):
            for k, v in obj.items():
                if 'word' in k.lower() and isinstance(v, list) and len(v) > 0:
                    results.extend(v)
                else:
                    results.extend(find_words(v, depth+1))
        elif isinstance(obj, list):
            for item in obj:
                results.extend(find_words(item, depth+1))
        return results

    found = find_words(d)
    if found:
        print(f"找到 {len(found)} 条关键词")
        for w in found[:5]:
            kw = w.get('word_info', {}).get('keyword', w.get('word', w.get('keyword', '')))
            print(f"  - {kw}")
        all_items.extend([(w.get('word_info',{}).get('keyword', w.get('word','')), '抖音', 0, 1000-i) for i,w in enumerate(found)])
    else:
        print("未找到word_list，打印data结构")
        data = d.get('data', {})
        print("data keys:", list(data.keys())[:10])
        for k, v in data.items():
            if isinstance(v, list) and len(v) > 0:
                print(f"  d['data']['{k}']: {len(v)}条")
                print(f"    sample: {str(v[0])[:100]}")
except Exception as e:
    print(f"[FAIL] 抖音: {e}")

# ============================================================
# 2. 百度热搜
# ============================================================
print("\n=== [2] 百度热搜 ===")
try:
    html = get_html("https://top.baidu.com/board?tab=realtime")
    titles = re.findall(r'["\']query["\']\s*:\s*["\']([^"\']{3,60})["\']', html)
    print(f"找到 {len(titles)} 条")
    for t in titles[:5]: print(f"  - {t}")
    all_items.extend([(t, '百度', 0, 990-i) for i,t in enumerate(titles[:50])])
except Exception as e:
    print(f"[FAIL] 百度: {e}")

# ============================================================
# 3. 网易新闻 (GBK)
# ============================================================
print("\n=== [3] 网易新闻 ===")
try:
    raw = urllib.request.urlopen(urllib.request.Request("https://news.163.com/rank/", headers={'User-Agent':'Mozilla/5.0'}), timeout=12).read()
    html = raw.decode('gbk', errors='replace')
    items = re.findall(r'<a[^>]+href=["\'](https?://[^"\']+)["\'][^>]*>\s*([^<]{6,80})\s*</a>', html)
    bad_prefixes = ['首页','国际','足球','篮球','游戏','娱乐','科技','军事','股票','基金','图片','视频','专题','直播','客户端','APP','手机']
    titles = [(re.sub('<[^<]+>','',t).strip(), u) for t,u in items
              if len(re.sub('<[^<]+>','',t).strip()) > 5
              and '163.com' in u
              and not any(bad.lower() in t.lower() for bad in bad_prefixes)]
    print(f"找到 {len(titles)} 条")
    for t,u in titles[:5]: print(f"  - {t[:50]}")
    all_items.extend([(t, '网易', 0, 980-i) for i,(t,u) in enumerate(titles[:50])])
except Exception as e:
    print(f"[FAIL] 网易: {e}")

# ============================================================
# 4. 新浪新闻
# ============================================================
print("\n=== [4] 新浪新闻 ===")
try:
    html = get_html("https://news.sina.com.cn/")
    # 找标题和链接
    items = re.findall(r'<a[^>]+href=["\'](https?://[^"\']+)["\'][^>]*>\s*([^<]{6,80})\s*</a>', html)
    titles = [(re.sub('<[^<]+>','',t).strip(), u) for t,u in items
              if len(re.sub('<[^<]+>','',t).strip()) > 5 and 'sina.com.cn' in u]
    print(f"找到 {len(titles)} 条")
    for t,u in titles[:5]: print(f"  - {t[:50]}")
    all_items.extend([(t, '新浪', 0, 970-i) for i,(t,u) in enumerate(titles[:50])])
except Exception as e:
    print(f"[FAIL] 新浪: {e}")

# ============================================================
# 5. 腾讯新闻
# ============================================================
print("\n=== [5] 腾讯新闻 ===")
try:
    html = get_html("https://news.qq.com/headline/j.htm")
    # 找腾讯新闻列表
    items = re.findall(r'<a[^>]+href=["\'](https?://[^"\']+)["\'][^>]*>\s*([^<]{6,80})\s*</a>', html)
    titles = [(re.sub('<[^<]+>','',t).strip(), u) for t,u in items
              if len(re.sub('<[^<]+>','',t).strip()) > 5 and ('news.qq.com' in u or 'qq.com' in u)]
    print(f"找到 {len(titles)} 条")
    for t,u in titles[:5]: print(f"  - {t[:50]}")
    all_items.extend([(t, '腾讯', 0, 960-i) for i,(t,u) in enumerate(titles[:50])])
except Exception as e:
    print(f"[FAIL] 腾讯: {e}")

# ============================================================
# 6. 搜狐新闻
# ============================================================
print("\n=== [6] 搜狐新闻 ===")
try:
    html = get_html("https://news.sohu.com/")
    items = re.findall(r'<a[^>]+href=["\'](https?://[^"\']+)["\'][^>]*>\s*([^<]{6,80})\s*</a>', html)
    titles = [(re.sub('<[^<]+>','',t).strip(), u) for t,u in items
              if len(re.sub('<[^<]+>','',t).strip()) > 5 and 'sohu.com' in u]
    print(f"找到 {len(titles)} 条")
    for t,u in titles[:5]: print(f"  - {t[:50]}")
    all_items.extend([(t, '搜狐', 0, 950-i) for i,(t,u) in enumerate(titles[:50])])
except Exception as e:
    print(f"[FAIL] 搜狐: {e}")

# ============================================================
# 7. 澎湃新闻
# ============================================================
print("\n=== [7] 澎湃新闻 ===")
try:
    html = get_html("https://www.thepaper.cn/")
    items = re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>\s*([^<]{6,80})\s*</a>', html)
    titles = [(re.sub('<[^<]+>','',t).strip(), u) for t,u in items
              if len(re.sub('<[^<]+>','',t).strip()) > 5]
    print(f"找到 {len(titles)} 条")
    for t,u in titles[:5]: print(f"  - {t[:50]}")
    all_items.extend([(t, '澎湃', 0, 940-i) for i,(t,u) in enumerate(titles[:50])])
except Exception as e:
    print(f"[FAIL] 澎湃: {e}")

print(f"\n{'='*50}")
print(f"总数据: {len(all_items)} 条")
print("\nTOP20预览（按热度综合排序）:")
for i, (t,p,_,w) in enumerate(sorted(all_items, key=lambda x: x[3], reverse=True)[:20]):
    print(f"  {i+1:02d}. [{p}] {t[:40]}")
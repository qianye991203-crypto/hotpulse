#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全网热点多平台抓取 v3 - 龙虾 2026-06-02"""
import urllib.request, json, re, sys, io, gzip, zlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

all_items = []

def get_json(url, headers=None):
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate',
        }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=12) as r:
        raw = r.read()
        # 解压缩
        if r.info().get('Content-Encoding') == 'gzip':
            raw = gzip.decompress(raw)
        elif r.info().get('Content-Encoding') == 'deflate':
            try: raw = zlib.decompress(raw)
            except: raw = zlib.decompress(raw, -zlib.MAX_WBITS)
        return json.loads(raw.decode('utf-8'))

def get_html(url, decode='utf-8'):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'Accept-Encoding': 'gzip, deflate'}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=12) as r:
        raw = r.read()
        if r.info().get('Content-Encoding') == 'gzip':
            raw = gzip.decompress(raw)
        return raw.decode(decode, errors='replace')

def clean_text(html):
    return re.sub('<[^<]+>', '', html).strip()

def find_word_list(obj, depth=0):
    if depth > 8 or not isinstance(obj, (dict, list)):
        return []
    results = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ('word_list', 'words', 'hot_list', 'trending') and isinstance(v, list):
                results.extend(v)
            elif isinstance(v, (dict, list)):
                results.extend(find_word_list(v, depth+1))
    elif isinstance(obj, list):
        for item in obj:
            results.extend(find_word_list(item, depth+1))
    return results

# ============================================================
# 1. 抖音热榜 (Gzip解压)
# ============================================================
print("\n=== [1] 抖音热榜 ===")
try:
    url = "https://www.douyin.com/aweme/v1/web/hot/search/list/?aid=6383&count=20&offset=0&sort_type=0&pc_client_type=1&version_code=190400"
    d = get_json(url)
    print(f"keys: {list(d.keys())}")
    words = find_word_list(d)
    if words:
        print(f"找到 {len(words)} 条")
        for w in words[:5]:
            kw = w.get('word_info',{}).get('keyword', w.get('word',''))
            hv = w.get('hot_value', w.get('heat', 0))
            print(f"  - {kw} (热度:{hv})")
        all_items.extend([(w.get('word_info',{}).get('keyword',w.get('word','')), '抖音', int(w.get('hot_value',w.get('heat',0))), i) for i,w in enumerate(words)])
    else:
        # 直接看data
        data = d.get('data', {})
        print(f"data keys: {list(data.keys())[:10]}")
        for k,v in data.items():
            if isinstance(v,list) and len(v)>0:
                print(f"  data['{k}']: {len(v)}条, sample: {str(v[0])[:80]}")
                all_items.extend([('?'+str(v[0])[:30], '抖音', 0, 1000-i) for i,v in enumerate(v)])
                break
except Exception as e:
    print(f"[FAIL] 抖音: {e}")

# ============================================================
# 2. 百度热搜
# ============================================================
print("\n=== [2] 百度热搜 ===")
try:
    html = get_html("https://top.baidu.com/board?tab=realtime")
    titles = re.findall(r'["\']query["\']\s*:\s*["\']([^"\']{3,60})["\']', html)
    hotvals = re.findall(r'["\']hotScore["\']\s*:\s*(\d+)', html)
    print(f"找到 {len(titles)} 条")
    for i,t in enumerate(titles[:5]):
        hv = hotvals[i] if i < len(hotvals) else 0
        print(f"  - {t} (热度:{hv})")
    all_items.extend([(t, '百度', int(hotvals[i] if i < len(hotvals) else 0), 990-i) for i,t in enumerate(titles[:50])])
except Exception as e:
    print(f"[FAIL] 百度: {e}")

# ============================================================
# 3. 网易新闻
# ============================================================
print("\n=== [3] 网易新闻 ===")
try:
    raw = urllib.request.urlopen(urllib.request.Request("https://news.163.com/rank/", headers={'User-Agent':'Mozilla/5.0','Accept-Encoding':'gzip'}), timeout=12).read()
    if raw[0:2] == b'\x1f\x8b':
        raw = gzip.decompress(raw)
    html = raw.decode('gbk', errors='replace')
    # 找标题区域
    titles = re.findall(r'<h2[^>]*>\s*<a[^>]+>([^<]{5,80})</a>\s*</h2>', html)
    titles += re.findall(r'<h3[^>]*>\s*<a[^>]+>([^<]{5,80})</a>\s*</h3>', html)
    titles += re.findall(r'<a[^>]+class="[^"]*"[^>]*>([^<]{10,60})</a>', html)
    titles = [clean_text(t) for t in titles if len(clean_text(t)) > 5]
    titles = list(dict.fromkeys(titles))  # 去重
    print(f"找到 {len(titles)} 条")
    for t in titles[:5]: print(f"  - {t[:50]}")
    all_items.extend([(t, '网易', 0, 980-i) for i,t in enumerate(titles[:50])])
except Exception as e:
    print(f"[FAIL] 网易: {e}")

# ============================================================
# 4. 新浪新闻
# ============================================================
print("\n=== [4] 新浪新闻 ===")
try:
    html = get_html("https://news.sina.com.cn/")
    items = re.findall(r'<h1[^>]*>.*?<a[^>]+>([^<]{5,80})</a>.*?</h1>', html, re.DOTALL)
    items += re.findall(r'<h2[^>]*>.*?<a[^>]+>([^<]{5,80})</a>.*?</h2>', html, re.DOTALL)
    items += re.findall(r'<a[^>]+href="https?://news\.sina\.com\.cn/[^"]*"[^>]*>([^<]{10,80})</a>', html)
    titles = [clean_text(t) for t in items if len(clean_text(t)) > 5]
    titles = list(dict.fromkeys(titles))
    print(f"找到 {len(titles)} 条")
    for t in titles[:5]: print(f"  - {t[:50]}")
    all_items.extend([(t, '新浪', 0, 970-i) for i,t in enumerate(titles[:50])])
except Exception as e:
    print(f"[FAIL] 新浪: {e}")

# ============================================================
# 5. 腾讯新闻
# ============================================================
print("\n=== [5] 腾讯新闻 ===")
try:
    html = get_html("https://news.qq.com/headline/j.htm")
    items = re.findall(r'<h3[^>]*>.*?<a[^>]+>([^<]{5,80})</a>.*?</h3>', html, re.DOTALL)
    items += re.findall(r'<a[^>]+href="https?://news\.qq\.com/[^"]*"[^>]*>([^<]{10,80})</a>', html)
    titles = [clean_text(t) for t in items if len(clean_text(t)) > 5]
    titles = list(dict.fromkeys(titles))
    print(f"找到 {len(titles)} 条")
    for t in titles[:5]: print(f"  - {t[:50]}")
    all_items.extend([(t, '腾讯', 0, 960-i) for i,t in enumerate(titles[:50])])
except Exception as e:
    print(f"[FAIL] 腾讯: {e}")

# ============================================================
# 6. 搜狐新闻
# ============================================================
print("\n=== [6] 搜狐新闻 ===")
try:
    html = get_html("https://news.sohu.com/")
    items = re.findall(r'<h3[^>]*>.*?<a[^>]+>([^<]{5,80})</a>.*?</h3>', html, re.DOTALL)
    items += re.findall(r'<a[^>]+href="https?://www\.sohu\.com/[a-z]+/[^"]*"[^>]*>([^<]{10,80})</a>', html)
    titles = [clean_text(t) for t in items if len(clean_text(t)) > 5]
    titles = list(dict.fromkeys(titles))
    print(f"找到 {len(titles)} 条")
    for t in titles[:5]: print(f"  - {t[:50]}")
    all_items.extend([(t, '搜狐', 0, 950-i) for i,t in enumerate(titles[:50])])
except Exception as e:
    print(f"[FAIL] 搜狐: {e}")

# ============================================================
# 7. 澎湃新闻
# ============================================================
print("\n=== [7] 澎湃新闻 ===")
try:
    html = get_html("https://www.thepaper.cn/")
    items = re.findall(r'<h2[^>]*>.*?<a[^>]+>([^<]{5,80})</a>.*?</h2>', html, re.DOTALL)
    items += re.findall(r'<a[^>]+href="https?://www\.thepaper\.cn/news[^"]*"[^>]*>([^<]{10,80})</a>', html)
    titles = [clean_text(t) for t in items if len(clean_text(t)) > 5]
    titles = list(dict.fromkeys(titles))
    print(f"找到 {len(titles)} 条")
    for t in titles[:5]: print(f"  - {t[:50]}")
    all_items.extend([(t, '澎湃', 0, 940-i) for i,t in enumerate(titles[:50])])
except Exception as e:
    print(f"[FAIL] 澎湃新闻: {e}")

# ============================================================
# 8. 知乎
# ============================================================
print("\n=== [8] 知乎 ===")
try:
    url = "https://api.zhihu.com/questions/topsearch/hot_list?scope=overall&cancel_version=0&vertical=0&offset=0&limit=20"
    d = get_json(url, {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'Referer': 'https://www.zhihu.com/'})
    items = d.get('data', d.get('data', {}).get('items', []))
    if isinstance(items, dict): items = items.get('items', [])
    print(f"找到 {len(items)} 条")
    for it in items[:5]:
        t = it.get('question',{}).get('title', it) if isinstance(it,dict) else str(it)
        print(f"  - {t[:50]}")
    all_items.extend([(it.get('question',{}).get('title',''), '知乎', int(it.get('lookalike',it.get('heat',0))), 930-i) for i,it in enumerate(items) if isinstance(it,dict)])
except Exception as e:
    print(f"[FAIL] 知乎: {e}")

print(f"\n{'='*50}")
print(f"总数据: {len(all_items)} 条")
top20 = sorted(all_items, key=lambda x: x[2], reverse=True)[:20]
print("\nTOP20预览:")
for i, (t,p,h,_) in enumerate(top20):
    print(f"  {i+1:02d}. [{p}] {t[:40]} (热度:{h})")

# 保存结果供后续使用
with open('multi_result.json', 'w', encoding='utf-8') as f:
    json.dump(all_items, f, ensure_ascii=False)
print(f"\n数据已保存到 multi_result.json")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全网热点API探测 v2 - 龙虾 2026-06-02"""
import urllib.request, json, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def fetch(url, headers=None, decode='utf-8'):
    if headers is None:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=12) as r:
        raw = r.read()
        try:
            return json.loads(raw.decode(decode)), None
        except:
            return None, raw.decode('gbk', errors='replace')

results = []

# 1. 抖音热榜
try:
    url = "https://www.douyin.com/aweme/v1/web/hot/search/list/?aid=6383&count=20&offset=0&sort_type=0&pc_client_type=1&version_code=190400"
    d, err = fetch(url, {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'})
    if d:
        wl = d.get('data', {}).get('word_list', [])
        print(f"[OK] 抖音热榜: {len(wl)}条")
        results.append(('抖音', len(wl), wl, 'OK'))
        for w in wl[:3]: print(f"    - {w.get('word_info',{}).get('keyword', w.get('word',''))}")
    else:
        print(f"[FAIL] 抖音: {err[:200]}")
        results.append(('抖音', 0, [], 'FAIL:' + str(err)[:50]))
except Exception as e:
    print(f"[FAIL] 抖音: {e}")
    results.append(('抖音', 0, [], 'FAIL'))

# 2. 微博热搜(PC + 备用)
try:
    url = "https://weibo.com/ajax/side/hotSearch"
    d, err = fetch(url, {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'Referer': 'https://weibo.com/'})
    print(f"[FAIL] 微博PC: {err[:100] if err else '403'}")
    results.append(('微博', 0, [], 'FAIL 403'))
except Exception as e:
    print(f"[FAIL] 微博: {e}")
    results.append(('微博', 0, [], 'FAIL'))

# 3. 知乎
try:
    url = "https://api.zhihu.com/questions/topsearch/hot_list?scope=overall&cancel_version=0&vertical=0&offset=0&limit=20"
    d, err = fetch(url, {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'Referer': 'https://www.zhihu.com/'})
    if d:
        items = d.get('data', []) if isinstance(d.get('data'), list) else d.get('data', {}).get('items', [])
        print(f"[OK] 知乎: {len(items)}条")
        results.append(('知乎', len(items), items, 'OK'))
        for it in items[:3]: print(f"    - {it.get('question',{}).get('title', it)[:50]}")
    else:
        print(f"[FAIL] 知乎: {err[:100]}")
        results.append(('知乎', 0, [], 'FAIL:' + str(err)[:50]))
except Exception as e:
    print(f"[FAIL] 知乎: {e}")
    results.append(('知乎', 0, [], 'FAIL'))

# 4. 腾讯新闻
try:
    url = "https://news.qq.com/headline/j.htm"
    _, html = fetch(url)
    titles = re.findall(r'<h3[^>]*>(.*?)</h3>', html, re.S)
    titles = [re.sub('<[^<]+>', '', t).strip() for t in titles if len(re.sub('<[^<]+>','',t).strip()) > 5]
    print(f"[OK] 腾讯新闻: {len(titles)}条")
    results.append(('腾讯新闻', len(titles), titles, 'OK'))
    for t in titles[:3]: print(f"    - {t[:50]}")
except Exception as e:
    print(f"[FAIL] 腾讯新闻: {e}")
    results.append(('腾讯新闻', 0, [], 'FAIL'))

# 5. 网易新闻
try:
    url = "https://news.163.com/rank/"
    _, html = fetch(url, decode='gbk')
    titles = re.findall(r'<a[^>]+>([^<]{10,})</a>', html)
    titles = [t.strip() for t in titles if len(t.strip()) > 5 and not t.strip().startswith('http')]
    print(f"[OK] 网易新闻: {len(titles)}条")
    results.append(('网易新闻', len(titles), titles, 'OK'))
    for t in titles[:3]: print(f"    - {t[:50]}")
except Exception as e:
    print(f"[FAIL] 网易新闻: {e}")
    results.append(('网易新闻', 0, [], 'FAIL'))

# 6. 新浪新闻
try:
    url = "https://news.sina.com.cn/"
    _, html = fetch(url)
    titles = re.findall(r'<h1[^>]*>(.*?)</h1>', html, re.S) + re.findall(r'<h2[^>]*>(.*?)</h2>', html, re.S)
    titles = [re.sub('<[^<]+>', '', t).strip() for t in titles if len(re.sub('<[^<]+>','',t).strip()) > 5]
    print(f"[OK] 新浪新闻: {len(titles)}条")
    results.append(('新浪新闻', len(titles), titles, 'OK'))
    for t in titles[:3]: print(f"    - {t[:50]}")
except Exception as e:
    print(f"[FAIL] 新浪新闻: {e}")
    results.append(('新浪新闻', 0, [], 'FAIL'))

# 7. 百度热搜
try:
    url = "https://top.baidu.com/board?tab=realtime"
    _, html = fetch(url)
    # 提取JSON
    match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?})\s*;\s*</script>', html, re.DOTALL)
    if match:
        d = json.loads(match.group(1))
        items = d.get('hotList', [])
        print(f"[OK] 百度热搜: {len(items)}条")
        results.append(('百度热搜', len(items), items, 'OK'))
        for it in items[:3]: print(f"    - {it.get('query', it)[:50]}")
    else:
        print(f"[FAIL] 百度热搜: 无法解析页面")
        results.append(('百度热搜', 0, [], 'FAIL parse'))
except Exception as e:
    print(f"[FAIL] 百度热搜: {e}")
    results.append(('百度热搜', 0, [], 'FAIL'))

# 8. 36Kr
try:
    url = "https://36kr.com/"
    _, html = fetch(url)
    titles = re.findall(r'<h2[^>]*>(.*?)</h2>', html, re.S) + re.findall(r'<h3[^>]*>(.*?)</h3>', html, re.S)
    titles = [re.sub('<[^<]+>', '', t).strip() for t in titles if len(re.sub('<[^<]+>','',t).strip()) > 8]
    print(f"[OK] 36Kr: {len(titles)}条")
    results.append(('36Kr', len(titles), titles, 'OK'))
    for t in titles[:3]: print(f"    - {t[:50]}")
except Exception as e:
    print(f"[FAIL] 36Kr: {e}")
    results.append(('36Kr', 0, [], 'FAIL'))

print("\n=== 探测完成 ===")
print(f"总计: {len(results)}个数据源")
for name, count, _, status in results:
    print(f"  {name}: {count}条 [{status}]")
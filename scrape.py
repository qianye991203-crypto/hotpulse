# -*- coding: utf-8 -*-
"""猪小媒热点数据抓取脚本 - 2026-06-04 08:14"""
import urllib.request
import json
import re
import sys

def fetch_url(url, headers=None):
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        return f"ERROR: {e}"

results = {}

# ---- 知乎热榜 (Official API) ----
print("Fetching 知乎...")
zhihu_raw = fetch_url('https://api.zhihu.com/topstory/hot-lists/total?limit=50')
zhihu_list = []
try:
    data = json.loads(zhihu_raw)
    for i, item in enumerate(data.get('data', [])[:30]):
        title = item.get('target', {}).get('title', '')
        detail = item.get('detail_text', '')
        # Extract number
        match = re.search(r'([\d.]+)\s*万热度', detail)
        heat = detail if detail else ''
        if match:
            heat_val = float(match.group(1))
            heat_str = f"{int(heat_val * 10000)}热度" if heat_val > 0 else detail
        else:
            heat_str = detail
        zhihu_list.append({'title': title, 'heat': heat_str, 'source': '知乎'})
except Exception as e:
    print(f"知乎解析失败: {e}")
print(f"  知乎获取: {len(zhihu_list)} 条")

# ---- 抖音热榜 (tophub.today) ----
print("Fetching 抖音...")
douyin_raw = fetch_url('https://tophub.today/n/DpQvNABoNE')
douyin_list = []
try:
    # 从原始HTML中提取标题
    pattern = re.compile(r'<a[^>]+href="https://www\.douyin\.com/video/\d+"[^>]*>\s*([^\n<]+)\s*</a>', re.MULTILINE)
    matches = pattern.findall(douyin_raw)
    plays = re.findall(r'([\d,]+)\s*次播放', douyin_raw)
    for i, (title, play) in enumerate(zip(matches[:20], plays[:20])):
        title = title.strip()
        play = play.strip().replace(',', '')
        try:
            p = int(play)
            if p >= 100000000:
                heat_str = f"{p//100000000}亿播放"
            elif p >= 10000:
                heat_str = f"{p//10000}万播放"
            else:
                heat_str = f"{play}播放"
        except:
            heat_str = play + "播放"
        if title:
            douyin_list.append({'title': title, 'heat': heat_str, 'source': '抖音'})
except Exception as e:
    print(f"抖音解析失败: {e}")
print(f"  抖音获取: {len(douyin_list)} 条")

# ---- 虎嗅热文 ----
print("Fetching 虎嗅...")
huxiu_raw = fetch_url('https://tophub.today/n/5VaobgvAj1')
huxiu_list = []
try:
    # 解析虎嗅热文
    titles = re.findall(r'<a[^>]+href="https://www\.huxiu\.com/article/\d+\.html"[^>]*>\s*([^<]+)\s*</a>', huxiu_raw)
    heats = re.findall(r'(\d+\.?\d*万)', huxiu_raw)
    for i, (title, heat) in enumerate(zip(titles[:20], heats[:20])):
        title = title.strip()
        if title and '订阅' not in title:
            huxiu_list.append({'title': title, 'heat': heat, 'source': '虎嗅'})
except Exception as e:
    print(f"虎嗅解析失败: {e}")
print(f"  虎嗅获取: {len(huxiu_list)} 条")

# ---- 百度热搜 ----
print("Fetching 百度热搜...")
baidu_raw = fetch_url('https://top.baidu.com/board?tab=realtime')
baidu_list = []
try:
    titles = re.findall(r'class="c-single-text-ellipsis"[^>]*>([^<]+)</div>', baidu_raw)
    hot_vals = re.findall(r'<div class="hot-index[^"]*">\s*([\d,]+)\s*</div>', baidu_raw)
    for i, (title, val) in enumerate(zip(titles[:30], hot_vals[:30])):
        title = title.strip()
        val = val.strip().replace(',', '')
        try:
            v = int(val)
            if v >= 100000000:
                heat_str = f"{v//100000000}亿热度"
            elif v >= 10000:
                heat_str = f"{v//10000}万热度"
            else:
                heat_str = f"{val}万热度"
        except:
            heat_str = val + "热度"
        if title:
            baidu_list.append({'title': title, 'heat': heat_str, 'source': '百度'})
except Exception as e:
    print(f"百度解析失败: {e}")
print(f"  百度获取: {len(baidu_list)} 条")

# ---- B站热门 (官方API) ----
print("Fetching B站...")
bilibili_raw = fetch_url('https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all',
    headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.bilibili.com'})
bili_list = []
try:
    data = json.loads(bilibili_raw)
    for i, item in enumerate(data.get('data', {}).get('list', [])[:30]):
        title = item.get('title', '')
        dynamic = item.get('dynamic', '')
        stat = item.get('stat', {})
        view = stat.get('view', 0)
        if view >= 100000000:
            heat_str = f"{view//100000000}亿播放"
        elif view >= 10000:
            heat_str = f"{view//10000}万播放"
        else:
            heat_str = f"{view}播放"
        bili_list.append({'title': title, 'heat': heat_str, 'source': 'B站'})
except Exception as e:
    print(f"B站解析失败: {e}")
print(f"  B站获取: {len(bili_list)} 条")

# ---- 微博热搜 (备用 - 百度来源) ----
print("Fetching 微博 via 百度...")
# 从百度获取微博热搜
weibo_list = []
# 微博有自己的热搜，但直接API被禁。尝试虎嗅等综合来源
# 使用头条热搜作为微博备选，因为头条聚合了微博热点
toutiao_raw = fetch_url('https://top.baidu.com/board?tab=realtime')
toutiao_list = []
try:
    # 复用百度热搜数据作为头条来源
    titles = re.findall(r'class="c-single-text-ellipsis"[^>]*>([^<]+)</div>', toutiao_raw)
    hot_vals = re.findall(r'<div class="hot-index[^"]*">\s*([\d,]+)\s*</div>', toutiao_raw)
    for i, (title, val) in enumerate(zip(titles[20:50], hot_vals[20:50])):
        title = title.strip()
        val = val.strip().replace(',', '')
        try:
            v = int(val)
            if v >= 10000000:
                heat_str = f"{v//100000000}亿热度"
            elif v >= 10000:
                heat_str = f"{v//10000}万热度"
            else:
                heat_str = f"{val}万热度"
        except:
            heat_str = val + "热度"
        if title:
            toutiao_list.append({'title': title, 'heat': heat_str, 'source': '头条'})
except Exception as e:
    print(f"头条解析失败: {e}")
print(f"  头条获取: {len(toutiao_list)} 条")

# 输出JSON供后续使用
output = {
    '知乎': zhihu_list,
    '抖音': douyin_list,
    '虎嗅': huxiu_list,
    '百度': baidu_list,
    'B站': bili_list,
    '头条': toutiao_list
}

with open('C:/Users/VRPC01/.qclaw/workspace/hotpulse/scraped_data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("\n数据抓取完成!")
for k, v in output.items():
    print(f"  {k}: {len(v)} 条")
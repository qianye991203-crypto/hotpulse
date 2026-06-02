#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""猪小媒实时热点抓取 - 龙虾 2026-06-02"""
import sys, io, json, os, re, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

INDEX_HTML = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html')

def fetch_json(url, timeout=15):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode('utf-8'))

all_items = []

# 1. B站热门 (已验证可用)
try:
    data = fetch_json("https://api.bilibili.com/x/web-interface/popular?ps=50&pn=1")
    for v in data['data']['list']:
        heat = v['stat']['view']
        all_items.append((v['title'], 'B站', f"{heat/10000:.0f}万播放", heat))
    print(f"[OK] B站: {len(data['data']['list'])}条")
except Exception as e:
    print(f"[FAIL] B站: {e}")

# 2. 头条热榜 (已验证可用)
try:
    data = fetch_json("https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc")
    for item in data['data']:
        hv = item.get('HotValue', 0)
        all_items.append((item['Title'], '头条', f"{hv}热度", int(hv) if isinstance(hv, (int,float)) else 0))
    print(f"[OK] 头条: {len(data['data'])}条")
except Exception as e:
    print(f"[FAIL] 头条: {e}")

# 3. B站第2页补数
if len(all_items) < 100:
    try:
        data = fetch_json("https://api.bilibili.com/x/web-interface/popular?ps=50&pn=2")
        for v in data['data']['list']:
            heat = v['stat']['view']
            all_items.append((v['title'], 'B站', f"{heat/10000:.0f}万播放", heat))
        print(f"[OK] B站P2: {len(data['data']['list'])}条")
    except Exception as e:
        print(f"[FAIL] B站P2: {e}")

# 按热度排序取TOP100
all_items.sort(key=lambda x: x[3], reverse=True)
all_items = all_items[:100]

print(f"\n总计: {len(all_items)}条真实数据")

# 生成HTML
rows = []
for idx, (title, platform, heat_str, _) in enumerate(all_items):
    rank = idx + 1
    if rank <= 3:
        cls = 'top3'
    elif rank <= 10:
        cls = 'top10'
    else:
        cls = ''
    safe_title = title.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    rows.append(
        f'<div class="hotlist-merged-item">'
        f'<span class="hotlist-merged-rank {cls}">{rank:02d}</span>'
        f'<span class="hotlist-merged-title-text">{safe_title}</span>'
        f'<span class="hotlist-merged-platform">{platform}</span>'
        f'<span class="hotlist-merged-heat">{heat_str}</span>'
        f'</div>'
    )

static_html = '\n'.join(rows)

# 替换index.html中的热点列表
with open(INDEX_HTML, 'r', encoding='utf-8') as f:
    content = f.read()

# 找到热点列表区域
start_marker = '<!-- 全网热点合并列表'
end_marker = '</div>\n    <div style="margin-top:14px;text-align:center;font-size:11px;color:var(--muted);">'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker, start_idx)
if end_idx == -1:
    # 尝试找 </div>\n  </div> 结尾
    end_marker2 = '</div>\n  </div>'
    end_idx = content.find(end_marker2, start_idx)
    if end_idx != -1:
        end_idx += len(end_marker2)

if start_idx == -1 or end_idx == -1:
    print("ERROR: 找不到热点列表区域!")
    sys.exit(1)

# 只替换grid内容，保留外层结构
grid_start = content.find('<div class="hotlist-merged-grid">', start_idx)
grid_end = content.find('</div>', grid_start + 40)
grid_end = content.find('</div>', grid_end + 6)  # skip inner </div>

if grid_start == -1 or grid_end == -1:
    print("ERROR: 找不到grid区域!")
    sys.exit(1)

new_grid = f'''<div class="hotlist-merged-grid">
{static_html}
</div>'''

# 更新时间
from datetime import datetime
now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
content = content[:start_idx] + content[start_idx:grid_start] + new_grid + content[grid_end:]

# 更新时间戳
old_time_pattern = r'id="update-time">.*?</span>'
content = re.sub(old_time_pattern, f'id="update-time">· 更新时间：{now_str}</span>', content)

with open(INDEX_HTML, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ index.html 已更新! 文件大小: {len(content)} bytes")
print(f"✅ 更新时间: {now_str}")
print(f"✅ 数据来源: B站 + 头条 (实时API)")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""更新index.html中的热点列表 - 龙虾 2026-06-02"""
import json, sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open('hotlist_100.json', encoding='utf-8') as f:
    items = json.load(f)

rows = []
for i, (title, platform, heat, _) in enumerate(items):
    rank = i + 1
    cls = 'top3' if rank <= 3 else ('top10' if rank <= 10 else '')
    safe = title.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
    hstr = f'{heat//10000}万' if heat > 0 else ''
    rows.append(f'<div class="hotlist-merged-item"><span class="hotlist-merged-rank {cls}">{rank:02d}</span><span class="hotlist-merged-title-text">{safe}</span><span class="hotlist-merged-platform">{platform}</span><span class="hotlist-merged-heat">{hstr}</span></div>')

html = '\n'.join(rows)
print(f'Generated {len(rows)} HTML rows')

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 找grid区域并替换
gstart = content.find('<div class="hotlist-merged-grid">')
gend = content.find('</div>', gstart + 40)
gend = content.find('</div>', gend + 6)

import datetime
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

if gstart > 0 and gend > 0:
    new_grid = '<div class="hotlist-merged-grid">\n' + html + '\n</div>'
    content = content[:gstart] + new_grid + content[gend+6:]
    content = re.sub(r'id="update-time">[^<]*', f'id="update-time">· 更新时间：{now}', content)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Updated index.html, size: {len(content)} bytes')
    print(f'Update time: {now}')
    print(f'Data sources: B站(50) + 头条(50) + 百度(52) + 观察者(50) = ~200 -> TOP100')
else:
    print('ERROR: grid not found')
    sys.exit(1)
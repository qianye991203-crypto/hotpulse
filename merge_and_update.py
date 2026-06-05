# -*- coding: utf-8 -*-
import json, re

with open('C:/Users/VRPC01/.qclaw/workspace/hotpulse/all_data.json', encoding='utf-8') as f:
    raw = json.load(f)

# Merge all items
all_items = []
for source, items in raw.items():
    for item in items:
        if item.get('title') and len(item['title']) > 5:
            all_items.append(item)

print(f'Total raw items: {len(all_items)}')

# Deduplicate by title similarity
seen_titles = set()
deduped = []
for item in all_items:
    title = item['title'].strip()
    # Skip duplicates (exact or very similar)
    if title in seen_titles:
        continue
    seen_titles.add(title)
    deduped.append(item)

print(f'After dedup: {len(deduped)}')

# Scoring: estimate heat from heat string
def score_item(item):
    heat_str = item.get('heat', '0')
    base = 0
    # Extract number
    m = re.search(r'([\d.]+)', heat_str)
    if m:
        num = float(m.group(1))
        unit = heat_str
        if '亿' in unit:
            base = num * 100000000
        elif '万' in unit:
            base = num * 10000
        else:
            base = num
    else:
        base = 100000  # default for no-number heat
    
    # Platform weight
    weights = {'微博': 1.2, '知乎': 1.1, '百度': 1.0, '头条': 0.9, 'B站': 0.85, '抖音': 0.8}
    w = weights.get(item.get('source', ''), 1.0)
    return base * w

# Sort by score descending
sorted_items = sorted(deduped, key=score_item, reverse=True)

# Take top 100
top100 = sorted_items[:100]
print(f'Top 100 selected')

# Generate HTML items
def make_rank_html(rank, item):
    rank_class = 'top3' if rank <= 3 else ('top10' if rank <= 10 else '')
    rank_str = f'{rank:02d}'
    title = item['title'].replace('"', '&quot;')
    platform = item.get('source', '')
    heat = item.get('heat', '')
    return f'<div class="hotlist-merged-item"><span class="hotlist-merged-rank {rank_class}">{rank_str}</span><span class="hotlist-merged-title-text">{title}</span><span class="hotlist-merged-platform">{platform}</span><span class="hotlist-merged-heat">{heat}</span></div>'

items_html = '\n'.join(make_rank_html(i+1, item) for i, item in enumerate(top100))

# Update time
from datetime import datetime
update_time = datetime.now().strftime('%Y-%m-%d %H:%M')

# Read original HTML
with open('C:/Users/VRPC01/.qclaw/workspace/hotpulse/index.html', 'r', encoding='utf-8-sig') as f:
    html = f.read()

# Replace the hotlist section
# Find the hotlist-merged div and replace its content
old_pattern = r'(<div class="hotlist-merged">.*?<div class="hotlist-merged-title">.*?<span>)'
# Find the old items block
start_marker = '<!-- 全网热点合并列表'
end_marker = '    </div>\n</div></div>'
start_idx = html.find(start_marker)
end_idx = html.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print('Could not find markers, trying alternate approach')
    # Try to find and replace the entire hotlist grid
    old_grid_start = html.find('<div class="hotlist-merged-grid">')
    old_grid_end = html.find('</div>\n</div></div>', old_grid_start)
    if old_grid_start > 0 and old_grid_end > 0:
        new_section = f'''<div class="hotlist-merged-grid">
{items_html}
    </div>
</div></div>'''
        html = html[:old_grid_start] + new_section
        print('Replaced via grid marker')
else:
    end_idx = end_idx + len(end_marker)
    new_section = f'''<div class="hotlist-merged-grid">
{items_html}
    </div>
</div></div>'''
    html = html[:start_idx] + new_section
    print('Replaced via start/end markers')

# Update the timestamp
html = re.sub(r'· 更新时间：\d{4}-\d{2}-\d{2} \d{2}:\d{2}', f'· 更新时间：{update_time}', html)

# Save
with open('C:/Users/VRPC01/.qclaw/workspace/hotpulse/index.html', 'w', encoding='utf-8-sig') as f:
    f.write(html)

print(f'HTML updated with {len(top100)} items, timestamp: {update_time}')

# Show top 10 for verification
print('\nTop 10:')
for i, item in enumerate(top100[:10]):
    print(f'  {i+1:02d}. [{item["source"]}] {item["title"][:50]} | {item["heat"]}')
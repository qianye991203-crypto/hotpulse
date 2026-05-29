#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# The problem: panel-hot div closes too early (after section-title)
# The platform-grid cards and hotlist-merged are OUTSIDE panel-hot
# We need to move them inside.

# Find the broken structure:
#   <div class="panel active" id="panel-hot">
#     <div class="section-title">...</div>
#   </div>                          <-- THIS CLOSES TOO EARLY
#   <p>点击平台卡片...</p>
#   <div class="platform-grid">...cards...</div>
#   <div class="hotlist-merged">...100 items...</div>

# Fix: remove the early </div> after section-title, add it after hotlist-merged

old_broken = '''<div class="panel active" id="panel-hot">
    <div class="section-title"><span class="icon">📡</span> 全网热点聚合</div>
  </div>'''

new_fixed = '''<div class="panel active" id="panel-hot">
    <div class="section-title"><span class="icon">📡</span> 全网热点聚合</div>'''

assert old_broken in content, 'Broken pattern not found!'
content = content.replace(old_broken, new_fixed)
print('Removed early panel-hot close tag')

# Now find where hotlist-merged ends and add the closing </div> for panel-hot
# Find the end of hotlist-merged block
merged_end_pattern = '💡 每日08:00自动更新 · 数据来源：微博/知乎/抖音/B站/小红书\n    </div>\n  </div>'
if merged_end_pattern in content:
    content = content.replace(merged_end_pattern, 
        '💡 每日08:00自动更新 · 数据来源：微博/知乎/抖音/B站/小红书\n    </div>\n  </div>\n  </div>')
    print('Added panel-hot close tag after hotlist-merged')
else:
    # Try alternative pattern
    alt = '数据为示例展示'
    idx = content.find(alt)
    if idx > -1:
        print(f'Found alt pattern at {idx}, context: ...{content[idx-20:idx+80]}...')
    else:
        print('WARNING: Could not find hotlist-merged end pattern')
        # Search for it
        for pat in ['每日08:00', '数据来源', 'hotlist-merged']:
            pidx = content.find(pat)
            print(f'  "{pat}" at {pidx}')

# Verify all 4 panels exist and have content
for pid in ['panel-hot', 'panel-analyze', 'panel-content', 'panel-history']:
    opentag = f'id="{pid}"'
    start = content.find(opentag)
    # Count depth to find close
    depth = 0
    end = start
    for i in range(start, len(content)):
        if content[i:i+4] == '<div': depth += 1
        if content[i:i+6] == '</div>': 
            depth -= 1
            if depth == 0:
                end = i + 6
                break
    size = end - start
    print(f'Panel {pid}: {size} bytes {"✅" if size > 200 else "⚠️ SMALL"}')

for tag in ['</script>', '</body>', '</html>']:
    assert tag in content, f'MISSING {tag} !!!'

with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\nFile size: {len(content)} bytes')

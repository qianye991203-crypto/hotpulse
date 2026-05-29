#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# === EXACT STRUCTURE FOUND ===
# panel-hot opens at ~13416, contains: section-title + <p> + platform-grid(9 cards) + analyze-box + </div>
# Then: hotlist-merged block (100 items, 24KB) is OUTSIDE panel-hot
# Then: panel-analyze, panel-content, panel-history (all nearly empty)
#
# FIX: The hotlist-merged block needs to be MOVED inside panel-hot
# Find the pattern: analyze-box close → some newlines → <!-- 全网热点合并列表 --> ... → </div> (hotlist close) → newlines → <!-- 选题分析 Panel -->

import re

# Pattern 1: the stray hotlist-merged block that sits between panels
stranded_pattern = r'(    <div class="analyze-box"[^>]*>.*?</div>\s*)(<!-- 全网热点合并列表.*?</div>\s*</div>)\s*(\s*<!-- 选题分析 Panel -->)'
match = re.search(stranded_pattern, content, re.DOTALL)

if not match:
    # Try without analyze-box
    stranded_pattern2 = r'(\s*)(<!-- 全网热点合并列表.*?</div>\s*</div>)\s*(\s*<!-- 选题分析 Panel -->)'
    match = re.search(stranded_pattern2, content, re.DOTALL)

if not match:
    print('ERROR: Cannot find stranded hotlist pattern!')
    # Debug: show area around <!-- 选题分析
    idx = content.find('<!-- 选题分析 Panel')
    if idx > -1:
        print(f'Found "选题分析" at {idx}')
        print(f'Context:\n{content[idx-200:idx+50]}')
    else:
        print('"选题分析" not found at all!')
    sys.exit(1)

print(f'Found stranded block! Length: {len(match.group(2))} bytes')
print(f'Starts with: {match.group(2)[:80].strip()}')

# The fix: remove the stranded block from between panels, 
# and insert it inside panel-hot before its closing </div>
before_panel_hot_close = match.group(1)  # everything before the stranded block (inside panel-hot already)
stranded_block = match.group(2)          # the hotlist-merged that's outside
after_stranded = match.group(3)         # comment before next panel

# New structure: before_panel_hot_close + stranded_block + after_stranded
# This puts hotlist-merged INSIDE panel-hot (since we're removing it from between panels)
new_content = content[:match.start(2)] + content[match.end(2):match.start(3)] + stranded_block + '\n' + content[match.start(3):]

# Wait - that's wrong. Let me think again.
# Current: [panel-hot content][</div>][stranded hotlist][newlines][next panel comment]
# Desired: [panel-hot content][stranded hotlist][</div>][newlines][next panel comment]
# 
# So I need to: move stranded_block to BEFORE the </div> that closes panel-hot

# Let me find the exact </div> that closes panel-hot (right before stranded block)
close_before_stranded = content.rfind('</div>', 0, match.start(2))
# But this might be the wrong </div>. Let me check context.
line_before = content[close_before_stranded-30:close_before_stranded+10].replace('\n','\\n')
print(f'\n</div> before stranded at {close_before_stranded}: ...{line_before}...')

# Actually simpler approach: just do string replacement
# Find: [stuff leading to stranded] + [stranded] + [after stranded]
# Replace with: [stuff leading to stranded] + [stranded] + [after stranded]
# BUT also need to make sure there's a proper </div> after stranded

# Simplest fix: find the exact boundary and rearrange
pre_stranded = content[:match.start(2)]
post_stranded_start = match.end(2)

# In pre_stranded, find the last </div> that closes panel-hot
# It should be right before match.start(2), possibly with whitespace
trailing = pre_stranded.rstrip()
print(f'\nPre-stranded ends with: ...{repr(trailing[-60:])}')

if trailing.endswith('</div>'):
    # Remove this closing div from end of pre_stranded
    pre_fixed = pre_stranded[:pre_stranded.rfind('</div>')].rstrip()
    # Reconstruct: pre_fixed + newline + stranded_block + newline + </div> + post_stranded
    new_content = pre_fixed + '\n    ' + stranded_block.strip() + '\n  </div>\n' + content[post_stranded_start:]
else:
    print('ERROR: pre_stranded does not end with </div>')
    sys.exit(1)

# Verify
for pid in ['panel-hot', 'panel-analyze', 'panel-content', 'panel-history']:
    s = new_content.find(f'id="{pid}"')
    d=0; e=s
    for i in range(s, len(new_content)):
        if new_content[i:i+4]=='<div':
            j=i+4
            while j<len(new_content) and new_content[j] in ' \t\n\r ':j+=1
            if j<len(new_content) and new_content[j] not in '/>':d+=1
        elif new_content[i:i+6]=='</div>':
            d-=1
            if d==0:e=i+6;break
    mi = new_content.find('hotlist-merged')
    inside = mi > s and mi < e if pid == 'panel-hot' else False
    print(f'Panel {pid}: {e-s} bytes {"✅" if e-s > 500 else "⚠️"}{" ← hotlist INSIDE!" if inside else ""}')

for tag in ['</script>', '</body>', '</html>']:
    assert tag in new_content, f'MISSING {tag}'

with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f'\n✅ Fixed! File size: {len(new_content)} bytes')

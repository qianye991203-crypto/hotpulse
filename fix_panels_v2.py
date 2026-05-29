#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# === PROBLEM ANALYSIS ===
# hotlist-merged (at ~11023) is OUTSIDE all panels (before panel-hot at 13416)
# .panel { display: none } means panels are hidden by default
# But hotlist-merged has no parent panel → always visible → shows on ALL tabs
# Other panels (analyze/content/history) have 0 bytes content

# === FIX STRATEGY ===
# 1. Find the hotlist-merged block (the stray content outside panels)
# 2. Move it INSIDE panel-hot
# 3. Make sure panel-hot properly wraps: cards + hotlist-merged

# Step 1: Find the exact hotlist-merged block
merged_start_tag = '<!-- 全网热点合并列表'
ms = content.find(merged_start_tag)
if ms == -1:
    # Try v8 pattern
    merged_start_tag = '<!-- 全网热点合并列表 (纯静态HTML'
    ms = content.find(merged_start_tag)
    
if ms == -1:
    print('ERROR: Cannot find hotlist-merged start!')
    sys.exit(1)

print(f'Found hotlist-merged at position {ms}')

# Find the end of this block (the closing </div> for hotlist-merged)
# We need to find the matching close
depth = 0
me = ms
for i in range(ms, len(content)):
    if content[i:i+4] == '<div':
        # Check it's a real div open tag
        j = i + 4
        while j < len(content) and content[j] in ' \t\n\r': j += 1
        if j < len(content) and content[j] not in '/>':
            depth += 1
    elif content[i:i+6] == '</div>':
        depth -= 1
        if depth == 0:
            me = i + 6
            break

print(f'hotlist-merged block: {ms} - {me} ({me-ms} bytes)')
hotlist_block = content[ms:me]
print(f'First 100 chars: {hotlist_block[:100].replace(chr(10)," ")}')

# Step 2: Find where panel-hot currently ends (it's tiny, just the section-title)
ph_start = content.find('id="panel-hot"')
depth2 = 0
ph_end = ph_start
for i in range(ph_start, len(content)):
    if content[i:i+4] == '<div':
        j = i + 4
        while j < len(content) and content[j] in ' \t\n\r': j += 1
        if j < len(content) and content[j] not in '/>':
            depth2 += 1
    elif content[i:i+6] == '</div>':
        depth2 -= 1
        if depth2 == 0:
            ph_end = i + 6
            break

print(f'\nCurrent panel-hot: {ph_start} - {ph_end} ({ph_end-ph_start} bytes)')
print(f'Content: {repr(content[ph_start:ph_end][:200])}')

# Step 3: Check what's between panel-hot close and the platform-grid / hotlist stuff
between = content[ph_end:ms]
print(f'\nBetween panel-hot close and hotlist-merged: {len(between)} bytes')
print(f'First 200: {repr(between[:200])}')

# The fix: 
# - Remove hotlist-merged from its current location (outside panels)
# - Insert it inside panel-hot, right before panel-hot's closing </div>
# - Also include the platform-grid and <p> text that's also stranded

# Actually, let's see what's between ph_end and the next panel
pa_start = content.find('id="panel-analyze"')
stranded_content = content[ph_end:pa_start]
print(f'\nStranded content (between panel-hot and panel-analyze): {len(stranded_content)} bytes')
print(f'Starts with: {repr(stranded_content[:150])}')
print(f'Ends with: {repr(stranded_content[-150:])}')

# Fix: rebuild panel-hot to include all stranded content
old_panel_hot = content[ph_start:ph_end]
new_panel_hot = old_panel_hot.rstrip().rstrip('\r\n').rstrip()
if new_panel_hot.endswith('</div>'):
    new_panel_hot = new_panel_hot[:-6]  # remove premature close
    new_panel_hot += '\n' + stranded_content.strip() + '\n  </div>'
else:
    print('ERROR: panel-hot does not end with </div>')
    sys.exit(1)

print(f'\nNew panel-hot size: {len(new_panel_hot)} bytes')

# Apply fix
content = content[:ph_start] + new_panel_hot + content[pa_start:]

# Verify
for pid in ['panel-hot', 'panel-analyze', 'panel-content', 'panel-history']:
    s = content.find(f'id="{pid}"')
    d = 0; e = s
    for i in range(s, len(content)):
        if content[i:i+4] == '<div':
            j = i+4
            while j < len(content) and content[j] in ' \t\n\r ': j+=1
            if j < len(content) and content[j] not in '/>': d+=1
        elif content[i:i+6] == '</div>':
            d-=1
            if d==0: e=i+6; break
    print(f'Panel {pid}: {e-s} bytes {"✅" if e-s > 500 else "⚠️"}')

# Verify hotlist-merged is now inside panel-hot
new_merged_idx = content.find('hotlist-merged')
new_ph_start = content.find('id="panel-hot"')
d=0; new_ph_end=new_ph_start
for i in range(new_ph_start, len(content)):
    if content[i:i+4]=='<div':
        j=i+4
        while j<len(content) and content[j] in ' \t\n\r ':j+=1
        if j<len(content) and content[j] not in '/>': d+=1
    elif content[i:i+6]=='</div>':
        d-=1
        if d==0: new_ph_end=i+6; break
print(f'\nhotlist-merged now INSIDE panel-hot? {new_merged_idx > new_ph_start and new_merged_idx < new_ph_end}')

for tag in ['</script>', '</body>', '</html>']:
    assert tag in content, f'MISSING {tag}'

with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\n✅ Fixed! File size: {len(content)} bytes')

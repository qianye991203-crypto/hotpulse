#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Insert panel-hot BEFORE '<!-- 选题分析 Panel -->'
marker = '<!-- 选题分析 Panel -->'
if marker not in content:
    print('ERROR: marker not found')
else:
    new_panel = '''  <!-- 平台热点 Panel -->
  <div class="panel active" id="panel-hot">
    <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;margin-bottom:16px;">
      <div class="section-title" style="margin-bottom:0;"><span class="icon">🔥</span> 实时热榜</div>
      <div style="display:flex;gap:8px;align-items:center;">
        <span style="font-size:11px;color:var(--muted);" id="hotlist-source">内置数据</span>
        <button class="btn btn-secondary" style="font-size:11px;padding:4px 12px;" onclick="refreshHotlist()">🔄 刷新</button>
      </div>
    </div>
    <div id="hotlist-tabs" class="hotlist-tabs"></div>
    <div id="hotlist-content"></div>
  </div>

'''
    content = content.replace(marker, new_panel + marker)
    print('Panel-hot inserted!')

# Also fix the switchTab function to call initHotlist
# Check if initHotlist is called in switchTab
if 'initHotlist' not in content:
    print('WARNING: initHotlist not found in content')
else:
    print('initHotlist exists:', content.count('initHotlist'))

# Verify
panels = __import__('re').findall(r'id="(panel-[^"]*)"', content)
print('Panels after fix:', panels)

with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done! File size:', len(content))

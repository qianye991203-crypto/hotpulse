#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all panel IDs
import re
panels = re.findall(r'id="(panel-[^"]*)"', content)
print('Panels found:', panels)

# Find panel-analyze location
idx = content.find('panel-analyze')
if idx != -1:
    # Show 100 chars before and after
    start = max(0, idx - 100)
    end = min(len(content), idx + 100)
    print('Around panel-analyze:')
    print(repr(content[start:end]))
    
# Check if panel-hot exists anywhere
idx2 = content.find('panel-hot')
print('panel-hot found at:', idx2)

# Show the tabs area
idx3 = content.find('class="tabs"')
if idx3 != -1:
    print('Tabs area:')
    print(repr(content[idx3:idx3+300]))

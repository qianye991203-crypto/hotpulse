#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

old = "if (tabName === 'history') renderHistory();\n}"
new = "if (tabName === 'history') renderHistory();\n  if (tabName === 'hot' && !_hotlistInited) { _hotlistInited=true; initHotlist(); }\n}"

if old in content:
    content = content.replace(old, new)
    with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('switchTab fixed - initHotlist will be called on first hot tab click')
else:
    print('ERROR: pattern not found')
    # Debug: show what's actually there
    idx = content.find("function switchTab")
    if idx != -1:
        print(repr(content[idx:idx+300]))

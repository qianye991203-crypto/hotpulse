#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract JS between <script> and </script>
idx1 = content.find('<script>')
idx2 = content.find('</script>', idx1)
if idx1 == -1 or idx2 == -1:
    print('ERROR: script tags not found')
else:
    js = content[idx1+8:idx2]
    
    # Check for common syntax issues
    lines = js.split('\n')
    print('Total JS lines:', len(lines))
    
    # Find the hotlist section
    hot_idx = js.find('// ── Hotlist')
    if hot_idx != -1:
        # Show first 2000 chars of hotlist section
        section = js[hot_idx:hotlist+3000] if 'hotlist' in dir() else js[hot_idx:hot_idx+3000]
        print('Hotlist section start:')
        print(repr(section[:2000]))
    
    # Look for obvious syntax errors
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Check for common issues
        if '{rank:' in line and 'title:' not in line and '}' not in line[:20]:
            print('Possible bad line %d: %s' % (i+1, repr(line[:120])))
        if 'title:' not in line and '{rank' in line:
            print('Rank without title at line %d: %s' % (i+1, repr(line[:120])))

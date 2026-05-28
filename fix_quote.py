#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix: replace the problematic onclick single-quote nesting
old = "onclick=\"_hlS(''+p.k+'')\""
new = 'onclick="_hlS(&apos;'+p.k+&apos;)"'

if old in content:
    content = content.replace(old, new)
    print('Fixed quote nesting')
else:
    print('Pattern not found, showing context:')
    idx = content.find("_hlS(")
    if idx != -1:
        print(repr(content[idx-20:idx+60]))

with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\index.html', 'w', encoding='utf-8') as f:
    f.write(content)

# Re-check with node
js = content[content.find('<script>')+8:content.rfind('</script>')]
with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\_check.js', 'w', encoding='utf-8') as f:
    f.write(js)

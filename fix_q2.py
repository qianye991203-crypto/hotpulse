#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# The problem line in JS:
# t.innerHTML=ps.map(function(p){return'<button class="hotlist-tab'+(p.k===_hlPlatform?' on':'')+'" onclick="_hlS(''+p.k+'')">'+p.n+'</button>';}).join('');
# Issue: onclick="_hlS(''+p.k+'')" has single quotes inside single-quoted string
# Fix: use data attribute + event delegation instead, or use &apos;

old = """onclick="_hlS(''+p.k+'')\""""
new = "onclick=\"_hlS(&apos;'+p.k+'&apos;)\""

if old in content:
    content = content.replace(old, new)
    print("Fixed")
else:
    # Try to find and show the exact text
    import re
    m = re.search(r'onclick="._hlS.', content)
    if m:
        print("Found:", repr(m.group()))
    else:
        print("Pattern not found at all")

with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\index.html', 'w', encoding='utf-8') as f:
    f.write(content)

# Extract and verify JS
js_start = content.find('<script>') + 8
js_end = content.rfind('</script>')
js = content[js_start:js_end]
with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\_check.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("JS extracted for checking")

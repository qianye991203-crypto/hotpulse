#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io, re, subprocess, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract JS from <script>...</script>
idx1 = content.find('<script>')
idx2 = content.rfind('</script>')
if idx1 == -1 or idx2 == -1:
    print('ERROR: no script tags'); sys.exit(1)

js = content[idx1+8:idx2]
print('JS size:', len(js), 'bytes')

# Write JS to temp file and check with node
with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\_check.js', 'w', encoding='utf-8') as f:
    f.write(js)

# Try to parse with node --check
try:
    result = subprocess.run(['node', '--check', r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\_check.js'],
                          capture_output=True, text=True, timeout=10)
    print('Node exit code:', result.returncode)
    print('STDOUT:', result.stdout[:500] if result.stdout else '(empty)')
    print('STDERR:', result.stderr[:1000] if result.stderr else '(empty)')
except Exception as e:
    print('Node error:', e)

# Also do basic brace/paren balance check
opens = js.count('{') + js.count('(') + js.count('[')
closes = js.count('}') + js.count(')') + js.count(']')
print('Brace balance: opens=%d closes=%d diff=%d' % (opens, closes, opens-closes))

# Find any remaining suspicious patterns
suspicious = re.findall(r'rank:\d+:|title:[^\'"]|\{[^}]*::', js)
if suspicious:
    print('SUSPICIOUS patterns found:')
    for s in suspicious[:10]:
        print(' ', repr(s))
else:
    print('No suspicious patterns found')

# Check for common issues
issues = []
# Unclosed strings
for i, line in enumerate(js.split('\n')):
    # Count quotes (rough)
    sq = line.count("'") - line.count("\\'")
    dq = line.count('"') - line.count('\\"')
    if sq < 0 or dq < 0:
        issues.append('Line %d: possible unclosed string (%d single, %d double)' % (i+1, sq, dq))
    # Check for :title: pattern
    if ':title:' in line:
        issues.append('Line %d: double colon :title: -> %s' % (i+1, line.strip()[:80]))

if issues:
    print('\nIssues found:')
    for iss in issues[:20]:
        print(' ', iss)
else:
    print('\nNo obvious issues found in quick scan')

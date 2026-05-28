#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# === Problem 1: Two panel-hot divs! Remove the first one (old card version) ===
old_panel = '''  <!-- 平台热点 Panel -->
  <div class="panel active" id="panel-hot">
    <div class="section-title"><span class="icon">📡</span> 全网热点聚合</div>
    <p style="font-size:13px;color:var(--muted);margin-bottom:20px;">点击平台卡片，跳转到对应热榜页面。建议每天刷一刷，培养选题敏感度。</p>
    <div class="platform-grid">
      <a class="platform-card" href="https://tophub.today/n/KqndgEeLl9" target="_blank">
        <div class="p-name">🐦 微博热搜</div>
        <div class="p-desc">娱乐/社会热点首发地</div>
      </a>
      <a class="platform-card" href="https://tophub.today/n/mproPpoq6O" target="_blank">
        <div class="p-name">📘 知乎热榜</div>
        <div class="p-desc">深度讨论/知识热点</div>
      </a>
      <a class="platform-card" href="https://tophub.today/n/DpQvNABoNE" target="_blank">
        <div class="p-name">🎵 抖音热点</div>
        <div class="p-desc">短视频风向标</div>
      </a>
      <a class="platform-card" href="https://tophub.today/n/5VaobgvAj1" target="_blank">
        <div class="p-name">📕 小红书</div>
        <div class="p-desc">种草/生活方式热点</div>
      </a>
      <a class="platform-card" href="https://tophub.today/n/xLngunu24O" target="_blank">
        <div class="p-name">📺 B站热门</div>
        <div class="p-desc">年轻用户聚集地</div>
      </a>
      <a class="platform-card" href="https://tophub.today/" target="_blank">
        <div class="p-name">📊 今日热榜</div>
        <div class="p-desc">全网热点聚合站</div>
      </a>
      <a class="platform-card" href="https://tophub.today/n/Ku7b7CB2Ql" target="_blank">
        <div class="p-name">🌍 Twitter趋势</div>
        <div class="p-desc">国际热点/英文趋势（聚合页，国内可访问）</div>
      </a>
      <a class="platform-card" href="https://tophub.today/n/yVowGg0oD0" target="_blank">
        <div class="p-name">🤖 Reddit热帖</div>
        <div class="p-desc">全球社区热点（聚合页，国内可访问）</div>
      </a>
      <a class="platform-card" href="https://tophub.today/n/7Ci93d60bJ" target="_blank">
        <div class="p-name">▶️ YouTube热门</div>
        <div class="p-desc">视频内容风向（聚合页，国内可访问）</div>
      </a>
    </div>
    <div class="analyze-box" style="margin-top:32px;">
      <div class="analyze-header">💡 小技巧：建议每天早中晚各刷一次热榜，把有意思的话题复制到「选题分析」里评分</div>
    </div>
  </div>'''

assert old_panel in content, 'Old panel not found!'
content = content.replace(old_panel, '')
print('Removed old panel-hot (card version)')

# === Problem 2: Add missing hotlist CSS styles ===
css_marker = '  @media (max-width: 600px) {'
hotlist_css = '''  /* Hotlist styles */
  .hotlist-tabs { display:flex; gap:6px; flex-wrap:wrap; margin-bottom:16px; }
  .hotlist-tab {
    font-size:12px; font-weight:600; padding:8px 16px; border-radius:20px;
    border:2px solid var(--border); cursor:pointer; color:var(--muted);
    background:var(--surface); transition:all .2s; font-family:inherit;
  }
  .hotlist-tab.on { background:linear-gradient(135deg,var(--accent),var(--accent2)); color:#fff; border-color:transparent; }
  .hotlist-tab:hover:not(.on) { color:var(--text); border-color:var(--accent); }
  .hotlist-platform-name { font-size:14px; font-weight:700; margin-bottom:12px; color:var(--accent); }
  .hotlist-grid { display:flex; flex-direction:column; gap:6px; }
  .hotlist-item {
    display:flex; align-items:center; gap:10px; padding:10px 14px;
    background:var(--surface); border:1px solid var(--border); border-radius:10px;
    transition:all .15s; cursor:default; font-size:14px;
  }
  .hotlist-item:hover { border-color:var(--accent); transform:translateX(4px); }
  .hotlist-rank {
    font-weight:900; font-size:16px; min-width:28px; text-align:center;
    color:var(--muted); flex-shrink:0;
  }
  .hotlist-rank.top { color:#ff4444; }
  .hotlist-title { flex:1; font-weight:500; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  .hotlist-hot { font-size:11px; color:var(--accent); font-weight:600; flex-shrink:0; }
  .hotlist-error { text-align:center; padding:40px; color:var(--muted); font-size:14px; }
  .hotlist-loading { text-align:center; padding:40px; color:var(--muted); font-size:14px; }

'''
assert css_marker in content, 'CSS marker not found!'
content = content.replace(css_marker, hotlist_css + css_marker)
print('Added hotlist CSS styles')

# Verify integrity
for tag in ['</script>', '</body>', '</html>']:
    assert tag in content, 'MISSING %s !!!' % tag
print('Integrity check: all end tags present ✅')

with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\index.html', 'w', encoding='utf-8') as f:
    f.write(content)

# Node syntax check
js_start = content.find('<script>') + 8
js_end = content.rfind('</script>')
js = content[js_start:js_end]
with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\_check.js', 'w', encoding='utf-8') as f:
    f.write(js)

print('Done! File size:', len(content))
print('JS extracted for node --check')

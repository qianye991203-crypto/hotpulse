#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Patch index.html: add hotlist CSS + panel + JS functions"""

with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# === EDIT 1: Add CSS rules BEFORE the @media block ===
new_css = '''
  .hotlist-tabs { display: flex; gap: 6px; margin-bottom: 20px; flex-wrap: wrap; }
  .hotlist-tab {
    font-size: 12px; padding: 7px 16px; border-radius: 20px;
    border: 2px solid var(--border); cursor: pointer;
    color: var(--muted); background: var(--surface); transition: all .2s; font-weight: 500;
  }
  .hotlist-tab.on { background: linear-gradient(135deg, var(--accent), var(--accent2)); color: #fff; border-color: transparent; }
  .hotlist-tab:hover:not(.on) { color: var(--text); border-color: var(--accent); }
  .hotlist-grid { display: flex; flex-direction: column; gap: 6px; }
  .hotlist-item {
    display: flex; align-items: center; gap: 12px; padding: 12px 16px;
    background: var(--surface); border: 1.5px solid var(--border);
    border-radius: 12px; transition: all .2s; cursor: pointer; text-decoration: none; color: inherit;
  }
  .hotlist-item:hover { border-color: var(--accent); box-shadow: 0 4px 12px rgba(255,123,84,0.1); }
  .hotlist-rank { font-weight: 900; font-size: 16px; min-width: 28px; text-align: center; color: var(--muted); }
  .hotlist-rank.top { background: linear-gradient(135deg, var(--accent), var(--accent2)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
  .hotlist-title { flex: 1; font-size: 14px; line-height: 1.5; }
  .hotlist-hot { font-size: 11px; color: var(--muted); white-space: nowrap; min-width: 60px; text-align: right; }
  .hotlist-loading { text-align: center; padding: 60px 24px; color: var(--muted); font-size: 14px; }
  .hotlist-error { text-align: center; padding: 40px 24px; color: var(--danger); font-size: 13px; }
  .hotlist-platform-name { font-size: 15px; font-weight: 700; margin-bottom: 14px; display: flex; align-items: center; gap: 8px; }
'''

if '@media (max-width: 600px)' in content:
    content = content.replace('@media (max-width: 600px)', new_css + '\n\n  @media (max-width: 600px)', 1)
else:
    print('WARNING: @media block not found, CSS not patched')

# === EDIT 2: Replace panel-hot HTML ===
old_panel_start = '  <!-- 平台热点 Panel -->'
old_panel_end = '    </div>\n  </div>\n\n  <!-- 选题分析 Panel -->'

start_idx = content.find(old_panel_start)
end_idx = content.find(old_panel_end, start_idx)
if start_idx == -1 or end_idx == -1:
    print('WARNING: panel-hot not found')
else:
    new_panel = '''  <!-- 平台热点 Panel -->
  <div class="panel active" id="panel-hot">
    <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;margin-bottom:16px;">
      <div class="section-title" style="margin-bottom:0;"><span class="icon">🔥</span> 实时热榜</div>
      <div style="font-size:12px;color:var(--muted);" id="hotlist-updated">加载中…</div>
    </div>
    <div id="hotlist-tabs" class="hotlist-tabs"></div>
    <div id="hotlist-content"></div>
  </div>
'''
    content = content[:start_idx] + new_panel + content[end_idx:]
    print('Panel-hot replaced successfully')

# === EDIT 3: Add JS functions BEFORE </script></body> ===
new_js = '''
// ── Hotlist (real-time hot topics) ──
var hotlistData = null;
var hotlistCurrentPlatform = 'all';

async function loadHotlist(platform) {
  platform = platform || 'all';
  hotlistCurrentPlatform = platform;
  var tabsEl = document.getElementById('hotlist-tabs');
  var contentEl = document.getElementById('hotlist-content');
  if (!tabsEl || !contentEl) return;

  // Render tabs
  var platforms = [
    {key:'all', name:'🌐 全部'},
    {key:'weibo', name:'🐦 微博'},
    {key:'zhihu', name:'📘 知乎'},
    {key:'bilibili', name:'📺 B站'},
    {key:'douyin', name:'🎵 抖音'},
    {key:'xiaohongshu', name:'📕 小红书'},
    {key:'twitter', name:'🌍 Twitter'},
    {key:'reddit', name:'🤖 Reddit'}
  ];
  tabsEl.innerHTML = platforms.map(function(p) {
    return '<button class="hotlist-tab' + (p.key===platform?' on':'') + '" onclick="loadHotlist(\\'' + p.key + '\\')">' + p.name + '</button>';
  }).join('');

  contentEl.innerHTML = '<div class="hotlist-loading">⏳ 正在从云端抓取热榜，请稍候…</div>';

  try {
    var resp = await fetch('/api/hotlist?platform=' + platform + '&_t=' + Date.now());
    var j = await resp.json();
    if (!j.success) throw new Error(j.error || '抓取失败');
    hotlistData = j.data;
    document.getElementById('hotlist-updated').textContent = '更新于 ' + new Date(j.updatedAt || Date.now()).toLocaleTimeString('zh-CN');
    renderHotlist(platform, j.data);
  } catch(e) {
    contentEl.innerHTML = '<div class="hotlist-error">❌ 加载失败：' + escapeHtml(e.message) + '<br><br><button class="btn btn-secondary" onclick="loadHotlist(\\'' + platform + '\\')">🔄 重新加载</button></div>';
  }
}

function renderHotlist(platform, data) {
  var contentEl = document.getElementById('hotlist-content');
  if (!contentEl) return;

  if (platform === 'all') {
    // Show all platforms that have data
    var keys = Object.keys(data || {});
    var html = '';
    for (var i=0; i<keys.length; i++) {
      var key = keys[i];
      var plat = data[key];
      if (!plat || !plat.data) {
        html += '<div class="hotlist-error" style="margin-bottom:16px;text-align:left;">⚠️ ' + escapeHtml(key) + '：数据源不可用</div>';
        continue;
      }
      html += renderHotlistSection(key, plat);
    }
    contentEl.innerHTML = html || '<div class="hotlist-error">暂无可用热榜数据</div>';
  } else {
    var plat = data;
    if (!plat || !plat.data) {
      contentEl.innerHTML = '<div class="hotlist-error">⚠️ ' + platform + ' 数据源暂不可用，请稍后重试</div>';
      return;
    }
    contentEl.innerHTML = renderHotlistSection(platform, plat);
  }
}

function renderHotlistSection(key, plat) {
  var items = plat.data || [];
  if (!items.length) return '<div class="hotlist-error" style="margin-bottom:20px;">' + (plat.icon||'') + ' ' + escapeHtml(plat.name||key) + '：暂无数据</div>';

  var rows = '';
  for (var i=0; i<Math.min(items.length,20); i++) {
    var item = items[i];
    var rankCls = i<3 ? ' top' : '';
    var url = item.url || '';
    var titleHtml = escapeHtml(item.title || '');
    var inner = '<span class="hotlist-rank' + rankCls + '">' + String(item.rank||i+1).padStart(2,'0') + '</span>' +
      '<span class="hotlist-title">' + titleHtml + '</span>' +
      (item.hot ? '<span class="hotlist-hot">' + escapeHtml(String(item.hot)) + '</span>' : '');
    if (url) {
      rows += '<a class="hotlist-item" href="' + escapeAttr(url) + '" target="_blank" rel="noopener">' + inner + '</a>';
    } else {
      rows += '<div class="hotlist-item" style="cursor:default;">' + inner + '</div>';
    }
  }
  return '<div style="margin-bottom:28px;"><div class="hotlist-platform-name">' + (plat.icon||'🔥') + ' ' + escapeHtml(plat.name||key) + '</div><div class="hotlist-grid">' + rows + '</div></div>';
}

function escapeAttr(s) {
  return String(s).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// Auto-load hotlist when panel becomes visible
var _origSwitchTab = switchTab;
// Override: call loadHotlist on first hot tab click
var _hotlistLoaded = false;
function switchTab(tabName, btn) {
  var panels = document.querySelectorAll('.panel');
  for (var i = 0; i < panels.length; i++) panels[i].classList.remove('active');
  var tabs = document.querySelectorAll('.tab-btn');
  for (var j = 0; j < tabs.length; j++) tabs[j].classList.remove('active');
  document.getElementById('panel-' + tabName).classList.add('active');
  btn.classList.add('active');
  if (tabName === 'history') renderHistory();
  if (tabName === 'hot' && !_hotlistLoaded) {
    _hotlistLoaded = true;
    loadHotlist('all');
  }
}
'''

# Insert new JS before </script> (the last </script> before </body>)
script_end = content.rfind('</script>')
if script_end != -1:
    content = content[:script_end] + new_js + '\n' + content[script_end:]
    print('JS functions inserted successfully')
else:
    print('WARNING: </script> not found, JS not patched')

# Write back
with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('All patches applied successfully!')

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# === 1. Add hotlist CSS before media query ===
css_marker = '  @media (max-width: 600px) {'
hotlist_css = '''  /* Hotlist merged styles */
  .hotlist-merged { margin-top:32px; }
  .hotlist-merged-title { font-size:15px; font-weight:700; color:var(--accent); margin-bottom:14px; display:flex; align-items:center; gap:8px; }
  .hotlist-merged-grid { display:flex; flex-direction:column; gap:6px; }
  .hotlist-merged-item {
    display:flex; align-items:center; gap:12px; padding:10px 16px;
    background:var(--surface); border:1px solid var(--border); border-radius:10px;
    transition:all .15s; font-size:14px;
  }
  .hotlist-merged-item:hover { border-color:var(--accent); transform:translateX(4px); }
  .hotlist-merged-rank {
    font-weight:900; font-size:15px; min-width:26px; text-align:center; flex-shrink:0;
  }
  .hotlist-merged-rank.top { color:#ff4444; }
  .hotlist-merged-rank.hot { color:var(--accent); }
  .hotlist-merged-title-text { flex:1; font-weight:500; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  .hotlist-merged-platform { font-size:11px; color:var(--muted); flex-shrink:0; background:var(--surface2); padding:2px 8px; border-radius:10px; }
  .hotlist-merged-heat { font-size:11px; color:var(--accent); font-weight:600; flex-shrink:0; min-width:48px; text-align:right; }
  .hotlist-loading { text-align:center; padding:40px; color:var(--muted); font-size:14px; }
  .hotlist-error { text-align:center; padding:40px; color:var(--muted); font-size:13px; }

'''

assert css_marker in content, 'CSS marker not found!'
content = content.replace(css_marker, hotlist_css + css_marker)
print('Added hotlist CSS')

# === 2. Insert merged hotlist HTML after the "小技巧" analyze-box ===
html_marker = '<!-- 选题分析 Panel -->'
merged_html = '''
  <!-- 全网热点合并列表 -->
  <div class="hotlist-merged" id="hotlist-merged">
    <div class="hotlist-merged-title"><span>🔥</span> 全网热点 · 实时聚合（按热度排列）</div>
    <div class="hotlist-merged-grid" id="hotlist-merged-grid"></div>
    <div style="margin-top:12px;text-align:center;">
      <button class="btn btn-secondary" style="font-size:11px;padding:5px 14px;" onclick="refreshMergedHotlist()">🔄 刷新</button>
      <span style="font-size:11px;color:var(--muted);margin-left:8px;" id="merged-source">内置数据</span>
    </div>
  </div>

'''

idx = content.find(html_marker)
assert idx != -1, 'HTML marker not found!'
# Insert BEFORE the panel-analyze (i.e., at end of panel-hot)
# Find the analyze-box tip div and insert after it
tip_marker = '建议每天早中晚各刷一次热榜'
tip_idx = content.find(tip_marker)
assert tip_idx != -1, 'Tip marker not found!'
# Find the closing </div> of that analyze-box, then insert
insert_idx = content.find('</div>\n  </div>', tip_idx)
assert insert_idx != -1, 'Closing div not found!'
insert_idx += len('</div>\n  </div>')

content = content[:insert_idx] + '\n' + merged_html + content[insert_idx:]
print('Inserted merged hotlist HTML')

# === 3. Insert merged hotlist JS before </script> ===
js_marker = '</script>'
merged_js = '''

// ── Merged hotlist (all platforms combined & sorted) ──
var _MERGED_DATA = [
  {r:1,t:'外交部回应美方涉华言论',p:'微博',h:'892万',w:95},
  {r:2,t:'全国多地高温预警',p:'微博',h:'756万',w:92},
  {r:3,t:'嫦娥六号任务进展',p:'微博',h:'623万',w:90},
  {r:4,t:'新能源汽车出口创新高',p:'微博',h:'512万',w:88},
  {r:5,t:'A股三大指数收涨',p:'微博',h:'489万',w:87},
  {r:6,t:'如何看待当前经济形势？',p:'知乎',h:'2856万',w:91},
  {r:7,t:'AI对就业市场的真实影响',p:'知乎',h:'2134万',w:89},
  {r:8,t:'年轻人为什么不愿意结婚了？',p:'知乎',h:'1876万',w:86},
  {r:9,t:'【年度盘点】2025最火视频合集',p:'B站',h:'1234万播放',w:84},
  {r:10,t:'UP主实测新款手机',p:'B站',h:'987万播放',w:82},
  {r:11,t:'#外交部回应# 热议中',p:'抖音',h:'987万',w:90},
  {r:12,t:'挑战类视频又火了',p:'抖音',h:'876万',w:83},
  {r:13,t:'夏日穿搭灵感｜这5套绝了！',p:'小红书',h:'45.6万收藏',w:81},
  {r:14,t:'平价好物分享｜学生党必看',p:'小红书',h:'38.2万收藏',w:78},
  {r:15,t:'知名演员去世',p:'微博',h:'398万',w:85},
  {r:16,t:'某地突发地震',p:'微博',h:'356万',w:82},
  {r:17,t:'网红主播被罚',p:'微博',h:'312万',w:76},
  {r:18,t:'有哪些值得一看的纪录片推荐？',p:'知乎',h:'1523万',w:80},
  {r:19,t:'如何提高工作效率？',p:'知乎',h:'1298万',w:77},
  {r:20,t:'UP主实测新款手机',p:'B站',h:'987万播放',w:82}
];

function renderMergedHotlist(){
  var el=document.getElementById('hotlist-merged-grid'); if(!el)return;
  // Sort by weight desc
  var d=_MERGED_DATA.slice().sort(function(a,b){return b.w-a.w;});
  var h='';
  for(var i=0;i<d.length;i++){
    var it=d[i],rk=i+1,rc=rk<=3?' top':(rk<=10?' hot':'');
    h+='<div class="hotlist-merged-item">'
      +'<span class="hotlist-merged-rank'+rc+'">'+String(rk).padStart(2,'0')+'</span>'
      +'<span class="hotlist-merged-title-text">'+_e(it.t)+'</span>'
      +'<span class="hotlist-merged-platform">'+_e(it.p)+'</span>'
      +'<span class="hotlist-merged-heat">'+_e(it.h)+'</span>'
      +'</div>';
  }
  el.innerHTML=h;
}

async function refreshMergedHotlist(){
  var el=document.getElementById('hotlist-merged-grid'); var sc=document.getElementById('merged-source');
  if(el)el.innerHTML='<div class="hotlist-loading">⏳ 正在刷新…</div>';
  try{
    var r=await fetch('/api/hotlist?platform=all&_t='+Date.now(),{signal:AbortSignal.timeout(10000)});
    var j=await r.json();
    if(j.success&&j.data){
      var nd=[],wp=0;
      var pmap={weibo:'微博',zhihu:'知乎',bilibili:'B站',douyin:'抖音',xiaohongshu:'小红书'};
      var ks=Object.keys(j.data);
      for(var ki=0;ki<ks.length;ki++){var kd=j.data[ks[ki]];if(!kd||!kd.d)continue;for(var di=0;di<kd.d.length;di++){var item=kd.d[di];nd.push({t:item.t,p:pmap[ks[ki]]||ks[ki],h:item.h||'',w:100-di});}}
      if(nd.length>0)_MERGED_DATA=nd;
      if(sc)sc.textContent='实时 ('+new Date().toLocaleTimeString('zh-CN')+')';
    }
  }catch(e){}
  renderMergedHotlist();
  if(sc&&sc.textContent.indexOf('实时')==-1)sc.textContent='内置数据';
}

// Call on page load
setTimeout(renderMergedHotlist, 300);
'''

assert js_marker in content, 'JS marker not found!'
content = content.replace(js_marker, merged_js + js_marker)
print('Added merged hotlist JS')

# Verify integrity
for tag in ['</script>', '</body>', '</html>']:
    assert tag in content, 'MISSING %s !!!' % tag
print('Integrity check: all end tags present ✅')

with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\index.html', 'w', encoding='utf-8') as f:
    f.write(content)

# Node syntax check
js = content[content.find('<script>')+8:content.rfind('</script>')]
with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\_check.js', 'w', encoding='utf-8') as f:
    f.write(js)
print('File size:', len(content))
print('JS extracted for node --check')

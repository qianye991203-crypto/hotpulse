#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLEAN APPROACH: Start from working v2.0 (64d7e87), add ONLY hotlist feature.
Two precise insertions, nothing else touched.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# === Insert 1: panel-hot HTML before '<!-- 选题分析 Panel -->' ===
html_marker = '<!-- 选题分析 Panel -->'
html_insert = '''  <!-- 平台热点 Panel -->
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
assert html_marker in content, 'HTML marker not found!'
content = content.replace(html_marker, html_insert + html_marker)
print('Insert 1: panel-hot HTML added')

# === Insert 2: Hotlist JS before '</script>' ===
js_marker = '</script>'
js_insert = '''

// ── Hotlist (static data) ──
var _hlPlatform = 'weibo';
var _hlInited = false;
var _HL_DATA = {
weibo:{n:'微博热搜',i:'🐦',d:[
{r:1,t:'外交部回应美方涉华言论',h:'892万'},{r:2,t:'全国多地高温预警',h:'756万'},
{r:3,t:'嫦娥六号任务进展',h:'623万'},{r:4,t:'新能源汽车出口创新高',h:'512万'},
{r:5,t:'A股三大指数收涨',h:'489万'},{r:6,t:'教育部发布最新通知',h:'421万'},
{r:7,t:'知名演员去世',h:'398万'},{r:8,t:'某地突发地震',h:'356万'},
{r:9,t:'网红主播被罚',h:'312万'},{r:10,t:'新剧开播热度登顶',h:'287万'},
{r:11,t:'国际金价波动',h:'254万'},{r:12,t:'手机新品发布会',h:'231万'},
{r:13,t:'体育赛事精彩瞬间',h:'198万'},{r:14,t:'旅游旺季出行提醒',h:'176万'},
{r:15,t:'健康科普辟谣',h:'153万'}
]},
zhihu:{n:'知乎热榜',i:'📘',d:[
{r:1,t:'如何看待当前经济形势？',h:'2856万'},{r:2,t:'AI对就业市场的真实影响',h:'2134万'},
{r:3,t:'年轻人为什么不愿意结婚了？',h:'1876万'},{r:4,t:'有哪些值得一看的纪录片推荐？',h:'1523万'},
{r:5,t:'如何提高工作效率？',h:'1298万'},{r:6,t:'大城市vs小城市生活选择',h:'1156万'},
{r:7,t:'最近有什么好书推荐？',h:'987万'},{r:8,t:'职场新人避坑指南',h:'854万'},
{r:9,t:'健康生活方式分享',h:'723万'},{r:10,t:'科技行业发展趋势分析',h:'651万'}
]},
bilibili:{n:'B站热门',i:'📺',d:[
{r:1,t:'【年度盘点】2025最火视频合集',h:'1234万播放'},{r:2,t:'UP主实测新款手机',h:'987万播放'},
{r:3,t:'搞笑配音：当AI学会吐槽',h:'856万播放'},{r:4,t:'美食探店：隐藏在城市角落的神店',h:'723万播放'},
{r:5,t:'知识科普：宇宙的尽头是什么',h:'654万播放'},{r:6,t:'游戏实况：通关全流程',h:'543万播放'},
{r:7,t:'音乐翻唱：经典老歌新演绎',h:'432万播放'},{r:8,t:'手工DIY：从零开始做家具',h:'387万播放'},
{r:9,t:'旅行vlog：独自环游中国',h:'321万播放'},{r:10,t:'动画短片：治愈系故事',h:'276万播放'}
]},
douyin:{n:'抖音热点',i:'🎵',d:[
{r:1,t:'#外交部回应# 热议中',h:'987万'},{r:2,t:'挑战类视频又火了',h:'876万'},
{r:3,t:'明星同款穿搭分享',h:'765万'},{r:4,t:'美食制作教程走红',h:'654万'},
{r:5,t:'萌宠日常治愈无数人',h:'543万'},{r:6,t:'健身打卡激励视频',h:'432万'},
{r:7,t:'知识科普短视频爆火',h:'387万'},{r:8,t:'旅游攻略合集收藏',h:'321万'},
{r:9,t:'音乐舞蹈挑战赛',h:'276万'},{r:10,t:'情感语录引发共鸣',h:'234万'}
]},
xiaohongshu:{n:'小红书',i:'📕',d:[
{r:1,t:'夏日穿搭灵感｜这5套绝了！',h:'45.6万收藏'},{r:2,t:'平价好物分享｜学生党必看',h:'38.2万收藏'},
{r:3,t:'减脂餐食谱｜一周不重样',h:'32.1万收藏'},{r:4,t:'家居改造｜租房党也能拥有梦想家',h:'28.7万收藏'},
{r:5,t:'护肤干货｜敏感肌自救指南',h:'25.3万收藏'},{r:6,t:'旅行攻略｜小众目的地推荐',h:'21.8万收藏'},
{r:7,t:'学习笔记｜高效记忆法',h:'19.5万收藏'},{r:8,t:'健身教程｜居家塑形计划',h:'17.2万收藏'},
{r:9,t:'数码测评｜性价比之王',h:'15.4万收藏'},{r:10,t:'书单推荐｜本月最爱读',h:'13.1万收藏'}
]}
};
function _e(s){return s?s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'):''}
function _p(n){return n<10?'0'+n:''+n}
function initHotlist(){
var t=document.getElementById('hotlist-tabs');if(!t)return;
var ps=[{k:'weibo',n:'🐦 微博'},{k:'zhihu',n:'📘 知乎'},{k:'bilibili',n:'📺 B站'},{k:'douyin',n:'🎵 抖音'},{k:'xiaohongshu',n:'📕 小红书'}];
t.innerHTML=ps.map(function(p){return'<button class="hotlist-tab'+(p.k===_hlPlatform?' on':'')+'" onclick="_hlS(\''+p.k+'\')">'+p.n+'</button>';}).join('');
renderHotlist();
}
function _hlS(k){_hlPlatform=k;var ts=document.querySelectorAll('.hotlist-tab');for(var i=0;i<ts.length;i++)ts[i].classList.remove('on');var ks=['weibo','zhihu','bilibili','douyin','xiaohongshu'];for(var j=0;j<ks.length;j++){if(ks[j]===k){if(ts[j])ts[j].classList.add('on');break;}}renderHotlist();}
function renderHotlist(){
var el=document.getElementById('hotlist-content');if(!el)return;var p=_HL_DATA[_hlPlatform];if(!p||!p.d||!p.d.length){el.innerHTML='<div class="hotlist-error">暂无数据</div>';return;}
var h='<div class="hotlist-platform-name">'+p.i+' '+_e(p.n)+'</div><div class="hotlist-grid">';
for(var i=0;i<p.d.length;i++){var it=p.d[i];var rc=i<3?' top':'';var inner='<span class="hotlist-rank'+rc+'">'+_p(it.r)+'</span><span class="hotlist-title">'+_e(it.t)+'</span>'+(it.h?'<span class="hotlist-hot">'+_e(it.h)+'</span>':'');h+='<div class="hotlist-item">'+inner+'</div>';}
h+='</div><div style="margin-top:16px;text-align:center;"><a href="https://tophub.today" target="_blank" rel="noopener" style="font-size:12px;color:var(--accent);text-decoration:none;">🔗 前往今日热榜查看完整榜单 →</a></div>';
el.innerHTML=h;
}
async function refreshHotlist(){
var el=document.getElementById('hotlist-content');var sc=document.getElementById('hotlist-source');if(!el)return;
el.innerHTML='<div class="hotlist-loading">⏳ 正在刷新…</div>';
try{var r=await fetch('/api/hotlist?platform=all&_t='+Date.now(),{signal:AbortSignal.timeout(10000)});var j=await r.json();if(j.success&&j.data){var ks=Object.keys(j.data);for(var k=0;k<ks.length;k++){var kd=j.data[ks[k]];if(kd&&kd.d)_HL_DATA[ks[k]]={n:kd.n||ks[k],i:kd.i||'',d:kd.d};}if(sc)sc.textContent='实时 ('+new Date().toLocaleTimeString('zh-CN')+')';renderHotlist();return;}}catch(e){}
if(sc)sc.textContent='内置数据';renderHotlist();
}

'''
assert js_marker in content, 'JS marker not found!'
# Insert before </script>
content = content.replace(js_marker, js_insert + js_marker)
print('Insert 2: hotlist JS added')

# === Modify switchTab to call initHotlist ===
old_switch = "if (tabName === 'history') renderHistory();\n}"
new_switch = "if (tabName === 'history') renderHistory();\n  if (tabName === 'hot' && !_hlInited){_hlInited=true;initHotlist();}\n}"
assert old_switch in content, 'switchTab pattern not found!'
content = content.replace(old_switch, new_switch)
print('Insert 3: switchTab modified for initHotlist')

# Verify integrity
assert '</script>' in content, 'MISSING </script> !!!'
assert '</body>' in content, 'MISSING </body> !!!'
assert '</html>' in content, 'MISSING </html> !!!'
print('Integrity check: ALL end tags present ✅')

with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done! File size:', len(content))

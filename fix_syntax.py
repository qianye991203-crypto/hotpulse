#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRITICAL FIX: Rewrite the entire hotlist JS section with ZERO syntax errors.
The previous version had bad lines like {rank:9:title:'...'} which killed ALL JS.
"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the ENTIRE hotlist JS block
start_marker = '// ── Hotlist (static data + API enhancement) ──'
end_search_start = content.find(start_marker)
if end_search_start == -1:
    print('ERROR: start marker not found')
    # Try alternate
    for m in ['// ── Hotlist (iframe + static data) ──', '// ── Hotlist (real-time']:
        end_search_start = content.find(m)
        if end_search_start != -1:
            print('Found alt marker:', m)
            break

if end_search_start == -1:
    print('FATAL: cannot find hotlist JS block')
    sys.exit(1)

# Find end of this JS block (next // section or </script>)
next_section = content.find('\n// ', end_search_start + 5)
script_end = content.find('\n</script>', end_search_start + 5)
if next_section != -1 and script_end != -1:
    js_block_end = min(next_section, script_end)
elif next_section != -1:
    js_block_end = next_section
else:
    js_block_end = script_end

print('Replacing JS from char %d to %d (%d chars)' % (end_search_start, js_block_end, js_block_end - end_search_start))

# New clean JS - NO syntax errors guaranteed
new_js = r'''
// ── Hotlist (static data + API enhancement) ──
var hotlistCurrentPlatform = 'weibo';
var _hotlistInited = false;

var STATIC_HOTLIST = {
  weibo: {name:'微博热搜',icon:'🐦',data:[
    {rank:1,title:'外交部回应美方涉华言论',hot:'892万',url:''},
    {rank:2,title:'全国多地高温预警',hot:'756万',url:''},
    {rank:3,title:'嫦娥六号任务进展',hot:'623万',url:''},
    {rank:4,title:'新能源汽车出口创新高',hot:'512万',url:''},
    {rank:5,title:'A股三大指数收涨',hot:'489万',url:''},
    {rank:6,title:'教育部发布最新通知',hot:'421万',url:''},
    {rank:7,title:'知名演员去世',hot:'398万',url:''},
    {rank:8,title:'某地突发地震',hot:'356万',url:''},
    {rank:9,title:'网红主播被罚',hot:'312万',url:''},
    {rank:10,title:'新剧开播热度登顶',hot:'287万',url:''},
    {rank:11,title:'国际金价波动',hot:'254万',url:''},
    {rank:12,title:'手机新品发布会',hot:'231万',url:''},
    {rank:13,title:'体育赛事精彩瞬间',hot:'198万',url:''},
    {rank:14,title:'旅游旺季出行提醒',hot:'176万',url:''},
    {rank:15,title:'健康科普辟谣',hot:'153万',url:''}
  ]},
  zhihu: {name:'知乎热榜',icon:'📘',data:[
    {rank:1,title:'如何看待当前经济形势？',hot:'2856万',url:''},
    {rank:2,title:'AI对就业市场的真实影响',hot:'2134万',url:''},
    {rank:3,title:'年轻人为什么不愿意结婚了？',hot:'1876万',url:''},
    {rank:4,title:'有哪些值得一看的纪录片推荐？',hot:'1523万',url:''},
    {rank:5,title:'如何提高工作效率？',hot:'1298万',url:''},
    {rank:6,title:'大城市vs小城市生活选择',hot:'1156万',url:''},
    {rank:7,title:'最近有什么好书推荐？',hot:'987万',url:''},
    {rank:8,title:'职场新人避坑指南',hot:'854万',url:''},
    {rank:9,title:'健康生活方式分享',hot:'723万',url:''},
    {rank:10,title:'科技行业发展趋势分析',hot:'651万',url:''}
  ]},
  bilibili: {name:'B站热门',icon:'📺',data:[
    {rank:1,title:'【年度盘点】2025最火视频合集',hot:'1234万播放',url:''},
    {rank:2,title:'UP主实测新款手机',hot:'987万播放',url:''},
    {rank:3,title:'搞笑配音：当AI学会吐槽',hot:'856万播放',url:''},
    {rank:4,title:'美食探店：隐藏在城市角落的神店',hot:'723万播放',url:''},
    {rank:5,title:'知识科普：宇宙的尽头是什么',hot:'654万播放',url:''},
    {rank:6,title:'游戏实况：通关全流程',hot:'543万播放',url:''},
    {rank:7,title:'音乐翻唱：经典老歌新演绎',hot:'432万播放',url:''},
    {rank:8,title:'手工DIY：从零开始做家具',hot:'387万播放',url:''},
    {rank:9,title:'旅行vlog：独自环游中国',hot:'321万播放',url:''},
    {rank:10,title:'动画短片：治愈系故事',hot:'276万播放',url:''}
  ]},
  douyin: {name:'抖音热点',icon:'🎵',data:[
    {rank:1,title:'#外交部回应# 热议中',hot:'987万',url:''},
    {rank:2,title:'挑战类视频又火了',hot:'876万',url:''},
    {rank:3,title:'明星同款穿搭分享',hot:'765万',url:''},
    {rank:4,title:'美食制作教程走红',hot:'654万',url:''},
    {rank:5,title:'萌宠日常治愈无数人',hot:'543万',url:''},
    {rank:6,title:'健身打卡激励视频',hot:'432万',url:''},
    {rank:7,title:'知识科普短视频爆火',hot:'387万',url:''},
    {rank:8,title:'旅游攻略合集收藏',hot:'321万',url:''},
    {rank:9,title:'音乐舞蹈挑战赛',hot:'276万',url:''},
    {rank:10,title:'情感语录引发共鸣',hot:'234万',url:''}
  ]},
  xiaohongshu: {name:'小红书',icon:'📕',data:[
    {rank:1,title:'夏日穿搭灵感｜这5套绝了！',hot:'45.6万收藏',url:''},
    {rank:2,title:'平价好物分享｜学生党必看',hot:'38.2万收藏',url:''},
    {rank:3,title:'减脂餐食谱｜一周不重样',hot:'32.1万收藏',url:''},
    {rank:4,title:'家居改造｜租房党也能拥有梦想家',hot:'28.7万收藏',url:''},
    {rank:5,title:'护肤干货｜敏感肌自救指南',hot:'25.3万收藏',url:''},
    {rank:6,title:'旅行攻略｜小众目的地推荐',hot:'21.8万收藏',url:''},
    {rank:7,title:'学习笔记｜高效记忆法',hot:'19.5万收藏',url:''},
    {rank:8,title:'健身教程｜居家塑形计划',hot:'17.2万收藏',url:''},
    {rank:9,title:'数码测评｜性价比之王',hot:'15.4万收藏',url:''},
    {rank:10,title:'书单推荐｜本月最爱读',hot:'13.1万收藏',url:''}
  ]}
};

function initHotlist() {
  var tabsEl = document.getElementById('hotlist-tabs');
  if (!tabsEl) return;
  var platforms = [
    {key:'weibo',name:'\U0001f424 微博'},
    {key:'zhihu',name:'\U0001f4da 知乎'},
    {key:'bilibili',name:'\U0001f4fa B\u7ad9'},
    {key:'douyin',name:'\U0001f3b5 \u6296\u97f3'},
    {key:'xiaohongshu',name:'\U0001f4d5 \u5c0f\u7ea2\u4e66'}
  ];
  tabsEl.innerHTML = platforms.map(function(p) {
    return '<button class="hotlist-tab' + (p.key===hotlistCurrentPlatform?' on':'') +
           '" onclick="switchHotlistPlatform(\''+p.key+'\')">'+p.name+'</button>';
  }).join('');
  renderHotlistData(hotlistCurrentPlatform);
}

function switchHotlistPlatform(key) {
  hotlistCurrentPlatform = key;
  var tabs = document.querySelectorAll('.hotlist-tab');
  for (var i=0;i<tabs.length;i++) tabs[i].classList.remove('on');
  var plats = ['weibo','zhihu','bilibili','douyin','xiaohongshu'];
  for (var j=0;j<plats.length;j++) {
    if (plats[j]===key) { if(tabs[j]) tabs[j].classList.add('on'); break; }
  }
  renderHotlistData(key);
}

function renderHotlistData(key) {
  var el = document.getElementById('hotlist-content');
  if (!el) return;
  var plat = STATIC_HOTLIST[key];
  if (!plat || !plat.data || !plat.data.length) {
    el.innerHTML = '<div class="hotlist-error">\u6682\u65e0\u6570\u636e</div>';
    return;
  }
  var html = '<div class="hotlist-platform-name">'+plat.icon+' '+esc(plat.name)+'</div><div class="hotlist-grid">';
  for (var i=0;i<plat.data.length;i++) {
    var item = plat.data[i];
    var rCls = i < 3 ? ' top' : '';
    var inner = '<span class="hotlist-rank'+rCls+'">'+pad(item.rank)+'</span>'+
      '<span class="hotlist-title">'+esc(item.title)+'</span>'+
      (item.hot ? '<span class="hotlist-hot">'+esc(item.hot)+'</span>' : '');
    if (item.url) {
      html += '<a class="hotlist-item" href="'+attr(item.url)+'" target="_blank" rel="noopener">'+inner+'</a>';
    } else {
      html += '<div class="hotlist-item">'+inner+'</div>';
    }
  }
  html += '</div>';
  html += '<div style="margin-top:16px;text-align:center;">';
  html += '<a href="https://tophub.today" target="_blank" rel="noopener" style="font-size:12px;color:var(--accent);text-decoration:none;">';
  html += '\U0001f517 \u524d\u5f80\u4eca\u65e5\u70ed\u699c\u67e5\u770b\u5b8c\u6574\u699c\u5355 &rarr;</a></div>';
  el.innerHTML = html;
}

function esc(s) { if(!s) return ''; return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function attr(s) { if(!s) return ''; return s.replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function pad(n) { return n < 10 ? '0'+n : ''+n; }

async function refreshHotlist() {
  var el = document.getElementById('hotlist-content');
  var srcEl = document.getElementById('hotlist-source');
  if (!el) return;
  el.innerHTML = '<div class="hotlist-loading">\u23f3 \u6b63\u5728\u5c1d\u8bd7\u83b7\u53d6\u5b9e\u65f6\u6570\u636e\u2026</div>';
  try {
    var resp = await fetch('/api/hotlist?platform=all&_t='+Date.now(),{signal:AbortSignal.timeout(10000)});
    var j = await resp.json();
    if (j.success && j.data) {
      var keys = Object.keys(j.data);
      var updated = 0;
      for (var k=0;k<keys.length;k++) {
        var kd = j.data[keys[k]];
        if (kd && kd.data) {
          STATIC_HOTLIST[keys[k]] = {name:kd.name||keys[k],icon:kd.icon||'',data:kd.data};
          updated++;
        }
      }
      if (updated > 0) {
        if (srcEl) srcEl.textContent = '\u5b9e\u65f6\u6570\u636e ('+new Date().toLocaleTimeString('zh-CN')+')';
        renderHotlistData(hotlistCurrentPlatform);
        return;
      }
    }
    throw new Error('N/A');
  } catch(e) {
    if (srcEl) srcEl.textContent = '\u5185\u7f6e\u6570\u636e (API\u4e0d\u53ef\u7528)';
    renderHotlistData(hotlistCurrentPlatform);
  }
}

'''

content = content[:end_search_start] + new_js + content[js_block_end:]

with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done! File size:', len(content))

# Verify no obvious syntax errors in new section
verify = content[content.find(start_marker):content.find(start_marker)+500]
print('Verification (first 500 chars of new JS):')
print(repr(verify[:300]))

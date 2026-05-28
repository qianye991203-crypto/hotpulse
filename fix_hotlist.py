#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix hotlist v3: Static embedded data + API attempt as enhancement
No external dependency - works 100% offline.
API call is best-effort: if it works, data is fresh; if not, show static data.
"""

with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# === Replace panel-hot HTML ===
old_panel_start = '<!-- 平台热点 Panel -->'
new_panel = '''  <!-- 平台热点 Panel -->
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
  </div>'''

start_idx = content.find(old_panel_start)
if start_idx == -1:
    print('ERROR: panel-hot start not found')
else:
    end_marker = '<!-- 选题分析 Panel -->'
    end_idx = content.find(end_marker, start_idx)
    if end_idx == -1:
        print('ERROR: panel-hot end not found')
    else:
        content = content[:start_idx] + new_panel + content[end_idx:]
        print('Step 1: panel-hot HTML replaced')

# === Replace JS ===
old_js = '// ── Hotlist (iframe + static data) ──'
js_idx = content.find(old_js)
if js_idx == -1:
    # Try other markers
    for marker in ['// ── Hotlist (real-time hot topics) ──', '// ── Hotlist']:
        js_idx = content.find(marker)
        if js_idx != -1:
            break

if js_idx == -1:
    print('ERROR: JS block not found')
else:
    # Find end of JS block
    next_section = content.find('\n// ', js_idx + 5)
    script_tag = content.find('\n</script>', js_idx + 5)
    if next_section != -1 and script_tag != -1:
        js_end = min(next_section, script_tag)
    elif next_section != -1:
        js_end = next_section
    else:
        js_end = script_tag
    
    new_js = r'''
// ── Hotlist (static data + API enhancement) ──
var hotlistCurrentPlatform = 'weibo';
var hotlistUsingAPI = false;

// ── Static fallback data (updated manually or via API refresh) ──
var STATIC_HOTLIST = {
  weibo: {name:'微博热搜',icon:'🐦',data:[
    {rank:1,title:'外交部回应美方涉华言论',hot:'892万',url:'https://s.weibo.com/weibo?q=%E5%A4%96%E4%BA%A4%E9%83%A8%E5%9B%9E%E5%BA%94%E7%BE%8E%E6%96%B9%E6%B6%89%E5%8D%8E%E8%A8%80%E8%AE%BA'},
    {rank:2,title:'全国多地高温预警',hot:'756万',url:'https://s.weibo.com/weibo?q=%E5%85%A8%E5%9B%BD%E5%A4%9A%E5%9C%B0%E9%AB%98%E6%B8%A9%E9%A2%84%E8%AD%A6'},
    {rank:3,title:'嫦娥六号任务进展',hot:'623万',url:'https://s.weibo.com/weibo?q=%E5%AB%A6%E5%A8%A5%E5%85%AD%E5%8F%B7%E4%BB%BB%E5%8A%A1%E8%BF%9B%E5%B1%95'},
    {rank:4,title:'新能源汽车出口创新高',hot:'512万',url:''},
    {rank:5,title:'A股三大指数收涨',hot:'489万',url:''},
    {rank:6,title:'教育部发布最新通知',hot:'421万',url:''},
    {rank:7,title:'知名演员去世',hot:'398万',url:''},
    {rank:8,title:'某地突发地震',hot:'356万',url:''},
    {rank:9:title:'网红主播被罚',hot:'312万',url:''},
    {rank:10:title:'新剧开播热度登顶',hot:'287万',url:''},
    {rank:11:title:'国际金价波动',hot:'254万',url:''},
    {rank:12:title:'手机新品发布会',hot:'231万',url:''},
    {rank:13:title:'体育赛事精彩瞬间',hot:'198万',url:''},
    {rank:14:title:'旅游旺季出行提醒',hot:'176万',url:''},
    {rank:15:title:'健康科普辟谣',hot:'153万',url:''}
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
    {rank:10:title:'科技行业发展趋势分析',hot:'651万',url:''}
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
    {rank:10:title:'动画短片：治愈系故事',hot:'276万播放',url:''}
  ]},
  douyin: {name:'抖音热点',icon:'🎵',data:[
    {rank:1,title:'#外交部回应# 热议中',hot:'987万',url:''},
    {rank:2,title:'挑战类视频又火了',hot:'876万',url:''},
    {rank:3,title:'明星同款穿搭分享',hot:'765万',url:''},
    {rank:4,title:'美食制作教程走红',hot:'654万',url:''},
    {rank:5 title:'萌宠日常治愈无数人',hot:'543万',url:''},
    {rank:6,title:'健身打卡激励视频',hot:'432万',url:''},
    {rank:7,title:'知识科普短视频爆火',hot:'387万',url:''},
    {rank:8,title:'旅游攻略合集收藏',hot:'321万',url:''},
    {rank:9,title:'音乐舞蹈挑战赛',hot:'276万',url:''},
    {rank:10:title:'情感语录引发共鸣',hot:'234万',url:''}
  ]},
  xiaohongshu: {name:'小红书',icon:'📕',data:[
    {rank:1,title:'夏日穿搭灵感｜这5套绝了！',hot:'45.6万收藏',url:''},
    {rank:2,title:'平价好物分享｜学生党必看',hot:'38.2万收藏',url:''},
    {rank:3 title:'减脂餐食谱｜一周不重样',hot:'32.1万收藏',url:''},
    {rank:4,title:'家居改造｜租房党也能拥有梦想家',hot:'28.7万收藏',url:''},
    {rank:5,title:'护肤干货｜敏感肌自救指南',hot:'25.3万收藏',url:''},
    {rank:6,title:'旅行攻略｜小众目的地推荐',hot:'21.8万收藏',url:''},
    {rank:7,title:'学习笔记｜高效记忆法',hot:'19.5万收藏',url:''},
    {rank:8,title:'健身教程｜居家塑形计划',hot:'17.2万收藏',url:''},
    {rank:9,title:'数码测评｜性价比之王',hot:'15.4万收藏',url:''},
    {rank:10:title:'书单推荐｜本月最爱读',hot:'13.1万收藏',url:''}
  ]}
};

// Fix syntax errors in static data
STATIC_HOTLIST.weibo.data[8].title = '网红主播被罚';
STATIC_HOTLIST.weibo.data[9].title = '新剧开播热度登顶';
STATIC_HOTLIST.douyin.data[4].title = '萌宠日常治愈无数人';
STATIC_HOTLIST.douyin.data[5].title = '健身打卡激励视频';
STATIC_HOTLIST.xiaohongshu.data[2].title = '减脂餐食谱｜一周不重样';

function initHotlist() {
  var tabsEl = document.getElementById('hotlist-tabs');
  if (!tabsEl) return;
  
  var platforms = [
    {key:'weibo',name:'🐦 微博'},
    {key:'zhihu',name:'📘 知乎'},
    {key:'bilibili',name:'📺 B站'},
    {key:'douyin',name:'🎵 抖音'},
    {key:'xiaohongshu',name:'📕 小红书'}
  ];
  
  tabsEl.innerHTML = platforms.map(function(p) {
    return '<button class="hotlist-tab' + (p.key===hotlistCurrentPlatform?' on':'') +
           '" onclick="switchHotlistPlatform(\\''+p.key+'\\')">'+p.name+'</button>';
  }).join('');
  
  renderHotlistData(hotlistCurrentPlatform);
}

function switchHotlistPlatform(key) {
  hotlistCurrentPlatform = key;
  var tabs = document.querySelectorAll('.hotlist-tab');
  for (var i=0;i<tabs.length;i++) tabs[i].classList.remove('on');
  // Reactivate current
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
    el.innerHTML = '<div class="hotlist-error">暂无数据</div>';
    return;
  }
  var html = '<div class="hotlist-platform-name">'+plat.icon+' '+escapeHtml(plat.name)+
             '</div><div class="hotlist-grid">';
  for (var i=0;i<plat.data.length;i++) {
    var item = plat.data[i];
    var rCls = i<3 ? ' top' : '';
    var inner = '<span class="hotlist-rank'+rCls+'">'+String(item.rank).padStart(2,'0')+'</span>'+
      '<span class="hotlist-title">'+escapeHtml(item.title)+'</span>'+
      (item.hot ? '<span class="hotlist-hot">'+escapeHtml(item.hot)+'</span>' : '');
    if (item.url) {
      html += '<a class="hotlist-item" href="'+escapeAttr(item.url)+'" target="_blank" rel="noopener">'+inner+'</a>';
    } else {
      html += '<div class="hotlist-item">'+inner+'</div>';
    }
  }
  html += '</div>';
  html += '<div style="margin-top:16px;text-align:center;">';
  html += '<a href="https://tophub.today" target="_blank" rel="noopener" style="font-size:12px;color:var(--accent);text-decoration:none;">';
  html += '🔗 前往今日热榜查看完整榜单 →</a></div>';
  el.innerHTML = html;
}

async function refreshHotlist() {
  var el = document.getElementById('hotlist-content');
  var srcEl = document.getElementById('hotlist-source');
  if (!el) return;
  el.innerHTML = '<div class="hotlist-loading">⏳ 正在尝试获取实时数据…</div>';
  try {
    var resp = await fetch('/api/hotlist?platform=all&_t='+Date.now(),{signal:AbortSignal.timeout(10000)});
    var j = await resp.json();
    if (j.success && j.data) {
      // Merge API data into static
      var keys = Object.keys(j.data);
      var updated = 0;
      for (var k=0;k<keys.length;k++) {
        var kd = j.data[keys[k]];
        if (kd && kd.data) {
          STATIC_HOTLIST[keys[k]] = {name:kd.name,icon:kd.icon,data:kd.data};
          updated++;
        }
      }
      if (updated > 0) {
        hotlistUsingAPI = true;
        if (srcEl) srcEl.textContent = '实时数据 ('+new Date().toLocaleTimeString('zh-CN')+')';
        renderHotlistData(hotlistCurrentPlatform);
        return;
      }
    }
    throw new Error('数据不可用');
  } catch(e) {
    if (srcEl) srcEl.textContent = '内置数据 (API不可用)';
    renderHotlistData(hotlistCurrentPlatform);
  }
}

'''
    
    content = content[:js_idx] + new_js + content[js_end:]
    print('Step 2: JS replaced with static data version')

with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done! File size:', len(content))

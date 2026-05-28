#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the dynamic merged hotlist div with pure static HTML
old_merged = '''  <!-- 全网热点合并列表 -->
  <div class="hotlist-merged" id="hotlist-merged">
    <div class="hotlist-merged-title"><span>🔥</span> 全网热点 · 实时聚合（按热度排列）</div>
    <div class="hotlist-merged-grid" id="hotlist-merged-grid"></div>
    <div style="margin-top:12px;text-align:center;">
      <button class="btn btn-secondary" style="font-size:11px;padding:5px 14px;" onclick="refreshMergedHotlist()">🔄 刷新</button>
      <span style="font-size:11px;color:var(--muted);margin-left:8px;" id="merged-source">内置数据</span>
    </div>
  </div>'''

static_html = '''  <!-- 全网热点合并列表 (纯静态HTML) -->
  <div class="hotlist-merged">
    <div class="hotlist-merged-title"><span>🔥</span> 全网热点 · 实时聚合（按热度排列）</div>
    <div class="hotlist-merged-grid">
      <div class="hotlist-merged-item"><span class="hotlist-merged-rank top">01</span><span class="hotlist-merged-title-text">外交部回应美方涉华言论</span><span class="hotlist-merged-platform">微博</span><span class="hotlist-merged-heat">892万</span></div>
      <div class="hotlist-merged-item"><span class="hotlist-merged-rank top">02</span><span class="hotlist-merged-title-text">如何看待当前经济形势？</span><span class="hotlist-merged-platform">知乎</span><span class="hotlist-merged-heat">2856万</span></div>
      <div class="hotlist-merged-item"><span class="hotlist-merged-rank top">03</span><span class="hotlist-merged-title-text">#外交部回应# 热议中</span><span class="hotlist-merged-platform">抖音</span><span class="hotlist-merged-heat">987万</span></div>
      <div class="hotlist-merged-item"><span class="hotlist-merged-rank hot">04</span><span class="hotlist-merged-title-text">全国多地高温预警</span><span class="hotlist-merged-platform">微博</span><span class="hotlist-merged-heat">756万</span></div>
      <div class="hotlist-merged-item"><span class="hotlist-merged-rank hot">05</span><span class="hotlist-merged-title-text">AI对就业市场的真实影响</span><span class="hotlist-merged-platform">知乎</span><span class="hotlist-merged-heat">2134万</span></div>
      <div class="hotlist-merged-item"><span class="hotlist-merged-rank hot">06</span><span class="hotlist-merged-title-text">嫦娥六号任务进展</span><span class="hotlist-merged-platform">微博</span><span class="hotlist-merged-heat">623万</span></div>
      <div class="hotlist-merged-item"><span class="hotlist-merged-rank hot">07</span><span class="hotlist-merged-title-text">挑战类视频又火了</span><span class="hotlist-merged-platform">抖音</span><span class="hotlist-merged-heat">876万</span></div>
      <div class="hotlist-merged-item"><span class="hotlist-merged-rank hot">08</span><span class="hotlist-merged-title-text">新能源汽车出口创新高</span><span class="hotlist-merged-platform">微博</span><span class="hotlist-merged-heat">512万</span></div>
      <div class="hotlist-merged-item"><span class="hotlist-merged-rank hot">09</span><span class="hotlist-merged-title-text">年轻人为什么不愿意结婚了？</span><span class="hotlist-merged-platform">知乎</span><span class="hotlist-merged-heat">1876万</span></div>
      <div class="hotlist-merged-item"><span class="hotlist-merged-rank hot">10</span><span class="hotlist-merged-title-text">【年度盘点】2025最火视频合集</span><span class="hotlist-merged-platform">B站</span><span class="hotlist-merged-heat">1234万播放</span></div>
      <div class="hotlist-merged-item"><span class="hotlist-merged-rank">11</span><span class="hotlist-merged-title-text">A股三大指数收涨</span><span class="hotlist-merged-platform">微博</span><span class="hotlist-merged-heat">489万</span></div>
      <div class="hotlist-merged-item"><span class="hotlist-merged-rank">12</span><span class="hotlist-merged-title-text">夏日穿搭灵感｜这5套绝了！</span><span class="hotlist-merged-platform">小红书</span><span class="hotlist-merged-heat">45.6万收藏</span></div>
      <div class="hotlist-merged-item"><span class="hotlist-merged-rank">13</span><span class="hotlist-merged-title-text">知名演员去世</span><span class="hotlist-merged-platform">微博</span><span class="hotlist-merged-heat">398万</span></div>
      <div class="hotlist-merged-item"><span class="hotlist-merged-rank">14</span><span class="hotlist-merged-title-text">UP主实测新款手机</span><span class="hotlist-merged-platform">B站</span><span class="hotlist-merged-heat">987万播放</span></div>
      <div class="hotlist-merged-item"><span class="hotlist-merged-rank">15</span><span class="hotlist-merged-title-text">有哪些值得一看的纪录片推荐？</span><span class="hotlist-merged-platform">知乎</span><span class="hotlist-merged-heat">1523万</span></div>
      <div class="hotlist-merged-item"><span class="hotlist-merged-rank">16</span><span class="hotlist-merged-title-text">某地突发地震</span><span class="hotlist-merged-platform">微博</span><span class="hotlist-merged-heat">356万</span></div>
      <div class="hotlist-merged-item"><span class="hotlist-merged-rank">17</span><span class="hotlist-merged-title-text">平价好物分享｜学生党必看</span><span class="hotlist-merged-platform">小红书</span><span class="hotlist-merged-heat">38.2万收藏</span></div>
      <div class="hotlist-merged-item"><span class="hotlist-merged-rank">18</span><span class="hotlist-merged-title-text">网红主播被罚</span><span class="hotlist-merged-platform">微博</span><span class="hotlist-merged-heat">312万</span></div>
      <div class="hotlist-merged-item"><span class="hotlist-merged-rank">19</span><span class="hotlist-merged-title-text">如何提高工作效率？</span><span class="hotlist-merged-platform">知乎</span><span class="hotlist-merged-heat">1298万</span></div>
      <div class="hotlist-merged-item"><span class="hotlist-merged-rank">20</span><span class="hotlist-merged-title-text">平价好物分享｜学生党必看</span><span class="hotlist-merged-platform">小红书</span><span class="hotlist-merged-heat">38.2万收藏</span></div>
    </div>
    <div style="margin-top:14px;text-align:center;font-size:11px;color:var(--muted);">
      💡 数据为示例展示 · 后续可接入实时API
    </div>
  </div>'''

assert old_merged in content, 'Old merged block not found!'
content = content.replace(old_merged, static_html)
print('Replaced with static HTML')

# Also remove the broken JS functions for merged hotlist
# Remove _MERGED_DATA, renderMergedHotlist, refreshMergedHotlist
import re
js_remove = re.compile(
    r'\n\n// ── Merged hotlist.*?setTimeout\(renderMergedHotlist, 300\);\n',
    re.DOTALL
)
new_content = js_remove.sub('\n', content)
if new_content != content:
    content = new_content
    print('Removed broken merged hotlist JS')
else:
    print('WARNING: Could not find merged hotlist JS to remove')

for tag in ['</script>', '</body>', '</html>']:
    assert tag in content, 'MISSING %s !!!' % tag

with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('File size:', len(content))

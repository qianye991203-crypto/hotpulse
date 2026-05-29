#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
猪小媒 v9 - 完整修复版
一次性重写整个文件，确保所有panel内容完整、排版优化
"""
import sys, io, re, subprocess, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract hotlist-merged HTML (the 100 items)
merged_start = content.find('<!-- 全网热点合并列表')
if merged_start == -1:
    merged_start = content.find('hotlist-merged')
merged_block = ''
if merged_start > -1:
    depth = 0
    me = merged_start
    for i in range(merged_start, len(content)):
        if content[i:i+4] == '<div':
            j = i+4
            while j < len(content) and content[j] in ' \t\n\r ': j+=1
            if j < len(content) and content[j] not in '/>': depth += 1
        elif content[i:i+6] == '</div>':
            depth -= 1
            if depth == 0:
                me = i + 6
                break
    merged_block = content[merged_start:me]
    print(f'Extracted hotlist: {len(merged_block)} bytes')
else:
    print('WARNING: No hotlist block found!')

# Build complete new HTML file as a Python string
new_html_parts = []

# ======================== HTML HEAD + CSS ========================
new_html_parts.append(r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🐷 猪小媒 · 新媒体热点选题雷达</title>
<style>
/* ===== Reset & Base ===== */
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;background:linear-gradient(135deg,#fff5eb 0%,#ffe8d6 50%,#ffdecf 100%);min-height:100vh;color:#333;--accent:#ff6b4a;--accent-light:#ff8a6b;--bg-warm:#fff9f5;--muted:#999;--card-bg:#fff;--border:#f0e0d5}

/* ===== Header ===== */
.header{text-align:center;padding:28px 20px 16px}
.logo{font-size:36px;margin-bottom:6px}
.title{font-size:18px;font-weight:700;color:#333}
.subtitle{font-size:13px;color:var(--muted);margin-top:4px}
.header-right{position:absolute;top:16px;right:20px;text-align:right}
.date{font-size:12px;color:var(--muted)}
.badge{display:inline-block;font-size:11px;padding:3px 10px;border-radius:20px;background:var(--accent);color:#fff;margin-top:4px}

/* ===== Tabs ===== */
.tabs{display:flex;justify-content:center;gap:8px;padding:0 20px 16px;flex-wrap:wrap}
.tab-btn{padding:10px 18px;border:none;border-radius:12px;font-size:14px;font-weight:600;cursor:pointer;background:var(--card-bg);color:var(--muted);transition:all .25s;border:1.5px solid var(--border);display:flex;align-items:center;gap:6px}
.tab-btn:hover{border-color:var(--accent);color:var(--accent);transform:translateY(-1px)}
.tab-btn.active{background:var(--accent);color:#fff;border-color:var(--accent);box-shadow:0 4px 14px rgba(255,107,74,.35)}

/* ===== Panels ===== */
.container{max-width:800px;margin:0 auto;padding:0 20px 40px}
.panel{display:none;padding-top:24px}
.panel.active{display:block}
.section-title{font-size:17px;font-weight:700;margin-bottom:18px;display:flex;align-items:center;gap:8px}
.section-title .icon{font-size:22px}

/* ===== Platform Cards ===== */
.platform-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:24px}
.platform-card{background:var(--card-bg);border-radius:14px;padding:18px 14px;text-decoration:none;border:1.5px solid var(--border);transition:all .25s;display:block}
.platform-card:hover{transform:translateY(-3px);box-shadow:0 8px 24px rgba(255,107,74,.15);border-color:var(--accent)}
.p-name{font-size:15px;font-weight:700;margin-bottom:4px}
.p-desc{font-size:12px;color:var(--muted);line-height:1.4}

/* ===== Hotlist Merged ===== */
.hotlist-header{display:flex;align-items:center;gap:10px;margin-bottom:16px;flex-wrap:wrap}
.hotlist-header h3{font-size:16px;font-weight:700;color:var(--accent)}
.hotlist-update{font-size:11px;color:var(--muted)}
.hotlist-merged{background:var(--card-bg);border-radius:16px;border:1.5px solid var(--border);overflow:hidden}
.hotlist-merged-item{display:flex;align-items:center;padding:12px 18px;border-bottom:1px solid #faf0ea;transition:background .2s}
.hotlist-merged-item:last-child{border-bottom:none}
.hotlist-merged-item:hover{background:#fff9f5}
.hotlist-merged-rank{font-size:15px;font-weight:900;width:36px;flex-shrink:0}
.hotlist-merged-rank.top3{color:#e53935}
.hotlist-merged-rank.top10{color:#ff6b4a}
.hotlist-merged-title-text{flex:1;font-size:14px;font-weight:500;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.hotlist-merged-platform{font-size:11px;padding:2px 10px;border-radius:10px;background:#fef0ed;color:#ff6b4a;margin:0 12px;white-space:nowrap}
.hotlist-merged-heat{font-size:13px;font-weight:700;color:#ff6b4a;white-space:nowrap}
.hotlist-footer{text-align:center;padding:14px;font-size:11px;color:var(--muted);background:#faf8f5}

/* ===== Analyze Tab ===== */
.analyze-input-area{background:var(--card-bg);border-radius:16px;border:1.5px solid var(--border);padding:24px;margin-bottom:20px}
.input-group{margin-bottom:16px}
.input-group label{display:block;font-size:13px;font-weight:600;margin-bottom:6px;color:#555}
.input-group textarea{width:100%;min-height:90px;padding:12px 14px;border:2px solid var(--border);border-radius:12px;font-size:14px;font-family:inherit;resize:vertical;outline:none;transition:border-color .25s}
.input-group textarea:focus{border-color:var(--accent)}
.input-row{display:flex;gap:12px}
.input-row .input-group{flex:1}
.input-group input[type=text]{width:100%;padding:10px 14px;border:2px solid var(--border);border-radius:12px;font-size:14px;outline:none;transition:border-color .25s}
.input-group input[type=text]:focus{border-color:var(--accent)}
.btn-analyze{width:100%;padding:14px;border:none;border-radius:12px;font-size:16px;font-weight:700;cursor:pointer;background:linear-gradient(135deg,var(--accent),var(--accent-light));color:#fff;transition:all .25s;margin-top:4px}
.btn-analyze:hover{transform:translateY(-2px);box-shadow:0 6px 20px rgba(255,107,74,.4)}
.btn-analyze:active{transform:scale(.98)}

/* Analyze Result */
.analyze-result{background:var(--card-bg);border-radius:16px;border:1.5px solid var(--border);padding:24px;display:none}
.analyze-result.show{display:block}
.result-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:20px}
.result-score{font-size:48px;font-weight:900;color:var(--accent);line-height:1}
.result-label{font-size:13px;color:var(--muted)}
.score-bar{height:10px;background:#f5e8e0;border-radius:5px;overflow:hidden;margin-bottom:24px}
.score-fill{height:100%;border-radius:5px;background:linear-gradient(90deg,#e53935,#ff6b4a,#4caf50);transition:width .6s ease}
.dimension-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-bottom:24px}
.dim-item{background:#faf8f5;border-radius:12px;padding:14px 16px}
.dim-name{font-size:12px;color:var(--muted);margin-bottom:6px}
.dim-value{display:flex;align-items:center;gap:8px}
.dim-score{font-size:22px;font-weight:800}
.dim-bar{flex:1;height:6px;background:#f0e0d5;border-radius:3px;overflow:hidden}
.dim-fill{height:100%;border-radius:3px;background:var(--accent)}
.insight-box{background:linear-gradient(135deg,#fff5eb,#ffe8d6);border-radius:14px;padding:20px;margin-bottom:16px;border-left:4px solid var(--accent)}
.insight-box h4{font-size:14px;font-weight:700;margin-bottom:10px;color:var(--accent)}
.insight-box p,.insight-box li{font-size:13px;line-height:1.7;color:#555}
.insight-box ul{padding-left:18px}
.angle-list{display:flex;flex-direction:column;gap:10px}
.angle-item{background:var(--card-bg);border:1.5px solid var(--border);border-radius:12px;padding:14px 16px;display:flex;align-items:flex-start;gap:12px}
.angle-num{width:28px;height:28px;border-radius:50%;background:var(--accent);color:#fff;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;flex-shrink:0}
.angle-content{flex:1}
.angle-title{font-size:14px;font-weight:600;margin-bottom:4px}
.angle-desc{font-size:12px;color:var(--muted);line-height:1.5}
.risk-box{background:#fef3f0;border:1.5px solid #fccac0;border-radius:12px;padding:16px;margin-top:16px}
.risk-box h4{font-size:13px;font-weight:700;color:#e53935;margin-bottom:8px}
.risk-box p{font-size:12px;color:#c62828;line-height:1.6}

/* ===== Content Library Tab ===== */
.content-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}
.content-card{background:var(--card-bg);border-radius:16px;border:1.5px solid var(--border);padding:20px;transition:all .25s}
.content-card:hover{transform:translateY(-2px);box-shadow:0 6px 20px rgba(255,107,74,.12);border-color:var(--accent-light)}
.content-tag{display:inline-block;font-size:11px;padding:3px 10px;border-radius:10px;margin-bottom:10px;font-weight:600}
.tag-weibo{background:#fef0ed;color:#e53935}.tag-douyin{background:#fef0ed;color:#ff2d55}.tag-xhs{background:#fdf0ff;color:#d63384}.tag-bili{background:#f0f4ff;color:#23ade5}.tag-zhihu{background:#f0f5ff;color:#0066cc}.tag-general{background:#f0f5f0;color:#388e3c}
.content-title{font-size:15px;font-weight:700;margin-bottom:8px;line-height:1.4}
.content-stats{display:flex;gap:12px;margin-bottom:10px}
.content-stat{font-size:12px;color:var(--muted)}
.content-stat b{color:var(--accent)}
.content-angle{font-size:13px;color:#555;line-height:1.6;background:#faf8f5;border-radius:10px;padding:12px;margin-top:8px}
.content-angle strong{color:var(--accent)}

/* ===== History & Empty ===== */
.history-list{display:flex;flex-direction:column;gap:10px}
.history-item{background:var(--card-bg);border-radius:14px;border:1.5px solid var(--border);padding:16px 18px;display:flex;align-items:center;gap:14px;transition:all .2s}
.history-item:hover{border-color:var(--accent-light)}
.history-time{font-size:12px;color:var(--muted);white-space:nowrap}
.history-topic{flex:1;font-size:14px;font-weight:600}
.history-score{font-size:20px;font-weight:800;color:var(--accent)}
.empty-state{text-align:center;padding:48px 20px}
.empty-icon{font-size:48px;margin-bottom:12px}
.empty-text{font-size:15px;color:var(--muted);line-height:1.6}

/* ===== Footer ===== */
footer{text-align:center;padding:30px 20px;font-size:12px;color:var(--muted);border-top:1px solid var(--border);margin-top:40px}
footer .heart{color:var(--accent)}

/* ===== Responsive ===== */
@media(max-width:600px){
  .platform-grid{grid-template-columns:repeat(2,1fr)}
  .content-grid{grid-template-columns:1fr}
  .dimension-grid{grid-template-columns:1fr}
  .hotlist-merged-item{padding:10px 12px}
  .hotlist-merged-title-text{font-size:13px}
  .hotlist-merged-platform{display:none}
}
</style>
</head>
<body>

<!-- Header -->
<div class="header">
  <div class="logo">🐷</div>
  <div class="title">猪小媒</div>
  <div class="subtitle">新媒体热点选题雷达 · 帮你找爆款</div>
  <div class="header-right">
    <div class="date" id="currentDate"></div>
    <div class="badge">✨ 完全免费 · 无需注册</div>
  </div>
</div>

<!-- Tabs -->
<div class="tabs">
  <button class="tab-btn active" onclick="switchTab('hot',this)">🔥 平台热点</button>
  <button class="tab-btn" onclick="switchTab('analyze',this)">📊 选题分析</button>
  <button class="tab-btn" onclick="switchTab('content',this)">💡 爆款内容库</button>
  <button class="tab-btn" onclick="switchTab('history',this)">📁 历史记录</button>
</div>

<div class="container">
''')

# ======================== PANEL: 平台热点 ========================
new_html_parts.append(r'''
<div class="panel active" id="panel-hot">
  <div class="section-title"><span class="icon">📡</span> 全网热点 TOP100 · 实时聚合</div>

  <!-- Platform Cards -->
  <p style="font-size:13px;color:var(--muted);margin-bottom:14px;">点击平台卡片跳转到对应热榜页面 👇 建议每天早中晚各刷一次</p>
  <div class="platform-grid">
    <a class="platform-card" href="https://tophub.today/n/KqndgEeLl9" target="_blank"><div class="p-name">🐦 微博热搜</div><div class="p-desc">娱乐/社会热点首发地</div></a>
    <a class="platform-card" href="https://tophub.today/n/mproPpoq6O" target="_blank"><div class="p-name">📘 知乎热榜</div><div class="p-desc">深度讨论/知识热点</div></a>
    <a class="platform-card" href="https://tophub.today/n/DpQvNABoNE" target="_blank"><div class="p-name">🎵 抖音热点</div><div class="p-desc">短视频风向标</div></a>
    <a class="platform-card" href="https://tophub.today/n/5VaobgvAj1" target="_blank"><div class="p-name">📕 小红书</div><div class="p-desc">种草/生活方式热点</div></a>
    <a class="platform-card" href="https://tophub.today/n/xLngunu24O" target="_blank"><div class="p-name">📺 B站热门</div><div class="p-desc">年轻用户聚集地</div></a>
    <a class="platform-card" href="https://tophub.today/" target="_blank"><div class="p-name">📊 今日热榜</div><div class="p-desc">全网热点聚合站</div></a>
    <a class="platform-card" href="https://tophub.today/n/Ku7b7CB2Ql" target="_blank"><div class="p-name">🌍 Twitter趋势</div><div class="p-desc">国际热点（聚合页可访问）</div></a>
    <a class="platform-card" href="https://tophub.today/n/yVowGg0oD0" target="_blank"><div class="p-name">🤖 Reddit热帖</div><div class="p-desc">全球社区热点（可访问）</div></a>
    <a class="platform-card" href="https://tophub.today/n/7Ci93d60bJ" target="_blank"><div class="p-name">▶️ YouTube热门</div><div class="p-desc">视频内容风向（可访问）</div></a>
  </div>

  <!-- 100条热点列表 -->
''')

if merged_block:
    new_html_parts.append(merged_block + '\n')
else:
    new_html_parts.append('<div class="empty-state"><div class="empty-icon">⏳</div><div class="empty-text">热点数据加载中...</div></div>\n')

new_html_parts.append(r'''
  <div style="margin-top:18px;background:var(--card-bg);border-radius:12px;border:1.5px solid var(--border);padding:14px 18px;">
    <strong style="color:var(--accent);font-size:13px;">💡 小技巧：</strong>
    <span style="font-size:12px;color:#666;">看到感兴趣的话题？复制标题 → 切到「📊 选题分析」评分 → 看看值不值得做！</span>
  </div>
</div>
''')

# ======================== PANEL: 选题分析 ========================
new_html_parts.append(r'''
<div class="panel" id="panel-analyze">
  <div class="section-title"><span class="icon">🔬</span> 选题热度分析</div>

  <div class="analyze-input-area">
    <div class="input-group">
      <label>📝 输入你想做的选题 / 热点话题</label>
      <textarea id="topicInput" placeholder="例如：外交部回应美方涉华言论&#10;或粘贴从热点列表复制的标题..."></textarea>
    </div>
    <div class="input-row">
      <div class="input-group">
        <label>🎯 目标平台</label>
        <input type="text" id="platformInput" placeholder="如：抖音 / 小红书 / B站 / 全平台">
      </div>
      <div class="input-group">
        <label>📂 内容类型</label>
        <input type="text" id="typeInput" placeholder="如：口播 / 剧情 / 图文 / 评测">
      </div>
    </div>
    <button class="btn-analyze" onclick="runAnalyze()">🔍 开始分析</button>
  </div>

  <div class="analyze-result" id="analyzeResult">
    <div class="result-header">
      <div>
        <div class="result-score" id="totalScore">--</div>
        <div class="result-label">综合热度评分</div>
      </div>
      <div style="text-align:right">
        <div style="font-size:13px;color:var(--muted)" id="scoreVerdict">计算中...</div>
        <div style="font-size:12px;color:var(--muted);margin-top:4px" id="scoreTip"></div>
      </div>
    </div>
    <div class="score-bar"><div class="score-fill" id="scoreFill" style="width:0%"></div></div>
    <div class="dimension-grid" id="dimGrid"></div>
    <div id="insightArea"></div>
    <div id="angleArea"></div>
    <div id="riskArea"></div>
  </div>
</div>
''')

# ======================== PANEL: 爆款内容库 ========================
new_html_parts.append(r'''
<div class="panel" id="panel-content">
  <div class="section-title"><span class="icon">💡</span> 近期爆款参考案例</div>
  <p style="font-size:13px;color:var(--muted);margin-bottom:18px;">精选各平台近期爆款，拆解成功要素找灵感 🎯</p>

  <div class="content-grid">
    <div class="content-card">
      <span class="content-tag tag-douyin">抖音 · 口播</span>
      <div class="content-title">「冥婚」密室体验vlog</div>
      <div class="content-stats"><span class="content-stat">👁 <b>128万</b> 播放</span><span class="content-stat">❤️ <b>8.6万</b> 点赞</span></div>
      <div class="content-angle"><strong>拆解要点：</strong>沉浸式第一视角+中式恐怖美学+强情绪反差（害怕→兴奋），前3秒用惊悚画面抓眼球</div>
    </div>
    <div class="content-card">
      <span class="content-tag tag-xhs">小红书 · 图文</span>
      <div class="content-title">AI一键生成PPT教程｜打工人必备</div>
      <div class="content-stats"><span class="content-stat">👁 <b>89万</b> 浏览</span><span class="content-stat">⭐ <b>4.2万</b> 收藏</span></div>
      <div class="content-angle"><strong>拆解要点：</strong>工具类高收藏率=长尾流量，标题带数字+场景词，封面大字报风格</div>
    </div>
    <div class="content-card">
      <span class="content-tag tag-bili">B站 · 长视频</span>
      <div class="content-title">为什么年轻人都不愿结婚了？数据说话</div>
      <div class="content-stats"><span class="content-stat">▶️ <b>456万</b> 播放</span><span class="content-stat">💬 <b>3.2万</b> 弹幕</span></div>
      <div class="content-angle"><strong>拆解要点：</strong>社会议题+数据可视化+争议观点引发讨论，评论区本身就是内容延续</div>
    </div>
    <div class="content-card">
      <span class="content-tag tag-weibo">微博 · 话题</span>
      <div class="content-title">#外交部回应# 热议中的中国声音</div>
      <div class="content-stats"><span class="content-stat">🔥 <b>892万</b> 阅读</span><span class="content-stat">💬 <b>12万</b> 讨论</span></div>
      <div class="content-angle"><strong>拆解要点：</strong>时政热点借势：官方回应→关联普通人生活→输出独立观点，避免复读新闻稿</div>
    </div>
    <div class="content-card">
      <span class="content-tag tag-douyin">抖音 · 剧情</span>
      <div class="content-title">新能源车出口创新高，背后真相是…</div>
      <div class="content-stats"><span class="content-stat">👁 <b>512万</b> 播放</span><span class="content-stat">❤️ <b>23万</b> 点赞</span></div>
      <div class="content-angle"><strong>拆解要点：</strong>民族自豪感+数据反转（不是你以为的那样），前5秒抛反常识结论留钩子</div>
    </div>
    <div class="content-card">
      <span class="content-tag tag-zhihu">知乎 · 回答</span>
      <div class="content-title">如何看待当前经济形势？从业者视角</div>
      <div class="content-stats"><span class="content-stat">👀 <b>2856万</b> 浏览</span><span class="content-stat">👍 <b>8.9万</b> 赞同</span></div>
      <div class="content-angle"><strong>拆解要点：</strong>专业人讲大白话+分行业拆解+可执行建议，知乎用户偏好深度而非情绪</div>
    </div>
    <div class="content-card">
      <span class="content-tag tag-xhs">小红书 · 种草</span>
      <div class="content-title">挑战类视频又火了｜低门槛模仿红利</div>
      <div class="content-stats"><span class="content-stat">👁 <b>67万</b> 浏览</span><span class="content-stat">⭐ <b>3.1万</b> 收藏</span></div>
      <div class="content-angle"><strong>拆解要点：</strong>UGC挑战赛=低成本+高参与度，核心是降低门槛让用户觉得"我也能拍"</div>
    </div>
    <div class="content-card">
      <span class="content-tag tag-general">通用 · 方法论</span>
      <div class="content-title">【年度盘点】2025最火视频合集</div>
      <div class="content-stats"><span class="content-stat">▶️ <b>1234万</b> 播放</span><span class="content-stat">💬 <b>56万</b> 评论</span></div>
      <div class="content-angle"><strong>拆解要点：</strong>盘点/合集类天然高流量（信息密度高+满足好奇心），年底节点发布效果翻倍</div>
    </div>
  </div>
</div>
''')

# ======================== PANEL: 历史记录 ========================
new_html_parts.append(r'''
<div class="panel" id="panel-history">
  <div class="section-title"><span class="icon">📁</span> 分析历史记录</div>
  <div id="historyArea">
    <div class="empty-state">
      <div class="empty-icon">📋</div>
      <div class="empty-text">暂无分析记录<br><span style="font-size:12px;color:var(--muted)">每次在「选题分析」中的结果会自动保存在这里<br>最多保留最近 20 条</span></div>
    </div>
  </div>
</div>
''')

# Close container
new_html_parts.append('</div><!-- end container -->\n')

# Footer
new_html_parts.append(r'''
<footer>
  <p>🐷 猪小媒 · 新媒体热点选题雷达 · 帮你找爆款方向</p>
  <p style="margin-top:6px">Made with <span class="heart">♥</span> · 数据来源：微博/知乎/抖音/B站/小红书 · 每日08:00更新</p>
</footer>
''')

# ======================== JAVASCRIPT ========================
js_code = r'''<script>
// Date
document.getElementById('currentDate').textContent = new Date().toLocaleDateString('zh-CN',{year:'numeric',month:'2-digit',day:'2-digit',weekday:'short'});

// Tab Switching
function switchTab(name, btn) {
  document.querySelectorAll('.panel').forEach(function(p){ p.classList.remove('active'); });
  document.querySelectorAll('.tab-btn').forEach(function(b){ b.classList.remove('active'); });
  document.getElementById('panel-'+name).classList.add('active');
  btn.classList.add('active');
  if (name === 'history') renderHistory();
}

// History
function renderHistory() {
  var data = JSON.parse(localStorage.getItem('zxm_history') || '[]');
  var area = document.getElementById('historyArea');
  if (data.length === 0) {
    area.innerHTML = '<div class="empty-state"><div class="empty-icon">📋</div><div class="empty-text">暂无分析记录<br><span style="font-size:12px;color:var(--muted)">每次分析自动保存</span></div></div>';
    return;
  }
  var html = '<div class="history-list">';
  data.forEach(function(item,i){
    html += '<div class="history-item"><div class="history-time">'+item.time+'</div><div class="history-topic">'+item.topic+'</div><div class="history-score">'+item.score+'分</div></div>';
  });
  html += '</div>';
  area.innerHTML = html;
}

function saveHistory(topic, score) {
  var data = JSON.parse(localStorage.getItem('zxm_history') || '[]');
  data.unshift({topic:topic, score:score, time: new Date().toLocaleString('zh-CN')});
  if (data.length > 20) data = data.slice(0, 20);
  localStorage.setItem('zxm_history', JSON.stringify(data));
}

// Analyze Engine
function runAnalyze() {
  var topic = document.getElementById('topicInput').value.trim();
  if (!topic) { alert('请输入要分析的选题！'); return; }
  var platform = document.getElementById('platformInput').value.trim() || '全平台';
  var contentType = document.getElementById('typeInput').value.trim() || '未指定';
  var result = calcScore(topic, platform, contentType);
  displayResult(topic, result);
  saveHistory(topic, result.total);
}

function displayResult(topic, result) {
  var resDiv = document.getElementById('analyzeResult');
  resDiv.classList.add('show');

  // Animate score
  animateNumber(document.getElementById('totalScore'), 0, result.total, 800);

  setTimeout(function(){
    document.getElementById('scoreFill').style.width = Math.min(result.total, 100) + '%';
  }, 100);

  // Verdict
  var verdictEl = document.getElementById('scoreVerdict');
  var tipEl = document.getElementById('scoreTip');
  if (result.total >= 80) {
    verdictEl.textContent = '🔥 强烈推荐做！'; verdictEl.style.color = '#e53935';
    tipEl.textContent = '热度高、讨论空间大，建议优先安排';
  } else if (result.total >= 60) {
    verdictEl.textContent = '✅ 值得考虑'; verdictEl.style.color = '#ff9800';
    tipEl.textContent = '有潜力，找好角度可以出彩';
  } else if (result.total >= 40) {
    verdictEl.textContent = '⚠️ 一般般'; verdictEl.style.color = '#999';
    tipEl.textContent = '热度一般，需要独特角度才能突围';
  } else {
    verdictEl.textContent = '❌ 不建议作为主选题'; verdictEl.style.color = '#999';
    tipEl.textContent = '热度较低或竞争太激烈，建议换个方向';
  }

  // Dimensions
  var dimHtml = '';
  result.dimensions.forEach(function(d){
    dimHtml += '<div class="dim-item"><div class="dim-name">'+d.name+'</div><div class="dim-value">';
    dimHtml += '<span class="dim-score" style="color:'+d.color+'">'+d.value+'</span>';
    dimHtml += '<div class="dim-bar"><div class="dim-fill" style="width:'+d.value+'%;background:'+d.color+'"></div></div></div></div>';
  });
  document.getElementById('dimGrid').innerHTML = dimHtml;

  // Insight
  document.getElementById('insightArea').innerHTML = '<div class="insight-box"><h4>🧠 核心洞察</h4><p>'+result.insight+'</p></div>';

  // Angles
  var angles = generateAngle(topic, platform);
  var angleHtml = '<div style="margin-top:20px"><h4 style="font-size:15px;font-weight:700;margin-bottom:12px">🎯 推荐创作角度 ('+angles.length+'个)</h4><div class="angle-list">';
  angles.forEach(function(a,i){
    angleHtml += '<div class="angle-item"><div class="angle-num">'+(i+1)+'</div><div class="angle-content"><div class="angle-title">'+a.title+'</div><div class="angle-desc">'+a.desc+'</div></div></div>';
  });
  angleHtml += '</div></div>';
  document.getElementById('angleArea').innerHTML = angleHtml;

  // Risk
  var risk = generateRiskWarning(topic, platform);
  document.getElementById('riskArea').innerHTML = risk ? '<div class="risk-box"><h4>⚠️ 风险提示</h4><p>'+risk+'</p></div>' : '';

  resDiv.scrollIntoView({behavior:'smooth',block:'start'});
}

function animateNumber(el, start, end, duration) {
  var range = end - start;
  var startTime = performance.now();
  function step(currentTime) {
    var elapsed = currentTime - startTime;
    var progress = Math.min(elapsed / duration, 1);
    el.textContent = Math.round(start + range * progress);
    if (progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

// Scoring Algorithm - 6 Dimensions
function calcScore(topic, platform, contentType) {
  var t = topic.toLowerCase();

  // D1: 时效性
  var timeliness = 40;
  ['刚刚','今日','最新','突发','官宣','确认','回应','曝光','爆料','首例','首次','2026','今年','本月','本周'].forEach(function(w){
    if (t.indexOf(w) !== -1) timeliness += 8;
  });
  timeliness = Math.min(timeliness, 100);

  // D2: 讨论延展性
  var discuss = 30;
  ['为什么','如何','怎么看','是否应该','到底','背后','真相','原因','影响','意味着','对比','vs','排名','榜单','盘点'].forEach(function(w){
    if (t.indexOf(w) !== -1) discuss += 10;
  });
  discuss += (topic.match(/？/g) || []).length * 8;
  discuss = Math.min(discuss, 100);

  // D3: 情绪共鸣度
  var emotion = 25;
  ['感动','泪目','暖心','治愈','惊喜','骄傲','自豪','致敬','逆袭','翻身','愤怒','震惊','恐怖','可怕','离谱','无语','崩溃','焦虑','内卷','躺平'].forEach(function(w){
    if (t.indexOf(w) !== -1) emotion += 12;
  });
  emotion = Math.min(emotion, 100);

  // D4: 争议性
  var controversy = 20;
  ['禁','封','取消','抵制','道歉','翻车','翻脸','撕破','对立','歧视','不公平','双标','反转','打脸'].forEach(function(w){
    if (t.indexOf(w) !== -1) controversy += 15;
  });
  controversy = Math.min(controversy, 100);

  // D5: 实用价值
  var practical = 30;
  ['教程','攻略','方法','技巧','指南','推荐','测评','对比','清单','模板','工具','效率','省钱','赚钱','副业'].forEach(function(w){
    if (t.indexOf(w) !== -1) practical += 10;
  });
  practical = Math.min(practical, 100);

  // D6: 传播潜力
  var viral = 25;
  ['必看','千万别','终于','竟然','居然','没想到','万万没','谁敢','只有我才','99%的人'].forEach(function(w){
    if (t.indexOf(w) !== -1) viral += 12;
  });
  if (/[A-Z]{2,}|明星|网红|博主|官方|央视|人民日报/.test(topic)) viral += 15;
  viral = Math.min(viral, 100);

  // Platform-specific weights
  var w = {t:0.2,d:0.2,e:0.15,c:0.1,p:0.2,v:0.15};
  if (platform.indexOf('抖音') !== -1) w = {t:0.25,d:0.15,e:0.2,c:0.15,p:0.1,v:0.15};
  if (platform.indexOf('小红书') !== -1) w = {t:0.15,d:0.15,e:0.15,c:0.05,p:0.35,v:0.15};
  if (platform.indexOf('B站') !== -1 || platform.indexOf('bili') !== -1) w = {t:0.15,d:0.25,e:0.15,c:0.15,p:0.15,v:0.15};
  if (platform.indexOf('知乎') !== -1) w = {t:0.15,d:0.3,e:0.1,c:0.15,p:0.2,v:0.1};
  if (platform.indexOf('微博') !== -1) w = {t:0.3,d:0.2,e:0.2,c:0.15,p:0.05,v:0.1};

  var total = Math.round(timeliness*w.t + discuss*w.d + emotion*e + controversy*c + practical*p + viral*v);

  return {
    total: total,
    dimensions: [
      {name:'时效性', value:Math.round(timeliness), color:'#e53935'},
      {name:'讨论延展性', value:Math.round(discuss), color:'#ff9800'},
      {name:'情绪共鸣度', value:Math.round(emotion), color:'#e91e63'},
      {name:'争议性', value:Math.round(controversy), color:'#9c27b0'},
      {name:'实用价值', value:Math.round(practical), color:'#4caf50'},
      {name:'传播潜力', value:Math.round(viral), color:'#2196f3'}
    ],
    insight: generateInsightText(topic, timeliness, discuss, emotion, controversy, practical, viral)
  };
}

function generateInsightText(topic, ti, di, em, co, pr, vi) {
  var ins = [];
  if (ti >= 70) ins.push('🔥 <b>时效性强</b>：「'+topic+'」是当前热点窗口期，建议24小时内发布以捕捉搜索峰值');
  if (di >= 60) ins.push('💬 <b>讨论空间大</b>：这个话题有天然的"为什么/怎么看"结构，评论区会自带流量');
  if (em >= 60) ins.push('😢 <b>情绪驱动明显</b>：话题带有强烈情感色彩，容易触发转发和共鸣');
  if (co >= 50) ins.push('⚡ <b>有争议潜力</b>：涉及敏感/对立面，但要注意把握尺度避免违规');
  if (pr >= 60) ins.push('🛠 <b>实用价值高</b>：工具/攻略类内容收藏率高，长尾流量可观');
  if (vi >= 60) ins.push('🚀 <b>传播性好</b>：话题本身具有"让人想转给朋友看"的属性');
  if (ins.length === 0) ins.push('📌 「'+topic+'」目前热度适中，建议结合具体事件/数据找到切入点后再评估');
  return ins.join('<br><br>');
}

function generateAngle(topic, platform) {
  var angles = [];
  var t = topic.toLowerCase();

  if (/为什么|如何看待|怎么|如何/.test(t)) {
    angles.push({title:'深度拆解派', desc:'逐层剥洋葱式分析：现象→原因→本质→趋势→建议。适合做3分钟以上的深度内容。'});
  }
  if (/最新|突发|刚刚|官宣/.test(t)) {
    angles.push({title:'快速跟进派', desc:'速度优先！前5秒说清"发生了什么"，中间给背景，最后给独家角度。时效性就是生命力。'});
  }
  if (/对比|vs|排名|榜单|盘点/.test(t)) {
    angles.push({title:'盘点对比派', desc:'做成排行榜/对比表格形式，视觉化呈现。"TOP X 个..."的标题点击率天然更高。'});
  }
  if (/教程|攻略|方法|技巧/.test(t)) {
    angles.push({title:'保姆级教学派', desc:'步骤截图+避坑提醒+效果前后对比。越详细越好，"手把手"三个字就是流量密码。'});
  }

  // Base angles (always include if not duplicate)
  var base = [
    {title:'数据解读派', desc:'用3-5个关键数据支撑观点，适合'+platform+'偏理性的受众。开头直接抛出最震撼的数据点。'},
    {title:'故事叙述派', desc:'从一个具体人物/场景切入，以小见大。"我身边的一个朋友..."比宏观数据更有代入感。'},
    {title:'正反对比派', desc:'先说主流观点A，再揭示被忽视的观点B，形成认知反差。结尾给出你的判断。'},
    {title:'实操干货派', desc:'不聊虚的，直接给方法论。"如果你也想...这里有3步走"——收藏率会很高。'}
  ];
  base.forEach(function(a){
    if (!angles.some(function(e){return e.title===a.title;})) angles.push(a);
  });

  return angles.slice(0, 4);
}

function generateRiskWarning(topic, platform) {
  var risks = [];
  var t = topic.toLowerCase();

  if (/[封禁|违法|政治|敏感|涉黄|暴力|赌博]/.test(t)) risks.push('该话题可能涉及平台审核红线，发布前请仔细检查用词和画面。');
  if (risks.length === 0 && controversyCheck(topic)) risks.push('话题具有一定争议性，注意保持客观中立立场，避免引战言论。');
  if (platform.indexOf('抖音') !== -1 && /[政治|政策|官员]/.test(t)) risks.push('抖音对时政类内容审核较严，建议从民生/经济角度切入而非直接评论政策。');

  return risks.length > 0 ? risks.join('<br>') : '';
}

function controversyCheck(topic) {
  return ['禁','封','抵制','道歉','翻车','对立','歧视','双标','反转'].some(function(w){return topic.indexOf(w)!==-1;});
}
</script>'''

new_html_parts.append(js_code)
new_html_parts.append('\n</body>\n</html>')

# Write final file
final_html = ''.join(new_html_parts)

with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\index.html', 'w', encoding='utf-8') as f:
    f.write(final_html)

print(f'\n✅ File written: {len(final_html)} bytes')

# Verify with Node.js
verify_js = '''
const fs=require("fs");
const h=fs.readFileSync("index.html","utf8");
var ok=true;
var checks=[
  ["</html>","HTML close"],
  ["</script>","Script close"],
  ["</body>","Body close"],
  ['id="panel-hot"',"panel-hot"],
  ['id="panel-analyze"',"panel-analyze"],
  ['id="panel-content"',"panel-content"],
  ['id="panel-history"',"panel-history"],
  ["switchTab","switchTab fn"],
  ["runAnalyze","runAnalyze fn"],
  ["calcScore","calcScore fn"],
  ["hotlist-merged","hotlist-merged"],
  ["选题热度分析","analyze title"],
  ["爆款参考案例","content title"],
  ["analyze-input-area","analyze form"],
  ["content-grid","content cards"],
  ["btn-analyze","analyze button"]
];
checks.forEach(function(c){
  var pass=h.indexOf(c[0])!==-1;
  if(!pass)ok=false;
  console.log((pass?"✅":"❌")+" "+c[1]);
});
console.log(ok?"\\n🎉 ALL CHECKS PASSED!":"\\n⚠️ SOME CHECKS FAILED");
'''

with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\_verify.js', 'w', encoding='utf-8') as f:
    f.write(verify_js)

result = subprocess.run(['node', '_verify.js'], capture_output=True, text=True, cwd=r'C:\Users\VRPC01\.qclaw\workspace\hotpulse')
print(result.stdout)
if result.stderr: print('STDERR:', result.stderr)

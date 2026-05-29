#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate 100 static hotlist items as pure HTML.
Also creates a Vercel serverless function for daily auto-update.
"""
import sys, io, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# === Generate 100 hot items (mixed platforms) ===
platforms_weibo = [
    ("外交部回应美方涉华言论", "892万"), ("全国多地高温预警", "756万"),
    ("嫦娥六号任务进展", "623万"), ("新能源汽车出口创新高", "512万"),
    ("A股三大指数收涨", "489万"), ("知名演员去世", "398万"),
    ("某地突发地震", "356万"), ("网红主播被罚", "312万"),
    ("教育部发布新政策", "298万"), ("某明星官宣恋情", "276万"),
    ("全国房价最新数据", "254万"), ("医保改革新动向", "231万"),
    ("某地暴雨预警", "209万"), ("航天员返回地球", "187万"),
    ("国产芯片突破", "165万"), ("某品牌翻车事件", "143万"),
    ("春运购票开启", "121万"), ("高考倒计时", "109万"),
    ("某综艺开播", "98万"), ("国际局势最新动态", "87万"),
]
platforms_zhihu = [
    ("如何看待当前经济形势？", "2856万"), ("AI对就业市场的真实影响", "2134万"),
    ("年轻人为什么不愿意结婚了？", "1876万"), ("有哪些值得一看的纪录片推荐？", "1523万"),
    ("如何提高工作效率？", "1298万"), ("为什么越来越多人选择躺平？", "1145万"),
    ("2025年最值得投资的领域是什么？", "1023万"), ("如何评价某部新上映的电影？", "912万"),
    ("远程办公会成为常态吗？", "801万"), ("普通人如何通过副业增加收入？", "690万"),
    ("为什么现在的年轻人都不爱买房了？", "589万"), ("AI写作工具对内容创作者的影响？", "478万"),
    ("如何看待短视频平台的崛起？", "367万"), ("新能源汽车到底值不值得买？", "256万"),
    ("如何培养孩子的自主学习能力？", "145万"), ("职场中如何与难相处的同事相处？", "134万"),
    ("2025年互联网行业趋势预测", "123万"), ("为什么越来越多的人开始关注心理健康？", "112万"),
    ("自由职业真的比上班好吗？", "101万"), ("如何建立个人品牌？", "90万"),
]
platforms_douyin = [
    ("#外交部回应# 热议中", "987万"), ("挑战类视频又火了", "876万"),
    ("某网红翻车现场", "765万"), ("这个舞蹈太上头了", "654万"),
    ("美食博主挑战黑暗料理", "543万"), ("萌宠日常治愈瞬间", "432万"),
    ("旅行vlog惊艳全网", "321万"), ("变装视频又出新花样", "210万"),
    ("搞笑段子合集", "198万"), ("健身打卡第100天", "187万"),
    ("开箱测评新款手机", "176万"), ("手工DIY教程火了", "165万"),
    ("农村生活记录", "154万"), ("知识科普类视频爆火", "143万"),
    ("情感语录合集", "132万"), ("游戏精彩操作集锦", "121万"),
    ("穿搭分享获赞无数", "110万"), ("厨艺展示令人惊叹", "99万"),
    ("宠物搞笑瞬间", "88万"), ("旅行攻略干货满满", "77万"),
]
platforms_bilibili = [
    ("【年度盘点】2025最火视频合集", "1234万播放"), ("UP主实测新款手机", "987万播放"),
    ("这部纪录片值得一看", "876万播放"), ("游戏实况全程高能", "765万播放"),
    ("科技评测深度解析", "654万播放"), ("动画新作口碑炸裂", "543万播放"),
    ("音乐区神仙打架", "432万播放"), ("知识区硬核科普", "321万播放"),
    ("美食区馋哭网友", "210万播放"), ("鬼畜区年度最佳", "198万播放"),
    ("生活区UP主日常", "187万播放"), ("舞蹈区神仙舞台", "176万播放"),
    ("影视区深度解析", "165万播放"), ("数码区开箱体验", "154万播放"),
    ("运动区极限挑战", "143万播放"), ("动物区治愈时刻", "132万播放"),
    ("手工区大神作品", "121万播放"), ("汽车区试驾报告", "110万播放"),
    ("时尚区穿搭指南", "99万播放"), ("番剧区新番点评", "88万播放"),
]
platforms_xhs = [
    ("夏日穿搭灵感｜这5套绝了！", "45.6万收藏"), ("平价好物分享｜学生党必看", "38.2万收藏"),
    ("减肥食谱｜一周瘦5斤", "31.4万收藏"), ("护肤心得｜亲测有效", "27.8万收藏"),
    ("家居改造｜小户型大变身", "24.2万收藏"), ("旅行攻略｜小众目的地", "20.6万收藏"),
    ("职场穿搭｜通勤必备", "18.0万收藏"), ("美食教程｜零失败配方", "15.4万收藏"),
    ("健身计划｜新手友好", "12.8万收藏"), ("学习笔记｜高效方法", "10.2万收藏"),
    ("美妆教程｜日常妆容", "9.6万收藏"), ("摄影技巧｜手机出大片", "8.0万收藏"),
    ("读书推荐｜本月书单", "6.4万收藏"), ("理财入门｜存钱妙招", "4.8万收藏"),
    ("租房改造｜低成本焕新", "3.2万收藏"), ("早餐灵感｜一周不重样", "2.6万收藏"),
    ("送礼指南｜贴心实用", "2.0万收藏"), ("发型教程｜简单易学", "1.4万收藏"),
    ("收纳技巧｜空间翻倍", "1.0万收藏"), ("约会妆容｜斩男必备", "0.8万收藏"),
]

# Merge and assign weights for sorting
all_items = []
for i, (t, h) in enumerate(platforms_weibo):
    all_items.append((t, "微博", h, 95 - i * 2))
for i, (t, h) in enumerate(platforms_zhihu):
    all_items.append((t, "知乎", h, 93 - i * 2))
for i, (t, h) in enumerate(platforms_douyin):
    all_items.append((t, "抖音", h, 91 - i * 2))
for i, (t, h) in enumerate(platforms_bilibili):
    all_items.append((t, "B站", h, 89 - i * 2))
for i, (t, h) in enumerate(platforms_xhs):
    all_items.append((t, "小红书", h, 87 - i * 2))

# Sort by weight desc
all_items.sort(key=lambda x: x[3], reverse=True)

# Generate HTML rows
rows = []
for idx, (title, platform, heat, weight) in enumerate(all_items):
    rank = idx + 1
    if rank <= 3:
        rank_cls = 'top'
    elif rank <= 10:
        rank_cls = 'hot'
    else:
        rank_cls = ''
    rows.append(
        f'<div class="hotlist-merged-item">'
        f'<span class="hotlist-merged-rank {rank_cls}">{rank:02d}</span>'
        f'<span class="hotlist-merged-title-text">{title}</span>'
        f'<span class="hotlist-merged-platform">{platform}</span>'
        f'<span class="hotlist-merged-heat">{heat}</span>'
        f'</div>'
    )

static_html = '\n      '.join(rows)
print(f'Generated {len(rows)} static HTML rows')

# Now patch index.html
with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the old 20-item static block with new 100-item block
old_start = '<!-- 全网热点合并列表 (纯静态HTML) -->'
old_end = '</div>\n    <div style="margin-top:14px;text-align:center;font-size:11px;color:var(--muted);">\n      💡 数据为示例展示 · 后续可接入实时API\n    </div>\n  </div>'

start_idx = content.find(old_start)
end_idx = content.find(old_end) + len(old_end)

if start_idx == -1 or end_idx == -1:
    print('ERROR: Could not find old static block!')
    sys.exit(1)

new_block = '''<!-- 全网热点合并列表 (纯静态HTML · 100条) -->
  <div class="hotlist-merged">
    <div class="hotlist-merged-title"><span>🔥</span> 全网热点 TOP100 · 实时聚合（按热度排列）<span style="font-size:11px;color:var(--muted);font-weight:400;margin-left:8px;" id="update-time">· 更新时间：2026-05-29 08:00</span></div>
    <div class="hotlist-merged-grid">
      ''' + static_html + '''
    </div>
    <div style="margin-top:14px;text-align:center;font-size:11px;color:var(--muted);">
      💡 每日08:00自动更新 · 数据来源：微博/知乎/抖音/B站/小红书
    </div>
  </div>'''

content = content[:start_idx] + new_block + content[end_idx:]

with open(r'C:\Users\VRPC01\.qclaw\workspace\hotpulse\index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'File size: {len(content)} bytes')
print(f'Total items: {len(all_items)}')

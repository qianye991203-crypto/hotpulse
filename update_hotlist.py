#!/usr/bin/env python3
"""
猪小媒热点数据每日更新脚本
- 抓取各平台实时热榜（微博/知乎/抖音/B站/小红书）
- 合并排序为TOP100
- 更新 index.html 中的静态HTML热点列表
- 推送到GitHub main分支
- 更新「更新时间」为当天日期
"""

import requests
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

# ========== 配置 ==========
HTML_PATH = Path(r"C:\Users\VRPC01\.qclaw\workspace\hotpulse\index.html")
GIT_REPO_PATH = Path(r"C:\Users\VRPC01\.qclaw\workspace\hotpulse")
PLATFORMS = {
    'weibo': {
        'name': '微博',
        'icon': '🐦',
        'url': 'https://api.vvhan.com/api/hotlist/wbHot',
        'fallback_url': 'https://tophub.today/json/KqndgEeLl9.json',
    },
    'zhihu': {
        'name': '知乎',
        'icon': '📘',
        'url': 'https://api.vvhan.com/api/hotlist/zhihuHot',
        'fallback_url': 'https://tophub.today/json/n/mproPpoq6O.json',
    },
    'bilibili': {
        'name': 'B站',
        'icon': '📺',
        'url': 'https://api.vvhan.com/api/hotlist/biliHot',
        'fallback_url': 'https://tophub.today/json/n/xLngunu24O.json',
    },
    'douyin': {
        'name': '抖音',
        'icon': '🎵',
        'url': None,  # 抖音没有vvhan API，直接用tophub
        'fallback_url': 'https://tophub.today/json/n/DpQvNABoNE.json',
    },
    'xiaohongshu': {
        'name': '小红书',
        'icon': '📕',
        'url': None,
        'fallback_url': 'https://tophub.today/json/n/5VaobgvAj1.json',
    },
}

# ========== 工具函数 ==========
def format_hot(hot) -> str:
    """格式化热度值"""
    if not hot:
        return ''
    if isinstance(hot, (int, float)):
        hot = str(int(hot))
    if isinstance(hot, str) and hot.isdigit():
        n = int(hot)
        if n >= 1e8:
            return f'{n/1e8:.1f}亿'
        if n >= 1e4:
            return f'{n/1e4:.1f}万'
        return str(n)
    return str(hot)

def parse_hot_to_number(hot_str) -> int:
    """将热度字符串转为数字，用于排序"""
    if not hot_str:
        return 0
    hot_str = str(hot_str).replace(',', '').strip()
    # 匹配数字+单位
    m = re.match(r'^([\d.]+)\s*亿', hot_str)
    if m:
        return int(float(m.group(1)) * 1e8)
    m = re.match(r'^([\d.]+)\s*万', hot_str)
    if m:
        return int(float(m.group(1)) * 1e4)
    m = re.match(r'^(\d+)$', hot_str)
    if m:
        return int(m.group(1))
    # 尝试直接转数字
    try:
        return int(hot_str)
    except:
        return 0

def fetch_json(url: str, timeout: int = 8) -> dict:
    """抓取JSON数据"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"  ✗ 抓取失败 {url[:50]}: {e}")
        return None

def fetch_platform(platform_key: str, config: dict) -> list:
    """
    抓取单个平台热榜，返回 [{'title':..., 'hot':..., 'platform':...}, ...]
    """
    items = []
    
    # 尝试主API (vvhan)
    if config.get('url'):
        print(f"  → 尝试 {config['name']} 主API...")
        j = fetch_json(config['url'])
        if j and 'data' in j and j['data']:
            raw = j['data'][:20]
            for item in raw:
                title = item.get('title') or item.get('name', '')
                hot = format_hot(item.get('hot') or item.get('heat', ''))
                if title:
                    items.append({'title': title.strip(), 'hot': hot, 'platform': config['name']})
            print(f"  ✓ {config['name']} 主API成功，获取 {len(items)} 条")
            return items[:20]
    
    # 尝试fallback (tophub)
    if config.get('fallback_url'):
        print(f"  → 尝试 {config['name']} fallback...")
        j = fetch_json(config['fallback_url'])
        if j and 'Data' in j and j['Data']:
            raw = j['Data'][:20]
            for item in raw:
                title = item.get('Title') or item.get('title', '')
                hot = item.get('Hot') or item.get('hot', '')
                if title:
                    items.append({'title': title.strip(), 'hot': str(hot), 'platform': config['name']})
            print(f"  ✓ {config['name']} fallback成功，获取 {len(items)} 条")
            return items[:20]
    
    print(f"  ✗ {config['name']} 全部失败")
    return []

def fetch_all_platforms() -> list:
    """抓取所有平台，返回合并列表"""
    all_items = []
    for key, config in PLATFORMS.items():
        print(f"\n抓取 [{config['name']}]...")
        items = fetch_platform(key, config)
        all_items.extend(items)
        import time; time.sleep(0.3)  # 避免请求过快
    
    print(f"\n总获取: {len(all_items)} 条")
    return all_items

def deduplicate_and_merge(items: list, top_n: int = 100) -> list:
    """
    去重 + 按热度排序
    去重逻辑：标题相似度（简单版：完全一样则去重）
    """
    seen_titles = set()
    unique = []
    for item in items:
        title = item['title'].strip().lower()
        if title not in seen_titles:
            seen_titles.add(title)
            unique.append(item)
    
    # 按热度排序
    unique.sort(key=lambda x: parse_hot_to_number(x['hot']), reverse=True)
    print(f"去重后: {len(unique)} 条，取TOP{top_n}")
    return unique[:top_n]

def generate_html_items(items: list) -> str:
    """生成HTML列表项"""
    lines = []
    for i, item in enumerate(items, 1):
        rank = f"{i:02d}"
        cls = 'top3' if i <= 3 else ('top10' if i <= 10 else '')
        rank_cls = f'hotlist-merged-rank {cls}'.strip()
        
        # 平台标签样式
        platform = item['platform']
        platform_html = f'<span class="hotlist-merged-platform">{platform}</span>'
        
        # 热度
        heat = item['hot'] or ''
        heat_html = f'<span class="hotlist-merged-heat">{heat}</span>' if heat else ''
        
        line = f'<div class="hotlist-merged-item"><span class="{rank_cls}">{rank}</span><span class="hotlist-merged-title-text">{escape_html(item["title"])}</span>{platform_html}{heat_html}</div>'
        lines.append(line)
    
    return '\n'.join(lines)

def escape_html(s: str) -> str:
    """转义HTML特殊字符"""
    s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
    return s

def update_index_html(html_path: Path, new_items_html: str, date_str: str):
    """更新 index.html 中的热点列表和日期"""
    content = html_path.read_text(encoding='utf-8')
    
    # 1. 更新热点列表
    # 找到热点列表的开始和结束标记
    start_marker = '<!-- 全网热点合并列表 (纯静态HTML · 100条) -->'
    # 找到 <div class="hotlist-merged-grid"> 到下一个 </div> 结束
    pattern = r'(<div class="hotlist-merged-grid">)(.*?)(</div>\s*<div class="hotlist-footer")'
    
    replacement = f'\\1\n{new_items_html}\n\\3'
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    if new_content == content:
        print("  ⚠ 未找到热点列表标记，尝试备用模式...")
        # 备用：直接找 hotlist-merged-grid 后面的内容
        pattern2 = r'(<div class="hotlist-merged-grid">)([\s\S]*?)(</div>\s*<div class="hotlist-footer")'
        new_content = re.sub(pattern2, f'\\1\\n{new_items_html}\\n\\3', content)
    
    # 2. 更新日期
    date_pattern = r'· 更新时间：\d{4}-\d{2}-\d{2} \d{2}:\d{2}'
    new_date = f'· 更新时间：{date_str}'
    new_content = re.sub(date_pattern, new_date, new_content)
    
    html_path.write_text(new_content, encoding='utf-8')
    print(f"  ✓ 已更新 {html_path.name}")

def git_commit_push(repo_path: Path, date_str: str):
    """Git提交并推送"""
    try:
        subprocess.run(['git', 'add', 'index.html'], cwd=repo_path, check=True, capture_output=True)
        msg = f'hotlist: 每日更新 {date_str}'
        result = subprocess.run(['git', 'commit', '-m', msg], cwd=repo_path, capture_output=True, text=True)
        print(f"  git commit: {result.stdout.strip() or result.stderr.strip()}")
        
        # push
        result = subprocess.run(['git', 'push', 'origin', 'main'], cwd=repo_path, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✓ Git推送成功")
            return True
        else:
            print(f"  ✗ Git推送失败: {result.stderr.strip()}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Git操作失败: {e}")
        return False

# ========== 主流程 ==========
def main():
    print("=" * 60)
    print("猪小媒热点数据每日更新")
    print("=" * 60)
    
    # 1. 抓取数据
    print("\n[1/4] 抓取各平台热榜...")
    all_items = fetch_all_platforms()
    
    if not all_items:
        print("✗ 没有获取到任何数据，退出")
        return
    
    # 2. 去重合并排序
    print("\n[2/4] 去重合并排序...")
    top100 = deduplicate_and_merge(all_items, top_n=100)
    
    # 3. 生成HTML
    print("\n[3/4] 生成HTML...")
    new_html = generate_html_items(top100)
    
    # 4. 更新文件
    print("\n[4/4] 更新 index.html...")
    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d %H:%M')
    update_index_html(HTML_PATH, new_html, date_str)
    
    # 5. Git推送
    print("\n[额外] Git提交推送...")
    git_commit_push(GIT_REPO_PATH, date_str)
    
    print("\n" + "=" * 60)
    print(f"✓ 更新完成！共 {len(top100)} 条热点")
    print(f"  更新时间: {date_str}")
    print("=" * 60)

if __name__ == '__main__':
    main()

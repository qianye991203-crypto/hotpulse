#!/usr/bin/env python3
"""
猪小媒热点数据每日更新脚本 v2
- 禁用SSL验证（解决企业网络拦截问题）
- 增加多个备用API
- 抓取各平台实时热榜（微博/知乎/抖音/B站/小红书）
- 合并排序为TOP100
- 更新 index.html 中的静态HTML热点列表
- 推送到GitHub main分支
"""

import requests
import json
import re
import subprocess
import sys
import warnings
from datetime import datetime
from pathlib import Path

# 禁用SSL警告
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
try:
    requests.packages.urllib3.disable_warnings()
except:
    pass

# ========== 配置 ==========
HTML_PATH = Path(r"C:\Users\VRPC01\.qclaw\workspace\hotpulse\index.html")
GIT_REPO_PATH = Path(r"C:\Users\VRPC01\.qclaw\workspace\hotpulse")

PLATFORMS = {
    'weibo': {
        'name': '微博',
        'icon': '🐦',
        'urls': [
            'https://api.vvhan.com/api/hotlist/wbHot',
            'https://tophub.today/json/KqndgEeLl9.json',
            'https://api.oioweb.cn/api/common/HotList?type=weibo',
        ],
    },
    'zhihu': {
        'name': '知乎',
        'icon': '📘',
        'urls': [
            'https://api.vvhan.com/api/hotlist/zhihuHot',
            'https://tophub.today/json/n/mproPpoq6O.json',
            'https://api.oioweb.cn/api/common/HotList?type=zhihu',
        ],
    },
    'bilibili': {
        'name': 'B站',
        'icon': '📺',
        'urls': [
            'https://api.vvhan.com/api/hotlist/biliHot',
            'https://tophub.today/json/n/xLngunu24O.json',
            'https://api.oioweb.cn/api/common/HotList?type=bilibili',
        ],
    },
    'douyin': {
        'name': '抖音',
        'icon': '🎵',
        'urls': [
            'https://tophub.today/json/n/DpQvNABoNE.json',
        ],
    },
    'xiaohongshu': {
        'name': '小红书',
        'icon': '📕',
        'urls': [
            'https://tophub.today/json/n/5VaobgvAj1.json',
        ],
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
    return str(hot).strip()

def parse_hot_to_number(hot_str) -> int:
    """将热度字符串转为数字，用于排序"""
    if not hot_str:
        return 0
    hot_str = str(hot_str).replace(',', '').strip()
    m = re.match(r'^([\d.]+)\s*亿', hot_str)
    if m:
        return int(float(m.group(1)) * 1e8)
    m = re.match(r'^([\d.]+)\s*万', hot_str)
    if m:
        return int(float(m.group(1)) * 1e4)
    m = re.match(r'^(\d+)$', hot_str)
    if m:
        return int(m.group(1))
    try:
        return int(hot_str)
    except:
        return 0

def fetch_json(url: str, timeout: int = 10) -> dict:
    """抓取JSON数据（禁用SSL验证）"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        resp = requests.get(url, headers=headers, timeout=timeout, verify=False)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return None

def fetch_platform(platform_key: str, config: dict) -> list:
    """
    抓取单个平台热榜，返回 [{'title':..., 'hot':..., 'platform':...}, ...]
    """
    items = []
    
    for url in config['urls']:
        print(f"    → 尝试 {url[:60]}...")
        j = fetch_json(url)
        
        if not j:
            continue
        
        # 尝试 vvhan 格式: {'data': [{'title':..., 'hot':...}, ...]}
        if 'data' in j and isinstance(j['data'], list) and j['data']:
            raw = j['data'][:20]
            for item in raw:
                title = item.get('title') or item.get('name', '')
                hot = format_hot(item.get('hot') or item.get('heat', ''))
                if title and isinstance(title, str):
                    items.append({'title': title.strip(), 'hot': hot, 'platform': config['name']})
            if items:
                print(f"      ✓ 成功获取 {len(items)} 条")
                return items[:20]
        
        # 尝试 tophub 格式: {'Data': [{'Title':..., 'Hot':...}, ...]}
        if 'Data' in j and isinstance(j['Data'], list) and j['Data']:
            raw = j['Data'][:20]
            for item in raw:
                title = item.get('Title') or item.get('title', '')
                hot = str(item.get('Hot') or item.get('hot', ''))
                if title and isinstance(title, str):
                    items.append({'title': title.strip(), 'hot': hot, 'platform': config['name']})
            if items:
                print(f"      ✓ 成功获取 {len(items)} 条")
                return items[:20]
        
        # 尝试其他格式
        data = j.get('data') or j.get('list') or j.get('result') or []
        if isinstance(data, list) and data:
            for item in data[:20]:
                if not isinstance(item, dict):
                    continue
                title = (item.get('title') or item.get('name', '') or 
                        item.get('word', '') or item.get('Title', ''))
                hot = format_hot(item.get('hot') or item.get('heat', '') or 
                              item.get('value', '') or item.get('Hot', ''))
                if title and isinstance(title, str):
                    items.append({'title': title.strip(), 'hot': hot, 'platform': config['name']})
            if items:
                print(f"      ✓ 成功获取 {len(items)} 条")
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
        import time; time.sleep(0.5)  # 避免请求过快
    
    print(f"\n总获取: {len(all_items)} 条")
    return all_items

def deduplicate_and_merge(items: list, top_n: int = 100) -> list:
    """
    去重 + 按热度排序
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
        
        platform = item['platform']
        platform_html = f'<span class="hotlist-merged-platform">{platform}</span>'
        
        heat = item['hot'] or ''
        heat_html = f'<span class="hotlist-merged-heat">{heat}</span>' if heat else ''
        
        title_escaped = (item['title'].replace('&', '&amp;')
                                       .replace('<', '&lt;')
                                       .replace('>', '&gt;')
                                       .replace('"', '&quot;'))
        
        line = (f'<div class="hotlist-merged-item">'
                f'<span class="{rank_cls}">{rank}</span>'
                f'<span class="hotlist-merged-title-text">{title_escaped}</span>'
                f'{platform_html}{heat_html}</div>')
        lines.append(line)
    
    return '\n'.join(lines)

def update_index_html(html_path: Path, new_items_html: str, date_str: str):
    """更新 index.html 中的热点列表和日期"""
    content = html_path.read_text(encoding='utf-8')
    
    # 找到热点列表区域并替换
    # 定位: <div class="hotlist-merged-grid"> 到下一个 </div> 之前
    pattern = r'(<div class="hotlist-merged-grid">)([\s\S]*?)(</div>\s*<div class="hotlist-footer">)'
    
    replacement = r'\1\n' + new_items_html + r'\n\3'
    new_content = re.sub(pattern, replacement, content)
    
    if new_content == content:
        print("  ⚠ 未找到热点列表标记，尝试备用模式...")
        # 备用：直接查找 hotlist-merged-grid
        idx = content.find('<div class="hotlist-merged-grid">')
        if idx >= 0:
            # 找到对应的结束位置
            end_idx = content.find('</div>', idx + 50)
            while end_idx > 0:
                # 检查后面是否是 hotlist-footer
                next_div = content.find('<div class="hotlist-footer">', end_idx)
                if next_div > 0 and next_div - end_idx < 20:
                    # 找到了
                    new_content = (content[:idx + len('<div class="hotlist-merged-grid">')] + 
                                  '\n' + new_items_html + '\n' +
                                  content[end_idx:])
                    break
                end_idx = content.find('</div>', end_idx + 1)
    
    # 更新日期
    date_pattern = r'· 更新时间：\d{4}-\d{2}-\d{2} \d{2}:\d{2}'
    new_date = f'· 更新时间：{date_str}'
    new_content = re.sub(date_pattern, new_date, new_content)
    
    html_path.write_text(new_content, encoding='utf-8')
    print(f"  ✓ 已更新 {html_path.name}")

def git_commit_push(repo_path: Path, date_str: str) -> bool:
    """Git提交并推送"""
    try:
        # git add
        result = subprocess.run(
            ['git', 'add', 'index.html'],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"  ✗ git add 失败: {result.stderr}")
            return False
        
        # git commit
        msg = f'hotlist: 每日更新 {date_str}'
        result = subprocess.run(
            ['git', 'commit', '-m', msg],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            # 可能没有变化
            if 'nothing to commit' in result.stdout or 'nothing to commit' in result.stderr:
                print(f"  ⚠ 没有变化需要提交")
                return True
            print(f"  ✗ git commit 失败: {result.stderr}")
            return False
        
        print(f"  ✓ git commit 成功")
        
        # git push
        result = subprocess.run(
            ['git', 'push', 'origin', 'main'],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"  ✓ Git推送成功")
            return True
        else:
            print(f"  ✗ Git推送失败: {result.stderr}")
            return False
    
    except Exception as e:
        print(f"  ✗ Git操作失败: {e}")
        return False

# ========== 主流程 ==========
def main():
    print("=" * 60)
    print("猪小媒热点数据每日更新 v2")
    print("=" * 60)
    
    # 1. 抓取数据
    print("\n[1/4] 抓取各平台热榜...")
    all_items = fetch_all_platforms()
    
    if not all_items:
        print("\n✗ 没有获取到任何数据")
        print("  可能原因：")
        print("  1. 网络被拦截（企业防火墙）")
        print("  2. API全部失效")
        print("  3. DNS解析失败")
        print("\n  建议：")
        print("  - 检查网络代理设置")
        print("  - 手动更新 index.html")
        print("  - 或部署到Vercel云端运行此脚本")
        return
    
    # 2. 去重合并排序
    print("\n[2/4] 去重合并排序...")
    top100 = deduplicate_and_merge(all_items, top_n=100)
    
    if not top100:
        print("✗ 去重后没有数据")
        return
    
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
    ok = git_commit_push(GIT_REPO_PATH, date_str)
    
    print("\n" + "=" * 60)
    if ok:
        print(f"✓ 更新完成！共 {len(top100)} 条热点")
        print(f"  更新时间: {date_str}")
        print(f"  Vercel将自动部署")
    else:
        print(f"⚠ 数据已更新，但Git推送失败")
        print(f"  请手动推送：cd {GIT_REPO_PATH} && git push")
    print("=" * 60)

if __name__ == '__main__':
    main()

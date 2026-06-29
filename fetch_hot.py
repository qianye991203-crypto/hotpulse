import urllib.request
import json
import ssl
import sys

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def fetch(url, headers=None):
    h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    return urllib.request.urlopen(req, context=ctx, timeout=15)

# 微博热搜
try:
    r = fetch('https://weibo.com/ajax/side/hotSearch')
    d = json.loads(r.read())
    weibo = d['data']['realtime'][:55]
    print('WEIBO_START')
    print(json.dumps([{'word': i['word'], 'hot': i.get('raw_hot', i.get('num', 0))} for i in weibo], ensure_ascii=False))
    print('WEIBO_END')
except Exception as e:
    print(f'微博失败: {e}', file=sys.stderr)

# 百度热点
try:
    r = fetch('https://top.baidu.com/api?get=topic_list&httped=1')
    d = json.loads(r.read())
    baidu = d['result']['topic_list'][:55]
    print('BAIDU_START')
    print(json.dumps([{'word': i['queryWord'], 'hot': i.get('hotScore', 0)} for i in baidu], ensure_ascii=False))
    print('BAIDU_END')
except Exception as e:
    print(f'百度失败: {e}', file=sys.stderr)

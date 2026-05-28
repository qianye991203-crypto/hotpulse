/**
 * 猪小媒 - 实时热榜 API（Vercel Serverless Function）
 * GET /api/hotlist?platform=weibo|zhihu|bilibili|douyin|xiaohongshu|twitter|reddit|all
 * 部署在 Vercel，云端抓取，无 CORS 限制
 */

const PLATFORMS = {
  weibo: {
    name: '微博热搜',
    icon: '🐦',
    fetchFn: async () => {
      // 优先用 vvhan API
      try {
        const r = await fetch('https://api.vvhan.com/api/hotlist/wbHot', {
          headers: { 'User-Agent': 'Mozilla/5.0' },
          signal: AbortSignal.timeout(6000)
        });
        if (r.ok) {
          const j = await r.json();
          if (j && j.data && j.data.length) {
            return j.data.slice(0, 20).map((item, i) => ({
              rank: i + 1,
              title: item.title || item.name || '',
              hot: formatHot(item.hot || item.heat || ''),
              url: item.url || item.link || `https://s.weibo.com/weibo?q=${encodeURIComponent(item.title || '')}`
            }));
          }
        }
      } catch(e) {}
      // fallback: tophub.today
      try {
        const r2 = await fetch('https://tophub.today/json/KqndgEeLl9.json', {
          headers: { 'User-Agent': 'Mozilla/5.0' },
          signal: AbortSignal.timeout(6000)
        });
        if (r2.ok) {
          const j2 = await r2.json();
          if (j2 && j2.Data && j2.Data.length) {
            return j2.Data.slice(0, 20).map((item, i) => ({
              rank: i + 1,
              title: item.Title || '',
              hot: item.Hot || '',
              url: item.Url || ''
            }));
          }
        }
      } catch(e) {}
      return null;
    }
  },
  zhihu: {
    name: '知乎热榜',
    icon: '📘',
    fetchFn: async () => {
      try {
        const r = await fetch('https://api.vvhan.com/api/hotlist/zhihuHot', {
          headers: { 'User-Agent': 'Mozilla/5.0' },
          signal: AbortSignal.timeout(6000)
        });
        if (r.ok) {
          const j = await r.json();
          if (j && j.data && j.data.length) {
            return j.data.slice(0, 20).map((item, i) => ({
              rank: i + 1,
              title: item.title || item.name || '',
              hot: formatHot(item.hot || ''),
              url: item.url || (item.id ? `https://www.zhihu.com/question/${item.id}` : '')
            }));
          }
        }
      } catch(e) {}
      try {
        const r2 = await fetch('https://tophub.today/json/n/mproPpoq6O.json', {
          headers: { 'User-Agent': 'Mozilla/5.0' },
          signal: AbortSignal.timeout(6000)
        });
        if (r2.ok) {
          const j2 = await r2.json();
          if (j2 && j2.Data && j2.Data.length) {
            return j2.Data.slice(0, 20).map((item, i) => ({
              rank: i + 1,
              title: item.Title || '',
              hot: item.Hot || '',
              url: item.Url || ''
            }));
          }
        }
      } catch(e) {}
      return null;
    }
  },
  bilibili: {
    name: 'B站热门',
    icon: '📺',
    fetchFn: async () => {
      try {
        const r = await fetch('https://api.vvhan.com/api/hotlist/biliHot', {
          headers: { 'User-Agent': 'Mozilla/5.0' },
          signal: AbortSignal.timeout(6000)
        });
        if (r.ok) {
          const j = await r.json();
          if (j && j.data && j.data.length) {
            return j.data.slice(0, 20).map((item, i) => ({
              rank: i + 1,
              title: item.title || item.name || '',
              hot: formatHot(item.hot || ''),
              url: item.url || (item.bvid ? `https://www.bilibili.com/video/${item.bvid}` : '')
            }));
          }
        }
      } catch(e) {}
      try {
        const r2 = await fetch('https://tophub.today/json/n/xLngunu24O.json', {
          headers: { 'User-Agent': 'Mozilla/5.0' },
          signal: AbortSignal.timeout(6000)
        });
        if (r2.ok) {
          const j2 = await r2.json();
          if (j2 && j2.Data && j2.Data.length) {
            return j2.Data.slice(0, 20).map((item, i) => ({
              rank: i + 1,
              title: item.Title || '',
              hot: item.Hot || '',
              url: item.Url || ''
            }));
          }
        }
      } catch(e) {}
      return null;
    }
  },
  douyin: {
    name: '抖音热点',
    icon: '🎵',
    fetchFn: async () => {
      try {
        const r = await fetch('https://tophub.today/json/n/DpQvNABoNE.json', {
          headers: { 'User-Agent': 'Mozilla/5.0' },
          signal: AbortSignal.timeout(6000)
        });
        if (r.ok) {
          const j = await r.json();
          if (j && j.Data && j.Data.length) {
            return j.Data.slice(0, 20).map((item, i) => ({
              rank: i + 1,
              title: item.Title || '',
              hot: item.Hot || '',
              url: item.Url || ''
            }));
          }
        }
      } catch(e) {}
      return null;
    }
  },
  xiaohongshu: {
    name: '小红书',
    icon: '📕',
    fetchFn: async () => {
      try {
        const r = await fetch('https://tophub.today/json/n/5VaobgvAj1.json', {
          headers: { 'User-Agent': 'Mozilla/5.0' },
          signal: AbortSignal.timeout(6000)
        });
        if (r.ok) {
          const j = await r.json();
          if (j && j.Data && j.Data.length) {
            return j.Data.slice(0, 20).map((item, i) => ({
              rank: i + 1,
              title: item.Title || '',
              hot: item.Hot || '',
              url: item.Url || ''
            }));
          }
        }
      } catch(e) {}
      return null;
    }
  },
  twitter: {
    name: 'Twitter趋势',
    icon: '🌍',
    fetchFn: async () => {
      try {
        const r = await fetch('https://tophub.today/json/n/Ku7b7CB2Ql.json', {
          headers: { 'User-Agent': 'Mozilla/5.0' },
          signal: AbortSignal.timeout(6000)
        });
        if (r.ok) {
          const j = await r.json();
          if (j && j.Data && j.Data.length) {
            return j.Data.slice(0, 20).map((item, i) => ({
              rank: i + 1,
              title: item.Title || '',
              hot: item.Hot || '',
              url: item.Url || ''
            }));
          }
        }
      } catch(e) {}
      return null;
    }
  },
  reddit: {
    name: 'Reddit热帖',
    icon: '🤖',
    fetchFn: async () => {
      try {
        const r = await fetch('https://tophub.today/json/n/yVowGg0oD0.json', {
          headers: { 'User-Agent': 'Mozilla/5.0' },
          signal: AbortSignal.timeout(6000)
        });
        if (r.ok) {
          const j = await r.json();
          if (j && j.Data && j.Data.length) {
            return j.Data.slice(0, 20).map((item, i) => ({
              rank: i + 1,
              title: item.Title || '',
              hot: item.Hot || '',
              url: item.Url || ''
            }));
          }
        }
      } catch(e) {}
      return null;
    }
  }
};

function formatHot(hot) {
  if (!hot) return '';
  if (typeof hot === 'number') hot = String(hot);
  if (typeof hot === 'string' && /^\d+$/.test(hot)) {
    const n = parseInt(hot, 10);
    if (n >= 1e8) return (n / 1e8).toFixed(1) + '亿';
    if (n >= 1e4) return (n / 1e4).toFixed(1) + '万';
    return String(n);
  }
  return hot;
}

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  if (req.method === 'OPTIONS') return res.status(200).end();

  const { platform = 'all' } = req.query;

  try {
    if (platform === 'all') {
      const results = {};
      const entries = Object.entries(PLATFORMS);
      const promises = entries.map(async ([key, p]) => {
        try {
          const data = await p.fetchFn();
          results[key] = data ? { name: p.name, icon: p.icon, data } : null;
        } catch (e) {
          results[key] = null;
        }
      });
      await Promise.all(promises);
      return res.status(200).json({ success: true, data: results, updatedAt: Date.now() });
    }

    const p = PLATFORMS[platform];
    if (!p) {
      return res.status(400).json({ success: false, error: '未知平台，支持: ' + Object.keys(PLATFORMS).join(',') });
    }
    const data = await p.fetchFn();
    if (!data) return res.status(502).json({ success: false, error: '抓取失败，数据源不可用' });
    return res.status(200).json({ success: true, name: p.name, icon: p.icon, data, updatedAt: Date.now() });

  } catch (err) {
    return res.status(500).json({ success: false, error: err.message });
  }
};

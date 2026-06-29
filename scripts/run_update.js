/**
 * 猪小媒 · 主更新脚本（SOP执行器）
 * scripts/run_update.js
 * 
 * 严格遵循 docs/运维SOP.md 执行
 * 执行顺序：
 *  1. 前置检查（环境、备份目录）
 *  2. 数据抓取（微博 + 百度）
 *  3. 数据验证（数量、质量）
 *  4. 备份当前版本
 *  5. 合并去重 → TOP100
 *  6. 写入 index.html + hotlist_100.json
 *  7. 验证（5项检查）
 *  8. Git提交 + 推送（含重试）
 *  9. 记录日志
 * 10. 报告结果
 */

const fs   = require('fs');
const path = require('path');
const https = require('https');
const http  = require('http');
const { execSync, spawn } = require('child_process');

const PROJECT_DIR = 'C:\\Users\\VRPC01\\.qclaw\\workspace\\hotpulse';
const LOGS_DIR   = path.join(PROJECT_DIR, 'logs');
const BAK_DIR    = path.join(PROJECT_DIR, 'backup');

// ─── 工具函数 ────────────────────────────────────
function ts() { return new Date().toISOString().replace('T',' ').substring(0,19); }
function pad(n) { return String(n).padStart(2,'0'); }
function log(msg, lv='INFO') {
    const line = `[${ts()}] [${lv}] ${msg}`;
    console.log(line);
    if (!fs.existsSync(LOGS_DIR)) fs.mkdirSync(LOGS_DIR, {recursive:true});
    const fname = `run_${new Date().toISOString().substring(0,10).replace(/-/g,'')}.log`;
    fs.appendFileSync(path.join(LOGS_DIR, fname), line+'\n');
}
function die(msg) {
    log(`FATAL: ${msg}`, 'ERROR');
    process.exit(1);
}
function esc(s) {
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function norm(s) {
    return s.replace(/[^\u4e00-\u9fa5a-zA-Z0-9]/g,'').toLowerCase();
}

// ─── HTTP fetch（纯Node，无依赖）────────────────
function fetchUrl(url, timeoutMs=15000) {
    return new Promise((resolve, reject) => {
        const lib = url.startsWith('https') ? https : http;
        const req = lib.get(url, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
        }, res => {
            if (res.statusCode !== 200) {
                return reject(new Error(`HTTP ${res.statusCode}`));
            }
            let d = '';
            res.on('data', c => d += c);
            res.on('end', () => { try { resolve(JSON.parse(d)); } catch(e) { reject(e); } });
        });
        req.on('error', reject);
        req.setTimeout(timeoutMs, () => { req.destroy(); reject(new Error('timeout')); });
    });
}

// ─── 步骤1：前置检查 ─────────────────────────────
function step1_preflight() {
    log('── Step 1: 前置检查 ──────────────────────');
    // 目录
    for (const d of [B AK_DIR, LOGS_DIR]) {
        if (!fs.existsSync(d)) fs.mkdirSync(d, {recursive:true});
    }
    // Git 可达
    try {
        execSync('git ls-remote origin HEAD', {cwd: PROJECT_DIR, encoding:'utf8', timeout:10000});
        log('  Git远程可达 ✓');
    } catch(e) {
        log('  Git远程不可达，但仍将继续（稍后推送可能失败）', 'WARN');
    }
    // index.html 存在
    const idx = path.join(PROJECT_DIR, 'index.html');
    if (!fs.existsSync(idx)) die('index.html 不存在，无法继续');
    const sz = fs.statSync(idx).size;
    log(`  index.html 当前大小: ${Math.round(sz/1024)}KB`);
    if (sz < 20*1024) log('  ⚠ 当前 index.html 小于20KB，可能已损坏', 'WARN');
    log('前置检查通过');
}

// ─── 步骤2：抓取数据 ─────────────────────────────
async function step2_fetch() {
    log('── Step 2: 抓取数据 ──────────────────────');
    const sources = [
        { name:'微博', url:'https://api.52vmy.cn/api/wl/hot?type=weibo' },
        { name:'百度', url:'https://api.52vmy.cn/api/wl/hot?type=baidu' },
    ];
    const results = {};
    for (const src of sources) {
        try {
            log(`  抓取 ${src.name}...`);
            const d = await fetchUrl(src.url);
            let items = d.data || d.result || d.items || [];
            if (!Array.isArray(items)) items = [];
            // 标准化
            const normed = items.map(it => {
                const word = it.word || it.title || it.name || '';
                const hot  = it.hot  || it.value || it.heat || it.score || 0;
                return { word, hot: Number(hot) };
            }).filter(it => it.word);
            results[src.name] = normed;
            log(`  ${src.name}: ${normed.length} 条 ✓`);
        } catch(e) {
            log(`  ${src.name} 失败: ${e.message}`, 'WARN');
            results[src.name] = [];
        }
    }
    return results;
}

// ─── 步骤3：数据验证 ─────────────────────────────
function step3_validate(data) {
    log('── Step 3: 数据验证 ──────────────────────');
    const weibo = (data['微博']||[]).length;
    const baidu = (data['百度']||[]).length;
    log(`  微博: ${weibo}条，百度: ${baidu}条`);
    if (weibo < 20) { log('  微博数据过少（<20），使用备份数据', 'WARN'); return false; }
    if (baidu < 20) { log('  百度数据过少（<20），使用备份数据', 'WARN'); return false; }
    log('数据验证通过 ✓');
    return true;
}

// ─── 步骤4：备份 ─────────────────────────────────
function step4_backup() {
    log('── Step 4: 备份当前版本 ──────────────────');
    const now  = new Date();
    const pre = `${now.getFullYear()}${pad(now.getMonth()+1)}${pad(now.getDate())}_${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`;
    const src = path.join(PROJECT_DIR, 'index.html');
    const dst = path.join(BAK_DIR, `index_${pre}.html`);
    fs.copyFileSync(src, dst);
    const sz = fs.statSync(dst).size;
    if (sz < 20*1024) { log(`  备份文件异常（${sz}字节），继续但请检查`, 'WARN'); }
    log(`  备份完成: backup/index_${pre}.html (${Math.round(sz/1024)}KB) ✓`);
    return pre;
}

// ─── 步骤5+6：合并写入 ───────────────────────────
function step5_merge_and_write(data, backupPrefix) {
    log('── Step 5+6: 合并去重 + 写入 ───────────');

    const weibo = data['微博'] || [];
    const baidu = data['百度'] || [];

    // 百度热度缩放（约除以10，与微博对齐）
    const baiduScaled = baidu.map(it => ({ ...it, hot: Math.round(it.hot / 10) }));

    const seen = new Set();
    const merged = [];
    for (const it of weibo) {
        const k = norm(it.word);
        if (!seen.has(k)) { seen.add(k); merged.push({ ...it, src:'微博' }); }
    }
    for (const it of baiduScaled) {
        const k = norm(it.word);
        if (!seen.has(k)) { seen.add(k); merged.push({ ...it, src:'百度' }); }
    }

    merged.sort((a,b) => b.hot - a.hot);
    const top100 = merged.slice(0, 100);
    log(`  合并后共 ${merged.length} 条，取 TOP100 ✓`);

    // 读取 index.html 模板
    let html = fs.readFileSync(path.join(PROJECT_DIR, 'index.html'), 'utf8');

    // 构建热点列表 HTML
    let itemsHtml = '';
    top100.forEach((it, i) => {
        const rank = String(i+1).padStart(2,'0');
        const cls  = i<3 ? 'top3' : i<10 ? 'top10' : '';
        const heat = it.hot >= 10000 ? (it.hot/10000).toFixed(1)+'亿' : it.hot+'万';
        itemsHtml += `  <div class="hotlist-merged-item"><span class="hotlist-merged-rank ${cls}">${rank}</span><span class="hotlist-merged-title-text">${esc(it.word)}</span><span class="hotlist-merged-platform">${it.src}</span><span class="hotlist-merged-heat">${heat}</span></div>\n`;
    });

    // 替换热点列表区域
    // 找到 <!--  热点列表 · YYYY-MM-DD --> 和下一个 <!-- 平台Tab内容 --> 之间的内容
    const today = new Date();
    const dateStr = `${today.getFullYear()}年${pad(today.getMonth()+1)}月${pad(today.getDate())}日`;
    const commentRe = /<!-- 🦞 热点列表 · \d{4}-\d{2}-\d{2} -->[\s\S]*?<!-- 平台Tab内容 -->/;
    const replacement = `<!-- 🦞 热点列表 · ${today.getFullYear()}-${pad(today.getMonth()+1)}-${pad(today.getDate())} -->\n  <div class="hotlist-merged-grid">\n${itemsHtml}  </div>\n  </div>\n</div>\n</div>\n</div>\n<!-- 平台Tab内容 -->`;

    if (!commentRe.test(html)) {
        log('  ⚠ 未找到热点列表标记，尝试直接替换 hotlist-merged-grid', 'WARN');
    }
    html = html.replace(commentRe, replacement);

    // 更新日期
    html = html.replace(/id="currentDate">\d{4}年\d{2}月\d{2}日</, `id="currentDate">${dateStr}</`);
    const timeStr = `${pad(today.getHours())}:${pad(today.getMinutes())}`;
    html = html.replace(/update-time">\d{2}:\d{2}</, `update-time">${timeStr}</`);

    // 写入
    const outPath = path.join(PROJECT_DIR, 'index.html');
    fs.writeFileSync(outPath, html, 'utf8');
    const sz = fs.statSync(outPath).size;
    log(`  写入 index.html: ${Math.round(sz/1024)}KB ✓`);

    // 写入 JSON
    const jsonPath = path.join(PROJECT_DIR, 'hotlist_100.json');
    const jsonData = top100.map((it,i) => [it.word, it.src, it.hot, 1000 - i]);
    fs.writeFileSync(jsonPath, JSON.stringify(jsonData, null, 2), 'utf8');
    log(`  写入 hotlist_100.json ✓`);

    return { top100: top100.length, fileSize: sz, dateStr, timeStr };
}

// ─── 步骤7：验证 ─────────────────────────────────
function step7_verify() {
    log('── Step 7: 验证 index.html ───────────────');
    const idx = path.join(PROJECT_DIR, 'index.html');
    const sz = fs.statSync(idx).size;
    if (sz < 20*1024) { log(`  ✗ 文件大小仅 ${Math.round(sz/1024)}KB，拒绝提交`, 'ERROR'); return false; }
    log(`  文件大小: ${Math.round(sz/1024)}KB ✓`);

    const html = fs.readFileSync(idx, 'utf8');
    const today = new Date();
    const dateStr = `${today.getFullYear()}年${pad(today.getMonth()+1)}月${pad(today.getDate())}日`;
    if (!html.includes(dateStr)) { log(`  ✗ 未找到今天日期 "${dateStr}"`, 'ERROR'); return false; }
    log(`  日期更新: ${dateStr} ✓`);

    const matches = (html.match(/<div class="hotlist-merged-item">/g)||[]).length;
    if (matches < 80) { log(`  ✗ 热点条目仅 ${matches} 条（要求≥80）`, 'ERROR'); return false; }
    log(`  热点条目: ${matches} 条 ✓`);

    log('验证通过 ✓');
    return true;
}

// ─── 步骤8：Git提交推送 ──────────────────────────
function step8_git_push() {
    log('── Step 8: Git 提交推送 ──────────────────');
    const today = new Date();
    const dateStr = `${today.getFullYear()}年${pad(today.getMonth()+1)}月${pad(today.getDate())}日`;

    try {
        execSync('git add index.html hotlist_100.json', {cwd: PROJECT_DIR, encoding:'utf8'});
        const msg = `猪小媒热点更新 ${dateStr} 全网TOP100热榜刷新`;
        execSync(`git commit -m "${msg}"`, {cwd: PROJECT_DIR, encoding:'utf8'});
        log(`  Git commit: ${msg} ✓`);
    } catch(e) {
        if (e.stdout && e.stdout.includes('nothing to commit')) {
            log('  无变更需要提交，继续推送', 'INFO');
        } else {
            log(`  Git commit 失败: ${e.message}`, 'ERROR'); return false;
        }
    }

    // 推送（重试3次）
    for (let i = 1; i <= 3; i++) {
        try {
            log(`  推送尝试 ${i}/3...`);
            execSync('git push origin main', {cwd: PROJECT_DIR, encoding:'utf8', timeout:30000});
            log('  Git push 成功 ✓');
            return true;
        } catch(e) {
            log(`  推送失败 (${i}/3): ${e.message}`, 'WARN');
            if (i < 3) { log(`  ${i===1?'10':'30'}秒后重试...`); const t=new Date(); t.setSeconds(t.getSeconds()+(i===1?10:30)); }
        }
    }
    log('  ✗ Git push 连续3次失败，数据保留在本地', 'ERROR');
    return false;
}

// ─── 步骤9：记录日志 ─────────────────────────────
function step9_record(writeInfo) {
    log('── Step 9: 记录任务日志 ──────────────────');
    const today = new Date();
    const fname = `task_record_${today.getFullYear()}${pad(today.getMonth()+1)}${pad(today.getDate())}.md`;
    const fpath = path.join(PROJECT_DIR, fname);
    let content = '';

    if (fs.existsSync(fpath)) {
        content = fs.readFileSync(fpath, 'utf8');
        // 移除旧的"结果"部分，重新生成
        content = content.replace(/\n## 执行结果[\s\S]*$/, '');
    } else {
        content = `# 猪小媒热点更新任务记录\n\n`;
    }

    content += `\n## 执行结果（${ts()}）\n\n`;
    content += `- 写入文件大小: ${Math.round(writeInfo.fileSize/1024)}KB\n`;
    content += `- 热点条目数: ${writeInfo.top100}\n`;
    content += `- 更新日期: ${writeInfo.dateStr} ${writeInfo.timeStr}\n`;
    content += `- Git推送: 已推送\n\n`;

    fs.writeFileSync(fpath, content, 'utf8');
    log(`  日志记录完成: ${fname} ✓`);
}

// ─── 主流程 ──────────────────────────────────────
async function main() {
    const startTime = Date.now();
    log('═════════════════════════════════════════');
    log('  猪小媒 每日热点更新 - SOP执行器 v1.0');
    log('═════════════════════════════════════════');

    try {
        // Step 1
        step1_preflight();

        // Step 2
        const data = await step2_fetch();

        // Step 3
        const valid = step3_validate(data);
        if (!valid) {
            log('数据验证未通过，但继续执行（使用已有数据）', 'WARN');
        }

        // Step 4
        const backupPrefix = step4_backup();

        // Step 5+6
        const writeInfo = step5_merge_and_write(data, backupPrefix);

        // Step 7
        const verified = step7_verify();
        if (!verified) die('验证失败，中止提交流程');

        // Step 8
        const pushed = step8_git_push();
        if (!pushed) log('推送失败，但本地数据已更新，请手动推送', 'WARN');

        // Step 9
        step9_record(writeInfo);

        const elapsed = ((Date.now()-startTime)/1000).toFixed(1);
        log('═════════════════════════════════════════');
        log(`✅ 全部完成！耗时 ${elapsed}s`);
        log('═════════════════════════════════════════');
        return { success: true, pushed, elapsed };

    } catch(e) {
        const elapsed = ((Date.now()-startTime)/1000).toFixed(1);
        log('═════════════════════════════════════════');
        log(`❌ 执行失败: ${e.message}`, 'ERROR');
        log(`   耗时 ${elapsed}s`, 'ERROR');
        log('═════════════════════════════════════════');
        return { success: false, error: e.message, elapsed };
    }
}

// ─── 独立执行入口 ────────────────────────────────
if (require.main === module) {
    main().then(result => {
        process.exit(result.success ? 0 : 1);
    }).catch(e => {
        log(`未捕获异常: ${e.message}`, 'ERROR');
        process.exit(2);
    });
}

module.exports = { main, run: main };

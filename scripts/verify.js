/**
 * 验证脚本 - verify.js
 * 验证 index.html 是否符合发布标准
 * 
 * 验证清单：
 *  ✓ 文件大小 ≥ 20KB
 *  ✓ HTML结构完整（<html>...</html>）
 *  ✓ 包含当天日期
 *  ✓ 热点条目 ≥ 80条
 *  ✓ JavaScript 无语法错误
 *  ✓ Git 仓库状态正常
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const PROJECT_DIR = 'C:\\Users\\VRPC01\\.qclaw\\workspace\\hotpulse';
const INDEX_HTML = path.join(PROJECT_DIR, 'index.html');

// ─── 日志 ──────────────────────────────────────────
const LOGS_DIR = path.join(PROJECT_DIR, 'logs');
const today = new Date();
const dateStr = `${today.getFullYear()}${String(today.getMonth()+1).padStart(2,'0')}${String(today.getDate()).padStart(2,'0')}`;
const LOG_FILE = path.join(LOGS_DIR, `verify_${dateStr}.log`);

function log(msg, type = 'INFO') {
    const ts = new Date().toISOString().replace('T',' ').substring(0,19);
    const line = `[${ts}] [${type}] ${msg}`;
    console.log(line);
    if (!fs.existsSync(LOGS_DIR)) fs.mkdirSync(LOGS_DIR, { recursive: true });
    fs.appendFileSync(LOG_FILE, line + '\n');
}

// ─── 验证项目 ──────────────────────────────────────
const checks = [];

function check(name, fn) {
    try {
        const result = fn();
        if (result.ok) {
            log(`✓ ${name}: ${result.msg}`);
            checks.push({ name, pass: true, msg: result.msg });
        } else {
            log(`✗ ${name}: ${result.msg}`, 'ERROR');
            checks.push({ name, pass: false, msg: result.msg });
        }
        return result.ok;
    } catch(e) {
        log(`✗ ${name}: 异常 - ${e.message}`, 'ERROR');
        checks.push({ name, pass: false, msg: `异常: ${e.message}` });
        return false;
    }
}

// ─── 主验证流程 ────────────────────────────────────
function run() {
    log('═'.repeat(60));
    log('开始验证 index.html');
    log('═'.repeat(60));

    let allPass = true;

    // 1. 文件存在性
    const existCheck = check('文件存在', () => {
        if (!fs.existsSync(INDEX_HTML)) return { ok: false, msg: 'index.html 不存在' };
        return { ok: true, msg: '存在' };
    });
    if (!existCheck) return { success: false, checks };

    // 2. 文件大小
    const size = fs.statSync(INDEX_HTML).size;
    check('文件大小', () => {
        if (size < 20 * 1024) return { ok: false, msg: `仅 ${Math.round(size/1024)}KB，要求 ≥ 20KB` };
        return { ok: true, msg: `${Math.round(size/1024)}KB` };
    }) || (allPass = false);

    // 3. HTML结构
    const html = fs.readFileSync(INDEX_HTML, 'utf8');
    check('HTML结构完整', () => {
        const hasOpen = html.includes('<html');
        const hasClose = html.includes('</html>');
        if (!hasOpen || !hasClose) return { ok: false, msg: `缺失标签: open=${hasOpen} close=${hasClose}` };
        return { ok: true, msg: '完整' };
    }) || (allPass = false);

    // 4. 包含当天日期
    const todayStr = `${today.getFullYear()}年${String(today.getMonth()+1).padStart(2,'0')}月${String(today.getDate()).padStart(2,'0')}日`;
    check('日期更新', () => {
        if (!html.includes(todayStr)) return { ok: false, msg: `未找到今天日期 "${todayStr}"` };
        return { ok: true, msg: todayStr };
    }) || (allPass = false);

    // 5. 热点条目数
    const matchCount = (html.match(/<div class="hotlist-merged-item">/g) || []).length;
    check('热点条目数', () => {
        if (matchCount < 80) return { ok: false, msg: `仅 ${matchCount} 条，要求 ≥ 80` };
        return { ok: true, msg: `${matchCount} 条` };
    }) || (allPass = false);

    // 6. JavaScript 语法检查
    check('JavaScript语法', () => {
        try {
            const scriptMatch = html.match(/<script>([\s\S]*?)<\/script>/g);
            if (!scriptMatch) return { ok: true, msg: '无内联JS' };
            // 提取所有JS代码并验证
            for (const block of scriptMatch) {
                const code = block.replace(/<\/?script>/g, '');
                try { new Function(code); } catch(e) { return { ok: false, msg: `语法错误: ${e.message}` }; }
            }
            return { ok: true, msg: '无语法错误' };
        } catch(e) {
            return { ok: false, msg: e.message };
        }
    }) || (allPass = false);

    // 7. Git 状态
    check('Git状态', () => {
        try {
            const status = execSync('git status --porcelain', { cwd: PROJECT_DIR, encoding: 'utf8' });
            if (status.trim()) return { ok: true, msg: `有未提交变更 (${status.trim().split('\n').length} 文件)` };
            return { ok: true, msg: '工作区干净' };
        } catch(e) {
            return { ok: false, msg: `Git错误: ${e.message}` };
        }
    });

    // 8. 远程可访问性（尝试简单curl）
    check('远程仓库可达', () => {
        try {
            execSync('git ls-remote origin HEAD', { cwd: PROJECT_DIR, encoding: 'utf8', timeout: 10000 });
            return { ok: true, msg: '可达' };
        } catch(e) {
            return { ok: false, msg: '不可达，推送可能失败' };
        }
    });

    // ─── 汇总报告 ─────────────────────────────────────
    log('═'.repeat(60));
    log(`验证结果: ${allPass ? '✅ 全部通过' : '❌ 存在失败项'}`);
    log('═'.repeat(60));
    for (const c of checks) {
        log(`  ${c.pass ? '✓' : '✗'} ${c.name}: ${c.msg}`);
    }
    log('═'.repeat(60));

    return {
        success: allPass,
        checks,
        summary: {
            total: checks.length,
            pass: checks.filter(c => c.pass).length,
            fail: checks.filter(c => !c.pass).length
        }
    };
}

// ─── 独立执行入口 ────────────────────────────────────
if (require.main === module) {
    const result = run();
    process.exit(result.success ? 0 : 2);
}

module.exports = { run, verify: run };

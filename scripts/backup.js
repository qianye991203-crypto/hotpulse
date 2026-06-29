/**
 * 备份脚本 - backup.js
 * 每次更新前必须执行
 * 
 * 执行标准：
 * 1. 读取当前 index.html 和 hotlist_100.json
 * 2. 命名格式: index_YYYYMMDD_HHMM.html / hotlist_YYYYMMDD.json
 * 3. 复制到 backup/ 目录
 * 4. 清理超过30天的旧备份
 * 5. 验证备份文件完整性
 */

const fs = require('fs');
const path = require('path');

const PROJECT_DIR = 'C:\\Users\\VRPC01\\.qclaw\\workspace\\hotpulse';
const BACKUP_DIR  = path.join(PROJECT_DIR, 'backup');
const LOGS_DIR    = path.join(PROJECT_DIR, 'logs');

// ─── 日志 ───────────────────────────────────────────
const LOG_FILE = path.join(LOGS_DIR, `backup_${stamp()}.log`);
function log(msg, type = 'INFO') {
    const line = `[${timestamp()}] [${type}] ${msg}`;
    console.log(line);
    fs.appendFileSync(LOG_FILE, line + '\n');
}
function timestamp() {
    const d = new Date();
    return d.toISOString().replace('T',' ').substring(0,19);
}
function stamp() {
    const d = new Date();
    return `${d.getFullYear()}${pad(d.getMonth()+1)}${pad(d.getDate())}`;
}
function pad(n) { return String(n).padStart(2,'0'); }

// ─── 核心逻辑 ─────────────────────────────────────────
function run() {
    // 1. 确保目录存在
    for (const dir of [BACKUP_DIR, LOGS_DIR]) {
        if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    }

    const now = new Date();
    const dateStr = `${now.getFullYear()}${pad(now.getMonth()+1)}${pad(now.getDate())}`;
    const timeStr = `${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`;
    const prefix = `${dateStr}_${timeStr}`;

    log(`开始备份，批次: ${prefix}`);

    let ok = 0, fail = 0;

    // 2. 备份 index.html
    const srcIndex = path.join(PROJECT_DIR, 'index.html');
    const dstIndex = path.join(BACKUP_DIR, `index_${prefix}.html`);
    if (fs.existsSync(srcIndex)) {
        const size = fs.statSync(srcIndex).size;
        fs.copyFileSync(srcIndex, dstIndex);
        const dstSize = fs.statSync(dstIndex).size;
        if (dstSize === size && size > 0) {
            log(`✓ index.html → backup/index_${prefix}.html (${size} bytes)`);
            ok++;
        } else {
            log(`✗ index.html 备份失败：大小不匹配 src=${size} dst=${dstSize}`, 'ERROR');
            fail++;
        }
    } else {
        log(`✗ index.html 不存在，备份中止`, 'ERROR');
        return { success: false, ok: 0, fail: 1, reason: 'source_missing' };
    }

    // 3. 备份 hotlist_100.json
    const srcJson = path.join(PROJECT_DIR, 'hotlist_100.json');
    const dstJson = path.join(BACKUP_DIR, `hotlist_${prefix}.json`);
    if (fs.existsSync(srcJson)) {
        const size = fs.statSync(srcJson).size;
        fs.copyFileSync(srcJson, dstJson);
        log(`✓ hotlist_100.json → backup/hotlist_${prefix}.json (${size} bytes)`);
        ok++;
    } else {
        log(`! hotlist_100.json 不存在，跳过`);
    }

    // 4. 清理超过30天的旧备份
    const cutoff = new Date(now);
    cutoff.setDate(cutoff.getDate() - 30);
    const cutoffStr = cutoff.toISOString().substring(0, 10); // YYYY-MM-DD

    const files = fs.readdirSync(BACKUP_DIR);
    let cleaned = 0;
    for (const file of files) {
        const fpath = path.join(BACKUP_DIR, file);
        const mtime = fs.statSync(fpath).mtime;
        if (mtime < cutoff) {
            fs.unlinkSync(fpath);
            cleaned++;
        }
    }
    if (cleaned > 0) log(`已清理 ${cleaned} 个超过30天的旧备份`);

    // 5. 输出结果摘要
    log(`备份完成：${ok} 成功，${fail} 失败`);
    
    return {
        success: fail === 0,
        ok, fail, cleaned,
        prefix,
        indexBackup: `backup/index_${prefix}.html`,
        jsonBackup: `backup/hotlist_${prefix}.json`
    };
}

// ─── 独立执行入口 ─────────────────────────────────────
if (require.main === module) {
    const result = run();
    process.exit(result.success ? 0 : 1);
}

module.exports = { run, backup: run };

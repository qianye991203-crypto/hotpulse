/**
 * 回滚脚本 - rollback.js
 * 从最新备份恢复 index.html
 * 
 * 使用方式：
 *   node scripts/rollback.js           ← 回滚到最近一次备份
 *   node scripts/rollback.js list      ← 列出所有可用备份
 *   node scripts/rollback.js apply <prefix>  ← 回滚到指定备份
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const PROJECT_DIR = 'C:\\Users\\VRPC01\\.qclaw\\workspace\\hotpulse';
const BACKUP_DIR  = path.join(PROJECT_DIR, 'backup');
const LOGS_DIR    = path.join(PROJECT_DIR, 'logs');

function log(msg, type = 'INFO') {
    const ts = new Date().toISOString().replace('T',' ').substring(0,19);
    const line = `[${ts}] [${type}] ${msg}`;
    console.log(line);
    if (!fs.existsSync(LOGS_DIR)) fs.mkdirSync(LOGS_DIR, { recursive: true });
    const logFile = path.join(LOGS_DIR, `rollback_${new Date().toISOString().substring(0,10).replace(/-/g,'')}.log`);
    fs.appendFileSync(logFile, line + '\n');
}

// ─── 列出所有备份 ──────────────────────────────────
function listBackups() {
    if (!fs.existsSync(BACKUP_DIR)) {
        log('backup/ 目录不存在', 'ERROR');
        return [];
    }
    const files = fs.readdirSync(BACKUP_DIR)
        .filter(f => f.startsWith('index_') && f.endsWith('.html'))
        .sort()
        .reverse(); // 最新的在前面

    if (files.length === 0) {
        log('没有找到任何备份', 'WARN');
        return [];
    }

    log(`找到 ${files.length} 个备份：`);
    files.forEach((f, i) => {
        const fpath = path.join(BACKUP_DIR, f);
        const size = fs.statSync(fpath).size;
        const mtime = fs.statSync(fpath).mtime.toISOString().substring(0,19).replace('T',' ');
        log(`  [${i+1}] ${f}  (${Math.round(size/1024)}KB, ${mtime})`);
    });
    return files;
}

// ─── 执行回滚 ──────────────────────────────────────
function doRollback(targetPrefix) {
    log('开始回滚...');
    log(`目标备份: ${targetPrefix}`);

    // 1. 验证备份文件存在
    const backupHtml = path.join(BACKUP_DIR, `index_${targetPrefix}.html`);
    const backupJson = path.join(BACKUP_DIR, `hotlist_${targetPrefix.split('_')[0]}.json`);

    if (!fs.existsSync(backupHtml)) {
        log(`备份文件不存在: ${backupHtml}`, 'ERROR');
        return { success: false, reason: 'backup_not_found' };
    }

    // 2. 验证备份文件大小（防止回滚到空文件）
    const backupSize = fs.statSync(backupHtml).size;
    if (backupSize < 20 * 1024) {
        log(`备份文件异常（仅 ${Math.round(backupSize/1024)}KB），拒绝回滚`, 'ERROR');
        return { success: false, reason: 'backup_too_small' };
    }
    log(`备份文件大小: ${Math.round(backupSize/1024)}KB ✓`);

    // 3. 备份当前版本（防止回滚后还需要恢复）
    const currentHtml = path.join(PROJECT_DIR, 'index.html');
    if (fs.existsSync(currentHtml)) {
        const preRollbackBackup = path.join(BACKUP_DIR, `index_pre_rollback_${Date.now()}.html`);
        fs.copyFileSync(currentHtml, preRollbackBackup);
        log(`当前版本已备份到: ${path.basename(preRollbackBackup)}`);
    }

    // 4. 执行回滚
    fs.copyFileSync(backupHtml, currentHtml);
    log(`✓ index.html 已回滚到备份: ${targetPrefix}`);

    // 5. 回滚 JSON（如果存在）
    if (fs.existsSync(backupJson)) {
        const currentJson = path.join(PROJECT_DIR, 'hotlist_100.json');
        fs.copyFileSync(backupJson, currentJson);
        log(`✓ hotlist_100.json 已回滚`);
    }

    // 6. 提交回滚
    try {
        execSync('git add index.html hotlist_100.json', { cwd: PROJECT_DIR, encoding: 'utf8' });
        const msg = `[回滚] 恢复到备份 ${targetPrefix}`;
        execSync(`git commit -m "${msg}"`, { cwd: PROJECT_DIR, encoding: 'utf8' });
        log(`✓ Git commit 完成: ${msg}`);

        // 尝试推送
        try {
            execSync('git push origin main', { cwd: PROJECT_DIR, encoding: 'utf8', timeout: 30000 });
            log(`✓ Git push 完成`);
        } catch(e) {
            log(`! Git push 失败，请手动执行: ${e.message}`, 'WARN');
        }
    } catch(e) {
        log(`! Git commit 失败: ${e.message}`, 'WARN');
    }

    return { success: true, prefix: targetPrefix, size: backupSize };
}

// ─── 主入口 ────────────────────────────────────────
function main() {
    const args = process.argv.slice(2);
    const cmd = args[0];

    if (cmd === 'list' || !cmd) {
        // 默认：列出备份，并回滚到最新的
        const files = listBackups();
        if (files.length > 0 && !cmd) {
            log('── 自动回滚到最新备份 ──────────────────');
            const prefix = files[0].replace('index_','').replace('.html','');
            return doRollback(prefix);
        }
        return { success: true, backups: files };
    }

    if (cmd === 'apply' && args[1]) {
        const prefix = args[1];
        return doRollback(prefix);
    }

    if (cmd === 'help' || cmd === '--help' || cmd === '-h') {
        console.log(`
回滚脚本使用说明：
  node scripts/rollback.js           ← 回滚到最新备份
  node scripts/rollback.js list      ← 列出所有备份
  node scripts/rollback.js apply <prefix>  ← 回滚到指定备份
  node scripts/rollback.js help      ← 显示帮助

示例：
  node scripts/rollback.js apply 20260628_080100
        `);
        return { success: true };
    }

    log(`未知命令: ${cmd}`, 'ERROR');
    return { success: false, reason: 'unknown_command' };
}

if (require.main === module) {
    const result = main();
    process.exit(result.success ? 0 : 1);
}

module.exports = { main, doRollback, listBackups };

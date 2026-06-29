# 🐷 猪小媒 · 运维标准操作规程（SOP）

> 版本：v1.0 | 建立日期：2026-06-29 | 维护者：龙虾（AI运营经理）
> 本文档是猪小媒热点数据每日更新的唯一权威操作依据。任何执行必须严格遵循本SOP。

---

## 一、每日更新标准流程（Pipeline）

```
[T-30min] 前置检查
    ↓
[T=0] 抓取数据（微博 + 百度）
    ↓
[数据验证] 数量≥80条 且 无明显异常
    ↓
[备份] 将当前 index.html 复制到 backup/
    ↓
[合并去重] 微博+百度去重 → 合并 → TOP100
    ↓
[写入] 更新 index.html + hotlist_100.json
    ↓
[验证] index.html 大小 ≥ 20KB
    ↓
[提交] Git add → commit → push
    ↓
[推送验证] 确认 GitHub 可见
    ↓
[部署验证] 确认 Vercel 部署成功
    ↓
[记录] 更新 task_record_YYYYMMDD.md
```

**每一步失败都必须停下来的「硬性规则」：**
- 抓取数据 < 30条 → 停止，使用昨日备份
- index.html 大小 < 20KB → 停止，拒绝提交
- Git push 失败 → 保留本地，重复push 3次，超时告警

---

## 二、数据源规范

| 平台 | API地址 | 最低要求 | 失败处理 |
|------|---------|---------|---------|
| 微博 | `https://api.52vmy.cn/api/wl/hot?type=weibo` | 30条 | 降级用昨日数据 |
| 百度 | `https://api.52vmy.cn/api/wl/hot?type=baidu` | 30条 | 降级用昨日数据 |
| B站 | `https://api.bilibili.com/x/web-interface/ranking/v2` | 10条 | 可选，跳过 |
| 知乎 | `https://api.52vmy.cn/api/wl/hot?type=zhihu` | 10条 | 可选，跳过 |

**数据有效性判断标准：**
- 每条数据必须有标题（word/title 字段）
- 热度值（hot/value）必须为正数
- 禁止使用编造数据填充数量

---

## 三、备份规范（强制）

**每次更新前必须执行备份，顺序不可颠倒。**

```
backup/
├── index_20260629_0812.html   ← 每次更新前的快照
├── index_20260628_0801.html
├── index_20260627_0803.html
└── hotlist_20260629.json     ← JSON备份（同步）
```

**保留策略：**
- 每日1份，保留最近 **30天**
- 每次备份自动清理超过30天的旧文件

---

## 四、Git工作流规范

### 4.1 提交信息格式
```
格式：[类型] 简短描述 日期

示例：
✨ 猪小媒热点更新 2026-06-29 全网TOP100热榜刷新
🔧 修复热榜显示异常
📝 更新配置文件
```

### 4.2 分支策略
- 只使用 `main` 分支，禁止直接 push 到其他分支
- 禁止 force push（除非重大故障恢复）

### 4.3 推送失败处理
```
第1次push失败 → 等10秒重试
第2次push失败 → 等30秒重试
第3次push失败 → 发送告警到主会话，保留本地
```

### 4.4 冲突处理
```
检测到远程有更新 → 自动 git pull --rebase
若发生冲突 → 保留本地版本（热点数据优先），强制推送
```

---

## 五、index.html 验证标准

在每次提交前，必须通过以下所有检查：

| 检查项 | 标准 | 不通过处理 |
|--------|------|----------|
| 文件大小 | ≥ 20KB | 停止并告警 |
| HTML结构完整性 | 包含 `<html>`, `</html>` 闭合 | 停止并告警 |
| 日期更新 | 包含当天日期字符串 | 停止并告警 |
| 热点条目数 | ≥ 80条 `<div class="hotlist-merged-item"` | 停止并告警 |
| JavaScript语法 | `node --check index.html` 通过 | 停止并告警 |

---

## 六、回滚机制

### 6.1 触发条件
- index.html 验证失败
- Git 推送连续3次失败
- Vercel 部署失败
- 发现数据严重异常（编造、过期超过48小时）

### 6.2 回滚步骤
```
1. 从 backup/ 目录找到最新的 .html 文件
2. 复制覆盖 index.html
3. 重新执行验证
4. 提交并推送（标记为 [回滚]）
5. 在 task_record 中记录回滚原因
```

### 6.3 紧急联系人
- 主要通知：主会话（WebChat）
- 失败次数 ≥ 3：需要人工介入

---

## 七、Cron任务管理规范

### 7.1 定时任务配置
- **执行时间**：每天 08:00（北京时间）
- **环境**：独立 isolated session
- **超时限制**：30分钟
- **重试策略**：失败自动重试1次

### 7.2 任务健康检查
每日检查项：
- [ ] 上一次执行是否成功
- [ ] GitHub 是否有最新 commit
- [ ] Vercel 部署状态是否正常
- [ ] index.html 是否包含当天日期

### 7.3 异常监控
```
连续失败2次 → 发送告警
连续失败5次 → 禁用任务，等待人工修复
```

---

## 八、部署与验证

### 8.1 部署流程
```
Git push 成功
    ↓
等待 Vercel webhook（约1-3分钟）
    ↓
访问 https://hotpulse-snowy.vercel.app 验证
    ↓
检查控制台无 JS Error
    ↓
确认日期显示为当天
```

### 8.2 验证检查清单
- [ ] 网站可访问（HTTP 200）
- [ ] 日期显示今天
- [ ] 热点列表 ≥ 80条
- [ ] 控制台无 Error 级别报错
- [ ] GitHub commit 时间戳正确

---

## 九、文件结构规范

```
hotpulse/
├── index.html              ← 主文件（始终保持有效）
├── hotlist_100.json        ← JSON备份
├── vercel.json             ← Vercel配置（无需修改）
├── README.md               ← 项目说明
│
├── backup/                 ← 【每日自动备份】
│   ├── index_YYYYMMDD_HHMM.html
│   └── hotlist_YYYYMMDD.json
│
├── docs/                   ← 文档
│   ├── 运维SOP.md          ← 本文档
│   └── CHANGELOG.md        ← 变更日志
│
├── scripts/                ← 自动化脚本
│   ├── run_update.js       ← 【主更新脚本】每日执行
│   ├── backup.js           ← 备份脚本
│   ├── verify.js           ← 验证脚本
│   ├── rollback.js         ← 回滚脚本
│   └── fetch_hot.js        ← 数据抓取
│
├── api/                    ← API代理（静态资源）
│
└── logs/                   ← 日志（每日生成）
    ├── run_20260629.log
    └── error_20260629.log
```

---

## 十、变更记录

| 日期 | 版本 | 变更内容 | 执行人 |
|------|------|---------|--------|
| 2026-06-29 | v1.0 | 初始建立SOP体系 | 龙虾 |

---

## 附录：快速命令参考

```bash
# 手动执行更新（生产环境）
node scripts/run_update.js

# 手动备份
node scripts/backup.js

# 验证当前状态
node scripts/verify.js

# 紧急回滚（最近一次备份）
node scripts/rollback.js

# 检查Git状态
git status
git log --oneline -5
```

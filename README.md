# HOTPULSE · 全网热点聚合 AI 分析工具

一个纯静态网页工具，粘贴各平台热榜内容，AI 自动完成去重、分类、评分、内容角度建议。

## 功能
- 支持国内外 9 大平台：微博、知乎、百度、B站、抖音、小红书、Twitter/X、Reddit、YouTube
- AI 自动识别话题、去重合并、按选题价值评分
- 每条热点附带内容创作角度建议
- 历史记录本地保存（localStorage，最多 20 条）
- 国内/国际/高分 快速筛选

## 部署到 Vercel（3 步）

### 方法一：直接上传（最简单）
1. 打开 [vercel.com](https://vercel.com) 注册/登录
2. 点击 **Add New → Project**
3. 选择 **「Deploy without a Git repository」** → 上传整个 `hotpulse` 文件夹
4. 点击 Deploy，完成！

### 方法二：通过 GitHub（推荐，后续可一键更新）
1. 在 GitHub 创建新仓库，上传这两个文件（`index.html` + `vercel.json`）
2. 打开 [vercel.com](https://vercel.com)，点击 **Add New → Project**
3. 选择刚创建的 GitHub 仓库，点击 Deploy
4. 后续修改 `index.html` 后 push 到 GitHub，Vercel 自动重新部署

## 本地使用
直接用浏览器打开 `index.html` 即可，无需服务器。

## 推荐数据源
| 平台 | 地址 |
|------|------|
| 国内综合（微博/知乎/B站等）| https://tophub.today |
| Twitter 实时趋势 | https://trends24.in/china/ |
| Reddit 热帖 | https://reddit.com/r/popular |
| YouTube 热门 | https://youtube.com/feed/trending |

## 技术栈
- 纯 HTML + CSS + JS，无任何依赖
- 调用 Anthropic Claude API 进行分析
- 历史记录存储在浏览器 localStorage

# 全网热点API可用性探测 - 龙虾 🦞
$ErrorActionPreference = "Continue"
$results = @()

function Test-HotAPI {
    param($Name, $Url, $Headers=@{})
    try {
        $r = Invoke-WebRequest -Uri $Url -Method Get -TimeoutSec 12 -Headers $Headers
        $results += "$Name|OK|$($r.StatusCode)|$Url"
        Write-Host "[OK]  $Name ($($r.StatusCode))" -ForegroundColor Green
        return $true
    } catch {
        $msg = $_.Exception.Message.Substring(0, [Math]::Min(80, $_.Exception.Message.Length))
        $results += "$Name|FAIL|$msg|$Url"
        Write-Host "[FAIL] $Name : $msg" -ForegroundColor Red
        return $false
    }
}

Write-Host "`n=== 全网热点API探测 ===" -ForegroundColor Cyan
Write-Host "`n[平台热榜]" -ForegroundColor Yellow
Test-HotAPI "微博热搜PC" "https://weibo.com/ajax/side/hotSearch"
Test-HotAPI "知乎热榜" "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=50"
Test-HotAPI "抖音热榜" "https://www.douyin.com/aweme/v1/web/hot/search/list/?aid=6383&count=20&offset=0&sort_type=0&pc_client_type=1&version_code=190400"
Test-HotAPI "小红书Feed" "https://edith.xiaohongshu.com/fe_api/burdock/v2/homefeed" @{"User-Agent"="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1";"Referer"="https://www.xiaohongshu.com/"}

Write-Host "`n[网媒/资讯]" -ForegroundColor Yellow
Test-HotAPI "腾讯新闻" "https://news.qq.com/headline/j.htm"
Test-HotAPI "网易新闻" "https://news.163.com/rank/"
Test-HotAPI "新浪新闻" "https://news.sina.com.cn/"
Test-HotAPI "搜狐新闻" "https://news.sohu.com/"

Write-Host "`n[搜索引擎热点]" -ForegroundColor Yellow
Test-HotAPI "百度热搜" "https://top.baidu.com/board?tab=realtime"
Test-HotAPI "360热搜" "https://top.so.com/?src=input&user=search"

Write-Host "`n[其他平台]" -ForegroundColor Yellow
Test-HotAPI "快手" "https://www.kuaishou.com/feed/index?countryCode=cn"
Test-HotAPI "贴吧热榜" "https://tieba.baidu.com/hottopic/browse/topicList"
Test-HotAPI "虎扑热榜" "https://apinew.hupu.com/topics"

Write-Host "`n[聚合站点]" -ForegroundColor Yellow
Test-HotAPI "今日热榜" "https://tophub.today/"
Test-HotAPI "AnyKnew" "https://www.36kr.com/"

Write-Host "`n=== 探测完成 ===" -ForegroundColor Cyan
Write-Host $results | Out-String
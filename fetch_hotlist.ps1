# 猪小媒热点数据抓取脚本（使用可用API）
# 作者：龙虾 🦞

Write-Host "🚀 开始抓取热点数据..." -ForegroundColor Cyan

$hotlist = @()

# ========== 1. B站热门视频 ==========
Write-Host "📡 正在抓取B站热门..." -ForegroundColor Yellow

try {
    $bilibiliUrl = "https://api.bilibili.com/x/web-interface/popular?ps=50&pn=1"
    $response = Invoke-RestMethod -Uri $bilibiliUrl -Method Get -TimeoutSec 15
    
    if ($response.code -eq 0) {
        foreach ($video in $response.data.list) {
            $hotlist += [PSCustomObject]@{
                Rank = $hotlist.Count + 1


                Title = $video.title
                Platform = "B站"
                Heat = $video.stat.view


                Url = "https://www.bilibili.com/video/av$($video.aid)"
                Category = $video.tname


            }
        }
        Write-Host "✅ B站：成功获取$($response.data.list.Count)条" -ForegroundColor Green


    }
} catch {
    Write-Host "❌ B站抓取失败：$($_.Exception.Message)" -ForegroundColor Red


}

# ... rest of the script continues
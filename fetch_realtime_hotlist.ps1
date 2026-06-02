# 猪小媒实时热点抓取脚本（使用可用API）
# 作者：龙虾 🦞 | 2026-06-02

Write-Host "==========================================" -ForegroundColor Cyan


Write-Host "🚀 猪小媒热点数据抓取开始..." -ForegroundColor Green


Write-Host "⏰ $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Yellow


Write-Host "==========================================" -ForegroundColor Cyan



$allHotItems = @()



# ========== 数据源1：B站热门视频 ==========


Write-Host "`n📡 [1/2] 正在抓取B站热门视频..." -ForegroundColor Cyan



try {


    $bilibiliUrl = "https://api.bilibili.com/x/web-interface/popular?ps=50&pn=1"


    $response = Invoke-RestMethod -Uri $bilibiliUrl -Method Get -TimeoutSec 20
    
    if ($response.code -eq 0) {
        $count = 0
        
        foreach ($video in $response.data.list) {
            $count++
            
            $allHotItems += [PSCustomObject]@{
                Rank = $count


                Title = $video.title
                Platform = "B站"
                Heat = [long]$video.stat.view


                Url = "https://www.bilibili.com/video/BV$($video.bvid)"
                Category = $video.tname
                Author = $video.owner.name
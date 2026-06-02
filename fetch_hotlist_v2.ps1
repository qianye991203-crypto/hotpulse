# 猪小媒实时热点抓取脚本（完整版）
# 作者：龙虾 🦞 | 2026-06-02

param(
    [int]$TopN = 100


)

$ErrorActionPreference = "Stop"
$allItems = @()

Write-Host "`n========================================" -ForegroundColor Cyan


Write-Host "🚀 猪小媒热点数据抓取（实时版）" -ForegroundColor Green


Write-Host "⏰ $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Yellow


Write-Host "========================================`n" -ForegroundColor Cyan



# ========== 数据源1：B站热门视频 ==========


Write-Host "[1/2] 正在抓取B站热门..." -ForegroundColor Cyan



try {


    $url = "https://api.bilibili.com/x/web-interface/popular?ps=50&pn=1"


    $resp = Invoke-RestMethod -Uri $url -Method Get -TimeoutSec 20
    
    if ($resp.code -eq ) {
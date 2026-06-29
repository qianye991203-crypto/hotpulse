$token = (gh auth token)
$b64 = [System.IO.File]::ReadAllText("$env:TEMP\index_b64.txt")
$body = @{
    message = "猪小媒热点更新 2026-06-28 08:00: 全网TOP100热榜数据刷新"
    content = $b64
    sha = "33886ae4abbb35ec72fb869230904845d64647b6"
}
$json = $body | ConvertTo-Json -Compress -Depth 3
$headers = @{
    Authorization = "Bearer $token"
    "Content-Type" = "application/json"
}
try {
    $resp = Invoke-RestMethod -Uri "https://api.github.com/repos/qianye991203-crypto/hotpulse/contents/index.html" -Method PUT -Headers $headers -Body ([System.Text.Encoding]::UTF8.GetBytes($json)) -TimeoutSec 30
    Write-Host "SUCCESS - Commit SHA: $($resp.commit.sha)"
} catch {
    Write-Host "FAILED: $($_.Exception.Message)"
}

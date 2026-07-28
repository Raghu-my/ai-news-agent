# run_live_cycle.ps1
# Script to launch Uvicorn and execute the first live autonomous cycle

# Refresh Environment PATH from System & User registry for FFmpeg
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " EXECUTING FIRST LIVE AUTONOMOUS CYCLE" -ForegroundColor Cyan
Write-Host "==========================================================`n" -ForegroundColor Cyan

# Start Uvicorn background process on port 8000
Write-Host "[1/3] Starting FastAPI server on port 8000..." -ForegroundColor Yellow
$proc = Start-Process -FilePath ".\venv\Scripts\python.exe" -ArgumentList "-m uvicorn main:app --port 8000" -PassThru -NoNewWindow
Start-Sleep -Seconds 5

try {
    Write-Host "[2/3] Sending POST /agent/run-cycle request..." -ForegroundColor Yellow
    $body = @{ topic = "The rise of autonomous AI coding agents" } | ConvertTo-Json

    $res = Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/agent/run-cycle" -ContentType "application/json" -Body $body -TimeoutSec 120

    Write-Host "`n[3/3] Autonomous Master Pipeline Execution Complete!" -ForegroundColor Green
    Write-Host "----------------------------------------------------------" -ForegroundColor Gray
    Write-Host "Record UUID  : $($res.video_id)" -ForegroundColor White
    Write-Host "Topic        : $($res.topic)" -ForegroundColor White
    Write-Host "Script       : `"$($res.script)`"" -ForegroundColor White
    Write-Host "Audio GCS    : $($res.audio_gcs_uri)" -ForegroundColor White
    Write-Host "Video GCS    : $($res.video_gcs_uri)" -ForegroundColor White
    Write-Host "DB Status    : $($res.status)" -ForegroundColor Green
    Write-Host "YouTube URL  : $($res.youtube_url)" -ForegroundColor Cyan
    Write-Host "----------------------------------------------------------`n" -ForegroundColor Gray

    # Output JSON to file for verification summary
    $res | ConvertTo-Json | Out-File -FilePath "last_cycle_result.json" -Encoding utf8
} catch {
    Write-Host "ERROR executing cycle: $_" -ForegroundColor Red
} finally {
    if ($proc -and -not $proc.HasExited) {
        Stop-Process -Id $proc.Id -Force
        Write-Host "Cleaned up FastAPI background process." -ForegroundColor Gray
    }
}

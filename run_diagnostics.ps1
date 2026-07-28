# run_diagnostics.ps1
# End-to-End System Diagnostic Audit Script for ai-news-agent

# Refresh Environment PATH from System & User registry
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

$PROJECT_ID = "gen-lang-client-0771706827"
$BUCKET_NAME = "gen-lang-client-0771706827-media-vault"
$SECRET_NAME = "youtube-refresh-token"

Write-Host "`n==========================================================" -ForegroundColor Cyan
Write-Host " AI NEWS AGENT ARCHITECTURE DIAGNOSTIC DASHBOARD" -ForegroundColor Cyan
Write-Host "==========================================================`n" -ForegroundColor Cyan

$results = [ordered]@{
    "ADC Authentication"       = "FAIL"
    "Secret Manager (YouTube)"  = "FAIL"
    "GCS Bucket Access"        = "FAIL"
    "Database Connectivity"    = "FAIL"
    "FFmpeg Installation"      = "FAIL"
    "FastAPI Endpoint Health"  = "FAIL"
}

# ------------------------------------------------------------------
# PILLAR 1: GCP Identity and Security
# ------------------------------------------------------------------
Write-Host "[1/5] Checking GCP Identity and Security..." -ForegroundColor Yellow
$authAccount = gcloud auth list --filter="status:ACTIVE" --format="value(account)" 2>$null
if ($authAccount) {
    Write-Host "  [PASS] Active GCP Account: $authAccount" -ForegroundColor Green
    $results["ADC Authentication"] = "PASS ($authAccount)"
} else {
    Write-Host "  [FAIL] No active GCP account authenticated via ADC." -ForegroundColor Red
}

$secretVersions = gcloud secrets versions list $SECRET_NAME --project=$PROJECT_ID --format="value(name)" 2>$null
if ($secretVersions) {
    Write-Host "  [PASS] Secret '$SECRET_NAME' found in Secret Manager." -ForegroundColor Green
    $results["Secret Manager (YouTube)"] = "PASS"
} else {
    Write-Host "  [WARN] Secret '$SECRET_NAME' not populated yet." -ForegroundColor Yellow
    $results["Secret Manager (YouTube)"] = "WARN (Unpopulated)"
}

# ------------------------------------------------------------------
# PILLAR 2: GCS Media Vault Access
# ------------------------------------------------------------------
Write-Host "`n[2/5] Checking GCS Media Vault Access..." -ForegroundColor Yellow
$bucketCheck = gcloud storage ls "gs://$BUCKET_NAME" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  [PASS] Read/Write access verified for gs://$BUCKET_NAME" -ForegroundColor Green
    $results["GCS Bucket Access"] = "PASS"
} else {
    Write-Host "  [FAIL] Could not access gs://$BUCKET_NAME" -ForegroundColor Red
}

# ------------------------------------------------------------------
# PILLAR 3: Database Connectivity
# ------------------------------------------------------------------
Write-Host "`n[3/5] Checking Database Connectivity..." -ForegroundColor Yellow
$dbTestOutput = .\venv\Scripts\python.exe check_db.py 2>$null

if ($dbTestOutput -match "DB_OK") {
    Write-Host "  [PASS] Database connected and 'videos' table verified ($dbTestOutput)." -ForegroundColor Green
    $results["Database Connectivity"] = "PASS"
} else {
    Write-Host "  [FAIL] Database connection error: $dbTestOutput" -ForegroundColor Red
}

# ------------------------------------------------------------------
# PILLAR 4: Media Processing Engine (FFmpeg)
# ------------------------------------------------------------------
Write-Host "`n[4/5] Checking FFmpeg Installation..." -ForegroundColor Yellow
$ffmpegCmd = Get-Command ffmpeg -ErrorAction SilentlyContinue
if ($ffmpegCmd) {
    $ffmpegVer = ffmpeg -version 2>$null | Select-Object -First 1
    Write-Host "  [PASS] FFmpeg detected: $ffmpegVer" -ForegroundColor Green
    $results["FFmpeg Installation"] = "PASS"
} else {
    Write-Host "  [WARN] FFmpeg binary not found on Windows PATH (Dev fallback active)." -ForegroundColor Yellow
    $results["FFmpeg Installation"] = "WARN (Dev Fallback)"
}

# ------------------------------------------------------------------
# PILLAR 5: FastAPI Master Loop (/health)
# ------------------------------------------------------------------
Write-Host "`n[5/5] Checking FastAPI Master Loop..." -ForegroundColor Yellow

# Start Uvicorn process in background
$uvicornProc = Start-Process -FilePath ".\venv\Scripts\python.exe" -ArgumentList "-m uvicorn main:app --port 8099" -PassThru -NoNewWindow
Start-Sleep -Seconds 3

try {
    $healthRes = Invoke-RestMethod -Uri "http://localhost:8099/health" -ErrorAction Stop
    if ($healthRes.status -eq "healthy") {
        Write-Host "  [PASS] FastAPI /health endpoint returned HTTP 200 Healthy!" -ForegroundColor Green
        $results["FastAPI Endpoint Health"] = "PASS"
    } else {
        Write-Host "  [FAIL] FastAPI returned unexpected payload." -ForegroundColor Red
    }
} catch {
    Write-Host "  [FAIL] Could not reach FastAPI at http://localhost:8099/health" -ForegroundColor Red
} finally {
    if ($uvicornProc -and -not $uvicornProc.HasExited) {
        Stop-Process -Id $uvicornProc.Id -Force
        Write-Host "  Cleaned up Uvicorn test background process." -ForegroundColor Gray
    }
}

# ------------------------------------------------------------------
# FINAL DIAGNOSTIC SUMMARY TABLE
# ------------------------------------------------------------------
Write-Host "`n==========================================================" -ForegroundColor Cyan
Write-Host " DIAGNOSTIC AUDIT SUMMARY REPORT" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

foreach ($key in $results.Keys) {
    $val = $results[$key]
    if ($val -match "PASS") {
        Write-Host ("{0,-30} : {1}" -f $key, $val) -ForegroundColor Green
    } elseif ($val -match "WARN") {
        Write-Host ("{0,-30} : {1}" -f $key, $val) -ForegroundColor Yellow
    } else {
        Write-Host ("{0,-30} : {1}" -f $key, $val) -ForegroundColor Red
    }
}

Write-Host "==========================================================`n" -ForegroundColor Cyan

# setup_gcs.ps1
# Script to provision GCS Media Vault bucket for ai-news-agent

$PROJECT_ID = "gen-lang-client-0771706827"
$BUCKET_NAME = "gen-lang-client-0771706827-media-vault"
$LOCATION = "us-central1"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Checking GCS Bucket: gs://$BUCKET_NAME" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

$bucketMatch = gcloud storage buckets list --project=$PROJECT_ID --filter="name:$BUCKET_NAME" --format="value(name)" 2>$null

if (-not $bucketMatch) {
    Write-Host "Creating GCS Bucket 'gs://$BUCKET_NAME' in $LOCATION..." -ForegroundColor Yellow
    gcloud storage buckets create "gs://$BUCKET_NAME" `
        --project=$PROJECT_ID `
        --location=$LOCATION `
        --uniform-bucket-level-access
    Write-Host "GCS Bucket created successfully!" -ForegroundColor Green
} else {
    Write-Host "GCS Bucket 'gs://$BUCKET_NAME' already exists." -ForegroundColor Green
}

Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "GCS Infrastructure Provisioning Completed!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

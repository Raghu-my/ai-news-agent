# setup_gcp_env.ps1
# Script to setup GCP environment & Workload Identity Federation for ai-news-agent project

$PROJECT_ID = "gen-lang-client-0771706827"
$POOL_NAME = "github-actions-pool"
$PROVIDER_NAME = "github-provider"
$REPO_NAME = "Raghu-my/ai-news-agent"
$SA_NAME = "github-actions-sa"
$SA_EMAIL = "$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Setting GCP Project context: $PROJECT_ID" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
gcloud config set project $PROJECT_ID

Write-Host "`nEnabling required GCP APIs..." -ForegroundColor Cyan
$apis = @(
    "aiplatform.googleapis.com",
    "texttospeech.googleapis.com",
    "run.googleapis.com",
    "storage.googleapis.com",
    "iamcredentials.googleapis.com",
    "artifactregistry.googleapis.com"
)
try {
    gcloud services enable $apis --project=$PROJECT_ID
} catch {
    Write-Host "Note: Enabling APIs requires Service Usage Admin or Project Editor roles on project '$PROJECT_ID'." -ForegroundColor Yellow
}

Write-Host "`nChecking Workload Identity Pool: $POOL_NAME..." -ForegroundColor Cyan
$pools = gcloud iam workload-identity-pools list --location="global" --project=$PROJECT_ID --format="value(name)" 2>$null

if (-not ($pools -match $POOL_NAME)) {
    Write-Host "Creating Workload Identity Pool '$POOL_NAME'..." -ForegroundColor Yellow
    gcloud iam workload-identity-pools create $POOL_NAME `
        --location="global" `
        --display-name="GitHub Actions Pool" `
        --description="Workload Identity Pool for GitHub Actions CI/CD" `
        --project=$PROJECT_ID
} else {
    Write-Host "Workload Identity Pool '$POOL_NAME' already exists." -ForegroundColor Green
}

Write-Host "`nChecking Workload Identity Provider: $PROVIDER_NAME..." -ForegroundColor Cyan
$providers = gcloud iam workload-identity-pools providers list `
    --workload-identity-pool=$POOL_NAME `
    --location="global" `
    --project=$PROJECT_ID `
    --format="value(name)" 2>$null

if (-not ($providers -match $PROVIDER_NAME)) {
    Write-Host "Creating OIDC Workload Identity Provider '$PROVIDER_NAME'..." -ForegroundColor Yellow
    gcloud iam workload-identity-pools providers create-oidc $PROVIDER_NAME `
        --workload-identity-pool=$POOL_NAME `
        --location="global" `
        --display-name="GitHub Provider" `
        --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" `
        --attribute-condition="assertion.repository == '$REPO_NAME'" `
        --issuer-uri="https://token.actions.githubusercontent.com" `
        --project=$PROJECT_ID
} else {
    Write-Host "Workload Identity Provider '$PROVIDER_NAME' already exists." -ForegroundColor Green
}

Write-Host "`nChecking Service Account: $SA_EMAIL..." -ForegroundColor Cyan
$saExists = gcloud iam service-accounts list --project=$PROJECT_ID --filter="email:$SA_EMAIL" --format="value(email)" 2>$null

if (-not $saExists) {
    Write-Host "Creating Service Account '$SA_NAME'..." -ForegroundColor Yellow
    gcloud iam service-accounts create $SA_NAME `
        --display-name="GitHub Actions CI/CD Service Account" `
        --project=$PROJECT_ID
} else {
    Write-Host "Service Account '$SA_EMAIL' already exists." -ForegroundColor Green
}

Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "GCP Infrastructure Setup Completed Successfully!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

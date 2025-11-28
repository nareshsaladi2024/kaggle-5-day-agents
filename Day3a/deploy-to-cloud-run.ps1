<#
.SYNOPSIS
    Deploys Day3a session agents to Google Cloud Run

.DESCRIPTION
    Builds and deploys session management agents to Cloud Run

.PARAMETER ProjectId
    Google Cloud Project ID

.PARAMETER Region
    Google Cloud region (default: us-central1)

.PARAMETER Agent
    Which agent to deploy: session_agent, compaction_agent, or basic_session_agent

.EXAMPLE
    .\deploy-to-cloud-run.ps1 -ProjectId "my-project" -Agent session_agent
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectId,
    
    [string]$Region = "us-central1",
    
    [ValidateSet('session_agent', 'compaction_agent', 'basic_session_agent')]
    [string]$Agent = 'session_agent'
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Day3a Session Agents - Cloud Run" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] gcloud CLI not found" -ForegroundColor Red
    exit 1
}

try {
    docker version | Out-Null
} catch {
    Write-Host "[ERROR] Docker not running" -ForegroundColor Red
    exit 1
}

Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  Project: $ProjectId" -ForegroundColor White
Write-Host "  Region: $Region" -ForegroundColor White
Write-Host "  Agent: $Agent" -ForegroundColor White
Write-Host ""

# Set project
gcloud config set project $ProjectId

# Enable APIs
Write-Host "Enabling required APIs..." -ForegroundColor Cyan
gcloud services enable cloudbuild.googleapis.com run.googleapis.com --project $ProjectId

# Build image
$imageName = "gcr.io/$ProjectId/day3a-$Agent:latest"
Write-Host "Building image: $imageName" -ForegroundColor Cyan

# Build from parent directory to include utility
$parentDir = Split-Path -Parent $ScriptDir
Set-Location $parentDir

# Create a temporary Dockerfile in parent directory for Cloud Build
$cloudDockerfile = Join-Path $parentDir "Day3a.Dockerfile"
Copy-Item "Day3a/Dockerfile.build" $cloudDockerfile

# Build using Cloud Build
gcloud builds submit --tag $imageName --file Day3a.Dockerfile --project $ProjectId

# Cleanup
Remove-Item $cloudDockerfile -ErrorAction SilentlyContinue

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Build failed" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Image built" -ForegroundColor Green

# Prepare environment variables
$envVars = @()
if ($env:GOOGLE_API_KEY) {
    $envVars += "--set-env-vars", "GOOGLE_API_KEY=$($env:GOOGLE_API_KEY)"
}
if ($env:GOOGLE_CLOUD_PROJECT) {
    $envVars += "--set-env-vars", "GOOGLE_CLOUD_PROJECT=$($env:GOOGLE_CLOUD_PROJECT)"
}

# Deploy to Cloud Run
$serviceName = "day3a-$Agent"
Write-Host "Deploying to Cloud Run..." -ForegroundColor Cyan

$deployArgs = @(
    "run", "deploy", $serviceName,
    "--image", $imageName,
    "--platform", "managed",
    "--region", $Region,
    "--allow-unauthenticated",
    "--project", $ProjectId
) + $envVars

gcloud @deployArgs

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Deployed successfully" -ForegroundColor Green
    
    $serviceUrl = gcloud run services describe $serviceName --region $Region --format="value(status.url)" --project $ProjectId
    Write-Host "Service URL: $serviceUrl" -ForegroundColor Cyan
} else {
    Write-Host "[ERROR] Deployment failed" -ForegroundColor Red
    exit 1
}

Write-Host ""


<#
.SYNOPSIS
    Deploy kaggle-5-day-agents to Google Cloud Run

.DESCRIPTION
    Builds Docker images and deploys agents to Cloud Run.
    Uses the existing Dockerfile and docker-compose configuration.

.PARAMETER ProjectId
    Google Cloud Project ID (default: from .env or aiagent-capstoneproject)

.PARAMETER Region
    Cloud Run region (default: us-central1)

.PARAMETER Service
    Specific service to deploy (optional, deploys all if not specified)

.EXAMPLE
    .\deploy-to-cloud-run.ps1

.EXAMPLE
    .\deploy-to-cloud-run.ps1 -ProjectId "my-project" -Region "us-central1"
#>

param(
    [string]$ProjectId = "",
    [string]$Region = "us-central1",
    [string]$Service = ""
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deploy to Google Cloud Run" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Load .env file if exists
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
}

# Get project ID
if ([string]::IsNullOrEmpty($ProjectId)) {
    $ProjectId = $env:GOOGLE_CLOUD_PROJECT
    if ([string]::IsNullOrEmpty($ProjectId)) {
        $ProjectId = "aiagent-capstoneproject"
    }
}

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Cyan

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

Write-Host "[OK] Prerequisites met" -ForegroundColor Green
Write-Host ""
Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  Project: $ProjectId" -ForegroundColor White
Write-Host "  Region: $Region" -ForegroundColor White
Write-Host ""

# Set project
gcloud config set project $ProjectId

# Enable APIs
Write-Host "Enabling required APIs..." -ForegroundColor Cyan
gcloud services enable cloudbuild.googleapis.com --project $ProjectId
gcloud services enable run.googleapis.com --project $ProjectId
gcloud services enable artifactregistry.googleapis.com --project $ProjectId

# Build Docker image
$imageName = "gcr.io/$ProjectId/kaggle-5-day-agents:latest"
Write-Host "Building Docker image..." -ForegroundColor Cyan
Write-Host "  Image: $imageName" -ForegroundColor Gray

gcloud builds submit --tag $imageName --project $ProjectId

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Build failed" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Image built successfully" -ForegroundColor Green
Write-Host ""

# Prepare environment variables from .env
$envVars = @()
if ($env:GOOGLE_API_KEY) {
    $envVars += "--set-env-vars", "GOOGLE_API_KEY=$($env:GOOGLE_API_KEY)"
}
if ($env:GOOGLE_CLOUD_PROJECT) {
    $envVars += "--set-env-vars", "GOOGLE_CLOUD_PROJECT=$($env:GOOGLE_CLOUD_PROJECT)"
}
if ($env:GOOGLE_CLOUD_LOCATION) {
    $envVars += "--set-env-vars", "GOOGLE_CLOUD_LOCATION=$($env:GOOGLE_CLOUD_LOCATION)"
}
if ($env:GOOGLE_GENAI_USE_VERTEXAI) {
    $envVars += "--set-env-vars", "GOOGLE_GENAI_USE_VERTEXAI=$($env:GOOGLE_GENAI_USE_VERTEXAI)"
}
if ($env:ADK_LOG_LEVEL) {
    $envVars += "--set-env-vars", "ADK_LOG_LEVEL=$($env:ADK_LOG_LEVEL)"
}

# Deploy to Cloud Run
$serviceName = "kaggle-5-day-agents"
Write-Host "Deploying to Cloud Run..." -ForegroundColor Cyan
Write-Host "  Service: $serviceName" -ForegroundColor Gray

$deployArgs = @(
    "run", "deploy", $serviceName,
    "--image", $imageName,
    "--platform", "managed",
    "--region", $Region,
    "--allow-unauthenticated",
    "--port", "8080",
    "--memory", "2Gi",
    "--cpu", "2",
    "--timeout", "300",
    "--max-instances", "10",
    "--project", $ProjectId
) + $envVars

gcloud @deployArgs

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[OK] Deployed successfully" -ForegroundColor Green
    Write-Host ""
    
    $serviceUrl = gcloud run services describe $serviceName --region $Region --format="value(status.url)" --project $ProjectId
    Write-Host "Service URL: $serviceUrl" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "ADK Web UI: $serviceUrl" -ForegroundColor Green
    Write-Host ""
    Write-Host "View in console:" -ForegroundColor Cyan
    Write-Host "  https://console.cloud.google.com/run/detail/$Region/$serviceName?project=$ProjectId" -ForegroundColor White
} else {
    Write-Host "[ERROR] Deployment failed" -ForegroundColor Red
    exit 1
}

Write-Host ""


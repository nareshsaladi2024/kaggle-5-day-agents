<#
.SYNOPSIS
    Deploy ADK Agents API Server to Google Cloud Run

.DESCRIPTION
    Builds and deploys the agents-api-server.py FastAPI server to Cloud Run.
    This exposes all agents from the agents/ directory as a REST API.

.PARAMETER ProjectId
    Google Cloud Project ID (default: from .env or aiagent-capstoneproject)

.PARAMETER Region
    Cloud Run region (default: us-central1)

.PARAMETER ServiceName
    Cloud Run service name (default: adk-agents-api)

.EXAMPLE
    .\deploy-agents-api-to-cloud-run.ps1

.EXAMPLE
    .\deploy-agents-api-to-cloud-run.ps1 -ProjectId "my-project" -Region "us-west1"
#>

param(
    [string]$ProjectId = "",
    [string]$Region = "us-central1",
    [string]$ServiceName = "adk-agents-api"
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deploy Agents API to Cloud Run" -ForegroundColor Cyan
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
    })
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

# Check if Docker is available (for local build)
$dockerAvailable = Get-Command docker -ErrorAction SilentlyContinue

Write-Host "[OK] Prerequisites met" -ForegroundColor Green
Write-Host ""
Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  Project: $ProjectId" -ForegroundColor White
Write-Host "  Region: $Region" -ForegroundColor White
Write-Host "  Service: $ServiceName" -ForegroundColor White
Write-Host ""

# Set project
gcloud config set project $ProjectId

# Enable APIs
Write-Host "Enabling required APIs..." -ForegroundColor Cyan
gcloud services enable run.googleapis.com --project $ProjectId
gcloud services enable cloudbuild.googleapis.com --project $ProjectId
gcloud services enable artifactregistry.googleapis.com --project $ProjectId

# Create Dockerfile for Cloud Run if it doesn't exist
$dockerfilePath = Join-Path $ScriptDir "Dockerfile.api"
if (-not (Test-Path $dockerfilePath)) {
    Write-Host "Creating Dockerfile for API server..." -ForegroundColor Cyan
    
    $dockerfileContent = @"
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

# Copy project files
COPY . .

# Copy agents directory
COPY agents/ ./agents/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Expose port
EXPOSE 8080

# Run the API server
CMD ["python", "agents-api-server.py"]
"@
    
    Set-Content -Path $dockerfilePath -Value $dockerfileContent
    Write-Host "[OK] Created Dockerfile.api" -ForegroundColor Green
}

# Build and deploy using Cloud Build
Write-Host "Building and deploying to Cloud Run..." -ForegroundColor Cyan
Write-Host ""

$imageName = "gcr.io/$ProjectId/$ServiceName"
$buildCmd = "gcloud builds submit --tag $imageName --dockerfile Dockerfile.api --project $ProjectId"

Write-Host "Running: $buildCmd" -ForegroundColor Gray
Write-Host ""

try {
    Invoke-Expression $buildCmd
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Build failed" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "[OK] Build successful" -ForegroundColor Green
    Write-Host ""
    
    # Deploy to Cloud Run
    Write-Host "Deploying to Cloud Run..." -ForegroundColor Cyan
    
    # Get environment variables from .env file
    $envVars = @()
    if (Test-Path ".env") {
        Get-Content ".env" | ForEach-Object {
            if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
                $name = $matches[1].Trim()
                $value = $matches[2].Trim()
                if ($name -notmatch "^(GOOGLE_APPLICATION_CREDENTIALS|PATH)$") {
                    $envVars += "$name=$value"
                }
            }
        })
    }
    
    $deployCmd = "gcloud run deploy $ServiceName " +
                 "--image $imageName " +
                 "--platform managed " +
                 "--region $Region " +
                 "--allow-unauthenticated " +
                 "--port 8080 " +
                 "--memory 2Gi " +
                 "--cpu 2 " +
                 "--timeout 300 " +
                 "--max-instances 10 " +
                 "--project $ProjectId"
    
    if ($envVars.Count -gt 0) {
        $deployCmd += " --set-env-vars " + ($envVars -join ",")
    }
    
    Write-Host "Running: $deployCmd" -ForegroundColor Gray
    Write-Host ""
    
    Invoke-Expression $deployCmd
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "[OK] Deployment successful!" -ForegroundColor Green
        Write-Host ""
        
        # Get service URL
        $serviceUrl = gcloud run services describe $ServiceName --region $Region --project $ProjectId --format="value(status.url)" 2>&1
        
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "Deployment Complete" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Service URL: $serviceUrl" -ForegroundColor Green
        Write-Host ""
        Write-Host "API Endpoints:" -ForegroundColor Cyan
        Write-Host "  Health: $serviceUrl/" -ForegroundColor White
        Write-Host "  Chat: $serviceUrl/chat" -ForegroundColor White
        Write-Host "  Agents: $serviceUrl/agents" -ForegroundColor White
        Write-Host "  Docs: $serviceUrl/docs" -ForegroundColor White
        Write-Host ""
        Write-Host "Use this URL in ChatGPT Custom GPT Actions:" -ForegroundColor Yellow
        Write-Host "  Update openapi.yaml server URL to: $serviceUrl" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host "[ERROR] Deployment failed" -ForegroundColor Red
        exit 1
    }
    
} catch {
    Write-Host "[ERROR] Deployment error: $_" -ForegroundColor Red
    exit 1
}

Write-Host "View service in console:" -ForegroundColor Cyan
Write-Host "  https://console.cloud.google.com/run/detail/$Region/$ServiceName?project=$ProjectId" -ForegroundColor White
Write-Host ""


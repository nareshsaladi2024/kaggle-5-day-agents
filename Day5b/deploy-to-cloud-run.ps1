<#
.SYNOPSIS
    Deploy WeatherAssistant agent to Google Cloud Run

.DESCRIPTION
    Builds and deploys the WeatherAssistant agent to Cloud Run as a REST API service.

.PARAMETER ProjectId
    Google Cloud Project ID (default: from .env or aiagent-capstoneproject)

.PARAMETER Region
    Cloud Run region (default: us-central1)

.PARAMETER ServiceName
    Cloud Run service name (default: weather-assistant)

.EXAMPLE
    .\deploy-to-cloud-run.ps1

.EXAMPLE
    .\deploy-to-cloud-run.ps1 -ProjectId "my-project" -Region "us-west1"
#>

param(
    [string]$ProjectId = "",
    [string]$Region = "us-central1",
    [string]$ServiceName = "weather-assistant"
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deploy WeatherAssistant to Cloud Run" -ForegroundColor Cyan
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
gcloud services enable run.googleapis.com --project $ProjectId 2>&1 | Out-Null
gcloud services enable cloudbuild.googleapis.com --project $ProjectId 2>&1 | Out-Null
gcloud services enable artifactregistry.googleapis.com --project $ProjectId 2>&1 | Out-Null

# Create Dockerfile if it doesn't exist
$dockerfilePath = Join-Path $ScriptDir "Dockerfile"
if (-not (Test-Path $dockerfilePath)) {
    Write-Host "Creating Dockerfile..." -ForegroundColor Cyan
    
    $dockerfileContent = @"
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY WeatherAssistant/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dependencies for API server
RUN pip install --no-cache-dir fastapi uvicorn python-multipart python-dotenv

# Copy agent files
COPY WeatherAssistant/ ./WeatherAssistant/

# Copy API server
COPY weather-assistant-api.py .

# Note: utility/ is optional - agent handles ImportError gracefully

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Run the API server
CMD ["python", "weather-assistant-api.py"]
"@
    
    Set-Content -Path $dockerfilePath -Value $dockerfileContent
    Write-Host "[OK] Created Dockerfile" -ForegroundColor Green
}

# Build and deploy using Cloud Build
Write-Host "Building and deploying to Cloud Run..." -ForegroundColor Cyan
Write-Host ""

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

# Verify required files exist before deployment
Write-Host "Verifying required files..." -ForegroundColor Cyan
$requiredFiles = @(
    "weather-assistant-api.py",
    "WeatherAssistant/agent.py",
    "WeatherAssistant/requirements.txt",
    "Dockerfile"
)

$missingFiles = @()
foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host "[ERROR] Missing required files:" -ForegroundColor Red
    foreach ($file in $missingFiles) {
        Write-Host "  - $file" -ForegroundColor Red
    }
    exit 1
}

Write-Host "[OK] All required files found" -ForegroundColor Green
Write-Host ""

# Build Docker image first, then deploy (more reliable than --source)
Write-Host "Building Docker image..." -ForegroundColor Cyan

# Use Cloud Build to build the image
# Build context is current directory (Day5b), Dockerfile is in same directory
$imageName = "gcr.io/$ProjectId/$ServiceName"
$buildCmd = "gcloud builds submit --tag $imageName --dockerfile Dockerfile . --project $ProjectId"

Write-Host "Running: $buildCmd" -ForegroundColor Gray
Write-Host "  Build context: . (Day5b directory)" -ForegroundColor Gray
Write-Host "  Dockerfile: Dockerfile" -ForegroundColor Gray
Write-Host ""

try {
    Invoke-Expression $buildCmd
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Docker build failed" -ForegroundColor Red
        Write-Host "Check the build logs above for details." -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host "[OK] Image built successfully: $imageName" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "[ERROR] Build error: $_" -ForegroundColor Red
    exit 1
}

# Deploy using gcloud run deploy with the built image
$deployArgs = @(
    "run", "deploy", $ServiceName,
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
)

if ($envVars.Count -gt 0) {
    $deployArgs += "--set-env-vars"
    $deployArgs += ($envVars -join ",")
}

Write-Host "Running: gcloud $($deployArgs -join ' ')" -ForegroundColor Gray
Write-Host ""

try {
    & gcloud @deployArgs
    
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
        Write-Host "  Health: $serviceUrl/health" -ForegroundColor White
        Write-Host "  Chat: $serviceUrl/chat" -ForegroundColor White
        Write-Host "  Docs: $serviceUrl/docs" -ForegroundColor White
        Write-Host ""
        Write-Host "View service in console:" -ForegroundColor Cyan
        Write-Host "  https://console.cloud.google.com/run/detail/$Region/$ServiceName?project=$ProjectId" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host "[ERROR] Deployment failed" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[ERROR] Deployment error: $_" -ForegroundColor Red
    exit 1
}


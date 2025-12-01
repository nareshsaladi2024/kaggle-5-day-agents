<#
.SYNOPSIS
    Deploy WeatherAssistant agent to Docker Desktop

.DESCRIPTION
    Builds and runs the WeatherAssistant agent in a Docker container on Docker Desktop.

.PARAMETER Port
    Port to expose the agent API on (default: 3000)

.EXAMPLE
    .\deploy-to-docker-desktop.ps1

.EXAMPLE
    .\deploy-to-docker-desktop.ps1 -Port 8080
#>

param(
    [int]$Port = 3000
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deploy WeatherAssistant to Docker Desktop" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Docker not found. Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

# Check if Docker is running
try {
    docker ps | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker not running"
    }
} catch {
    Write-Host "[ERROR] Docker Desktop is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Docker is running" -ForegroundColor Green
Write-Host ""

# Load .env file if exists
if (Test-Path ".env") {
    Write-Host "Loading environment variables from .env..." -ForegroundColor Cyan
    Get-Content ".env" | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
}

# Set defaults
$ProjectId = $env:GOOGLE_CLOUD_PROJECT
if ([string]::IsNullOrEmpty($ProjectId)) {
    $ProjectId = "aiagent-capstoneproject"
}

Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  Project: $ProjectId" -ForegroundColor White
Write-Host "  Port: $Port" -ForegroundColor White
Write-Host "  Agent: WeatherAssistant" -ForegroundColor White
Write-Host ""

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
COPY Day5b/WeatherAssistant/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dependencies for API server
RUN pip install --no-cache-dir fastapi uvicorn python-multipart python-dotenv

# Copy utility directory (agent handles ImportError gracefully if missing)
COPY utility/ ./utility/

# Copy agent files
COPY Day5b/WeatherAssistant/ ./WeatherAssistant/

# Copy API server
COPY Day5b/weather-assistant-api.py .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV GOOGLE_CLOUD_PROJECT=$ProjectId

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

# Build Docker image
$imageName = "weather-assistant:latest"
Write-Host "Building Docker image: $imageName" -ForegroundColor Cyan
Write-Host ""

# Build from parent directory to include utility directory
$parentDir = Split-Path -Parent $ScriptDir
Set-Location $parentDir

# Build with context from parent directory (.) so utility/ is accessible
docker build -f "Day5b/Dockerfile" -t $imageName .

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Docker build failed" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Image built successfully" -ForegroundColor Green
Write-Host ""

# Stop and remove existing container if it exists
Write-Host "Stopping existing container (if any)..." -ForegroundColor Cyan
docker stop weather-assistant 2>$null
docker rm weather-assistant 2>$null

# Run container
Write-Host "Starting container..." -ForegroundColor Cyan
Write-Host ""

$envVars = @()
if ($env:GOOGLE_CLOUD_PROJECT) {
    $envVars += "-e", "GOOGLE_CLOUD_PROJECT=$($env:GOOGLE_CLOUD_PROJECT)"
}
if ($env:GOOGLE_CLOUD_LOCATION) {
    $envVars += "-e", "GOOGLE_CLOUD_LOCATION=$($env:GOOGLE_CLOUD_LOCATION)"
}
if ($env:GOOGLE_API_KEY) {
    $envVars += "-e", "GOOGLE_API_KEY=$($env:GOOGLE_API_KEY)"
}

docker run -d `
    --name weather-assistant `
    -p "${Port}:8080" `
    $envVars `
    $imageName

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[OK] Container started successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Deployment Complete" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Service running at:" -ForegroundColor Green
    Write-Host "  http://localhost:$Port" -ForegroundColor White
    Write-Host ""
    Write-Host "API Endpoints:" -ForegroundColor Cyan
    Write-Host "  Health: http://localhost:$Port/health" -ForegroundColor White
    Write-Host "  Chat: http://localhost:$Port/chat" -ForegroundColor White
    Write-Host "  Docs: http://localhost:$Port/docs" -ForegroundColor White
    Write-Host ""
    Write-Host "View logs:" -ForegroundColor Cyan
    Write-Host "  docker logs -f weather-assistant" -ForegroundColor White
    Write-Host ""
    Write-Host "Stop container:" -ForegroundColor Cyan
    Write-Host "  docker stop weather-assistant" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "[ERROR] Failed to start container" -ForegroundColor Red
    exit 1
}


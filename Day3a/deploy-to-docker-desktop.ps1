<#
.SYNOPSIS
    Deploys Day3a session agents to Docker Desktop

.DESCRIPTION
    Builds and runs the session management agents in Docker Desktop

.PARAMETER Agent
    Which agent to run: session_agent, compaction_agent, or basic_session_agent
    Default: session_agent

.PARAMETER BuildOnly
    Only build the image without starting container

.PARAMETER Stop
    Stop the running container

.EXAMPLE
    .\deploy-to-docker-desktop.ps1
    Builds and runs session_agent

.EXAMPLE
    .\deploy-to-docker-desktop.ps1 -Agent compaction_agent
    Builds and runs compaction_agent
#>

param(
    [ValidateSet('session_agent', 'compaction_agent', 'basic_session_agent')]
    [string]$Agent = 'session_agent',
    [switch]$BuildOnly = $false,
    [switch]$Stop = $false
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Day3a Session Agents - Docker Desktop" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Docker
try {
    docker version | Out-Null
    Write-Host "[OK] Docker is running" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Docker is not running" -ForegroundColor Red
    exit 1
}

# Handle Stop
if ($Stop) {
    Write-Host "Stopping container..." -ForegroundColor Yellow
    docker stop day3a-$Agent 2>$null
    docker rm day3a-$Agent 2>$null
    Write-Host "[OK] Container stopped" -ForegroundColor Green
    exit 0
}

# Check environment variables
$apiKeySet = [bool]$env:GOOGLE_API_KEY
$projectSet = [bool]$env:GOOGLE_CLOUD_PROJECT

if (-not $apiKeySet) {
    Write-Host "[WARN] GOOGLE_API_KEY not set" -ForegroundColor Yellow
    Write-Host "Set it with: `$env:GOOGLE_API_KEY = 'your-key'" -ForegroundColor Gray
}

if (-not $projectSet) {
    Write-Host "[WARN] GOOGLE_CLOUD_PROJECT not set" -ForegroundColor Yellow
    Write-Host "Set it with: `$env:GOOGLE_CLOUD_PROJECT = 'your-project'" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Building Docker image for $Agent..." -ForegroundColor Cyan

# Build from parent directory to include utility
$parentDir = Split-Path -Parent $ScriptDir
Set-Location $parentDir

# Build image using the build context from parent directory
docker build -f Day3a/Dockerfile.build -t day3a-$Agent:latest .

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Build failed" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Image built successfully" -ForegroundColor Green

if ($BuildOnly) {
    Write-Host "Build-only mode: Skipping container start" -ForegroundColor Yellow
    exit 0
}

# Stop existing container
docker stop day3a-$Agent 2>$null
docker rm day3a-$Agent 2>$null

Write-Host ""
Write-Host "Starting container..." -ForegroundColor Cyan

# Prepare environment variables
$envArgs = @()
if ($env:GOOGLE_API_KEY) {
    $envArgs += "-e", "GOOGLE_API_KEY=$($env:GOOGLE_API_KEY)"
}
if ($env:GOOGLE_CLOUD_PROJECT) {
    $envArgs += "-e", "GOOGLE_CLOUD_PROJECT=$($env:GOOGLE_CLOUD_PROJECT)"
}
if ($env:GOOGLE_CLOUD_LOCATION) {
    $envArgs += "-e", "GOOGLE_CLOUD_LOCATION=$($env:GOOGLE_CLOUD_LOCATION)"
}

# Run container
$dbPath = Join-Path $ScriptDir "session_data.db"
$compactionPath = Join-Path $ScriptDir "compaction_data.db"

$containerArgs = @(
    "run", "-d",
    "--name", "day3a-$Agent",
    "-v", "${dbPath}:/app/session_data.db",
    "-v", "${compactionPath}:/app/compaction_data.db"
) + $envArgs + @(
    "day3a-$Agent:latest"
)

docker @containerArgs

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Container started" -ForegroundColor Green
    Write-Host ""
    Write-Host "Container: day3a-$Agent" -ForegroundColor Cyan
    Write-Host "View logs: docker logs -f day3a-$Agent" -ForegroundColor Gray
    Write-Host "Stop: .\deploy-to-docker-desktop.ps1 -Stop" -ForegroundColor Gray
} else {
    Write-Host "[ERROR] Failed to start container" -ForegroundColor Red
    exit 1
}

Write-Host ""


# Quick start script for Docker deployment
# This script builds and starts the ADK web server with all agents

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Kaggle 5-Day Agents - Docker Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "Checking Docker..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    Write-Host "✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Check if .env files exist
Write-Host ""
Write-Host "Checking .env files..." -ForegroundColor Yellow
$days = @("Day1a", "Day1b", "Day2a", "Day2b", "Day3a", "Day3b", "Day4a", "Day4b", "Day5a", "Day5b")
$missing = @()
foreach ($day in $days) {
    $envPath = Join-Path $day ".env"
    if (Test-Path $envPath) {
        Write-Host "  ✓ $day/.env exists" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $day/.env missing" -ForegroundColor Red
        $missing += $day
    }
}

if ($missing.Count -gt 0) {
    Write-Host ""
    Write-Host "Warning: Some .env files are missing. They will be created from templates." -ForegroundColor Yellow
}

# Check root .env
if (Test-Path ".env") {
    Write-Host "  ✓ Root .env exists" -ForegroundColor Green
} else {
    Write-Host "  ✗ Root .env missing - creating from Day1a..." -ForegroundColor Yellow
    if (Test-Path "Day1a\helpful_assistant\.env") {
        Copy-Item "Day1a\helpful_assistant\.env" ".env"
        Write-Host "  ✓ Root .env created" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Cannot create root .env - Day1a/helpful_assistant/.env not found" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Building and starting Docker container..." -ForegroundColor Yellow
Write-Host ""

# Build and start
docker-compose up --build

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ADK Web Server should be running at:" -ForegroundColor Green
Write-Host "  http://localhost:8080" -ForegroundColor White
Write-Host ""
Write-Host "To stop: docker-compose down" -ForegroundColor Gray
Write-Host "To view logs: docker-compose logs -f" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan


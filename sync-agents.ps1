<#
.SYNOPSIS
    Syncs all agents from Day folders to unified agents/ directory
#>

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "Syncing agents to unified agents/ directory..." -ForegroundColor Cyan
Write-Host ""

# Create agents directory if it doesn't exist
if (-not (Test-Path "agents")) {
    New-Item -ItemType Directory -Path "agents" | Out-Null
    Write-Host "Created agents/ directory" -ForegroundColor Green
}

# Clear existing agents (optional - comment out to keep existing)
# Remove-Item -Path "agents\*" -Recurse -Force -ErrorAction SilentlyContinue

# Define main agents
$mainAgents = @(
    "Day1a/helpful_assistant",
    "Day1a/sample-agent",
    "Day2a/CurrencyAgent",
    "Day2b/image_agent",
    "Day2b/shipping_agent",
    "Day4a/ResearchAgent",
    "Day5a/CustomerSupportAgent",
    "Day5a/ProductCatalogAgent",
    "Day5b/WeatherAssistant"
)

# Copy main agents
foreach ($agentDir in $mainAgents) {
    if (Test-Path $agentDir) {
        $agentName = Split-Path $agentDir -Leaf
        $destPath = Join-Path "agents" $agentName
        
        # Remove existing if present
        if (Test-Path $destPath) {
            Remove-Item -Path $destPath -Recurse -Force
        }
        
        Copy-Item -Path $agentDir -Destination $destPath -Recurse -Force
        Write-Host "  Synced: $agentName" -ForegroundColor Green
    }
}

# Copy Day1b agents
if (Test-Path "Day1b") {
    Write-Host ""
    Write-Host "Syncing Day1b agents..." -ForegroundColor Cyan
    Get-ChildItem -Path "Day1b" -Directory | Where-Object { 
        Test-Path (Join-Path $_.FullName "agent.py") -or 
        Test-Path (Join-Path $_.FullName "root_agent.yaml")
    } | ForEach-Object {
        $destPath = Join-Path "agents" $_.Name
        
        # Remove existing if present
        if (Test-Path $destPath) {
            Remove-Item -Path $destPath -Recurse -Force
        }
        
        Copy-Item -Path $_.FullName -Destination $destPath -Recurse -Force
        Write-Host "  Synced: $($_.Name)" -ForegroundColor Green
    }
}

# Copy Day3a and Day3b agents if they exist
foreach ($day in @("Day3a", "Day3b")) {
    if (Test-Path $day) {
        Write-Host ""
        Write-Host "Syncing $day agents..." -ForegroundColor Cyan
        Get-ChildItem -Path $day -Directory -Recurse | Where-Object { 
            Test-Path (Join-Path $_.FullName "agent.py") -or 
            Test-Path (Join-Path $_.FullName "root_agent.yaml")
        } | ForEach-Object {
            $agentName = $_.Name
            $destPath = Join-Path "agents" $agentName
            
            # Remove existing if present
            if (Test-Path $destPath) {
                Remove-Item -Path $destPath -Recurse -Force
            }
            
            Copy-Item -Path $_.FullName -Destination $destPath -Recurse -Force
            Write-Host "  Synced: $agentName" -ForegroundColor Green
        }
    }
}

Write-Host ""
Write-Host "Sync complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Run ADK web from agents directory:" -ForegroundColor Cyan
Write-Host "  cd agents" -ForegroundColor White
Write-Host "  adk web ." -ForegroundColor White
Write-Host ""
Write-Host "Or from root:" -ForegroundColor Cyan
Write-Host "  adk web agents" -ForegroundColor White


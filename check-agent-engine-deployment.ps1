<#
.SYNOPSIS
    Check deployment status of agents in Vertex AI Agent Engine

.DESCRIPTION
    Lists all deployed agents and their status in Vertex AI Agent Engine.
#>

param(
    [string]$ProjectId = "",
    [string]$Region = "us-central1"
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Check Agent Engine Deployment Status" -ForegroundColor Cyan
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

Write-Host "Project: $ProjectId" -ForegroundColor Cyan
Write-Host "Region: $Region" -ForegroundColor Cyan
Write-Host ""

# Set project
gcloud config set project $ProjectId | Out-Null

# Check if ADK CLI is available
if (-not (Get-Command adk -ErrorAction SilentlyContinue)) {
    Write-Host "[WARNING] ADK CLI not found. Install with: pip install google-adk" -ForegroundColor Yellow
    Write-Host ""
}

# Try to list agents using gcloud
Write-Host "Checking deployed agents..." -ForegroundColor Cyan
Write-Host ""

try {
    # Try using gcloud to list agents
    $agents = gcloud ai agents list --project $ProjectId --region $Region --format="json" 2>&1
    
    if ($LASTEXITCODE -eq 0 -and $agents) {
        $agentsJson = $agents | ConvertFrom-Json
        if ($agentsJson.Count -gt 0) {
            Write-Host "Found $($agentsJson.Count) deployed agent(s):" -ForegroundColor Green
            Write-Host ""
            foreach ($agent in $agentsJson) {
                Write-Host "  Agent: $($agent.name)" -ForegroundColor White
                Write-Host "    Display Name: $($agent.displayName)" -ForegroundColor Gray
                Write-Host "    State: $($agent.state)" -ForegroundColor $(if ($agent.state -eq "ACTIVE") { "Green" } else { "Yellow" })
                Write-Host ""
            }
        } else {
            Write-Host "[INFO] No agents found in Agent Engine" -ForegroundColor Yellow
            Write-Host ""
        }
    } else {
        Write-Host "[INFO] Could not list agents (may need to deploy first)" -ForegroundColor Yellow
        Write-Host ""
    }
} catch {
    Write-Host "[INFO] Could not query agents: $_" -ForegroundColor Yellow
    Write-Host ""
}

# Check local agents
Write-Host "Local agents in agents/ directory:" -ForegroundColor Cyan
$agentsDir = Join-Path $ScriptDir "agents"
if (Test-Path $agentsDir) {
    $localAgents = Get-ChildItem -Path $agentsDir -Directory | Where-Object {
        (Test-Path (Join-Path $_.FullName "agent.py")) -or 
        (Test-Path (Join-Path $_.FullName "root_agent.yaml"))
    }
    
    if ($localAgents.Count -gt 0) {
        Write-Host "Found $($localAgents.Count) local agent(s):" -ForegroundColor Green
        $localAgents | ForEach-Object {
            Write-Host "  - $($_.Name)" -ForegroundColor White
        }
        Write-Host ""
        Write-Host "To deploy these agents, run:" -ForegroundColor Yellow
        Write-Host "  .\deploy-agents-to-agent-engine.ps1" -ForegroundColor White
    } else {
        Write-Host "[WARNING] No agents found in agents/ directory" -ForegroundColor Yellow
        Write-Host "Run .\sync-agents.ps1 first to sync agents" -ForegroundColor White
    }
} else {
    Write-Host "[WARNING] agents/ directory not found" -ForegroundColor Yellow
    Write-Host "Run .\sync-agents.ps1 first" -ForegroundColor White
}

Write-Host ""
Write-Host "Console URL:" -ForegroundColor Cyan
Write-Host "  https://console.cloud.google.com/vertex-ai/agents/agent-engines?project=$ProjectId" -ForegroundColor White
Write-Host ""
Write-Host "If no agents are deployed:" -ForegroundColor Yellow
Write-Host "  1. Run: .\deploy-agents-to-agent-engine.ps1" -ForegroundColor White
Write-Host "  2. Wait 2-5 minutes for deployment to complete" -ForegroundColor White
Write-Host "  3. Refresh the console" -ForegroundColor White
Write-Host ""



<#
.SYNOPSIS
    Deploy agents from agents/ directory to Vertex AI Agent Engine

.DESCRIPTION
    Deploys all agents from the unified agents/ directory to Vertex AI Agent Engine using ADK CLI.
    Each agent is deployed separately with its own configuration.

.PARAMETER ProjectId
    Google Cloud Project ID (default: from .env or aiagent-capstoneproject)

.PARAMETER Region
    Agent Engine region (default: us-east4)

.PARAMETER Agent
    Specific agent to deploy (optional, deploys all if not specified)

.EXAMPLE
    .\deploy-agents-to-agent-engine.ps1

.EXAMPLE
    .\deploy-agents-to-agent-engine.ps1 -ProjectId "my-project" -Region "us-east4"

.EXAMPLE
    .\deploy-agents-to-agent-engine.ps1 -Agent "sample-agent"
#>

param(
    [string]$ProjectId = "",
    [string]$Region = "us-east4",
    [string]$Agent = ""
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deploy Agents to Vertex AI Agent Engine" -ForegroundColor Cyan
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

if (-not (Get-Command adk -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] ADK CLI not found. Install with: pip install google-adk" -ForegroundColor Red
    exit 1
}

if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] gcloud CLI not found" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Prerequisites met" -ForegroundColor Green
Write-Host ""
Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  Project: $ProjectId" -ForegroundColor White
Write-Host "  Region: $Region" -ForegroundColor White
Write-Host "  Agents Directory: agents/" -ForegroundColor White
Write-Host ""

# Set project
gcloud config set project $ProjectId

# Enable APIs
Write-Host "Enabling required APIs..." -ForegroundColor Cyan
gcloud services enable aiplatform.googleapis.com --project $ProjectId
gcloud services enable agentengine.googleapis.com --project $ProjectId

# Discover agents from agents/ directory
$agentsDir = Join-Path $ScriptDir "agents"
if (-not (Test-Path $agentsDir)) {
    Write-Host "[ERROR] agents/ directory not found. Run sync-agents.ps1 first." -ForegroundColor Red
    exit 1
}

Write-Host "Discovering agents from agents/ directory..." -ForegroundColor Cyan
$agentDirs = Get-ChildItem -Path $agentsDir -Directory | Where-Object {
    (Test-Path (Join-Path $_.FullName "agent.py")) -or 
    (Test-Path (Join-Path $_.FullName "root_agent.yaml"))
}

if ($agentDirs.Count -eq 0) {
    Write-Host "[ERROR] No agents found in agents/ directory" -ForegroundColor Red
    exit 1
}

# Filter if specific agent requested
if (-not [string]::IsNullOrEmpty($Agent)) {
    $agentDirs = $agentDirs | Where-Object { $_.Name -like "*$Agent*" }
    if ($agentDirs.Count -eq 0) {
        Write-Host "[ERROR] Agent not found: $Agent" -ForegroundColor Red
        exit 1
    }
}

Write-Host "Found $($agentDirs.Count) agents to deploy" -ForegroundColor Cyan
Write-Host ""

# Deploy each agent
$deployed = 0
$failed = 0

foreach ($agentDir in $agentDirs) {
    $agentName = $agentDir.Name
    $agentPath = $agentDir.FullName
    
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Deploying: $agentName" -ForegroundColor Cyan
    Write-Host "Path: agents/$agentName" -ForegroundColor Gray
    Write-Host "========================================" -ForegroundColor Cyan
    
    # Check for agent engine config
    $configFile = Join-Path $agentPath ".agent_engine_config.json"
    if (-not (Test-Path $configFile)) {
        # Create default config
        $config = @{
            min_instances = 0
            max_instances = 1
            resource_limits = @{
                cpu = "1"
                memory = "1Gi"
            }
        } | ConvertTo-Json
        
        Set-Content -Path $configFile -Value $config
        Write-Host "[INFO] Created default .agent_engine_config.json" -ForegroundColor Yellow
    }
    
    # Deploy using ADK
    $deployCmd = "adk deploy agent_engine --project $ProjectId --region $Region `"$agentPath`" --agent_engine_config_file `"$configFile`""
    
    Write-Host "Running: $deployCmd" -ForegroundColor Gray
    Write-Host ""
    
    try {
        Invoke-Expression $deployCmd
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] $agentName deployed successfully" -ForegroundColor Green
            $deployed++
            Write-Host ""
        } else {
            Write-Host "[ERROR] Failed to deploy $agentName" -ForegroundColor Red
            $failed++
        }
    } catch {
        Write-Host "[ERROR] Deployment error: $_" -ForegroundColor Red
        $failed++
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deployment Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Deployed: $deployed" -ForegroundColor Green
Write-Host "Failed: $failed" -ForegroundColor $(if ($failed -gt 0) { "Red" } else { "Green" })
Write-Host "Total: $($agentDirs.Count)" -ForegroundColor Cyan
Write-Host ""
Write-Host "View deployed agents:" -ForegroundColor Cyan
Write-Host "  https://console.cloud.google.com/vertex-ai/agents/agent-engines?project=$ProjectId" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Wait 2-5 minutes for agents to be ready" -ForegroundColor White
Write-Host "  2. Test agents using ADK CLI or console" -ForegroundColor White
Write-Host "  3. Monitor usage in Cloud Console" -ForegroundColor White
Write-Host ""


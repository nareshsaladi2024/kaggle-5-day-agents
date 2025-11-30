<#
.SYNOPSIS
    Deploy kaggle-5-day-agents to Vertex AI Agent Engine

.DESCRIPTION
    Deploys all agents from kaggle-5-day-agents to Vertex AI Agent Engine using ADK CLI.
    Each agent is deployed separately with its own configuration.

.PARAMETER ProjectId
    Google Cloud Project ID (default: from .env or aiagent-capstoneproject)

.PARAMETER Region
    Agent Engine region (default: us-east4)

.PARAMETER Agent
    Specific agent to deploy (optional, deploys all if not specified)

.EXAMPLE
    .\deploy-to-agent-engine.ps1

.EXAMPLE
    .\deploy-to-agent-engine.ps1 -ProjectId "my-project" -Region "us-east4"

.EXAMPLE
    .\deploy-to-agent-engine.ps1 -Agent "Day1a/helpful_assistant"
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
Write-Host "Deploy to Vertex AI Agent Engine" -ForegroundColor Cyan
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
Write-Host ""

# Set project
gcloud config set project $ProjectId

# Enable APIs
Write-Host "Enabling required APIs..." -ForegroundColor Cyan
gcloud services enable aiplatform.googleapis.com --project $ProjectId
gcloud services enable agentengine.googleapis.com --project $ProjectId

# Define agents to deploy
$agents = @(
    @{Path="Day1a/helpful_assistant"; Name="helpful-assistant"},
    @{Path="Day1a/sample-agent"; Name="sample-agent"},
    @{Path="Day2a/CurrencyAgent"; Name="currency-agent"},
    @{Path="Day2b/image_agent"; Name="image-agent"},
    @{Path="Day2b/shipping_agent"; Name="shipping-agent"},
    @{Path="Day3a/agents/session_agent"; Name="session-agent"},
    @{Path="Day3b/agents/memory_agent"; Name="memory-agent"},
    @{Path="Day4a/ResearchAgent"; Name="research-agent"},
    @{Path="Day5a/CustomerSupportAgent"; Name="customer-support-agent"},
    @{Path="Day5b/WeatherAssistant"; Name="weather-assistant"}
)

# Filter if specific agent requested
if (-not [string]::IsNullOrEmpty($Agent)) {
    $agents = $agents | Where-Object { $_.Path -like "*$Agent*" }
    if ($agents.Count -eq 0) {
        Write-Host "[ERROR] Agent not found: $Agent" -ForegroundColor Red
        exit 1
    }
}

Write-Host "Agents to deploy: $($agents.Count)" -ForegroundColor Cyan
Write-Host ""

# Deploy each agent
foreach ($agent in $agents) {
    $agentPath = Join-Path $ScriptDir $agent.Path
    
    if (-not (Test-Path $agentPath)) {
        Write-Host "[SKIP] Agent directory not found: $($agent.Path)" -ForegroundColor Yellow
        continue
    }
    
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Deploying: $($agent.Name)" -ForegroundColor Cyan
    Write-Host "Path: $($agent.Path)" -ForegroundColor Gray
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
            Write-Host "[OK] $($agent.Name) deployed successfully" -ForegroundColor Green
            Write-Host ""
        } else {
            Write-Host "[ERROR] Failed to deploy $($agent.Name)" -ForegroundColor Red
        }
    } catch {
        Write-Host "[ERROR] Deployment error: $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deployment Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "View deployed agents:" -ForegroundColor Cyan
Write-Host "  https://console.cloud.google.com/vertex-ai/agents/agent-engines?project=$ProjectId" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Wait 2-5 minutes for agents to be ready" -ForegroundColor White
Write-Host "  2. Test agents using ADK CLI or console" -ForegroundColor White
Write-Host "  3. Monitor usage in Cloud Console" -ForegroundColor White
Write-Host ""


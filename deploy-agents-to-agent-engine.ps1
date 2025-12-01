<#
.SYNOPSIS
    Deploy agents from agents/ directory to Vertex AI Agent Engine

.DESCRIPTION
    Deploys all agents from the unified agents/ directory to Vertex AI Agent Engine using ADK CLI.
    Each agent is deployed separately with its own configuration.

.PARAMETER ProjectId
    Google Cloud Project ID (default: from .env or aiagent-capstoneproject)

.PARAMETER Region
    Agent Engine region (default: us-central1)

.PARAMETER Agent
    Specific agent to deploy (optional, deploys all if not specified)

.EXAMPLE
    .\deploy-agents-to-agent-engine.ps1

.EXAMPLE
    .\deploy-agents-to-agent-engine.ps1 -ProjectId "my-project" -Region "us-central1"

.EXAMPLE
    .\deploy-agents-to-agent-engine.ps1 -Agent "sample-agent"
#>

param(
    [string]$ProjectId = "",
    [string]$Region = "us-central1",
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

# Configure Authentication - Enforce Application Default Credentials (ADC)
Write-Host "Configuring authentication..." -ForegroundColor Cyan

# Unset GOOGLE_APPLICATION_CREDENTIALS to enforce use of ADC
if ($env:GOOGLE_APPLICATION_CREDENTIALS) {
    Write-Host "[INFO] Unsetting GOOGLE_APPLICATION_CREDENTIALS to enforce ADC" -ForegroundColor Yellow
    Remove-Item Env:\GOOGLE_APPLICATION_CREDENTIALS
}

# Check if user is authenticated with gcloud
$authCheck = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
if ($LASTEXITCODE -ne 0 -or -not $authCheck) {
    Write-Host "[WARNING] No active gcloud authentication found!" -ForegroundColor Yellow
    Write-Host "  Please run: gcloud auth application-default login" -ForegroundColor Cyan
    Write-Host "  Then run this script again." -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "[OK] Authenticated as: $authCheck" -ForegroundColor Green
    
    # Set the quota project for ADC (optional, may fail in some environments)
    Write-Host "Setting ADC quota project to: $ProjectId" -ForegroundColor Gray
    try {
        $quotaOutput = gcloud auth application-default set-quota-project $ProjectId 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] ADC quota project set" -ForegroundColor Green
        } else {
            Write-Host "[WARNING] Could not set quota project (non-critical, continuing...)" -ForegroundColor Yellow
            Write-Host "  This is usually fine - ADC will use your default project" -ForegroundColor Gray
        }
    } catch {
        Write-Host "[WARNING] Error setting quota project: $_" -ForegroundColor Yellow
        Write-Host "  This is usually fine - ADC will use your default project" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "Using Application Default Credentials (ADC) for deployment" -ForegroundColor Cyan
Write-Host ""

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
    # ADK requires deployment from the agents/ directory, not from individual agent directories
    Write-Host "Deploying to Vertex AI Agent Engine..." -ForegroundColor Cyan
    Write-Host "  Agent: $agentName" -ForegroundColor Gray
    Write-Host "  Config: $configFile" -ForegroundColor Gray
    Write-Host ""
    
    try {
        $originalLocation = Get-Location
        # Change to agents directory (ADK requirement)
        Set-Location $agentsDir
        
        # Deploy using relative path from agents directory
        $relativeAgentPath = $agentName
        $relativeConfigPath = Join-Path $agentName ".agent_engine_config.json"
        
        Write-Host "  Running from: $agentsDir" -ForegroundColor Gray
        Write-Host "  Command: adk deploy agent_engine --project $ProjectId --region $Region $relativeAgentPath --agent_engine_config_file $relativeConfigPath" -ForegroundColor Gray
        Write-Host ""
        
        # Run deployment
        $deployOutput = adk deploy agent_engine --project $ProjectId --region $Region $relativeAgentPath --agent_engine_config_file $relativeConfigPath 2>&1
        $exitCode = $LASTEXITCODE
        
        # Check output for errors
        $hasError = $false
        $deployOutput | ForEach-Object {
            if ($_ -match "Deploy failed|FAILED_PRECONDITION|ERROR|ModuleNotFoundError") {
                Write-Host "  $_" -ForegroundColor Red
                $hasError = $true
            } elseif ($_ -match "Deploy succeeded|deployed successfully") {
                Write-Host "  $_" -ForegroundColor Green
            } else {
                Write-Host "  $_" -ForegroundColor Gray
            }
        }
        
        if ($exitCode -eq 0 -and -not $hasError) {
            Write-Host "[OK] $agentName deployed successfully" -ForegroundColor Green
            $deployed++
        } else {
            Write-Host "[ERROR] Failed to deploy $agentName" -ForegroundColor Red
            if ($hasError) {
                Write-Host "  Check the error messages above for details" -ForegroundColor Yellow
            }
            $failed++
        }
        
        Set-Location $originalLocation
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


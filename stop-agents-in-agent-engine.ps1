<#
.SYNOPSIS
    Stop or delete agents from Vertex AI Agent Engine

.DESCRIPTION
    Lists and optionally deletes agents deployed to Vertex AI Agent Engine.
    Can delete all agents or specific agents by name.

.PARAMETER ProjectId
    Google Cloud Project ID (default: from .env or aiagent-capstoneproject)

.PARAMETER Region
    Agent Engine region (default: us-central1)

.PARAMETER AgentName
    Specific agent name to delete (optional, deletes all if not specified)

.PARAMETER ListOnly
    Only list agents, don't delete (default: false)

.PARAMETER Force
    Force deletion even if agent has associated resources (default: true)

.EXAMPLE
    .\stop-agents-in-agent-engine.ps1 -ListOnly

.EXAMPLE
    .\stop-agents-in-agent-engine.ps1 -AgentName "sample-agent"

.EXAMPLE
    .\stop-agents-in-agent-engine.ps1 -Force $false
#>

param(
    [string]$ProjectId = "",
    [string]$Region = "us-central1",
    [string]$AgentName = "",
    [switch]$ListOnly = $false,
    [bool]$Force = $true
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Stop/Delete Agents in Vertex AI Engine" -ForegroundColor Cyan
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

# Set defaults
if ([string]::IsNullOrEmpty($ProjectId)) {
    $ProjectId = $env:GOOGLE_CLOUD_PROJECT
    if ([string]::IsNullOrEmpty($ProjectId)) {
        $ProjectId = "aiagent-capstoneproject"
    }
}

Write-Host "Project ID: $ProjectId" -ForegroundColor Yellow
Write-Host "Region: $Region" -ForegroundColor Yellow
Write-Host ""

# Check if Python and required packages are available
$pythonCmd = "python"
try {
    $pythonVersion = & $pythonCmd --version 2>&1
    Write-Host "Using Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python not found. Please install Python to use this script." -ForegroundColor Red
    exit 1
}

# Check if vertexai package is installed
try {
    & $pythonCmd -c "import vertexai; from vertexai import agent_engines" 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "vertexai package not found"
    }
} catch {
    Write-Host "Error: vertexai package not found. Installing..." -ForegroundColor Yellow
    & $pythonCmd -m pip install google-cloud-aiplatform --quiet
}

# Create temporary Python script to list/delete agents
$tempScript = [System.IO.Path]::GetTempFileName() + ".py"
$pythonScript = @"
import os
import sys
from pathlib import Path

import vertexai
from vertexai import agent_engines

# Initialize Vertex AI
vertexai.init(project="$ProjectId", location="$Region")

print("=" * 60)
print("Vertex AI Agent Engine - Agent Management")
print("=" * 60)
print(f"Project ID: $ProjectId")
print(f"Region: $Region")
print("=" * 60)

# List all agents
try:
    agents_list = list(agent_engines.list())
    
    if not agents_list:
        print("\n✅ No agents found.")
        sys.exit(0)
    
    print(f"\nFound {len(agents_list)} agent(s):")
    for i, agent in enumerate(agents_list, 1):
        agent_id = agent.resource_name.split('/')[-1]
        print(f"  {i}. {agent_id}")
        print(f"     Resource: {agent.resource_name}")
    
    if "$ListOnly" == "True":
        print("\n✅ List complete (ListOnly mode - no deletions)")
        sys.exit(0)
    
    # Filter by agent name if specified
    agents_to_delete = agents_list
    if "$AgentName":
        agents_to_delete = [a for a in agents_list if "$AgentName" in a.resource_name]
        if not agents_to_delete:
            print(f"\n❌ No agents found matching name: $AgentName")
            sys.exit(1)
        print(f"\nFiltered to {len(agents_to_delete)} agent(s) matching '$AgentName'")
    
    # Delete agents
    if agents_to_delete:
        print(f"\n⚠️  Deleting {len(agents_to_delete)} agent(s)...")
        for agent in agents_to_delete:
            try:
                agent_id = agent.resource_name.split('/')[-1]
                print(f"\nDeleting: {agent_id}")
                agent_engines.delete(resource_name=agent.resource_name, force=$Force)
                print(f"✅ Successfully deleted: {agent_id}")
            except Exception as e:
                print(f"❌ Failed to delete {agent.resource_name}: {e}")
        
        print("\n✅ Deletion completed!")
        print("\nNote: Deletion typically takes 1-2 minutes.")
        print(f"Verify in console: https://console.cloud.google.com/vertex-ai/agents/agent-engines?project=$ProjectId")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
"@

$pythonScript | Out-File -FilePath $tempScript -Encoding UTF8

try {
    Write-Host "Listing agents in Vertex AI Agent Engine..." -ForegroundColor Cyan
    Write-Host ""
    
    if ($ListOnly) {
        Write-Host "Mode: LIST ONLY (no deletions)" -ForegroundColor Yellow
    } else {
        if ($AgentName) {
            Write-Host "Mode: DELETE SPECIFIC AGENT: $AgentName" -ForegroundColor Red
        } else {
            Write-Host "Mode: DELETE ALL AGENTS" -ForegroundColor Red
        }
        Write-Host "Force deletion: $Force" -ForegroundColor Yellow
    }
    Write-Host ""
    
    & $pythonCmd $tempScript
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Operation completed successfully!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "❌ Operation failed. Check errors above." -ForegroundColor Red
        exit 1
    }
} finally {
    # Clean up temp script
    if (Test-Path $tempScript) {
        Remove-Item $tempScript -Force
    }
}

Write-Host ""
Write-Host "Console URL:" -ForegroundColor Cyan
Write-Host "https://console.cloud.google.com/vertex-ai/agents/agent-engines?project=$ProjectId" -ForegroundColor White
Write-Host ""


<#
.SYNOPSIS
    Creates root_agent.yaml files for all agents in subfolders

.DESCRIPTION
    This script scans for agent.py files and creates corresponding root_agent.yaml
    files based on the agent definitions found in the Python code.

.PARAMETER BaseDir
    Base directory to scan (default: current directory)

.PARAMETER Overwrite
    Overwrite existing YAML files
#>

param(
    [string]$BaseDir = ".",
    [switch]$Overwrite = $false
)

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Create YAML Agent Configurations" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Find all agent.py files
$agentFiles = Get-ChildItem -Path $BaseDir -Recurse -Filter "agent.py" | Where-Object {
    $_.FullName -notmatch '\\__pycache__\\' -and
    $_.FullName -notmatch '\\\.venv\\' -and
    $_.FullName -match 'root_agent'
}

Write-Host "Found $($agentFiles.Count) agent.py files with root_agent" -ForegroundColor Green
Write-Host ""

$createdCount = 0
$skippedCount = 0

foreach ($agentFile in $agentFiles) {
    $agentDir = $agentFile.DirectoryName
    $yamlFile = Join-Path $agentDir "root_agent.yaml"
    
    # Check if YAML already exists
    if ((Test-Path $yamlFile) -and -not $Overwrite) {
        Write-Host "  [SKIP] $yamlFile (already exists, use -Overwrite to replace)" -ForegroundColor Yellow
        $skippedCount++
        continue
    }
    
    # Read agent.py to extract basic info
    $content = Get-Content $agentFile -Raw
    
    # Try to extract agent name
    $nameMatch = if ($content -match 'name\s*=\s*["'']([^"'']+)["'']') { $matches[1] } else { $agentFile.Directory.Name }
    
    # Try to extract model
    $modelMatch = if ($content -match 'model\s*=\s*["'']([^"'']+)["'']') { $matches[1] } else { "gemini-2.5-flash-lite" }
    
    # Check for tools
    $hasGoogleSearch = $content -match 'google_search'
    
    # Create basic YAML
    $yamlContent = @"
name: $nameMatch
model:
  type: gemini
  model: $modelMatch
description: Agent defined in $($agentFile.Name)
instruction: |
  Agent loaded from Python configuration.
  See $($agentFile.Name) for full configuration.
"@
    
    if ($hasGoogleSearch) {
        $yamlContent += @"

tools:
  - google_search
"@
    }
    
    # Write YAML file
    $yamlContent | Out-File -FilePath $yamlFile -Encoding utf8 -NoNewline
    Write-Host "  [OK] Created: $yamlFile" -ForegroundColor Green
    $createdCount++
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Created: $createdCount" -ForegroundColor Green
Write-Host "Skipped: $skippedCount" -ForegroundColor Yellow
Write-Host ""

if ($createdCount -gt 0) {
    Write-Host "YAML files created! You can now:" -ForegroundColor Green
    Write-Host "  1. Edit the YAML files to customize agent configurations" -ForegroundColor Gray
    Write-Host "  2. Run: adk web . (from kaggle-5-day-agents directory)" -ForegroundColor Gray
    Write-Host "  3. ADK will discover agents from YAML files" -ForegroundColor Gray
}

Write-Host ""


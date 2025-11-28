<#
.SYNOPSIS
    Verifies that all required environment variables are set in .env file

.DESCRIPTION
    This script checks if the .env file contains all required credentials for
    running agents in Day1a. It validates:
    - GOOGLE_CLOUD_PROJECT (required for Vertex AI)
    - GOOGLE_CLOUD_LOCATION (optional, defaults to us-central1)
    - GOOGLE_API_KEY (required for Google AI API / Gemini)
    - GOOGLE_APPLICATION_CREDENTIALS (optional, for service account auth)
#>

$ErrorActionPreference = "Continue"

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$EnvFile = Join-Path $ScriptDir "helpful_assistant\.env"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Environment Variables Verification" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Checking .env file: $EnvFile" -ForegroundColor Gray
Write-Host ""

# Check if .env file exists
if (-not (Test-Path $EnvFile)) {
    Write-Host "[ERROR] .env file not found at: $EnvFile" -ForegroundColor Red
    Write-Host ""
    Write-Host "Create a .env file with the following content:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "# Google Cloud Configuration" -ForegroundColor Gray
    Write-Host "GOOGLE_CLOUD_PROJECT=aiagent-capstoneproject" -ForegroundColor Gray
    Write-Host "GOOGLE_CLOUD_LOCATION=us-central1" -ForegroundColor Gray
    Write-Host "" -ForegroundColor Gray
    Write-Host "# Google AI API Key (for Gemini)" -ForegroundColor Gray
    Write-Host "GOOGLE_API_KEY=AIzaSyAaPeS-PaJ0UGRG6vAMuSoa5joAOpdQ5O8" -ForegroundColor Gray
    Write-Host "" -ForegroundColor Gray
    Write-Host "# Optional: Service Account (or use gcloud auth application-default login)" -ForegroundColor Gray
    Write-Host "# GOOGLE_APPLICATION_CREDENTIALS=path\to\service-account.json" -ForegroundColor Gray
    Write-Host ""
    exit 1
}

Write-Host "[OK] .env file found" -ForegroundColor Green
Write-Host ""

# Load .env file and check variables
$envContent = Get-Content $EnvFile
$envVars = @{}

foreach ($line in $envContent) {
    # Skip comments and empty lines
    if ($line -match '^\s*#' -or $line -match '^\s*$') {
        continue
    }
    
    # Parse KEY=VALUE
    if ($line -match '^\s*([^=]+)=(.*)$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        $envVars[$key] = $value
    }
}

# Required variables
$required = @(
    @{Name="GOOGLE_CLOUD_PROJECT"; Description="Google Cloud Project ID (for Vertex AI)"},
    @{Name="GOOGLE_API_KEY"; Description="Google AI API Key (for Gemini API)"}
)

# Optional variables
$optional = @(
    @{Name="GOOGLE_CLOUD_LOCATION"; Description="Google Cloud Location (default: us-central1)"; Default="us-central1"},
    @{Name="GOOGLE_APPLICATION_CREDENTIALS"; Description="Service Account JSON path (optional)"}
)

$allGood = $true

Write-Host "Required Variables:" -ForegroundColor Cyan
Write-Host ""

foreach ($var in $required) {
    $name = $var.Name
    $desc = $var.Description
    
    if ($envVars.ContainsKey($name) -and $envVars[$name] -and $envVars[$name] -ne "") {
        if ($name -eq "GOOGLE_API_KEY") {
            $masked = "***" + $envVars[$name].Substring([Math]::Max(0, $envVars[$name].Length - 4))
            Write-Host "  [OK] $name = $masked" -ForegroundColor Green
        } else {
            Write-Host "  [OK] $name = $($envVars[$name])" -ForegroundColor Green
        }
    } else {
        Write-Host "  [MISSING] $name - NOT SET" -ForegroundColor Red
        Write-Host "    $desc" -ForegroundColor Gray
        $allGood = $false
    }
}

Write-Host ""
Write-Host "Optional Variables:" -ForegroundColor Cyan
Write-Host ""

foreach ($var in $optional) {
    $name = $var.Name
    $desc = $var.Description
    $default = $var.Default
    
    if ($envVars.ContainsKey($name) -and $envVars[$name] -and $envVars[$name] -ne "") {
        Write-Host "  [OK] $name = $($envVars[$name])" -ForegroundColor Green
    } else {
        if ($default) {
            Write-Host "  [WARN] $name - NOT SET (will use default: $default)" -ForegroundColor Yellow
        } else {
            Write-Host "  [WARN] $name - NOT SET (optional)" -ForegroundColor Yellow
        }
        Write-Host "    $desc" -ForegroundColor Gray
    }
}

Write-Host ""

# Check for authentication
Write-Host "Authentication:" -ForegroundColor Cyan
Write-Host ""

if ($envVars.ContainsKey("GOOGLE_APPLICATION_CREDENTIALS") -and $envVars["GOOGLE_APPLICATION_CREDENTIALS"]) {
    $credPath = $envVars["GOOGLE_APPLICATION_CREDENTIALS"]
    # Resolve relative paths
    if (-not [System.IO.Path]::IsPathRooted($credPath)) {
        $credPath = Join-Path $ScriptDir $credPath
    }
    
    if (Test-Path $credPath) {
        Write-Host "  [OK] Service account file found: $credPath" -ForegroundColor Green
    } else {
        Write-Host "  [WARN] Service account file not found: $credPath" -ForegroundColor Yellow
        Write-Host "    You can use 'gcloud auth application-default login' instead" -ForegroundColor Gray
    }
} else {
    Write-Host "  [INFO] No service account path set" -ForegroundColor Gray
    Write-Host "    Use: gcloud auth application-default login" -ForegroundColor Gray
    Write-Host "    Or: Set GOOGLE_APPLICATION_CREDENTIALS in .env file" -ForegroundColor Gray
}

Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($allGood) {
    Write-Host "[OK] All required environment variables are set!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your .env file is properly configured." -ForegroundColor Green
    Write-Host ""
    Write-Host "Note: Make sure to:" -ForegroundColor Yellow
    Write-Host "  1. Replace placeholder values with actual credentials" -ForegroundColor Gray
    Write-Host "  2. Set up authentication (gcloud auth or service account)" -ForegroundColor Gray
    Write-Host "  3. Verify GOOGLE_API_KEY is valid (get from https://aistudio.google.com/app/apikey)" -ForegroundColor Gray
} else {
    Write-Host "[ERROR] Some required environment variables are missing!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please add the missing variables to your .env file." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Example .env file content:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "GOOGLE_CLOUD_PROJECT=aiagent-capstoneproject" -ForegroundColor White
    Write-Host "GOOGLE_CLOUD_LOCATION=us-central1" -ForegroundColor White
    Write-Host "GOOGLE_API_KEY=AIzaSyAaPeS-PaJ0UGRG6vAMuSoa5joAOpdQ5O8" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host ""


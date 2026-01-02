# PowerShell script to set up dbt MCP server for MetricFlow POC
# Run this script from the project root directory

Write-Host "=== dbt MCP Server Setup ===" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Check if dbt is installed
Write-Host "Checking dbt installation..." -ForegroundColor Yellow
$dbtPath = Get-Command dbt -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source
if ($dbtPath) {
    Write-Host "✓ dbt found at: $dbtPath" -ForegroundColor Green
} else {
    Write-Host "✗ dbt not found. Please install dbt-core" -ForegroundColor Red
    exit 1
}

# Check if MetricFlow is installed
Write-Host "Checking MetricFlow installation..." -ForegroundColor Yellow
$mfPath = Get-Command mf -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source
if ($mfPath) {
    Write-Host "✓ MetricFlow found at: $mfPath" -ForegroundColor Green
} else {
    Write-Host "✗ MetricFlow not found. Please install dbt-metricflow" -ForegroundColor Red
    exit 1
}

# Get current directory
$projectDir = Get-Location
Write-Host ""
Write-Host "Project directory: $projectDir" -ForegroundColor Cyan

# Check if dbt_project.yml exists
if (Test-Path "dbt_project.yml") {
    Write-Host "✓ dbt_project.yml found" -ForegroundColor Green
} else {
    Write-Host "✗ dbt_project.yml not found. Are you in the project root?" -ForegroundColor Red
    exit 1
}

# Install uv (if not already installed)
Write-Host ""
Write-Host "Installing uv (Python package manager)..." -ForegroundColor Yellow
$uvInstalled = Get-Command uv -ErrorAction SilentlyContinue
if (-not $uvInstalled) {
    Write-Host "Installing uv..." -ForegroundColor Yellow
    pip install uv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ uv installed successfully" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to install uv. Trying alternative method..." -ForegroundColor Yellow
        Write-Host "You can install uv manually: powershell -ExecutionPolicy ByPass -c `"irm https://astral.sh/uv/install.ps1 | iex`"" -ForegroundColor Yellow
    }
} else {
    Write-Host "✓ uv already installed" -ForegroundColor Green
}

# Test dbt-mcp installation
Write-Host ""
Write-Host "Testing dbt-mcp installation..." -ForegroundColor Yellow
$mcpTest = uvx dbt-mcp --help 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ dbt-mcp is accessible via uvx" -ForegroundColor Green
} else {
    Write-Host "⚠ dbt-mcp not found via uvx. Installing..." -ForegroundColor Yellow
    pip install dbt-mcp
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ dbt-mcp installed via pip" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to install dbt-mcp" -ForegroundColor Red
        exit 1
    }
}

# Create .cursor directory if it doesn't exist
Write-Host ""
Write-Host "Creating MCP configuration..." -ForegroundColor Yellow
$cursorDir = ".cursor"
if (-not (Test-Path $cursorDir)) {
    New-Item -ItemType Directory -Path $cursorDir | Out-Null
    Write-Host "✓ Created .cursor directory" -ForegroundColor Green
} else {
    Write-Host "✓ .cursor directory exists" -ForegroundColor Green
}

# Create MCP configuration file
$mcpConfig = @{
    mcpServers = @{
        dbt = @{
            command = "uvx"
            args = @("dbt-mcp")
            env = @{
                DBT_PROJECT_DIR = $projectDir.ToString()
                DBT_PROFILES_DIR = $projectDir.ToString()
                DBT_PATH = $dbtPath
            }
        }
    }
} | ConvertTo-Json -Depth 10

$mcpConfigPath = Join-Path $cursorDir "mcp.json"
$mcpConfig | Out-File -FilePath $mcpConfigPath -Encoding UTF8
Write-Host "✓ Created MCP configuration at: $mcpConfigPath" -ForegroundColor Green

# Display configuration
Write-Host ""
Write-Host "=== MCP Configuration ===" -ForegroundColor Cyan
Write-Host $mcpConfig
Write-Host ""

# Verify dbt project can be parsed
Write-Host "Verifying dbt project..." -ForegroundColor Yellow
dbt parse --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ dbt project parses successfully" -ForegroundColor Green
} else {
    Write-Host "⚠ dbt project has parsing errors. Check the output above." -ForegroundColor Yellow
}

# Final instructions
Write-Host ""
Write-Host "=== Setup Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Restart Cursor to load the MCP server configuration" -ForegroundColor White
Write-Host "2. Test the integration by asking Cursor about your metrics" -ForegroundColor White
Write-Host "3. Try: 'What metrics do we have in this project?'" -ForegroundColor White
Write-Host ""
Write-Host "Configuration file location: $mcpConfigPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "To test MCP server manually, run:" -ForegroundColor Yellow
Write-Host "  uvx dbt-mcp" -ForegroundColor White
Write-Host ""


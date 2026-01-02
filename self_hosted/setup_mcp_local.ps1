# PowerShell script to set up dbt MCP server from local clone
# Run this script from the MetricFlow POC project root directory

Write-Host "=== dbt MCP Server Setup (Local Clone) ===" -ForegroundColor Cyan
Write-Host ""

# Configuration
$mcpServerPath = "C:\Rif\dbt_mcp\dbt-mcp"
$projectDir = Get-Location
$dbtPath = "C:\Users\Timer\.local\bin\dbt.exe"

# Check if MCP server clone exists
Write-Host "Checking dbt-mcp clone..." -ForegroundColor Yellow
if (Test-Path $mcpServerPath) {
    Write-Host "✓ dbt-mcp clone found at: $mcpServerPath" -ForegroundColor Green
} else {
    Write-Host "✗ dbt-mcp clone not found at: $mcpServerPath" -ForegroundColor Red
    Write-Host "Please clone the repository first:" -ForegroundColor Yellow
    Write-Host "  git clone https://github.com/dbt-labs/dbt-mcp.git C:\Rif\dbt_mcp\dbt-mcp" -ForegroundColor White
    exit 1
}

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Check Python version (dbt-mcp requires >=3.12,<3.14)
$pythonVersionNum = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>&1
$pythonMajor = [int]($pythonVersionNum -split '\.')[0]
$pythonMinor = [int]($pythonVersionNum -split '\.')[1]
if ($pythonMajor -lt 3 -or ($pythonMajor -eq 3 -and $pythonMinor -lt 12)) {
    Write-Host "⚠ Warning: dbt-mcp requires Python >=3.12,<3.14" -ForegroundColor Yellow
    Write-Host "  Your Python version: $pythonVersionNum" -ForegroundColor Yellow
    Write-Host "  You may need to upgrade Python or use a virtual environment with Python 3.12" -ForegroundColor Yellow
}

# Check if dbt is installed
Write-Host "Checking dbt installation..." -ForegroundColor Yellow
if (Test-Path $dbtPath) {
    Write-Host "✓ dbt found at: $dbtPath" -ForegroundColor Green
} else {
    $dbtCmd = Get-Command dbt -ErrorAction SilentlyContinue
    if ($dbtCmd) {
        $dbtPath = $dbtCmd.Source
        Write-Host "✓ dbt found at: $dbtPath" -ForegroundColor Green
    } else {
        Write-Host "✗ dbt not found. Please install dbt-core" -ForegroundColor Red
        exit 1
    }
}

# Check if MetricFlow is installed
Write-Host "Checking MetricFlow installation..." -ForegroundColor Yellow
$mfPath = Get-Command mf -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source
if ($mfPath) {
    Write-Host "✓ MetricFlow found at: $mfPath" -ForegroundColor Green
} else {
    Write-Host "⚠ MetricFlow not found. Install with: pip install dbt-metricflow" -ForegroundColor Yellow
}

# Check if dbt_project.yml exists
Write-Host "Checking dbt project..." -ForegroundColor Yellow
if (Test-Path "dbt_project.yml") {
    Write-Host "✓ dbt_project.yml found" -ForegroundColor Green
} else {
    Write-Host "✗ dbt_project.yml not found. Are you in the project root?" -ForegroundColor Red
    exit 1
}

# Install dbt-mcp in development mode
Write-Host ""
Write-Host "Installing dbt-mcp from local clone..." -ForegroundColor Yellow
Push-Location $mcpServerPath
try {
    # Check if uv is available (recommended)
    $uvInstalled = Get-Command uv -ErrorAction SilentlyContinue
    if ($uvInstalled) {
        Write-Host "Using uv to install dependencies..." -ForegroundColor Yellow
        uv sync
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Dependencies installed with uv" -ForegroundColor Green
            $useUv = $true
        } else {
            Write-Host "⚠ uv sync failed, trying pip..." -ForegroundColor Yellow
            $useUv = $false
        }
    } else {
        Write-Host "uv not found, using pip..." -ForegroundColor Yellow
        $useUv = $false
    }
    
    if (-not $useUv) {
        # Install in development mode with pip
        pip install -e .
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ dbt-mcp installed in development mode" -ForegroundColor Green
        } else {
            Write-Host "✗ Failed to install dbt-mcp" -ForegroundColor Red
            exit 1
        }
    }
} finally {
    Pop-Location
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
            command = "python"
            args = @(
                "-m",
                "dbt_mcp.main"
            )
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

# Test MCP server
Write-Host ""
Write-Host "Testing MCP server..." -ForegroundColor Yellow
$env:DBT_PROJECT_DIR = $projectDir.ToString()
$env:DBT_PROFILES_DIR = $projectDir.ToString()
$env:DBT_PATH = $dbtPath

Push-Location $mcpServerPath
try {
    if ($useUv) {
        $testResult = uv run python -m dbt_mcp.main --help 2>&1
    } else {
        $testResult = python -m dbt_mcp.main --help 2>&1
    }
    if ($LASTEXITCODE -eq 0 -or $testResult -match "usage|help") {
        Write-Host "✓ MCP server can be started" -ForegroundColor Green
    } else {
        Write-Host "⚠ MCP server test inconclusive. Check manually." -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ Could not test MCP server: $_" -ForegroundColor Yellow
} finally {
    Pop-Location
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
Write-Host "MCP server location: $mcpServerPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "To test MCP server manually, run:" -ForegroundColor Yellow
Write-Host "  cd $mcpServerPath" -ForegroundColor White
Write-Host "  python -m dbt_mcp.main" -ForegroundColor White
Write-Host ""


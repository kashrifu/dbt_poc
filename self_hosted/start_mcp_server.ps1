# Start dbt MCP Server with proper environment variables
# Run this script to start the MCP server manually

$env:DBT_PROJECT_DIR = "C:\Rif\dbt_poc\metricflow_poc"
$env:DBT_PROFILES_DIR = "C:\Rif\dbt_poc\metricflow_poc"
$env:DBT_PATH = "C:\Users\Timer\.local\bin\dbt.exe"

Write-Host "Starting dbt MCP Server..." -ForegroundColor Cyan
Write-Host "Project Directory: $env:DBT_PROJECT_DIR" -ForegroundColor Yellow
Write-Host "Profiles Directory: $env:DBT_PROFILES_DIR" -ForegroundColor Yellow
Write-Host "dbt Path: $env:DBT_PATH" -ForegroundColor Yellow
Write-Host ""

cd C:\Rif\dbt_mcp\dbt-mcp
py -3.12 -m dbt_mcp.main


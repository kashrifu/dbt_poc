# Headless BI API Server - Installation Guide

## Quick Install

### Step 1: Install Required Packages

```powershell
pip install mcp fastapi uvicorn requests
```

### Step 2: Install dbt Core (if not already installed)

```powershell
pip install dbt-core dbt-databricks dbt-metricflow
```

### Step 3: Install dbt-mcp from Local Clone

```powershell
cd C:\Rif\dbt_mcp\dbt-mcp
pip install -e .
cd C:\Rif\dbt_poc\metricflow_poc
```

## Complete Installation Command

**All in one command:**

```powershell
pip install mcp fastapi uvicorn requests dbt-core dbt-databricks dbt-metricflow
```

**Then install dbt-mcp:**

```powershell
cd C:\Rif\dbt_mcp\dbt-mcp
pip install -e .
```

## Verify Installation

```powershell
# Check MCP
python -c "import mcp; print('MCP OK')"

# Check FastAPI
python -c "import fastapi; print('FastAPI OK')"

# Check dbt
dbt --version

# Check dbt-mcp
py -3.12 -m dbt_mcp.main --help
```

## Start the Server

```powershell
cd C:\Rif\dbt_poc\metricflow_poc
python headless_bi_api_server.py
```

## Package Versions (Tested)

- `mcp>=1.23.1`
- `fastapi>=0.116.1`
- `uvicorn>=0.31.1`
- `dbt-core>=1.10.17`
- `dbt-databricks>=1.11.0`
- `dbt-metricflow>=0.11.0`
- `requests>=2.32.4`

## Troubleshooting

If you get dependency conflicts:
```powershell
# Install compatible dbt-protos version
pip install "dbt-protos==1.0.382"
```


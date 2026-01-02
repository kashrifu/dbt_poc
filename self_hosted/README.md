# Self-Hosted dbt MetricFlow Implementation

This folder contains all files needed to run a self-hosted dbt MetricFlow semantic layer API.

## Files Overview

### Python API Servers

- **`headless_bi_fastapi_mcp.py`** - Main FastAPI server with MCP integration (recommended)
- **`headless_bi_api_server.py`** - Alternative API server implementation
- **`headless_bi_api_simple.py`** - Simple API server example
- **`headless_bi_example.py`** - Example usage script
- **`headless_bi_mcp_client.py`** - MCP client implementation

### Testing & Setup

- **`test_mcp_connection.py`** - Test MCP connection
- **`test_mcp_manual.py`** - Manual MCP testing script
- **`setup_mcp.ps1`** - PowerShell setup script
- **`setup_mcp_local.ps1`** - Local setup script
- **`start_mcp_server.ps1`** - Start MCP server script

### Configuration

- **`mcp.json`** - MCP server configuration
- **`mcp.json.template`** - MCP configuration template
- **`requirements_headless_bi.txt`** - Python dependencies

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements_headless_bi.txt
   ```

2. **Configure MCP:**
   - Copy `mcp.json.template` to `mcp.json`
   - Update paths in `mcp.json`

3. **Run the API server:**
   ```bash
   python headless_bi_fastapi_mcp.py
   ```

4. **Test the API:**
   ```bash
   python test_mcp_connection.py
   ```

## Documentation

See the main `docs/` folder for detailed guides:
- `docs/HEADLESS_BI_GUIDE.md` - Complete headless BI guide
- `docs/HEADLESS_BI_MCP_USAGE.md` - MCP usage guide
- `docs/INSTALL_HEADLESS_BI.md` - Installation guide
- `docs/DBT_MCP_SETUP.md` - dbt MCP setup
- `docs/SELF_HOSTED_METRICFLOW_ARCHITECTURE.md` - Architecture overview

## API Endpoints

When running `headless_bi_fastapi_mcp.py`, the API provides:

- `GET /health` - Health check
- `GET /metrics` - List all metrics
- `GET /metrics/{metric_name}` - Get metric details
- `POST /metrics/sql` - Generate SQL for metrics
- `GET /semantic-models` - List semantic models
- `GET /dbt/models` - List dbt models
- `GET /dbt/lineage/{model_name}` - Get model lineage

## Requirements

- Python 3.8+
- dbt Core installed
- dbt MetricFlow installed
- dbt project configured
- MCP server (dbt-mcp) installed


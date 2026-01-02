# dbt MCP Server Setup Guide

This guide will help you integrate the dbt Model Context Protocol (MCP) server with your MetricFlow POC project, enabling AI assistants to interact with your dbt project.

## Prerequisites

- Python 3.8+ (you have Python 3.11.8 ✅)
- dbt Core installed (you have dbt installed ✅)
- dbt MetricFlow installed (you have MetricFlow installed ✅)
- Cursor IDE (for MCP integration)

## Installation Options

### Option 1: Using Local Clone (Your Setup)

You have cloned the dbt-mcp repository to `C:\Rif\dbt_mcp\dbt-mcp`. This is the recommended approach for development.

#### Step 1: Install from Local Clone

**Using the setup script:**
```powershell
.\setup_mcp_local.ps1
```

**Or manually:**
```powershell
cd C:\Rif\dbt_mcp\dbt-mcp
pip install -e .
```

This installs dbt-mcp in development mode from your local clone.

### Option 2: Using `uv` (Alternative)

`uv` is a fast Python package manager that dbt Labs recommends for MCP server installation.

#### Step 1: Install `uv`

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Or using pip:**
```bash
pip install uv
```

#### Step 2: Install dbt-mcp

```bash
uvx dbt-mcp --help
```

This will automatically download and run the dbt-mcp server.

### Option 3: Using pip (Alternative)

If you prefer not to use `uv`, you can install directly:

```bash
pip install dbt-mcp
```

Then run:
```bash
dbt-mcp
```

## Configuration

### Step 1: Create MCP Configuration File

Create a file named `.cursor/mcp.json` in your project root (or update Cursor's global MCP settings).

**For Windows, create the file at:**
```
C:\Rif\dbt_poc\metricflow_poc\.cursor\mcp.json
```

**Configuration for Local Clone (Recommended):**

```json
{
  "mcpServers": {
    "dbt": {
      "command": "python",
      "args": ["-m", "dbt_mcp.main"],
      "env": {
        "DBT_PROJECT_DIR": "C:\\Rif\\dbt_poc\\metricflow_poc",
        "DBT_PROFILES_DIR": "C:\\Rif\\dbt_poc\\metricflow_poc",
        "DBT_PATH": "C:\\Users\\Timer\\.local\\bin\\dbt.exe"
      }
    }
  }
}
```

**Or if using uvx:**

```json
{
  "mcpServers": {
    "dbt": {
      "command": "uvx",
      "args": ["dbt-mcp"],
      "env": {
        "DBT_PROJECT_DIR": "C:\\Rif\\dbt_poc\\metricflow_poc",
        "DBT_PROFILES_DIR": "C:\\Rif\\dbt_poc\\metricflow_poc",
        "DBT_PATH": "C:\\Users\\Timer\\.local\\bin\\dbt.exe"
      }
    }
  }
}
```

**Or if using pip installation:**

```json
{
  "mcpServers": {
    "dbt": {
      "command": "dbt-mcp",
      "args": [],
      "env": {
        "DBT_PROJECT_DIR": "C:\\Rif\\dbt_poc\\metricflow_poc",
        "DBT_PROFILES_DIR": "C:\\Rif\\dbt_poc\\metricflow_poc",
        "DBT_PATH": "C:\\Users\\Timer\\.local\\bin\\dbt.exe"
      }
    }
  }
}
```

### Step 2: Configure Cursor Settings

1. Open Cursor Settings (Ctrl+,)
2. Search for "MCP" or "Model Context Protocol"
3. Add the MCP server configuration, or
4. Point to the `.cursor/mcp.json` file you created

**Alternative: Global Cursor Configuration**

You can also configure MCP servers globally in Cursor:
- Go to Settings → Features → MCP Servers
- Add a new server with the configuration above

## Verification

### Test 1: Check MCP Server Installation

```bash
# Using uv
uvx dbt-mcp --help

# Or using pip
dbt-mcp --help
```

### Test 2: Verify dbt Project Access

The MCP server should be able to:
- Read your `dbt_project.yml`
- Parse your semantic models
- List your metrics
- Access your profiles.yml

### Test 3: Test in Cursor

Once configured, try asking Cursor:
- "What metrics do we have in this project?"
- "Show me the semantic models"
- "What's the definition of total_revenue metric?"

## Troubleshooting

### Issue: MCP server not found

**Solution:**
- Ensure `uv` is installed: `uv --version`
- Or ensure `dbt-mcp` is installed: `pip install dbt-mcp`

### Issue: Cannot find dbt project

**Solution:**
- Verify `DBT_PROJECT_DIR` path is correct (use absolute path)
- Ensure the path uses forward slashes or escaped backslashes in JSON
- Check that `dbt_project.yml` exists in that directory

### Issue: Cannot find dbt executable

**Solution:**
- Find your dbt path: `where dbt` (Windows) or `which dbt` (Mac/Linux)
- Update `DBT_PATH` in the configuration
- Ensure dbt is in your PATH

### Issue: Profile not found

**Solution:**
- Set `DBT_PROFILES_DIR` to the directory containing `profiles.yml`
- Or ensure `profiles.yml` is in `~/.dbt/` (default location)

### Issue: MCP server starts but Cursor can't connect

**Solution:**
- Restart Cursor after configuration changes
- Check Cursor's MCP server logs
- Verify the JSON configuration is valid (use a JSON validator)

## What the MCP Server Enables

Once configured, the AI assistant can:

1. **List Metrics**: `list_metrics()` - See all your MetricFlow metrics
2. **List Semantic Models**: `list_semantic_models()` - See your semantic model definitions
3. **Query Metrics**: `query_metric()` - Execute metric queries
4. **Get Lineage**: `get_lineage()` - Understand data dependencies
5. **Read Definitions**: `get_metric_definition()` - Get YAML definitions
6. **Compile SQL**: `compile_sql()` - Generate SQL for metric queries
7. **Run dbt Commands**: Execute dbt parse, run, test, etc.

## Next Steps

1. **Install the MCP server** using one of the methods above
2. **Create the configuration file** with your project paths
3. **Restart Cursor** to load the MCP server
4. **Test the integration** by asking questions about your project
5. **Try the use cases** from `DBT_MCP_USE_CASES.md`

## Additional Resources

- [dbt MCP Documentation](https://docs.getdbt.com/docs/dbt-ai/setup-local-mcp)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Cursor MCP Integration](https://cursor.sh/docs/mcp)

## Project-Specific Notes

Your MetricFlow POC has:
- **15+ metrics** defined in `models/semantic/metrics/revenue.yml`
- **4 semantic models**: orders, customers, stores, visits
- **Conversion metrics**: visit_to_order_conversion_rate_7d, visit_to_order_conversion_rate_30d
- **Multi-hop joins**: Orders → Customers, Orders → Stores

The MCP server will have full access to all of these definitions and can help you:
- Query metrics using natural language
- Understand metric definitions
- Debug metric queries
- Create new metrics following your patterns
- Analyze impact of changes


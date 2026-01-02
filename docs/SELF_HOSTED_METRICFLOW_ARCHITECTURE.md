# Self-Hosted dbt MetricFlow Architecture

## Overview

This document explains how to self-host dbt MetricFlow and create a semantic layer **without using dbt Cloud**. The architecture uses open-source components that you can deploy on your own infrastructure.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CLIENT APPLICATIONS                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │   BI Tools   │  │  Web Apps    │  │  API Clients │                 │
│  │ (Tableau,    │  │  (Custom     │  │  (Python,    │                 │
│  │  Power BI)   │  │   Dashboards)│  │   R, etc.)   │                 │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                 │
│         │                 │                  │                          │
│         └─────────────────┴──────────────────┘                          │
│                            │                                             │
│                            │ HTTP/REST API                               │
└────────────────────────────┼─────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    SEMANTIC LAYER API (FastAPI)                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  FastAPI Application (headless_bi_fastapi_mcp.py)                │  │
│  │  - /metrics              (List all metrics)                     │  │
│  │  - /metrics/{name}       (Get metric details)                   │  │
│  │  - /metrics/sql          (Generate SQL for metrics)             │  │
│  │  - /semantic-models      (List semantic models)                 │  │
│  │  - /dbt/models           (List dbt models)                      │  │
│  │  - /health               (Health check)                         │  │
│  └───────────────────────────────┬──────────────────────────────────┘  │
│                                  │                                       │
│                                  │ MCP Protocol (stdio)                  │
└──────────────────────────────────┼───────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    MCP SERVER (dbt-MCP)                                  │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  dbt_mcp.main (Python Module)                                    │  │
│  │  - Handles MCP protocol communication                            │  │
│  │  - Exposes dbt and MetricFlow tools                              │  │
│  │  - Tools:                                                         │  │
│  │    • metricflow.list_metrics                                     │  │
│  │    • metricflow.generate_sql                                     │  │
│  │    • metricflow.list_semantic_models                             │  │
│  │    • dbt.list_models                                              │  │
│  │    • dbt.get_lineage                                             │  │
│  └───────────────────────────────┬──────────────────────────────────┘  │
│                                  │                                       │
│                                  │ Python API Calls                      │
└──────────────────────────────────┼───────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    DBT METRICFLOW ENGINE                                 │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  dbt-metricflow (Python Package)                                 │  │
│  │  - Parses semantic models (YAML)                                 │  │
│  │  - Parses metrics definitions (YAML)                             │  │
│  │  - Validates metric queries                                      │  │
│  │  - Generates SQL queries                                         │  │
│  │  - Handles multi-hop joins                                       │  │
│  │  - Manages time dimensions                                       │  │
│  └───────────────────────────────┬──────────────────────────────────┘  │
│                                  │                                       │
│                                  │ Reads dbt Project                    │
└──────────────────────────────────┼───────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    DBT PROJECT (Local Filesystem)                       │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  dbt_project.yml              (Project config)                  │  │
│  │  profiles.yml                 (Database connection)              │  │
│  │  models/                                                         │  │
│  │    ├── staging/              (Staging models)                   │  │
│  │    ├── marts/                (Mart models)                      │  │
│  │    └── semantic/             (Semantic layer definitions)      │  │
│  │         ├── semantic_models/ (YAML: entities, dimensions)       │  │
│  │         └── metrics/         (YAML: metric definitions)          │  │
│  │  target/                      (Compiled artifacts)               │  │
│  │    ├── manifest.json         (dbt metadata)                     │  │
│  │    └── semantic_manifest.json (MetricFlow metadata)             │  │
│  └───────────────────────────────┬──────────────────────────────────┘  │
│                                  │                                       │
│                                  │ SQL Execution                         │
└──────────────────────────────────┼───────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    DATA WAREHOUSE                                        │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Databricks / Snowflake / BigQuery / Redshift / etc.             │  │
│  │                                                                  │  │
│  │  Tables:                                                         │  │
│  │  - Raw source tables                                             │  │
│  │  - Staging views (stg_*)                                         │  │
│  │  - Mart tables (fct_*, dim_*)                                    │  │
│  │  - Time spine table                                              │  │
│  │                                                                  │  │
│  │  MetricFlow executes generated SQL against these tables          │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

### 1. **Client Applications** (Top Layer)
- **BI Tools**: Tableau, Power BI, Looker, etc.
- **Custom Web Applications**: React, Vue, or any frontend
- **API Clients**: Python scripts, R scripts, Jupyter notebooks

**Communication**: HTTP REST API calls to FastAPI server

---

### 2. **Semantic Layer API** (FastAPI)
**File**: `headless_bi_fastapi_mcp.py`

**Responsibilities**:
- Expose REST endpoints for metric queries
- Handle HTTP requests/responses
- Manage MCP client connection
- Transform MCP responses to JSON

**Key Endpoints**:
```python
GET  /metrics                    # List all available metrics
GET  /metrics/{metric_name}      # Get metric definition
POST /metrics/sql                # Generate SQL for metric query
GET  /semantic-models            # List semantic models
GET  /dbt/models                 # List dbt models
GET  /health                     # Health check
```

**Technology**: FastAPI (Python web framework)

---

### 3. **MCP Server** (dbt-MCP)
**Module**: `dbt_mcp.main`

**Responsibilities**:
- Implement Model Context Protocol (MCP)
- Bridge between FastAPI and dbt MetricFlow
- Expose dbt and MetricFlow functionality as MCP tools
- Handle stdio-based communication

**MCP Tools Exposed**:
- `metricflow.list_metrics`
- `metricflow.generate_sql`
- `metricflow.list_semantic_models`
- `metricflow.validate_dimensions`
- `dbt.list_models`
- `dbt.get_model`
- `dbt.get_lineage`

**Communication**: MCP protocol over stdio (standard input/output)

---

### 4. **dbt MetricFlow Engine**
**Package**: `dbt-metricflow` (Python package)

**Responsibilities**:
- Parse semantic model YAML files
- Parse metric definition YAML files
- Validate metric queries
- Generate optimized SQL queries
- Handle multi-hop joins automatically
- Manage time dimensions and granularities
- Compile semantic manifest

**Key Files It Reads**:
- `models/semantic/semantic_models/*.yml` - Semantic model definitions
- `models/semantic/metrics/*.yml` - Metric definitions
- `target/manifest.json` - dbt project metadata
- `target/semantic_manifest.json` - Compiled semantic layer metadata

---

### 5. **dbt Project** (Local Filesystem)
**Structure**:
```
metricflow_poc/
├── dbt_project.yml              # Project configuration
├── profiles.yml                 # Database connection credentials
├── models/
│   ├── staging/                 # Staging layer models
│   ├── marts/                   # Mart layer models
│   └── semantic/                # Semantic layer definitions
│       ├── semantic_models/     # Entity and dimension definitions
│       │   └── *.yml
│       └── metrics/             # Metric definitions
│           └── *.yml
└── target/                      # Compiled artifacts
    ├── manifest.json            # dbt metadata
    └── semantic_manifest.json   # MetricFlow metadata
```

**Semantic Model Example** (`models/semantic/semantic_models/orders.yml`):
```yaml
semantic_models:
  - name: orders
    model: ref('fct_orders')
    entities:
      - name: order
        type: primary
      - name: customer
        type: foreign
    dimensions:
      - name: order_date
        type: time
        type_params:
          time_granularity: day
    measures:
      - name: order_total
        agg: sum
        expr: amount
```

**Metric Example** (`models/semantic/metrics/revenue.yml`):
```yaml
metrics:
  - name: total_revenue
    description: Total revenue from all orders
    type: simple
    type_params:
      measure: order_total
```

---

### 6. **Data Warehouse**
**Supported Warehouses**:
- Databricks
- Snowflake
- BigQuery
- Redshift
- Postgres
- DuckDB
- And more...

**What Happens**:
1. MetricFlow generates SQL based on metric query
2. SQL is executed against the warehouse
3. Results are returned to the API
4. API returns JSON response to client

---

## Data Flow Example

### Example: Query "Total Revenue by Date"

```
1. Client Request
   POST /metrics/sql
   {
     "metric_names": ["total_revenue"],
     "dimensions": ["orders__order_date"],
     "time_granularity": "day"
   }

2. FastAPI receives request
   → Calls ensure_mcp() to connect to MCP server
   → Calls mcp_session.call_tool("metricflow.generate_sql", payload)

3. MCP Server (dbt_mcp.main)
   → Receives MCP tool call
   → Calls dbt MetricFlow Python API
   → metricflow.generate_sql(metric_names=["total_revenue"], ...)

4. dbt MetricFlow Engine
   → Reads semantic_manifest.json
   → Finds "total_revenue" metric definition
   → Finds "orders" semantic model
   → Generates SQL:
     SELECT 
       order_date,
       SUM(amount) as total_revenue
     FROM fct_orders
     GROUP BY order_date
   → Returns SQL string

5. MCP Server
   → Returns SQL as MCP response

6. FastAPI
   → Returns JSON: {"sql": "SELECT ..."}

7. Client
   → Receives SQL (can execute directly or via API)
```

---

## Setup Instructions

### Prerequisites
1. **Python 3.8+**
2. **dbt Core** installed
3. **dbt MetricFlow** installed
4. **dbt adapter** for your warehouse (e.g., `dbt-databricks`)
5. **Data warehouse** with connection configured

### Step 1: Install Dependencies

```bash
# Install dbt Core
pip install dbt-core

# Install dbt adapter (choose one)
pip install dbt-databricks    # For Databricks
# OR
pip install dbt-snowflake     # For Snowflake
# OR
pip install dbt-bigquery      # For BigQuery

# Install dbt MetricFlow
pip install dbt-metricflow

# Install FastAPI and MCP dependencies
pip install fastapi uvicorn mcp
```

### Step 2: Configure dbt Project

1. **Create `profiles.yml`** (usually in `~/.dbt/profiles.yml`):
```yaml
metricflow_poc:
  target: dev
  outputs:
    dev:
      type: databricks  # or snowflake, bigquery, etc.
      schema: default
      host: your-warehouse-host
      # ... other connection details
```

2. **Create `dbt_project.yml`**:
```yaml
name: 'metricflow_poc'
version: '1.0.0'
config-version: 2
profile: 'metricflow_poc'

model-paths: ["models"]
target-path: "target"
```

### Step 3: Create Semantic Layer Definitions

1. **Create semantic models** (`models/semantic/semantic_models/orders.yml`):
```yaml
semantic_models:
  - name: orders
    model: ref('fct_orders')
    entities:
      - name: order
        type: primary
    dimensions:
      - name: order_date
        type: time
        type_params:
          time_granularity: day
    measures:
      - name: order_total
        agg: sum
        expr: amount
```

2. **Create metrics** (`models/semantic/metrics/revenue.yml`):
```yaml
metrics:
  - name: total_revenue
    description: Total revenue
    type: simple
    type_params:
      measure: order_total
```

### Step 4: Compile dbt Project

```bash
# Install dbt packages
dbt deps

# Run dbt models
dbt run

# Compile semantic layer (creates semantic_manifest.json)
dbt parse
```

### Step 5: Start FastAPI Server

```bash
# Run the FastAPI server
python headless_bi_fastapi_mcp.py

# Server starts on http://localhost:8080
```

### Step 6: Test the API

```bash
# Health check
curl http://localhost:8080/health

# List metrics
curl http://localhost:8080/metrics

# Generate SQL
curl -X POST http://localhost:8080/metrics/sql \
  -H "Content-Type: application/json" \
  -d '{
    "metric_names": ["total_revenue"],
    "dimensions": ["orders__order_date"]
  }'
```

---

## Key Differences from dbt Cloud

| Aspect | dbt Cloud | Self-Hosted (This Architecture) |
|--------|-----------|--------------------------------|
| **Hosting** | Managed by dbt Labs | Your own infrastructure |
| **Cost** | Subscription-based | Infrastructure costs only |
| **Setup** | Web UI configuration | Manual setup (this guide) |
| **API** | dbt Cloud API | Custom FastAPI server |
| **Authentication** | dbt Cloud auth | Custom auth (to be implemented) |
| **Scalability** | Managed scaling | Manual scaling |
| **Control** | Limited | Full control |
| **Updates** | Automatic | Manual updates |
| **Support** | dbt Labs support | Community/self-support |

---

## Deployment Options

### Option 1: Local Development
- Run FastAPI server locally
- Good for development and testing

### Option 2: Docker Container
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "headless_bi_fastapi_mcp.py"]
```

### Option 3: Cloud VM (AWS EC2, Azure VM, GCP Compute)
- Deploy FastAPI server on VM
- Use systemd or supervisor for process management
- Set up reverse proxy (nginx) for HTTPS

### Option 4: Container Orchestration (Kubernetes)
- Deploy as Kubernetes deployment
- Use ConfigMaps for dbt project files
- Use Secrets for database credentials
- Auto-scaling based on load

### Option 5: Serverless (AWS Lambda, Azure Functions)
- Requires adaptation (MCP may need adjustments)
- Good for low-traffic scenarios

---

## Security Considerations

### 1. **Authentication & Authorization**
- Add API key authentication to FastAPI
- Implement user roles and permissions
- Rate limiting

### 2. **Database Credentials**
- Store `profiles.yml` securely (not in git)
- Use environment variables or secret management
- Rotate credentials regularly

### 3. **Network Security**
- Use HTTPS (TLS/SSL)
- Restrict API access to internal network or VPN
- Firewall rules

### 4. **SQL Injection Prevention**
- MetricFlow handles SQL generation safely
- Validate all API inputs
- Sanitize user-provided filters

---

## Monitoring & Maintenance

### 1. **Health Checks**
- `/health` endpoint for monitoring
- Check MCP connection status
- Monitor dbt project compilation

### 2. **Logging**
- FastAPI logs (uvicorn access logs)
- dbt logs (`logs/dbt.log`)
- MetricFlow logs (`logs/metricflow.log`)

### 3. **Updates**
- Keep dbt Core updated
- Keep dbt MetricFlow updated
- Keep dbt adapters updated
- Test updates in staging first

### 4. **Backup**
- Backup dbt project files (Git)
- Backup `target/` directory (compiled artifacts)
- Backup database credentials

---

## Troubleshooting

### Issue: MCP Connection Fails
**Solution**: 
- Check `DBT_PROJECT_DIR` and `DBT_PROFILES_DIR` environment variables
- Verify dbt is installed and accessible
- Check dbt project compiles: `dbt parse`

### Issue: Metrics Not Found
**Solution**:
- Run `dbt parse` to compile semantic layer
- Check `target/semantic_manifest.json` exists
- Verify metric YAML files are valid

### Issue: SQL Generation Fails
**Solution**:
- Check semantic model definitions
- Verify referenced models exist
- Check dbt models are compiled: `dbt compile`

### Issue: Database Connection Errors
**Solution**:
- Verify `profiles.yml` is correct
- Test connection: `dbt debug`
- Check network connectivity to warehouse

---

## Next Steps

1. **Add Authentication**: Implement API keys or OAuth
2. **Add Caching**: Cache metric definitions and SQL queries
3. **Add Query Execution**: Execute SQL and return results (not just SQL)
4. **Add Metrics Dashboard**: Web UI for exploring metrics
5. **Add CI/CD**: Automate dbt runs and semantic layer updates
6. **Add Monitoring**: Prometheus metrics, Grafana dashboards
7. **Add Load Balancing**: Multiple FastAPI instances behind load balancer

---

## Summary

This architecture provides a **complete self-hosted semantic layer** using:
- **dbt Core** for data transformation
- **dbt MetricFlow** for metric definitions and SQL generation
- **FastAPI** for REST API
- **MCP** for communication between API and dbt
- **Your data warehouse** for data storage and query execution

You have **full control** over the infrastructure, can customize as needed, and avoid vendor lock-in while maintaining all the benefits of dbt MetricFlow's semantic layer capabilities.


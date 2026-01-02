# Headless BI Use Cases with dbt MCP

This guide demonstrates how to build headless BI applications using dbt MCP server to query metrics programmatically.

## What is Headless BI?

Headless BI separates the **data layer** (metrics, semantic models) from the **presentation layer** (dashboards, UI). Instead of using a traditional BI tool, you:

- Query metrics via APIs or code
- Build custom dashboards and applications
- Integrate metrics into your own systems
- Automate reporting and alerting

## Architecture

```
Your Application
    ↓
dbt MCP Server (via MCP Protocol)
    ↓
dbt MetricFlow (Semantic Layer)
    ↓
Data Warehouse (Databricks/Snowflake/etc.)
```

## Use Cases

### 1. Automated Daily Reports

Generate and email daily revenue reports automatically.

**Example:**
```python
# Run: python headless_bi_example.py
# See: generate_daily_revenue_report()
```

**Output:**
- Daily revenue for last 7 days
- Completed vs total revenue
- Order counts

### 2. Real-time Dashboard APIs

Expose metrics as REST APIs for custom dashboards.

**Example:**
```bash
# Start API server
python headless_bi_api_server.py

# Query revenue by store type
curl "http://localhost:8000/api/query/revenue?dimension=store__store_type"

# List all metrics
curl "http://localhost:8000/api/metrics"
```

### 3. Conversion Funnel Analysis

Track conversion rates across different stages.

**Example:**
```python
# See: analyze_conversion_funnel()
# Tracks:
# - Visit → Order conversion (7d, 30d)
# - Order completion rate
# - Credit card adoption rate
```

### 4. Automated Alerting

Monitor metrics and send alerts when thresholds are breached.

**Example:**
```python
# See: check_revenue_threshold()
# Alerts when:
# - Daily revenue < threshold
# - Conversion rate drops
# - Order completion rate decreases
```

### 5. Custom Analysis SQL Generation

Generate SQL for custom analysis without writing it manually.

**Example:**
```python
# See: generate_custom_analysis_sql()
# Returns compiled SQL for:
# - Revenue by store type and customer region
# - Filtered by order status
```

### 6. Mobile App Integration

Build mobile apps that display real-time metrics.

**Example API Call:**
```python
import requests

response = requests.get(
    "http://localhost:8000/api/query/revenue",
    params={
        "dimension": "order__order_date__day",
        "limit": 30
    }
)
data = response.json()
```

## Setup

### Prerequisites

```bash
pip install mcp fastapi uvicorn requests
```

### Running Examples

**1. Basic Example (All Use Cases):**
```bash
python headless_bi_example.py
```

**2. API Server:**
```bash
python headless_bi_api_server.py
# Then visit: http://localhost:8000/docs
```

## API Endpoints

When running the API server:

### List Metrics
```
GET /api/metrics
```

### Query Metrics
```
POST /api/query?metrics=total_revenue&metrics=total_orders&dimensions=store__store_type
```

### Revenue Query (Convenience)
```
GET /api/query/revenue?dimension=store__store_type&store_type=Premium
```

### Get SQL
```
GET /api/sql?metrics=total_revenue&dimensions=store__store_type
```

### Metric Details
```
GET /api/metrics/total_revenue
```

## Integration Examples

### Python Application

```python
from headless_bi_example import DbtMetricQueryClient
import asyncio

async def get_revenue():
    client = DbtMetricQueryClient(
        project_dir=r"C:\Rif\dbt_poc\metricflow_poc",
        profiles_dir=r"C:\Rif\dbt_poc\metricflow_poc",
        dbt_path=r"C:\Users\Timer\.local\bin\dbt.exe"
    )
    
    await client.connect()
    result = await client.query_metrics(
        metrics=["total_revenue"],
        dimensions=["store__store_type"]
    )
    await client.close()
    return result

data = asyncio.run(get_revenue())
```

### JavaScript/TypeScript

```javascript
// Using the API server
const response = await fetch(
  'http://localhost:8000/api/query/revenue?dimension=store__store_type'
);
const data = await response.json();
console.log(data);
```

### Scheduled Reports (Cron/Windows Task Scheduler)

```python
# daily_report.py
import asyncio
from headless_bi_example import DbtMetricQueryClient, generate_daily_revenue_report

async def main():
    client = DbtMetricQueryClient(...)
    await client.connect()
    await generate_daily_revenue_report(client)
    # Send email with report
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Benefits

1. **Flexibility**: Build exactly what you need
2. **Integration**: Embed metrics in any application
3. **Automation**: Schedule reports and alerts
4. **Customization**: Full control over presentation
5. **Consistency**: Use the same metrics everywhere

## Next Steps

1. **Run the examples**: Test the use cases
2. **Customize**: Modify for your specific needs
3. **Deploy**: Set up API server in production
4. **Integrate**: Connect to your applications
5. **Monitor**: Set up alerting and reporting

## Files

- `headless_bi_example.py` - Complete examples of all use cases
- `headless_bi_api_server.py` - REST API server
- `HEADLESS_BI_GUIDE.md` - This guide


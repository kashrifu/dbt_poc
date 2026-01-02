# How Headless BI Uses dbt MCP Server

## Architecture Flow

```
Headless BI Application
    ↓
MCP Client (Python)
    ↓
dbt MCP Server (dbt-mcp)
    ↓
MetricFlow (Semantic Layer)
    ↓
SQL Generation
    ↓
Databricks (Execution)
    ↓
Results Returned
```

## How It Works

### 1. **Headless BI App Connects to MCP Server**

```python
from headless_bi_mcp_client import HeadlessBIClient

client = HeadlessBIClient()
await client.connect()
```

### 2. **Query Metrics (Executes on Databricks)**

```python
# This query executes on Databricks, not in the app
result = await client.query_metrics(
    metrics=["total_revenue", "total_orders"],
    dimensions=["store__store_type"]
)
```

**What happens:**
- MCP server receives the request
- MetricFlow generates optimized SQL
- SQL executes on Databricks
- Results returned to your app

### 3. **Process Results Programmatically**

```python
for row in result["data"]:
    store_type = row["store__store_type"]
    revenue = row["total_revenue"]
    # Process data in your application
    print(f"{store_type}: ${revenue:,.2f}")
```

## Use Cases

### Use Case 1: Automated Reports

```python
async def daily_report():
    client = HeadlessBIClient()
    await client.connect()
    
    # Query executes on Databricks
    result = await client.query_metrics(
        metrics=["total_revenue"],
        dimensions=["order__order_date__day"],
        where="{{ TimeDimension('order__order_date__day') }} = CURRENT_DATE"
    )
    
    # Generate report from results
    generate_pdf_report(result)
    send_email(result)
```

### Use Case 2: Real-time Dashboard

```python
async def update_dashboard():
    client = HeadlessBIClient()
    await client.connect()
    
    # Get dashboard data (executes on Databricks)
    data = await client.query_metrics(
        metrics=["total_revenue", "total_orders"],
        dimensions=["store__store_type"]
    )
    
    # Update dashboard UI
    dashboard.update(data)
```

### Use Case 3: Data Pipeline

```python
async def etl_pipeline():
    client = HeadlessBIClient()
    await client.connect()
    
    # Query metrics (executes on Databricks)
    metrics_data = await client.query_metrics(
        metrics=["total_revenue"],
        dimensions=["order__order_date__month"]
    )
    
    # Transform and load to another system
    transformed = transform(metrics_data)
    load_to_warehouse(transformed)
```

## Key Points

1. **No Browser Needed**: Everything is programmatic
2. **Executes on Databricks**: All queries run on your warehouse
3. **Uses Semantic Layer**: Consistent metric definitions
4. **MCP Protocol**: Standard way to access metrics
5. **Headless**: No UI, just code

## Running Examples

```powershell
# Example 1: Basic usage
python headless_bi_mcp_client.py

# Example 2: Daily report
python -c "import asyncio; from headless_bi_mcp_client import generate_daily_report; asyncio.run(generate_daily_report())"
```

## Benefits

✅ **True Headless**: No API server, no browser  
✅ **Direct Execution**: Queries run on Databricks  
✅ **Semantic Layer**: Uses your metric definitions  
✅ **Programmatic**: Full control in your code  
✅ **Scalable**: MCP server handles connections  


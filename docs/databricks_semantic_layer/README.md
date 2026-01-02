# Databricks Unity Catalog Semantic Layer - Jaffle Shop POC

This project demonstrates Databricks' native semantic layer capabilities using Unity Catalog Metrics and Business Views with the Jaffle Shop dataset.

## Project Structure

```
databricks_semantic_layer/
├── README.md                    # This file
├── business_views/             # SQL views for business-friendly metrics
│   ├── revenue_metrics.sql
│   ├── order_metrics.sql
│   └── customer_metrics.sql
├── metrics/                    # Unity Catalog metric view YAML definitions
│   ├── revenue_metrics.yaml              # Revenue metrics (enhanced format)
│   ├── order_metrics.yaml                 # Order metrics (enhanced format)
│   ├── revenue_metrics_with_stores.yaml   # Revenue with store dimensions
│   ├── revenue_metrics_with_customers.yaml # Revenue with customer dimensions
│   ├── create_metric_views.sql           # SQL with embedded YAML
│   ├── query_examples.sql                 # Query examples
│   ├── YAML_FORMAT_CHECKLIST.md          # Format verification
│   ├── revenue_metrics.sql                # Reference only
│   ├── order_metrics.sql                  # Reference only
│   └── ratio_metrics.sql                  # Reference only
└── scripts/                     # Setup and utility scripts
    ├── setup_tables.sql        # Create base tables (if needed)
    └── grant_permissions.sql   # Unity Catalog permissions
```

## Prerequisites

1. **Databricks Workspace** with Unity Catalog enabled
2. **Unity Catalog Catalog** (e.g., `workspace` or custom catalog)
3. **Schema** in Unity Catalog (e.g., `dbt_poc`)
4. **Base Tables**: The following tables should exist (from dbt project):
   - `fct_orders` - Fact table with order data
   - `dim_customers` - Customer dimension table
   - `dim_stores` - Store dimension table

## Setup

### 1. Ensure Base Tables Exist

The Databricks semantic layer references tables created by the dbt project. Ensure you've run:

```bash
# From the dbt project root
dbt run --select marts
```

This creates:
- `workspace.dbt_poc.fct_orders`
- `workspace.dbt_poc.dim_customers`
- `workspace.dbt_poc.dim_stores`

### 2. Create Business Views

Business views provide SQL interfaces to metrics. Run the SQL files in `business_views/`:

```sql
-- In Databricks SQL Editor or Notebook
-- Run: business_views/revenue_metrics.sql
-- Run: business_views/order_metrics.sql
-- Run: business_views/customer_metrics.sql
```

### 3. Create Unity Catalog Metric Views

Unity Catalog Metric Views are defined in **YAML format**. You have two options:

**Option A: Using Catalog Explorer UI (Recommended)**
1. Navigate to your catalog/schema in Databricks Catalog Explorer
2. Click "+ Create" > "Metric View"
3. Paste the YAML content from:
   - `metrics/revenue_metrics.yaml` - Basic revenue metrics
   - `metrics/order_metrics.yaml` - Order count metrics
   - `metrics/revenue_metrics_with_stores.yaml` - Revenue with store dimensions (multi-hop)
   - `metrics/revenue_metrics_with_customers.yaml` - Revenue with customer dimensions (multi-hop)

**Option B: Using SQL with Embedded YAML**
```sql
-- Run: metrics/create_metric_views.sql
-- This embeds YAML definitions in CREATE VIEW statements
```

### 4. Grant Permissions (Optional)

If you need to share metrics with other users or groups:

```sql
-- Run: scripts/grant_permissions.sql
```

## Business Views

Business views are SQL views that expose pre-aggregated metrics for easy consumption:

### Revenue Metrics View
- `total_revenue` - Sum of all order amounts
- `credit_card_revenue` - Revenue from credit card payments
- `coupon_revenue` - Revenue from coupon payments
- `bank_transfer_revenue` - Revenue from bank transfers
- `completed_revenue` - Revenue from completed orders only

### Order Metrics View
- `total_orders` - Count of distinct orders
- `completed_orders` - Count of completed orders
- `average_order_value` - Average value per order

### Customer Metrics View
- Revenue by customer region
- Order counts by customer region
- Customer-level aggregations

## Unity Catalog Metric Views

Unity Catalog Metric Views provide a native semantic layer with **measures** and **dimensions**:

### Key Features
- **Measures**: Numerical values (SUM, COUNT, AVG, etc.)
- **Dimensions**: Categorical attributes for grouping and filtering
- **Multi-hop Joins**: Support star and snowflake schemas
- **Auto-materialization**: Optional performance optimization

### Defined Measures
- `total_revenue` - Sum of all order amounts
- `credit_card_revenue` - Revenue from credit card payments
- `coupon_revenue` - Revenue from coupon payments
- `bank_transfer_revenue` - Revenue from bank transfers
- `completed_revenue` - Revenue from completed orders
- `total_orders` - Count of distinct orders
- `completed_orders` - Count of completed orders

**Note**: 
- **Ratio and percentage metrics** can be defined as measures with calculated expressions
- **Conversion metrics are fully supported** as percentage measures (e.g., conversion_rate, adoption_rate)
- See `metrics/ratio_measures_example.yaml` for examples
- See `CONVERSION_METRICS_GUIDE.md` for complete guide to conversion metrics
- See `DERIVED_METRICS_GUIDE.md` for guide to derived metrics using MEASURE() function
- See `SUPPORTED_METRIC_TYPES.md` for what is and isn't supported in metric views
- See `LIMITATIONS.md` for complete list of unsupported features (December 2025)
- See `IMPLEMENTATION_REVIEW.md` for comprehensive review of our implementation
- See `WINDOWED_METRICS_NOTE.md` for window function limitations and workarounds

### Usage

Query metric views using the `MEASURE()` function:

```sql
-- Query revenue by month
SELECT 
    order_date_month,
    MEASURE(total_revenue) AS revenue
FROM workspace.dbt_poc.metric_revenue_metrics
GROUP BY order_date_month
ORDER BY order_date_month DESC;

-- Query revenue by store type (with multi-hop join)
SELECT 
    store_type,
    MEASURE(total_revenue) AS revenue
FROM workspace.dbt_poc.metric_revenue_with_stores
GROUP BY store_type;

-- Calculate ratios in queries
SELECT 
    order_date_month,
    MEASURE(total_revenue) / NULLIF(MEASURE(total_orders), 0) AS avg_order_value
FROM workspace.dbt_poc.metric_revenue_metrics
GROUP BY order_date_month;
```

**Important Notes:**
- Always use `MEASURE()` function to aggregate measures
- Must `GROUP BY` dimensions explicitly
- No `SELECT *` allowed - specify dimensions and measures
- See `metrics/query_examples.sql` for more examples

## Comparison: dbt MetricFlow vs Databricks Semantic Layer

| Feature | dbt MetricFlow | Databricks Unity Catalog |
|---------|---------------|-------------------------|
| **Platform** | Multi-warehouse | Databricks only |
| **Definition** | YAML files | YAML files (embedded in CREATE VIEW) |
| **Version Control** | Git (YAML) | Unity Catalog |
| **Access Control** | Warehouse-level | Unity Catalog RBAC |
| **BI Integration** | JDBC/GraphQL | Native Databricks SQL |
| **AI Integration** | GraphQL API | Databricks Assistant |
| **Multi-hop Joins** | Automatic | Manual SQL joins |
| **Metric Types** | Simple, Ratio, Derived, Conversion | Simple, Ratio, Derived |

## Key Differences

### dbt MetricFlow
- ✅ Works across multiple warehouses
- ✅ Metrics as code (YAML in git)
- ✅ Automatic join path detection
- ✅ Rich metric type support
- ❌ Requires dbt infrastructure
- ❌ Extra network hop for queries

### Databricks Unity Catalog
- ✅ Native to Databricks platform
- ✅ Zero external dependencies
- ✅ Unity Catalog governance
- ✅ Direct SQL access
- ❌ Databricks-only
- ❌ Manual join definitions

## Next Steps

1. Run the SQL files to create business views and metrics
2. Query metrics using Databricks SQL Editor
3. Integrate with Databricks Assistant for natural language queries
4. Set up Unity Catalog permissions for team access

## References

- [Databricks Unity Catalog Metric Views Documentation](https://docs.databricks.com/en/metric-views/index.html)
- [Creating Metric Views via UI](https://docs.databricks.com/en/metric-views/create/ui.html)
- [Querying Metric Views](https://docs.databricks.com/en/metric-views/query.html)
- [Unity Catalog Business Semantics](https://docs.databricks.com/en/connect/unity-catalog/business-semantics.html)


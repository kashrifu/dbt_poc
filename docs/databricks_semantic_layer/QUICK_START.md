# Databricks Semantic Layer - Quick Start Guide

## Prerequisites

1. Ensure base tables exist (run from dbt project):
   ```bash
   cd ..  # Go back to dbt project root
   dbt run --select marts
   ```

2. Verify tables in Databricks:
   ```sql
   SHOW TABLES IN workspace.dbt_poc;
   -- Should show: fct_orders, dim_customers, dim_stores
   ```

## Step 1: Create Business Views

Run these SQL files in Databricks SQL Editor or Notebook:

```sql
-- 1. Revenue Metrics View
-- Run: business_views/revenue_metrics.sql

-- 2. Order Metrics View
-- Run: business_views/order_metrics.sql

-- 3. Customer Metrics View
-- Run: business_views/customer_metrics.sql
```

## Step 2: Create Unity Catalog Metric Views

**Option A: Using Catalog Explorer UI (Recommended)**
1. Open Databricks Catalog Explorer
2. Navigate to `workspace.dbt_poc` schema
3. Click "+ Create" > "Metric View"
4. Copy and paste YAML from:
   - `metrics/revenue_metrics.yaml`
   - `metrics/order_metrics.yaml`
   - `metrics/revenue_metrics_with_stores.yaml` (for store dimensions)

**Option B: Using SQL**
```sql
-- Run: metrics/create_metric_views.sql
-- This embeds YAML in CREATE VIEW statements
```

## Step 3: Query Business Views

```sql
-- Query revenue by month and store type
SELECT 
    order_month,
    store_type,
    total_revenue,
    total_orders,
    average_order_value
FROM workspace.dbt_poc.business_revenue_metrics
WHERE order_month >= '2024-01-01'
ORDER BY order_month DESC, total_revenue DESC;

-- Query customer metrics
SELECT 
    customer_region,
    SUM(total_revenue) AS region_revenue,
    SUM(total_orders) AS region_orders,
    AVG(average_order_value) AS avg_aov
FROM workspace.dbt_poc.business_customer_metrics
GROUP BY customer_region;
```

## Step 4: Query Unity Catalog Metric Views

```sql
-- Query revenue by month (use MEASURE() function)
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

-- See metrics/query_examples.sql for more examples
```

## Step 5: Grant Permissions (Optional)

If you need to share with other users:

```sql
-- Run: scripts/grant_permissions.sql
-- Adjust user/group names as needed
```

## Example Queries

### Revenue by Store Type and Month
```sql
SELECT 
    order_month,
    store_type,
    SUM(total_revenue) AS revenue,
    SUM(total_orders) AS orders,
    AVG(average_order_value) AS avg_aov
FROM workspace.dbt_poc.business_revenue_metrics
GROUP BY 1, 2
ORDER BY 1 DESC, 2;
```

### Top Customers by Revenue
```sql
SELECT 
    customer_name,
    customer_region,
    total_revenue,
    total_orders,
    average_order_value
FROM workspace.dbt_poc.business_customer_metrics
ORDER BY total_revenue DESC
LIMIT 10;
```

### Payment Method Analysis
```sql
SELECT 
    order_month,
    SUM(credit_card_revenue) AS cc_revenue,
    SUM(coupon_revenue) AS coupon_revenue,
    SUM(bank_transfer_revenue) AS bank_revenue,
    SUM(credit_card_revenue) / NULLIF(SUM(total_revenue), 0) AS cc_ratio
FROM workspace.dbt_poc.business_revenue_metrics
GROUP BY 1
ORDER BY 1 DESC;
```

## Troubleshooting

### Tables Not Found
- Ensure you've run `dbt run --select marts` from the main project
- Check catalog and schema names match your environment

### Metric Views Not Found
- Verify Unity Catalog is enabled
- Check Databricks Runtime version (13.3+ required for metric views)
- Ensure metric views were created successfully (check Catalog Explorer)
- Verify YAML syntax is correct
- Use `DESCRIBE TABLE EXTENDED workspace.dbt_poc.metric_revenue_metrics AS JSON` to inspect

### Permission Errors
- Run `scripts/grant_permissions.sql`
- Adjust user/group names to match your workspace
- Verify Unity Catalog permissions on underlying tables


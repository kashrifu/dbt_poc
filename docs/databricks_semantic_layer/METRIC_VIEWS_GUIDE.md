# Unity Catalog Metric Views - Complete Guide

## Overview

Unity Catalog Metric Views are a key feature of Databricks' semantic layer, providing a centralized way to define and manage business metrics. They separate **measures** (numerical aggregations) from **dimensions** (categorical attributes) for flexible, governed metric querying.

## Key Concepts

### Measures
Numerical values that summarize business activity:
- Aggregations: `SUM()`, `COUNT()`, `AVG()`, `COUNT(DISTINCT)`
- Examples: `total_revenue`, `order_count`, `average_satisfaction`

### Dimensions
Categorical attributes for grouping and filtering:
- Types: `time`, `categorical`
- Examples: `order_date`, `store_type`, `customer_region`

### Joins
Support for star and snowflake schemas:
- Predefined joins in YAML
- Multi-hop joins to dimension tables
- Automatic join handling at query time

## YAML Structure

### Basic Metric View

```yaml
version: 1.1
source: catalog.schema.table_name
dimensions:
  - name: dimension_name
    expr: column_or_expression
    type: time | categorical
measures:
  - name: measure_name
    expr: aggregation_function(column)
    description: "Optional description"
```

### With Joins

```yaml
version: 1.1
source: catalog.schema.fact_table
joins:
  - name: dimension_alias
    source: catalog.schema.dimension_table
    on: fact_table.key = dimension_alias.key
dimensions:
  - name: dimension_from_fact
    expr: fact_table.column
  - name: dimension_from_join
    expr: dimension_alias.column
measures:
  - name: measure_name
    expr: SUM(fact_table.amount)
```

## Creating Metric Views

### Method 1: Catalog Explorer UI (Recommended)

1. Navigate to your catalog/schema in Databricks
2. Click "+ Create" > "Metric View"
3. Paste your YAML definition
4. Name the metric view (e.g., `metric_revenue_metrics`)
5. Click "Create"

### Method 2: SQL with Embedded YAML

```sql
CREATE OR REPLACE VIEW catalog.schema.metric_view_name AS
$$
version: 1.1
source: catalog.schema.table_name
dimensions:
  - name: order_date_month
    expr: DATE_TRUNC('month', order_date)
    type: time
measures:
  - name: total_revenue
    expr: SUM(amount)
$$
```

## Querying Metric Views

### Basic Query

```sql
SELECT 
    dimension_name,
    MEASURE(measure_name) AS alias
FROM catalog.schema.metric_view_name
GROUP BY dimension_name;
```

### Important Rules

1. **Always use `MEASURE()` function** - Measures must be wrapped in `MEASURE()`
2. **Must GROUP BY dimensions** - All dimensions in SELECT must be in GROUP BY
3. **No `SELECT *`** - Must explicitly list dimensions and measures
4. **Joins predefined** - Joins must be defined in YAML, not in queries

### Examples

```sql
-- Revenue by month
SELECT 
    order_date_month,
    MEASURE(total_revenue) AS revenue
FROM workspace.dbt_poc.metric_revenue_metrics
GROUP BY order_date_month
ORDER BY order_date_month DESC;

-- Multiple measures
SELECT 
    order_date_month,
    MEASURE(total_revenue) AS revenue,
    MEASURE(total_orders) AS orders
FROM workspace.dbt_poc.metric_revenue_metrics
GROUP BY order_date_month;

-- With dimensions from joins
SELECT 
    store_type,
    MEASURE(total_revenue) AS revenue
FROM workspace.dbt_poc.metric_revenue_with_stores
GROUP BY store_type;
```

## Calculating Ratios

Unity Catalog Metric Views don't support ratio metrics that reference other metrics directly. Instead, calculate ratios in your queries:

```sql
SELECT 
    order_date_month,
    MEASURE(total_revenue) / NULLIF(MEASURE(total_orders), 0) AS avg_order_value
FROM workspace.dbt_poc.metric_revenue_metrics
GROUP BY order_date_month;
```

## Multi-Hop Joins

Define joins in the YAML:

```yaml
version: 1.1
source: workspace.dbt_poc.fct_orders
joins:
  - name: stores
    source: workspace.dbt_poc.dim_stores
    on: fct_orders.store_id = stores.store_id
  - name: customers
    source: workspace.dbt_poc.dim_customers
    on: fct_orders.customer_id = customers.customer_id
dimensions:
  - name: store_type
    expr: stores.store_type
  - name: customer_region
    expr: customers.region
measures:
  - name: total_revenue
    expr: SUM(fct_orders.amount)
```

## Auto-Materialization

Metric views can be auto-materialized for performance:

- Precomputes frequent aggregations
- Incremental updates
- Smart query routing
- Configure via Catalog Explorer UI

## Governance

### Permissions

```sql
-- Grant SELECT on metric view
GRANT SELECT ON VIEW catalog.schema.metric_view_name TO `group@company.com`;

-- Grant SELECT on underlying tables
GRANT SELECT ON TABLE catalog.schema.fact_table TO `group@company.com`;
```

### Lineage

Unity Catalog automatically tracks:
- Dependencies on source tables
- Usage in queries and dashboards
- Impact analysis for changes

### Certifications

Mark metric views as certified in Catalog Explorer:
- Indicates trusted, production-ready metrics
- Prioritized in search results
- Visible in lineage

## Best Practices

1. **Naming Convention**: Use `metric_` prefix (e.g., `metric_revenue_metrics`)
2. **Descriptions**: Always include descriptions for measures
3. **Version Control**: Store YAML files in git alongside dbt project
4. **Documentation**: Document metric definitions and business logic
5. **Testing**: Validate metric views with sample queries before production
6. **Performance**: Consider auto-materialization for frequently queried metrics

## Limitations

- ❌ No Delta Sharing support
- ❌ No data profiling
- ❌ Ratio metrics must be calculated in queries
- ❌ No `SELECT *` - explicit dimension/measure listing required
- ❌ Joins must be predefined (no dynamic joins)

## Integration Points

### Databricks Tools
- **SQL Editor**: Direct querying
- **Notebooks**: Use in Python/Scala/R notebooks
- **Dashboards**: Create visualizations
- **Alerts**: Set up metric-based alerts
- **Genie Spaces**: Natural language queries
- **Databricks Assistant**: AI-powered metric discovery

### External Tools
- **JDBC/ODBC**: Connect BI tools (Tableau, Power BI, etc.)
- **REST API**: Programmatic access
- **SQL Warehouse**: Query from external applications

## Troubleshooting

### Metric View Not Found
- Verify Unity Catalog is enabled
- Check Databricks Runtime version (13.3+ required)
- Ensure metric view was created successfully
- Verify catalog/schema names are correct

### Query Errors

**Error: "MEASURE() function not found"**
- Ensure you're querying a metric view, not a regular view
- Check Databricks Runtime version supports metric views

**Error: "Column not found"**
- Verify dimension/measure names match YAML definition
- Check join conditions in YAML

**Error: "GROUP BY required"**
- All dimensions in SELECT must be in GROUP BY
- Measures cannot be in GROUP BY

### Inspecting Metric Views

```sql
-- Get metadata
DESCRIBE TABLE EXTENDED catalog.schema.metric_view_name AS JSON;

-- List metric views
SHOW VIEWS IN catalog.schema;
```

## References

- [Databricks Metric Views Documentation](https://docs.databricks.com/en/metric-views/index.html)
- [Creating Metric Views](https://docs.databricks.com/en/metric-views/create/ui.html)
- [Querying Metric Views](https://docs.databricks.com/en/metric-views/query.html)
- [Unity Catalog Business Semantics](https://docs.databricks.com/en/connect/unity-catalog/business-semantics.html)


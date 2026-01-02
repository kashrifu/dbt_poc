# Windowed Metrics in Unity Catalog Metric Views

## Status: ⚠️ Limited Support

Window functions (rolling windows, period-to-date, cumulative sums) have **limited or no direct support** in Unity Catalog Metric View measure expressions.

## Why?

Metric views are designed for **aggregated measures** that can be grouped by dimensions. Window functions typically require:
- ORDER BY clauses
- PARTITION BY clauses
- ROWS/RANGE specifications

These are more complex than simple aggregations and may not be supported directly in measure expressions.

## Workarounds

### Option 1: Use Business Views

Create a business view with window functions, then aggregate in metric view:

```sql
CREATE VIEW business_rolling_metrics AS
SELECT 
    order_date,
    customer_id,
    amount,
    SUM(amount) OVER (
        PARTITION BY customer_id 
        ORDER BY order_date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_7_day_revenue,
    SUM(amount) OVER (
        PARTITION BY DATE_TRUNC('month', order_date)
        ORDER BY order_date
    ) AS month_to_date_revenue
FROM workspace.dbt_poc.fct_orders;
```

Then create metric view on the business view:

```yaml
version: 1.1
source: workspace.dbt_poc.business_rolling_metrics

measures:
  - name: avg_rolling_7_day_revenue
    expr: AVG(source.rolling_7_day_revenue)
    display_name: Average Rolling 7-Day Revenue
```

### Option 2: Calculate in Queries

Calculate windowed metrics directly in SQL queries:

```sql
SELECT 
    order_date_month,
    MEASURE(total_revenue) AS total_revenue,
    SUM(MEASURE(total_revenue)) OVER (
        ORDER BY order_date_month 
        ROWS UNBOUNDED PRECEDING
    ) AS cumulative_revenue
FROM workspace.dbt_poc.metric_revenue_metrics
GROUP BY order_date_month
ORDER BY order_date_month;
```

### Option 3: Materialized Views

Use Databricks materialized views for pre-computed windowed metrics:

```sql
CREATE MATERIALIZED VIEW rolling_metrics AS
SELECT 
    order_date,
    customer_id,
    SUM(amount) OVER (
        PARTITION BY customer_id 
        ORDER BY order_date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_7_day_revenue
FROM workspace.dbt_poc.fct_orders;
```

## Recommendation

For windowed metrics:
1. **Use business views** for complex window functions
2. **Calculate in queries** for simple windowed aggregations
3. **Use materialized views** for performance-critical windowed metrics

## Testing

To test if window functions work in metric views, try:

```yaml
measures:
  - name: test_window
    expr: SUM(source.amount) OVER (ORDER BY source.order_date)
```

If this fails, window functions are not supported in measure expressions.

## Conclusion

Windowed metrics are **not directly supported** in metric view measure expressions, but can be achieved through:
- ✅ Business views (recommended)
- ✅ Query-level calculations
- ✅ Materialized views

This is a reasonable limitation given the aggregation-focused design of metric views.


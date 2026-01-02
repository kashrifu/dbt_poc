# Unity Catalog Metric Views - Source Alias

## Using `source` Alias

Unity Catalog Metric Views automatically provide `source` as an alias for the main source table. Always use `source.` prefix when referencing columns from the main table.

### ✅ Correct Syntax

```yaml
version: 1.1
source: workspace.dbt_poc.fct_orders

dimensions:
  - name: order_date
    expr: source.order_date  # Use 'source.' prefix

measures:
  - name: total_revenue
    expr: SUM(source.amount)  # Use 'source.' prefix
```

### ❌ Incorrect Syntax

```yaml
version: 1.1
source: workspace.dbt_poc.fct_orders

dimensions:
  - name: order_date
    expr: order_date  # Missing 'source.' prefix
    # OR
    expr: fct_orders.order_date  # Don't use full table name

measures:
  - name: total_revenue
    expr: SUM(amount)  # Missing 'source.' prefix
```

## Join Syntax with Source

When using joins, reference the main table using `source`:

```yaml
version: 1.1
source: workspace.dbt_poc.fct_orders

joins:
  - name: stores
    source: workspace.dbt_poc.dim_stores
    on: source.store_id = stores.store_id  # Use 'source.' for main table

dimensions:
  - name: store_type
    expr: stores.store_type  # Use join alias for joined table
  - name: order_date
    expr: source.order_date   # Use 'source.' for main table
```

## Key Points

1. **Always use `source.` prefix** for columns from the main source table
2. **Use join aliases** (e.g., `stores.`, `customers.`) for columns from joined tables
3. **Never use full table names** (e.g., `fct_orders.amount`) in expressions
4. **Never omit table prefix** (e.g., just `amount`) - always qualify with `source.`

## Examples

### Simple Metric View (No Joins)
```yaml
version: 1.1
source: workspace.dbt_poc.fct_orders

dimensions:
  - name: order_date_month
    expr: DATE_TRUNC('month', source.order_date)
  - name: order_status
    expr: source.status

measures:
  - name: total_revenue
    expr: SUM(source.amount)
  - name: completed_revenue
    expr: SUM(CASE WHEN source.status = 'completed' THEN source.amount ELSE 0 END)
```

### Metric View with Joins
```yaml
version: 1.1
source: workspace.dbt_poc.fct_orders

joins:
  - name: stores
    source: workspace.dbt_poc.dim_stores
    on: source.store_id = stores.store_id

dimensions:
  - name: order_date_month
    expr: DATE_TRUNC('month', source.order_date)  # Main table
  - name: store_type
    expr: stores.store_type  # Joined table

measures:
  - name: total_revenue
    expr: SUM(source.amount)  # Main table
```

## Updated Files

All YAML files have been updated to use `source.` alias:
- ✅ `revenue_metrics.yaml`
- ✅ `order_metrics.yaml`
- ✅ `revenue_metrics_with_stores.yaml`
- ✅ `revenue_metrics_with_customers.yaml`


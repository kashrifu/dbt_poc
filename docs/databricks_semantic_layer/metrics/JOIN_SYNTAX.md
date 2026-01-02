# Unity Catalog Metric Views - Join Syntax

## Correct Join Syntax

Unity Catalog Metric Views use the `on:` keyword for join conditions, not `condition:` or `type:`.

### ✅ Correct Syntax

```yaml
joins:
  - name: stores
    source: workspace.dbt_poc.dim_stores
    on: fct_orders.store_id = stores.store_id
```

### Key Points:

1. **Use `on:` not `condition:`** - The join condition is specified with `on:`
2. **Use join alias in condition** - Reference the joined table using the `name` alias (e.g., `stores.store_id` not `dim_stores.store_id`)
3. **No `type:` needed** - Join type (left/inner/right) is not specified in the YAML (defaults to left join)

### Example: Multi-hop Joins

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
    expr: stores.store_type  # Use join alias
  - name: customer_region
    expr: customers.region   # Use join alias
```

### Common Mistakes

❌ **Wrong:**
```yaml
joins:
  - name: stores
    source: workspace.dbt_poc.dim_stores
    condition: fct_orders.store_id = dim_stores.store_id  # Wrong keyword
    type: left  # Not needed
```

✅ **Correct:**
```yaml
joins:
  - name: stores
    source: workspace.dbt_poc.dim_stores
    on: fct_orders.store_id = stores.store_id  # Use 'on:' and join alias
```

## Updated Files

All YAML files have been updated to use the correct join syntax:
- ✅ `revenue_metrics_with_stores.yaml`
- ✅ `revenue_metrics_with_customers.yaml`
- ✅ `create_metric_views.sql`
- ✅ Documentation files


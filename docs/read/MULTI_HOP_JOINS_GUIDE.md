# MetricFlow Multi-Hop Joins Guide

This guide demonstrates how to use multi-hop joins in MetricFlow to query metrics across related semantic models.

## What are Multi-Hop Joins?

Multi-hop joins allow you to query metrics from one semantic model while grouping by dimensions from another semantic model that is connected through intermediate models.

**Example:**
- **Orders** semantic model (has `customer_id` and `store_id`)
- **Customers** semantic model (has `customer_id` and `customer_region`)
- **Stores** semantic model (has `store_id` and `store_type`)

You can query revenue from Orders grouped by customer region (Orders → Customers) or store type (Orders → Stores).

## Setup in This POC

### Semantic Models Created:

1. **orders** - Fact table with orders, customers, and stores
   - Entities: `order` (primary), `customer` (foreign), `store` (foreign)
   - Measures: `order_total`, `order_count`, etc.
   - Dimensions: `order_date`, `order_status`, etc.

2. **customers** - Customer dimension table
   - Entity: `customer` (primary)
   - Dimensions: `customer_region`, `customer_name`, etc.

3. **stores** - Store dimension table
   - Entity: `store` (primary)
   - Dimensions: `store_type`, `store_region`, `store_name`

### Join Paths:

- **Orders → Customers**: Via `customer_id`
- **Orders → Stores**: Via `store_id`

## Multi-Hop Join Examples

### Example 1: Revenue by Customer Region

Query revenue from Orders grouped by customer region (Orders → Customers):

```bash
mf query --metrics total_revenue --group-by customers__customer_region
```

**What happens:**
1. MetricFlow identifies `total_revenue` is in the `orders` semantic model
2. It sees you want to group by `customers__customer_region`
3. It finds the join path: Orders (customer entity) → Customers (customer entity)
4. It generates SQL with the appropriate join

### Example 2: Revenue by Store Type

Query revenue from Orders grouped by store type (Orders → Stores):

```bash
mf query --metrics total_revenue --group-by stores__store_type
```

**What happens:**
1. MetricFlow identifies `total_revenue` is in the `orders` semantic model
2. It sees you want to group by `stores__store_type`
3. It finds the join path: Orders (store entity) → Stores (store entity)
4. It generates SQL with the appropriate join

### Example 3: Revenue by Store Region

```bash
mf query --metrics total_revenue --group-by stores__store_region
```

### Example 4: Multiple Dimensions from Different Models

```bash
mf query --metrics total_revenue --group-by order__order_date__month,stores__store_type
```

This groups by both order date (from orders) and store type (from stores).

### Example 5: Revenue by Customer Name

```bash
mf query --metrics total_revenue --group-by customers__customer_name
```

## Viewing the Generated SQL

To see how MetricFlow handles multi-hop joins, use `--explain`:

```bash
# See SQL for multi-hop join
mf query --metrics total_revenue --group-by stores__store_type --explain

# See dataflow plan
mf query --metrics total_revenue --group-by stores__store_type --explain --show-dataflow-plan
```

**Expected SQL Structure:**
```sql
WITH orders_base AS (
  SELECT 
    store_id,
    SUM(amount) as order_total
  FROM fct_orders
  GROUP BY store_id
),
stores_dim AS (
  SELECT 
    store_id,
    store_type
  FROM dim_stores
)
SELECT 
  s.store_type,
  o.order_total as total_revenue
FROM orders_base o
JOIN stores_dim s ON o.store_id = s.store_id
GROUP BY s.store_type
```

## Key Requirements for Multi-Hop Joins

### 1. Shared Entities

For multi-hop joins to work, semantic models must share entities:

- **Orders** has: `customer` (foreign) and `store` (foreign)
- **Customers** has: `customer` (primary)
- **Stores** has: `store` (primary)

The shared entity names (`customer`, `store`) enable MetricFlow to find the join path.

### 2. Entity Types

- **Primary entities**: Unique identifiers in dimension tables
- **Foreign entities**: References to primary entities in fact tables

### 3. Naming Convention

When grouping by dimensions from other semantic models, use:
```
{semantic_model_name}__{dimension_name}
```

Examples:
- `customers__customer_region`
- `stores__store_type`
- `stores__store_name`

## Testing Multi-Hop Joins

### Step 1: Build the Models

```bash
# Build dimension tables
dbt run --select dim_customers dim_stores

# Build fact table (if needed)
dbt run --select fct_orders
```

### Step 2: Parse to Validate

```bash
dbt parse
```

### Step 3: Test Queries

```bash
# Test Orders → Stores join
mf query --metrics total_revenue --group-by stores__store_type --explain

# Test Orders → Customers join
mf query --metrics total_revenue --group-by customers__customer_region --explain
```

### Step 4: Run Actual Queries

```bash
# Revenue by store type
mf query --metrics total_revenue --group-by stores__store_type

# Revenue by customer region
mf query --metrics total_revenue --group-by customers__customer_region

# Revenue by store type and month
mf query --metrics total_revenue --group-by stores__store_type,order__order_date__month
```

## Common Multi-Hop Patterns

### Pattern 1: Fact → Dimension (1 Hop)

```
Orders (fact) → Stores (dimension)
```

**Use case**: Revenue by store attributes

### Pattern 2: Fact → Dimension → Dimension (2 Hops)

If you had:
- Orders → Customers → Customer Segments

You could query: Revenue by customer segment

### Pattern 3: Multiple Dimensions from Different Models

```
Orders → Stores (for store_type)
Orders → Customers (for customer_region)
```

**Use case**: Revenue by store type and customer region together

## Troubleshooting

### Error: "No valid join path exists"

**Cause**: Entities don't match between semantic models

**Solution**: 
- Ensure entity names match exactly
- Check entity types (primary vs foreign)
- Verify the join path exists

### Error: "Multiple matching join paths"

**Cause**: Ambiguous join path (rare)

**Solution**: 
- Use explicit semantic model names in group-by
- Check entity relationships

### Performance Issues

**Cause**: Large joins or inefficient paths

**Solution**:
- Use `--explain` to review SQL
- Check if indexes exist on join keys
- Consider materializing intermediate tables

## Best Practices

1. **Name Entities Consistently**: Use the same entity names across related semantic models
2. **Use Descriptive Names**: `customer` not `cust`, `store` not `st`
3. **Document Join Paths**: Add descriptions explaining relationships
4. **Test with Explain**: Always use `--explain` first to validate joins
5. **Optimize Dimension Tables**: Materialize dimension tables for performance

## Summary

Multi-hop joins in MetricFlow enable:
- ✅ Query metrics from fact tables grouped by dimension attributes
- ✅ Automatic join path detection
- ✅ Flexible analysis across related models
- ✅ No manual SQL joins required

The key is ensuring semantic models share entities with matching names, allowing MetricFlow to automatically discover and use the correct join paths.


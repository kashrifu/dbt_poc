# Testing Multi-Hop Joins - Step by Step

## Step 1: Build the Dimension Tables

First, ensure the dimension tables are built:

```bash
dbt run --select dim_customers dim_stores
```

## Step 2: Validate Parsing

Verify that dbt can parse the semantic models:

```bash
dbt parse
```

## Step 3: Test Multi-Hop Joins

### Test 1: Revenue by Store Type (Orders → Stores)

This queries revenue from the `orders` semantic model grouped by `store_type` from the `stores` semantic model.

```bash
# View the SQL that will be generated
mf query --metrics total_revenue --group-by stores__store_type --explain

# Run the actual query
mf query --metrics total_revenue --group-by stores__store_type
```

**Expected**: Revenue aggregated by store type (Premium/Standard)

### Test 2: Revenue by Store Region (Orders → Stores)

```bash
# View SQL
mf query --metrics total_revenue --group-by stores__store_region --explain

# Run query
mf query --metrics total_revenue --group-by stores__store_region
```

**Expected**: Revenue aggregated by store region (North/South/East)

### Test 3: Revenue by Customer Region (Orders → Customers)

This queries revenue from `orders` grouped by `customer_region` from the `customers` semantic model.

```bash
# View SQL
mf query --metrics total_revenue --group-by customers__customer_region --explain

# Run query
mf query --metrics total_revenue --group-by customers__customer_region
```

**Expected**: Revenue aggregated by customer region

### Test 4: Multiple Dimensions from Different Models

Query revenue grouped by both order date (from orders) and store type (from stores):

```bash
# View SQL
mf query --metrics total_revenue --group-by order__order_date__month,stores__store_type --explain

# Run query
mf query --metrics total_revenue --group-by order__order_date__month,stores__store_type
```

**Expected**: Revenue by month and store type

### Test 5: Revenue by Store Name

```bash
# View SQL
mf query --metrics total_revenue --group-by stores__store_name --explain

# Run query
mf query --metrics total_revenue --group-by stores__store_name
```

**Expected**: Revenue by individual store

### Test 6: Multiple Metrics with Multi-Hop

```bash
# View SQL
mf query --metrics total_revenue,total_orders --group-by stores__store_type --explain

# Run query
mf query --metrics total_revenue,total_orders --group-by stores__store_type
```

**Expected**: Both revenue and order count by store type

## Step 4: Verify the Join Path

Use `--show-dataflow-plan` to see how MetricFlow resolves the join:

```bash
mf query --metrics total_revenue --group-by stores__store_type --explain --show-dataflow-plan
```

This shows:
- How MetricFlow finds the join path (Orders → Stores via `store` entity)
- The dataflow transformation steps
- The generated SQL

## Step 5: Validate SQL Output

When you use `--explain`, you should see SQL like:

```sql
-- The SQL should show:
-- 1. Aggregation from orders table
-- 2. Join to stores dimension table
-- 3. Grouping by store attributes
```

## Quick Test Script

Run all tests at once:

```bash
# Test 1: Store Type
echo "=== Test 1: Revenue by Store Type ==="
mf query --metrics total_revenue --group-by stores__store_type --explain

# Test 2: Store Region
echo "=== Test 2: Revenue by Store Region ==="
mf query --metrics total_revenue --group-by stores__store_region --explain

# Test 3: Customer Region
echo "=== Test 3: Revenue by Customer Region ==="
mf query --metrics total_revenue --group-by customers__customer_region --explain

# Test 4: Combined dimensions
echo "=== Test 4: Revenue by Month and Store Type ==="
mf query --metrics total_revenue --group-by order__order_date__month,stores__store_type --explain
```

## Troubleshooting

### Error: "No valid join path exists"

**Check:**
1. Entity names match between semantic models
   - Orders has: `store` (foreign entity)
   - Stores has: `store` (primary entity)
2. Run `dbt parse` to validate configuration

### Error: "Dimension not found"

**Check:**
1. Dimension name is correct: `stores__store_type` (not `store__store_type`)
2. Semantic model name matches: `stores` (from stores.yml)
3. Dimension exists in stores.yml

### No Results Returned

**Check:**
1. Dimension tables have data: `dbt run --select dim_stores dim_customers`
2. Store IDs match between orders and stores
3. Use `--explain` to see the generated SQL

## Success Indicators

✅ **Multi-hop join is working if:**
- `--explain` shows SQL with JOIN to stores/customers tables
- Queries return results grouped by store/customer dimensions
- Dataflow plan shows the join path
- No "no valid join path" errors

## Next Steps

Once multi-hop joins work:
1. Try more complex queries with multiple dimensions
2. Test with different metrics
3. Explore the generated SQL to understand join patterns
4. Test performance with larger datasets


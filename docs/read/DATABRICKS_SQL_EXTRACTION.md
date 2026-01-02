# Extracting SQL from MetricFlow for Databricks

## Method 1: Using `--explain` and Copying SQL

### Step 1: Get the SQL with explain
```bash
mf query --metrics total_revenue --group-by store__store_type --explain
```

### Step 2: Copy the SQL from Output
The output will show the compiled SQL. Copy the SQL portion (the SELECT statement).

### Step 3: Clean for Databricks
Remove the MetricFlow-specific aliases if needed, or use them as-is (they work fine in Databricks).

## Method 2: Save SQL to File

### Option A: Redirect Output
```bash
mf query --metrics total_revenue --group-by store__store_type --explain > query.sql
```

Then open `query.sql` and extract the SQL portion.

### Option B: Use CSV Output (includes SQL in logs)
```bash
mf query --metrics total_revenue --group-by store__store_type --csv results.csv
```

Check the MetricFlow log file for the SQL:
```bash
# SQL is logged in:
logs/metricflow.log
```

## Method 3: Extract from Compiled SQL Files

MetricFlow compiles SQL to dbt's target directory:

```bash
# View compiled SQL
cat target/compiled/metricflow_poc/models/semantic/metrics/*.sql
```

## Method 4: Direct SQL Extraction Script

Create a Python script to extract SQL:

```python
# extract_sql.py
import json
import sys

# Read the semantic manifest
with open('target/semantic_manifest.json', 'r') as f:
    manifest = json.load(f)

# MetricFlow stores query plans here
# You can parse the manifest to extract SQL patterns
```

## Formatting SQL for Databricks

### What Works Directly
- ✅ Standard SQL syntax
- ✅ JOINs (LEFT OUTER JOIN, INNER JOIN, etc.)
- ✅ Aggregations (SUM, COUNT, etc.)
- ✅ GROUP BY, ORDER BY
- ✅ CTEs (WITH clauses)

### Potential Adjustments

#### 1. Table References
MetricFlow generates:
```sql
FROM `workspace`.`dbt_poc`.`fct_orders`
```

For Databricks, this should work as-is if:
- Your catalog is `workspace`
- Your schema is `dbt_poc`
- Your table is `fct_orders`

If you need to change the catalog/schema:
```sql
-- Replace in the SQL:
FROM `your_catalog`.`your_schema`.`fct_orders`
```

#### 2. String Functions
Databricks uses Spark SQL, so some functions might differ:

**If you see PostgreSQL/Snowflake syntax:**
```sql
-- Replace if needed:
CAST(value AS STRING)  -- Databricks
-- vs
CAST(value AS VARCHAR)  -- Other warehouses
```

#### 3. Date Functions
Databricks date functions:
```sql
-- These should work:
DATE_TRUNC('month', order_date)
DATE_FORMAT(order_date, 'yyyy-MM-dd')
```

## Example: Clean SQL for Databricks

### Original MetricFlow SQL:
```sql
SELECT
  stores_src_10000.store_type AS store__store_type
  , SUM(orders_src_10000.amount) AS total_revenue
FROM `workspace`.`dbt_poc`.`fct_orders` orders_src_10000
LEFT OUTER JOIN
  `workspace`.`dbt_poc`.`dim_stores` stores_src_10000
ON
  orders_src_10000.store_id = stores_src_10000.store_id
GROUP BY
  stores_src_10000.store_type
```

### Cleaned for Databricks (optional - aliases work fine):
```sql
SELECT
  s.store_type AS store_type,
  SUM(o.amount) AS total_revenue
FROM `workspace`.`dbt_poc`.`fct_orders` o
LEFT OUTER JOIN
  `workspace`.`dbt_poc`.`dim_stores` s
ON
  o.store_id = s.store_id
GROUP BY
  s.store_type
ORDER BY
  s.store_type
```

## Running in Databricks

### Option 1: Databricks SQL Editor
1. Copy the SQL from MetricFlow
2. Paste into Databricks SQL Editor
3. Adjust catalog/schema if needed
4. Run the query

### Option 2: Databricks Notebook
```python
# In a Databricks notebook
sql_query = """
SELECT
  stores_src_10000.store_type AS store__store_type,
  SUM(orders_src_10000.amount) AS total_revenue
FROM `workspace`.`dbt_poc`.`fct_orders` orders_src_10000
LEFT OUTER JOIN
  `workspace`.`dbt_poc`.`dim_stores` stores_src_10000
ON
  orders_src_10000.store_id = stores_src_10000.store_id
GROUP BY
  stores_src_10000.store_type
"""

df = spark.sql(sql_query)
display(df)
```

### Option 3: Databricks SQL API
Use the SQL API to execute the query programmatically.

## Best Practices

### 1. Always Use `--explain` First
```bash
mf query --metrics total_revenue --group-by store__store_type --explain
```

### 2. Save SQL to File
```bash
# Save full output
mf query --metrics total_revenue --group-by store__store_type --explain > query_output.txt

# Extract just the SQL portion
mf query --metrics total_revenue --group-by store__store_type --explain | grep -A 50 "SELECT" > query.sql
```

### 3. Test in Databricks
- Run the SQL in Databricks SQL Editor first
- Verify results match MetricFlow output
- Check performance

### 4. Parameterize for Reusability
```sql
-- Create a view or function in Databricks
CREATE OR REPLACE VIEW revenue_by_store_type AS
SELECT
  stores_src_10000.store_type AS store_type,
  SUM(orders_src_10000.amount) AS total_revenue
FROM `workspace`.`dbt_poc`.`fct_orders` orders_src_10000
LEFT OUTER JOIN
  `workspace`.`dbt_poc`.`dim_stores` stores_src_10000
ON
  orders_src_10000.store_id = stores_src_10000.store_id
GROUP BY
  stores_src_10000.store_type;
```

## Quick Reference Commands

```bash
# Get SQL for a query
mf query --metrics total_revenue --group-by store__store_type --explain

# Save to file
mf query --metrics total_revenue --group-by store__store_type --explain > databricks_query.sql

# Get SQL with dataflow plan
mf query --metrics total_revenue --group-by store__store_type --explain --show-dataflow-plan

# Multiple metrics
mf query --metrics total_revenue,total_orders --group-by store__store_type --explain
```

## Troubleshooting

### Issue: Catalog/Schema Not Found
**Solution**: Update the table references in the SQL:
```sql
-- Change from:
FROM `workspace`.`dbt_poc`.`fct_orders`

-- To your actual catalog/schema:
FROM `your_catalog`.`your_schema`.`fct_orders`
```

### Issue: Column Not Found
**Solution**: Verify column names match your actual tables:
```sql
-- Check if column exists:
DESCRIBE `workspace`.`dbt_poc`.`fct_orders`;
```

### Issue: Performance Issues
**Solution**: 
- Add WHERE clauses to filter data
- Check if indexes exist on join keys
- Consider partitioning

## Summary

1. **Extract SQL**: Use `--explain` flag
2. **Copy SQL**: From the output
3. **Adjust if needed**: Catalog/schema names
4. **Run in Databricks**: SQL Editor or Notebook
5. **Verify**: Results match MetricFlow output

The SQL MetricFlow generates is standard SQL and should work directly in Databricks with minimal or no modifications!


# MetricFlow SQL Compilation Guide

This guide shows you how to use MetricFlow to compile and view the SQL it generates, so you can trust and validate the queries before execution.

## Why Compile SQL?

- **Trust & Validation**: See exactly what SQL MetricFlow generates
- **Debugging**: Understand why queries behave a certain way
- **Performance**: Review SQL for optimization opportunities
- **Learning**: Understand how MetricFlow translates metrics to SQL
- **Documentation**: Save SQL for reference or sharing

## Methods to View Compiled SQL

### 1. Using `--explain` Flag (Recommended)

The `--explain` flag shows the SQL query that MetricFlow will execute:

```bash
# Basic explain - shows SQL for a simple query
mf query --metrics total_revenue --explain

# Explain with grouping
mf query --metrics total_revenue --group-by order__order_date__day --explain

# Explain with multiple metrics
mf query --metrics total_revenue,total_orders --group-by order__order_date__month --explain

# Explain with filters
mf query --metrics total_revenue --group-by order__order_date__day --where "{{ Dimension('order__order_status') }} = 'completed'" --explain
```

**Output includes:**
- The compiled SQL query
- Query execution plan
- Dataflow information

### 2. Using `--show-dataflow-plan`

Shows the dataflow plan in addition to SQL:

```bash
mf query --metrics total_revenue --group-by order__order_date__day --explain --show-dataflow-plan
```

This provides:
- Step-by-step dataflow transformation
- How metrics are calculated
- Join paths and aggregations

### 3. Using `--display-plans` (Browser View)

Opens an interactive visualization in your browser:

```bash
mf query --metrics total_revenue --group-by order__order_date__day --display-plans
```

**Benefits:**
- Visual representation of the query plan
- Interactive exploration
- Better understanding of complex queries

### 4. Using `--show-sql-descriptions`

Adds inline descriptions to the SQL for better understanding:

```bash
mf query --metrics total_revenue --group-by order__order_date__day --explain --show-sql-descriptions
```

## Practical Examples

### Example 1: Simple Metric Query

```bash
# View SQL for total revenue
mf query --metrics total_revenue --explain
```

**What you'll see:**
- SELECT statement with aggregations
- FROM clause pointing to your semantic model
- Any necessary joins
- WHERE clauses (if filters applied)

### Example 2: Time-Based Grouping

```bash
# View SQL for revenue by date
mf query --metrics total_revenue --group-by order__order_date__day --explain
```

**What you'll see:**
- GROUP BY clause with date dimension
- Date formatting/truncation
- Time-based aggregations

### Example 3: Multiple Metrics

```bash
# View SQL for multiple metrics
mf query --metrics total_revenue,total_orders,average_order_value --group-by order__order_date__month --explain
```

**What you'll see:**
- Multiple aggregations in SELECT
- How ratio metrics are calculated
- Subqueries or CTEs if needed

### Example 4: Filtered Metrics

```bash
# View SQL for filtered metric
mf query --metrics completed_revenue --group-by order__order_date__day --explain
```

**What you'll see:**
- WHERE clause with filter conditions
- How metric filters are applied
- Impact on joins and aggregations

### Example 5: Complex Query with Filters

```bash
# View SQL with custom filters
mf query --metrics total_revenue --group-by order__order_date__day --where "{{ Dimension('order__order_status') }} = 'completed'" --explain
```

**What you'll see:**
- Custom WHERE conditions
- How filters interact with metric definitions
- Filtered aggregations

## Saving Compiled SQL

### Method 1: Redirect Output to File

```bash
# Save SQL to a file
mf query --metrics total_revenue --group-by order__order_date__day --explain > compiled_query.sql

# Or append to a file
mf query --metrics total_revenue --explain >> all_queries.sql
```

### Method 2: Using `--csv` for Results + SQL

```bash
# Get results and SQL
mf query --metrics total_revenue --group-by order__order_date__day --explain --csv results.csv
```

### Method 3: Copy from Terminal

Simply copy the SQL output from the terminal and save it to a file.

## Validating SQL

### Step 1: Compile SQL
```bash
mf query --metrics total_revenue --group-by order__order_date__day --explain
```

### Step 2: Review the SQL
- Check joins are correct
- Verify aggregations match expectations
- Ensure filters are applied correctly
- Review performance implications

### Step 3: Test in Your Warehouse
Copy the SQL and run it directly in your data warehouse to validate:
- Results match expectations
- Performance is acceptable
- No unexpected behavior

### Step 4: Compare with Manual SQL
Write the same query manually and compare:
- Same results?
- Same performance?
- Any differences in logic?

## Understanding Compiled SQL Structure

### Typical SQL Structure:

```sql
-- MetricFlow generates SQL like this:
WITH metric_time__extended AS (
  -- Time dimension preparation
),
metric_time__base AS (
  -- Base aggregations
),
metric_time__final AS (
  -- Final calculations
)
SELECT
  metric_time,
  metric_value
FROM metric_time__final
ORDER BY metric_time
```

### Key Components:

1. **CTEs (Common Table Expressions)**: MetricFlow uses CTEs for clarity
2. **Time Dimensions**: Properly formatted time columns
3. **Aggregations**: SUM, COUNT, AVG based on measure definitions
4. **Joins**: Automatic joins between semantic models
5. **Filters**: Applied at appropriate levels

## Best Practices

### 1. Always Use `--explain` First
```bash
# Before running actual queries, explain them
mf query --metrics total_revenue --explain
```

### 2. Review Complex Queries
```bash
# For complex queries, use dataflow plan
mf query --metrics total_revenue,total_orders,average_order_value --explain --show-dataflow-plan
```

### 3. Validate Performance
- Check for unnecessary joins
- Review aggregation strategies
- Look for optimization opportunities

### 4. Document Important Queries
Save compiled SQL for:
- Performance benchmarks
- Query patterns
- Team reference

### 5. Compare Versions
When metrics change:
```bash
# Before change
mf query --metrics total_revenue --explain > old_query.sql

# After change
mf query --metrics total_revenue --explain > new_query.sql

# Compare differences
diff old_query.sql new_query.sql
```

## Troubleshooting

### SQL Looks Wrong?

1. **Check Semantic Model**: Verify measure definitions
2. **Check Metric Definition**: Review metric YAML
3. **Check Time Dimensions**: Ensure time spine is configured
4. **Check Filters**: Verify filter syntax

### Performance Issues?

1. **Review Joins**: Check if joins are efficient
2. **Check Aggregations**: Look for expensive operations
3. **Review Grouping**: Ensure proper indexing
4. **Check Filters**: Apply filters early if possible

### Understanding Complex SQL?

1. Use `--show-dataflow-plan` for step-by-step view
2. Use `--display-plans` for visual representation
3. Break down into smaller queries
4. Review MetricFlow documentation

## Example Workflow

```bash
# 1. Define your query
METRIC="total_revenue"
GROUP_BY="order__order_date__day"

# 2. Explain first (see SQL without executing)
mf query --metrics $METRIC --group-by $GROUP_BY --explain

# 3. Review the SQL output
# - Check joins
# - Verify aggregations
# - Review filters

# 4. If SQL looks good, run the query
mf query --metrics $METRIC --group-by $GROUP_BY

# 5. Save SQL for reference
mf query --metrics $METRIC --group-by $GROUP_BY --explain > revenue_by_day.sql
```

## Summary

Using MetricFlow's compilation features helps you:
- ✅ **Trust** the generated SQL
- ✅ **Validate** query logic
- ✅ **Debug** issues quickly
- ✅ **Optimize** performance
- ✅ **Document** query patterns
- ✅ **Learn** how MetricFlow works

Always use `--explain` before running production queries to ensure the SQL matches your expectations!


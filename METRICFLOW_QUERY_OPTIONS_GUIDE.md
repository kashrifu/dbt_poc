# MetricFlow Query Options - Complete Guide

This guide covers all available options for the `mf query` command.

## Basic Query Structure

```bash
mf query --metrics <metric_name> [OPTIONS]
```

## Core Options

### 1. `--metrics` (Required)

Specify one or more metrics to query.

**Single metric:**
```bash
mf query --metrics total_revenue
```

**Multiple metrics:**
```bash
mf query --metrics total_revenue,total_orders,average_order_value
```

**Examples:**
```bash
# Single
mf query --metrics total_revenue

# Multiple (comma-separated, no spaces)
mf query --metrics total_revenue,total_orders

# With explain
mf query --metrics total_revenue,total_orders --explain
```

### 2. `--group-by`

Group results by dimensions or entities.

**Single dimension:**
```bash
mf query --metrics total_revenue --group-by order__order_date__day
```

**Multiple dimensions:**
```bash
mf query --metrics total_revenue --group-by order__order_date__month,store__store_type
```

**Examples:**
```bash
# By time dimension
mf query --metrics total_revenue --group-by order__order_date__day

# By categorical dimension
mf query --metrics total_revenue --group-by order__order_status

# By entity (multi-hop)
mf query --metrics total_revenue --group-by store__store_type

# Multiple dimensions
mf query --metrics total_revenue --group-by order__order_date__month,store__store_type,customers__customer_region
```

### 3. `--where` (Filtering)

Add SQL-like WHERE conditions. Use `Dimension()` wrapper for dimensions.

**Single filter:**
```bash
mf query --metrics total_revenue --where "{{ Dimension('order__order_status') }} = 'completed'"
```

**Multiple filters:**
```bash
mf query --metrics total_revenue \
  --where "{{ Dimension('order__order_status') }} = 'completed'" \
  --where "{{ Dimension('order__order_date__day') }} >= '2024-01-01'"
```

**Examples:**
```bash
# Filter by status
mf query --metrics total_revenue --where "{{ Dimension('order__order_status') }} = 'completed'"

# Filter by date range
mf query --metrics total_revenue \
  --where "{{ Dimension('order__order_date__day') }} >= '2024-01-01'" \
  --where "{{ Dimension('order__order_date__day') }} <= '2024-12-31'"

# Filter by amount
mf query --metrics total_revenue --where "{{ Dimension('order__order_total') }} > 100"

# Combined filters
mf query --metrics total_revenue \
  --group-by order__order_date__month \
  --where "{{ Dimension('order__order_status') }} = 'completed'"
```

### 4. `--start-time` and `--end-time`

Filter by time range using ISO8601 timestamps.

**Format:** `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SS`

**Examples:**
```bash
# Start time only
mf query --metrics total_revenue --start-time "2024-01-01"

# End time only
mf query --metrics total_revenue --end-time "2024-12-31"

# Date range
mf query --metrics total_revenue \
  --start-time "2024-01-01" \
  --end-time "2024-12-31"

# With time
mf query --metrics total_revenue \
  --start-time "2024-01-01T00:00:00" \
  --end-time "2024-12-31T23:59:59"

# Combined with group-by
mf query --metrics total_revenue \
  --group-by order__order_date__day \
  --start-time "2024-01-01" \
  --end-time "2024-12-31"
```

### 5. `--limit`

Limit the number of rows returned.

**Examples:**
```bash
# Limit to 10 rows
mf query --metrics total_revenue --limit 10

# Limit with group-by
mf query --metrics total_revenue --group-by order__order_date__day --limit 100

# No limit (default)
mf query --metrics total_revenue
```

### 6. `--order`

Specify sorting order. Use `-` prefix for descending.

**Examples:**
```bash
# Ascending by date (default)
mf query --metrics total_revenue --group-by order__order_date__day --order order__order_date__day

# Descending by date
mf query --metrics total_revenue --group-by order__order_date__day --order -order__order_date__day

# Descending by revenue
mf query --metrics total_revenue --group-by order__order_date__day --order -total_revenue

# Multiple sort columns
mf query --metrics total_revenue --group-by order__order_date__day,store__store_type \
  --order order__order_date__day,-total_revenue

# Sort by metric_time (automatic time dimension)
mf query --metrics total_revenue --group-by order__order_date__day --order -metric_time
```

## Output Options

### 7. `--explain`

Show the SQL query that will be executed.

**Examples:**
```bash
# Basic explain
mf query --metrics total_revenue --explain

# Explain with group-by
mf query --metrics total_revenue --group-by store__store_type --explain

# Explain with filters
mf query --metrics total_revenue \
  --group-by order__order_date__day \
  --where "{{ Dimension('order__order_status') }} = 'completed'" \
  --explain
```

### 8. `--show-dataflow-plan`

Display the dataflow plan in explain output.

**Examples:**
```bash
# Show dataflow plan
mf query --metrics total_revenue --group-by store__store_type \
  --explain --show-dataflow-plan

# See how MetricFlow resolves joins and aggregations
mf query --metrics total_revenue,total_orders \
  --group-by order__order_date__month,store__store_type \
  --explain --show-dataflow-plan
```

### 9. `--display-plans`

Open an interactive visualization in your browser.

**Examples:**
```bash
# Open browser visualization
mf query --metrics total_revenue --group-by store__store_type --display-plans

# Visualize complex queries
mf query --metrics total_revenue,total_orders,average_order_value \
  --group-by order__order_date__month,store__store_type \
  --display-plans
```

### 10. `--show-sql-descriptions`

Add inline descriptions to the SQL output.

**Examples:**
```bash
# SQL with descriptions
mf query --metrics total_revenue --group-by store__store_type \
  --explain --show-sql-descriptions
```

### 11. `--csv`

Write results to a CSV file.

**Examples:**
```bash
# Save to CSV
mf query --metrics total_revenue --group-by order__order_date__day --csv results.csv

# CSV with multiple metrics
mf query --metrics total_revenue,total_orders \
  --group-by order__order_date__month \
  --csv monthly_revenue.csv
```

### 12. `--decimals`

Format numeric values with fixed decimal places.

**Examples:**
```bash
# 2 decimal places
mf query --metrics total_revenue --decimals 2

# 4 decimal places for ratios
mf query --metrics average_order_value --decimals 4
```

### 13. `--quiet`

Minimize console output.

**Examples:**
```bash
# Quiet mode
mf query --metrics total_revenue --quiet

# Quiet with CSV output
mf query --metrics total_revenue --group-by order__order_date__day \
  --csv results.csv --quiet
```

### 14. `--saved-query`

Use a saved query configuration.

**Step 1: Create Saved Query YAML**

Create `models/semantic/saved_queries.yml`:

```yaml
saved_queries:
  - name: monthly_revenue_by_store
    description: "Monthly revenue grouped by store type for completed orders"
    metrics:
      - total_revenue
      - total_orders
    group_by:
      - order__order_date__month
      - store__store_type
    where:
      - "{{ Dimension('order__order_status') }} = 'completed'"
    order_by:
      - order__order_date__month
      - -total_revenue  # Descending
    limit: 100

  - name: daily_revenue_trend
    description: "Daily revenue trend for the last 30 days"
    metrics:
      - total_revenue
    group_by:
      - order__order_date__day
    order_by:
      - order__order_date__day
    limit: 30

  - name: revenue_by_customer_region
    description: "Revenue breakdown by customer region"
    metrics:
      - total_revenue
      - total_orders
    group_by:
      - customers__customer_region
    order_by:
      - -total_revenue
```

**Step 2: Use Saved Queries**

**Examples:**
```bash
# Run saved query
mf query --saved-query monthly_revenue_by_store

# With explain to see SQL
mf query --saved-query monthly_revenue_by_store --explain

# Export to CSV
mf query --saved-query monthly_revenue_by_store --csv monthly_report.csv

# Override saved query settings
mf query --saved-query monthly_revenue_by_store --limit 50

# List all saved queries
mf list saved-queries
```

**Benefits:**
- Reuse complex queries without retyping
- Share standard queries with team
- Maintain consistency across reports
- Easy to update query logic in one place

## Common Query Patterns

### Pattern 1: Basic Metric Query
```bash
mf query --metrics total_revenue
```

### Pattern 2: Time Series Analysis
```bash
mf query --metrics total_revenue \
  --group-by order__order_date__day \
  --start-time "2024-01-01" \
  --end-time "2024-12-31" \
  --order order__order_date__day
```

### Pattern 3: Multi-Dimensional Analysis
```bash
mf query --metrics total_revenue,total_orders \
  --group-by order__order_date__month,store__store_type \
  --order order__order_date__month,-total_revenue
```

### Pattern 4: Filtered Analysis
```bash
mf query --metrics total_revenue \
  --group-by order__order_date__day \
  --where "{{ Dimension('order__order_status') }} = 'completed'" \
  --start-time "2024-01-01"
```

### Pattern 5: Export for Reporting
```bash
mf query --metrics total_revenue,total_orders,average_order_value \
  --group-by order__order_date__month,store__store_type \
  --order order__order_date__month \
  --csv monthly_report.csv \
  --decimals 2
```

### Pattern 6: Debug/Development
```bash
mf query --metrics total_revenue \
  --group-by store__store_type \
  --explain \
  --show-dataflow-plan \
  --show-sql-descriptions
```

## Complete Example

```bash
# Comprehensive query with all options
mf query \
  --metrics total_revenue,total_orders,average_order_value \
  --group-by order__order_date__month,store__store_type \
  --where "{{ Dimension('order__order_status') }} = 'completed'" \
  --start-time "2024-01-01" \
  --end-time "2024-12-31" \
  --order order__order_date__month,-total_revenue \
  --limit 100 \
  --decimals 2 \
  --csv monthly_report.csv \
  --explain
```

## Tips

1. **Always use `--explain` first** to see the SQL before running
2. **Use `--show-dataflow-plan`** to understand complex queries
3. **Combine `--start-time`/`--end-time`** with `--where` for flexible filtering
4. **Use `--csv`** to export results for analysis
5. **Use `--decimals`** for consistent number formatting
6. **Use `--order`** to control result sorting
7. **Use `--limit`** for testing to avoid large result sets

## Summary

| Option | Purpose | Example |
|--------|---------|---------|
| `--metrics` | Specify metrics | `--metrics total_revenue` |
| `--group-by` | Group results | `--group-by order__order_date__day` |
| `--where` | Filter data | `--where "{{ Dimension('order__order_status') }} = 'completed'"` |
| `--start-time` | Start date filter | `--start-time "2024-01-01"` |
| `--end-time` | End date filter | `--end-time "2024-12-31"` |
| `--limit` | Limit rows | `--limit 100` |
| `--order` | Sort results | `--order -total_revenue` |
| `--explain` | Show SQL | `--explain` |
| `--csv` | Export to CSV | `--csv results.csv` |
| `--decimals` | Format numbers | `--decimals 2` |
| `--quiet` | Minimal output | `--quiet` |


# MetricFlow POC - Quick Start Commands

## Installation & Setup

```bash
# Set dbt profiles directory to current folder
set DBT_PROFILES_DIR=.

# Install dbt packages (dbt_utils)
dbt deps

# Load seed data (if using CSV seeds)
dbt seed

# Run all models (staging → marts → semantic)
dbt run

# Run tests on sources and models
dbt test

# Parse project (validate configuration)
dbt parse

# Generate documentation
dbt docs generate

# Serve documentation locally
dbt docs serve
```

## MetricFlow Commands

```bash
# List all available metrics
mf list metrics

# List all dimensions
mf list dimensions

# List all entities
mf list entities

# Query a single metric
mf query --metrics total_revenue

# Query multiple metrics
mf query --metrics total_revenue,total_orders

# Query with grouping by date
mf query --metrics total_revenue --group-by order__order_date__day

# Query with grouping by store type (multi-hop join)
mf query --metrics total_revenue --group-by store__store_type

# Query with date range
mf query --metrics total_revenue --start-time "2024-01-01" --end-time "2024-12-31"

# Query with custom filter
mf query --metrics total_revenue --where "{{ Dimension('order__order_status') }} = 'completed'"

# View generated SQL (for Databricks)
mf query --metrics total_revenue --group-by store__store_type --explain

# View SQL with dataflow plan
mf query --metrics total_revenue --group-by store__store_type --explain --show-dataflow-plan

# Export results to CSV
mf query --metrics total_revenue --group-by order__order_date__month --csv results.csv

# Query with ordering
mf query --metrics total_revenue --group-by order__order_date__day --order -total_revenue

# Query with limit
mf query --metrics total_revenue --group-by order__order_date__day --limit 100
```

## Common Workflows

### Initial Setup
```bash
set DBT_PROFILES_DIR=.
dbt deps
dbt seed          # If using seeds
dbt run
dbt test
dbt parse
```

### Daily Development
```bash
# Run specific models
dbt run --select staging
dbt run --select marts
dbt run --select dim_customers dim_stores

# Test specific models
dbt test --select sources
dbt test --select staging

# Parse to validate
dbt parse
```

### MetricFlow Testing
```bash
# Test basic metric
mf query --metrics total_revenue

# Test multi-hop join
mf query --metrics total_revenue --group-by store__store_type --explain

# Test ratio metric
mf query --metrics average_order_value --group-by order__order_date__month

# Test filtered metric
mf query --metrics completed_revenue --group-by order__order_date__day
```

### SQL Extraction for Databricks
```bash
# Get SQL for a query
mf query --metrics total_revenue --group-by store__store_type --explain > query.sql

# Get SQL with dataflow plan
mf query --metrics total_revenue --group-by store__store_type --explain --show-dataflow-plan
```

## Quick Reference

| Command | Description |
|---------|-------------|
| `set DBT_PROFILES_DIR=.` | Set profiles directory to current folder |
| `dbt deps` | Install dbt packages |
| `dbt seed` | Load seed data from CSV files |
| `dbt run` | Run all models |
| `dbt test` | Run all tests |
| `dbt parse` | Validate project configuration |
| `dbt docs generate` | Generate documentation |
| `dbt docs serve` | Serve docs locally |
| `mf list metrics` | List all available metrics |
| `mf query --metrics <name>` | Query a metric |
| `mf query --explain` | Show generated SQL |
| `mf query --csv <file>` | Export results to CSV |


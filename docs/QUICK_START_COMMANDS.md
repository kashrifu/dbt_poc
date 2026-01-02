# dbt MetricFlow - Complete Setup Guide for Beginners

> **Purpose:** This guide provides step-by-step instructions to set up and run dbt MetricFlow from scratch. Perfect for new team members or anyone starting with MetricFlow.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Project Setup](#project-setup)
4. [Database Connection Configuration](#database-connection-configuration)
5. [Initial Project Run](#initial-project-run)
6. [Understanding the Project Structure](#understanding-the-project-structure)
7. [Working with Metrics](#working-with-metrics)
8. [Common Commands Reference](#common-commands-reference)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, ensure you have:

- ✅ **Python 3.8 or higher** installed
- ✅ **Access to a data warehouse** (Databricks, Snowflake, BigQuery, Redshift, or PostgreSQL)
- ✅ **Database credentials** (host, username, password, schema, etc.)
- ✅ **Command line access** (Terminal on Mac/Linux, PowerShell on Windows)
- ✅ **Git** (if cloning from repository)

### Verify Python Installation

```bash
# Check Python version (should be 3.8+)
python --version

# Or on some systems
python3 --version
```

---

## Installation

### Step 1: Install dbt Core

```bash
# Install dbt Core
pip install dbt-core

# Verify installation
dbt --version
```

**Expected Output:**
```
Core:
  - installed: 1.10.16
  - latest:    1.10.16 - Up to date!
```

---

### Step 2: Install dbt Databricks Adapter

```bash
pip install dbt-databricks
```

### Step 3: Install dbt MetricFlow

```bash
# Install dbt MetricFlow
pip install dbt-metricflow

# Verify installation
mf --version
```

**Expected Output:**
```
MetricFlow version: 0.XXX.X
```

---

### Step 4: Verify All Installations

```bash
# Check dbt version
dbt --version

# Check MetricFlow version
mf --version

# Test dbt connection (will prompt for profile)
dbt debug
```

---

## Project Setup

### Step 1: Navigate to Project Directory

```bash
# Navigate to your project folder
cd path/to/metricflow_poc

# Verify you're in the right directory (should see dbt_project.yml)
ls dbt_project.yml
```

---

### Step 2: Set Profiles Directory (Windows)

```bash
# Windows PowerShell
$env:DBT_PROFILES_DIR = "."

# Windows CMD
set DBT_PROFILES_DIR=.

# Verify it's set
echo $env:DBT_PROFILES_DIR  # PowerShell
echo %DBT_PROFILES_DIR%     # CMD
```

### Set Profiles Directory (Mac/Linux)

```bash
# Mac/Linux
export DBT_PROFILES_DIR=.

# Verify it's set
echo $DBT_PROFILES_DIR
```

**Note:** You'll need to set this every time you open a new terminal, or add it to your shell profile (`.bashrc`, `.zshrc`, etc.)

---

### Step 3: Install dbt Packages

```bash
# Install required packages (dbt_utils, etc.)
dbt deps
```

**Expected Output:**
```
Running with dbt=1.10.16
Installing dbt-utils
  Installed from version 1.1.1
```

---

## Database Connection Configuration

### Step 1: Create profiles.yml

Create a file named `profiles.yml` in your project root directory (same folder as `dbt_project.yml`).

---

### Step 2: Configure Databricks Connection

```yaml
metricflow_poc:
  target: dev
  outputs:
    dev:
      type: databricks
      catalog: your_catalog_name
      host: your-workspace.cloud.databricks.com
      http_path: /sql/1.0/warehouses/your_warehouse_id
      schema: your_schema_name
      token: your_databricks_personal_access_token
      threads: 4
```

**How to get Databricks credentials:**
1. **Host:** Your Databricks workspace URL (e.g., `mycompany.cloud.databricks.com`)
2. **HTTP Path:** Found in SQL Warehouse settings → Connection details
3. **Token:** User Settings → Access Tokens → Generate new token
4. **Catalog & Schema:** Your Unity Catalog catalog and schema names

---

### Step 3: Test Database Connection

```bash
# Test connection (will use profiles.yml in current directory)
dbt debug
```

**Expected Output:**
```
Connection test: [OK connection ok]
All checks passed!
```

**If connection fails:**
- Check your credentials in `profiles.yml`
- Verify network access to your warehouse
- Ensure your user has proper permissions

---

## Initial Project Run

### Step 1: Load Seed Data (If Using CSV Seeds)

```bash
# Load seed data from CSV files
dbt seed
```

**Expected Output:**
```
Running with dbt=1.10.16
Found 3 seed files:
  - raw_customers.csv
  - raw_orders.csv
  - raw_payments.csv
```

**Note:** If you're using existing tables in your database, skip this step and ensure your `sources.yml` points to the correct tables.

---

### Step 2: Run All dbt Models

```bash
# Run all models in order: staging → marts → semantic
dbt run
```

**Expected Output:**
```
Running with dbt=1.10.16
Found 10 models, 3 sources, 0 tests, 3 seeds, 0 snapshots

1 of 10 START sql table model dbt_poc.stg_customers ................ [RUN]
1 of 10 OK created sql table model dbt_poc.stg_customers ........... [SUCCESS]
...
10 of 10 OK created sql view model dbt_poc.time_spine .............. [SUCCESS]

Completed successfully
```

**This will create:**
- Staging layer models (views)
- Marts layer models (tables)
- Semantic layer models (views)
- Time spine table

---

### Step 3: Run Tests

```bash
# Run all tests to validate data quality
dbt test
```

**Expected Output:**
```
Running with dbt=1.10.16
Found 10 models, 3 sources, 5 tests, 3 seeds, 0 snapshots

1 of 5 START test not_null_stg_customers_id ....................... [RUN]
1 of 5 PASS not_null_stg_customers_id ............................. [PASS]
...
5 of 5 PASS unique_fct_orders_order_id ............................ [PASS]

Completed successfully
```

---

### Step 4: Parse Project (Compile Semantic Layer)

```bash
# Parse project to compile semantic layer
dbt parse
```

**This step is critical!** It compiles your semantic models and metrics into `target/semantic_manifest.json`, which MetricFlow uses.

**Expected Output:**
```
Running with dbt=1.10.16
Found 10 models, 3 sources, 5 tests, 3 seeds, 0 snapshots
```

**Verify semantic manifest was created:**
```bash
# Check if semantic_manifest.json exists
ls target/semantic_manifest.json
```

---

### Step 5: Verify MetricFlow Setup

```bash
# List all available metrics
mf list metrics
```

**Expected Output:**
```
Metrics:
  - average_order_value
  - bank_transfer_revenue
  - completed_orders
  - completed_revenue
  - coupon_revenue
  - credit_card_adoption_rate
  - credit_card_payment_ratio
  - credit_card_revenue
  - order_completion_rate
  - revenue_per_customer
  - total_orders
  - total_payment_revenue
  - total_revenue
```

```bash
# List all semantic models
mf list semantic-models
```

**Expected Output:**
```
Semantic Models:
  - customers
  - orders
  - stores
  - visits
```

```bash
# List all dimensions
mf list dimensions
```

```bash
# List all entities
mf list entities
```

---

## Understanding the Project Structure

### Directory Layout

```
metricflow_poc/
├── dbt_project.yml              # Main dbt configuration
├── profiles.yml                  # Database connection (create this)
├── packages.yml                  # dbt package dependencies
├── models/
│   ├── staging/                 # Staging layer (cleans raw data)
│   │   ├── sources.yml          # Source table definitions
│   │   ├── stg_customers.sql
│   │   ├── stg_orders.sql
│   │   └── stg_payments.sql
│   ├── marts/                   # Marts layer (business-ready tables)
│   │   ├── dim_customers.sql
│   │   ├── dim_stores.sql
│   │   ├── fct_orders.sql
│   │   └── fct_visits.sql
│   └── semantic/                # Semantic layer (MetricFlow)
│       ├── semantic_models/     # Define entities, dimensions, measures
│       │   ├── orders.yml
│       │   ├── customers.yml
│       │   ├── stores.yml
│       │   └── visits.yml
│       ├── metrics/            # Define business metrics
│       │   └── revenue.yml
│       ├── time_spine.sql      # Time dimension table
│       └── time_spine.yml      # Time spine configuration
├── seeds/                       # Seed data (CSV files)
│   ├── raw_customers.csv
│   ├── raw_orders.csv
│   └── raw_payments.csv
└── target/                      # Compiled artifacts (auto-generated)
    ├── manifest.json           # dbt metadata
    └── semantic_manifest.json  # MetricFlow metadata
```

### Key Concepts

**Semantic Models** (`models/semantic/semantic_models/*.yml`):
- Define the structure of your data
- Specify entities (primary/foreign keys)
- Define dimensions (time, categorical)
- Define measures (aggregations like SUM, COUNT)

**Metrics** (`models/semantic/metrics/*.yml`):
- Business metrics built on semantic models
- Types: simple, ratio, filtered, conversion
- Examples: total_revenue, average_order_value

**Time Spine** (`models/semantic/time_spine.sql`):
- Table with all dates for time-based queries
- Required for time dimension queries

---

## Working with Metrics

### Basic Metric Queries

#### Query a Single Metric

```bash
# Get total revenue
mf query --metrics total_revenue
```

**Expected Output:**
```
| total_revenue |
|---------------|
| 12345.67      |
```

---

#### Query Multiple Metrics

```bash
# Get multiple metrics at once
mf query --metrics total_revenue,total_orders
```

**Expected Output:**
```
| total_revenue | total_orders |
|---------------|--------------|
| 12345.67      | 99           |
```

---

#### Query with Time Grouping

```bash
# Revenue by day
mf query --metrics total_revenue --group-by order__order_date__day
```

**Expected Output:**
```
| order__order_date__day | total_revenue |
|------------------------|---------------|
| 2024-01-01             | 1234.56       |
| 2024-01-02             | 2345.67       |
| ...                    | ...           |
```

**Available Time Granularities:**
- `order__order_date__day` - Daily
- `order__order_date__week` - Weekly
- `order__order_date__month` - Monthly
- `order__order_date__quarter` - Quarterly
- `order__order_date__year` - Yearly

---

#### Query with Dimension Grouping

```bash
# Revenue by order status
mf query --metrics total_revenue --group-by order__order_status
```

```bash
# Revenue by store type (multi-hop join - automatic!)
mf query --metrics total_revenue --group-by store__store_type
```

```bash
# Revenue by customer region (multi-hop join - automatic!)
mf query --metrics total_revenue --group-by customer__customer_region
```

---

#### Query with Date Range

```bash
# Revenue for specific date range
mf query --metrics total_revenue \
  --start-time "2024-01-01" \
  --end-time "2024-12-31" \
  --group-by order__order_date__month
```

---

#### Query with Filters

```bash
# Revenue for completed orders only
mf query --metrics total_revenue \
  --where "{{ Dimension('order__order_status') }} = 'completed'" \
  --group-by order__order_date__month
```

---

#### Query Ratio Metrics

```bash
# Average order value over time
mf query --metrics average_order_value --group-by order__order_date__month
```

```bash
# Credit card adoption rate
mf query --metrics credit_card_adoption_rate --group-by order__order_date__month
```

---

### View Generated SQL

```bash
# See the SQL that MetricFlow generates
mf query --metrics total_revenue --group-by store__store_type --explain
```

**Useful for:**
- Understanding how MetricFlow generates queries
- Debugging metric queries
- Extracting SQL for BI tools
- Learning multi-hop join logic

---

#### View SQL with Dataflow Plan

```bash
# See SQL with execution plan
mf query --metrics total_revenue --group-by store__store_type \
  --explain --show-dataflow-plan
```

---

### Export Results

```bash
# Export query results to CSV
mf query --metrics total_revenue \
  --group-by order__order_date__month \
  --csv revenue_by_month.csv
```

---

### Advanced Query Options

```bash
# Query with ordering (descending by revenue)
mf query --metrics total_revenue \
  --group-by order__order_date__day \
  --order -total_revenue
```

```bash
# Query with limit (top 10)
mf query --metrics total_revenue \
  --group-by order__order_date__day \
  --limit 10
```

```bash
# Combine multiple options
mf query --metrics total_revenue,total_orders \
  --group-by order__order_date__month \
  --start-time "2024-01-01" \
  --end-time "2024-12-31" \
  --order -total_revenue \
  --limit 5 \
  --csv top_months.csv
```

---

## Common Commands Reference

### dbt Commands

| Command | Description | When to Use |
|---------|-------------|-------------|
| `dbt deps` | Install dbt packages | After cloning project or updating packages.yml |
| `dbt seed` | Load CSV seed data | Initial setup or when seed data changes |
| `dbt run` | Run all models | After code changes or initial setup |
| `dbt run --select staging` | Run only staging models | When testing staging layer |
| `dbt run --select marts` | Run only marts models | When testing marts layer |
| `dbt test` | Run all tests | To validate data quality |
| `dbt parse` | Compile project | **Required after semantic layer changes** |
| `dbt docs generate` | Generate documentation | To create/update docs |
| `dbt docs serve` | Serve docs locally | To view documentation in browser |
| `dbt debug` | Test connection | To verify database connection |

### MetricFlow Commands

| Command | Description | When to Use |
|---------|-------------|-------------|
| `mf list metrics` | List all metrics | To see available metrics |
| `mf list dimensions` | List all dimensions | To see available dimensions |
| `mf list entities` | List all entities | To see available entities |
| `mf list semantic-models` | List semantic models | To see semantic model definitions |
| `mf query --metrics <name>` | Query a metric | To get metric values |
| `mf query --explain` | Show SQL | To see generated SQL |
| `mf query --csv <file>` | Export to CSV | To save results |

---

## Common Workflows

### Initial Setup (First Time)

```bash
# 1. Set profiles directory
set DBT_PROFILES_DIR=.  # Windows
export DBT_PROFILES_DIR=.  # Mac/Linux

# 2. Install packages
dbt deps

# 3. Load seed data (if using)
dbt seed

# 4. Run all models
dbt run

# 5. Run tests
dbt test

# 6. Parse project (compile semantic layer)
dbt parse

# 7. Verify MetricFlow
mf list metrics
```

---

### Daily Development Workflow

```bash
# 1. Make changes to models/metrics

# 2. Run specific models you changed
dbt run --select staging
dbt run --select marts

# 3. If you changed semantic layer, parse again
dbt parse

# 4. Test your metrics
mf query --metrics total_revenue
```

---

### Adding a New Metric

```bash
# 1. Edit models/semantic/metrics/revenue.yml
#    Add your new metric definition

# 2. Parse project to compile
dbt parse

# 3. Verify metric appears
mf list metrics

# 4. Test the metric
mf query --metrics your_new_metric
```

---

### Testing Multi-hop Joins

```bash
# Test automatic join to stores
mf query --metrics total_revenue --group-by store__store_type --explain

# Test automatic join to customers
mf query --metrics total_revenue --group-by customer__customer_region --explain
```

---

### Extracting SQL for BI Tools

```bash
# Get SQL for Tableau/Power BI
mf query --metrics total_revenue \
  --group-by order__order_date__month,store__store_type \
  --explain > revenue_query.sql
```

---

## Troubleshooting

### Issue: "Profile not found"

**Error:**
```
Runtime Error
  Profile 'metricflow_poc' not found
```

**Solution:**
```bash
# Ensure profiles.yml exists in project root
ls profiles.yml

# Set profiles directory
set DBT_PROFILES_DIR=.  # Windows
export DBT_PROFILES_DIR=.  # Mac/Linux

# Test connection
dbt debug
```

---

### Issue: "Connection test failed"

**Error:**
```
Connection test: [ERROR connection failed]
```

**Solution:**
1. Check `profiles.yml` credentials
2. Verify network access to warehouse
3. Test connection manually (e.g., Databricks SQL Editor)
4. Check user permissions

---

### Issue: "Metric not found"

**Error:**
```
Metric 'total_revenue' not found
```

**Solution:**
```bash
# 1. Ensure you've parsed the project
dbt parse

# 2. Verify semantic_manifest.json exists
ls target/semantic_manifest.json

# 3. List available metrics
mf list metrics

# 4. Check metric name spelling
```

---

### Issue: "Semantic model not found"

**Error:**
```
Semantic model 'orders' not found
```

**Solution:**
```bash
# 1. Ensure semantic models are defined
ls models/semantic/semantic_models/*.yml

# 2. Run dbt parse
dbt parse

# 3. List semantic models
mf list semantic-models
```

---

### Issue: "Dimension not found"

**Error:**
```
Dimension 'order__order_date__day' not found
```

**Solution:**
```bash
# 1. Check dimension name format: semantic_model__dimension__granularity
#    Example: order__order_date__day

# 2. List available dimensions
mf list dimensions

# 3. Verify semantic model has time dimension defined
cat models/semantic/semantic_models/orders.yml
```

---

### Issue: "Models not found in database"

**Error:**
```
Model 'fct_orders' not found in database
```

**Solution:**
```bash
# 1. Run dbt models first
dbt run

# 2. Verify models exist
dbt run --select fct_orders

# 3. Check database schema
dbt show --select fct_orders
```

---

### Issue: "Time spine not found"

**Error:**
```
Time spine table not found
```

**Solution:**
```bash
# 1. Run time spine model
dbt run --select time_spine

# 2. Verify time_spine.yml is configured
cat models/semantic/time_spine.yml
```

---

## Quick Reference Cheat Sheet

### Setup Commands
```bash
set DBT_PROFILES_DIR=.
dbt deps
dbt seed
dbt run
dbt test
dbt parse
```

### MetricFlow Discovery
```bash
mf list metrics
mf list dimensions
mf list entities
mf list semantic-models
```

### Basic Queries
```bash
mf query --metrics total_revenue
mf query --metrics total_revenue --group-by order__order_date__month
mf query --metrics total_revenue --group-by store__store_type
```

### SQL Extraction
```bash
mf query --metrics total_revenue --group-by store__store_type --explain
```

---

## Next Steps

After completing this setup:

1. ✅ **Explore Metrics:** Try querying different metrics
2. ✅ **Understand Semantic Models:** Review `models/semantic/semantic_models/*.yml`
3. ✅ **Understand Metrics:** Review `models/semantic/metrics/*.yml`
4. ✅ **Read Documentation:** Run `dbt docs serve` and explore
5. ✅ **Create Your Own Metrics:** Add new metrics to `revenue.yml`
6. ✅ **Test Multi-hop Joins:** Query metrics with different dimensions

---

## Additional Resources

- **dbt Documentation:** https://docs.getdbt.com
- **MetricFlow Documentation:** https://docs.getdbt.com/docs/build/metricflows
- **dbt Community:** https://getdbt.com/community
- **Project README:** See `README.md` in project root

---

## Support

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section above
2. Review error messages carefully
3. Verify all prerequisites are met
4. Check `dbt debug` output
5. Consult project documentation
6. Ask your team lead or data engineering team

---

**Last Updated:** 2024
**Version:** 1.0

# dbt MetricFlow Setup with Databricks - Step by Step Guide

> **Project:** metricflow_poc  
> **Warehouse:** Databricks with Unity Catalog  
> **Purpose:** Complete setup from installation to running your first metric query

---

## Prerequisites

- Python 3.8 or higher
- Databricks workspace with Unity Catalog enabled
- Databricks Personal Access Token (PAT)
- SQL Warehouse in Databricks
- Access to create schemas in Unity Catalog

---

## Step 1: Install Required Packages

### Install dbt Core

```bash
pip install dbt-core
```

Verify:
```bash
dbt --version
```

### Install dbt Databricks Adapter

```bash
pip install dbt-databricks
```

### Install dbt MetricFlow

```bash
pip install dbt-metricflow
```

Verify:
```bash
mf --version
```

---

## Step 2: Configure Databricks Connection

### Get Databricks Credentials

1. **Workspace Host:** Your Databricks URL (e.g., `mycompany.cloud.databricks.com`)
2. **SQL Warehouse HTTP Path:** 
   - Go to SQL Warehouses → Your warehouse → Connection details
   - Copy HTTP path (e.g., `/sql/1.0/warehouses/abc123def456`)
3. **Personal Access Token:**
   - User Settings → Access Tokens → Generate new token
   - Copy token immediately
4. **Unity Catalog Info:**
   - Catalog name (e.g., `workspace`, `main`, or custom)
   - Schema name (e.g., `metricflow_poc`)

### Create profiles.yml

Create `profiles.yml` in project root:

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

**Replace:**
- `your_catalog_name` → Your Unity Catalog catalog
- `your-workspace.cloud.databricks.com` → Your workspace host
- `/sql/1.0/warehouses/your_warehouse_id` → Your warehouse HTTP path
- `your_schema_name` → Your target schema (e.g., `metricflow_poc`)
- `your_databricks_personal_access_token` → Your PAT

### Set Profiles Directory

**Windows PowerShell:**
```powershell
$env:DBT_PROFILES_DIR = "."
```

**Windows CMD:**
```cmd
set DBT_PROFILES_DIR=.
```

**Mac/Linux:**
```bash
export DBT_PROFILES_DIR=.
```

### Test Connection

```bash
dbt debug
```

Should show: `Connection test: [OK connection ok]`

---

## Step 3: Project Setup

### Navigate to Project

```bash
cd path/to/metricflow_poc
```

### Install dbt Packages

```bash
dbt deps
```

This installs `dbt_utils` (version 1.3.3) as defined in `packages.yml`.

---

## Step 4: Load Seed Data

The project uses seed files to create initial tables in Databricks.

### Available Seed Files

- `seeds/raw_customers.csv` - Customer data
- `seeds/raw_orders.csv` - Order data  
- `seeds/raw_products.csv` - Product data
- `seeds/raw_stores.csv` - Store data
- `seeds/raw_items.csv` - Order items
- `seeds/raw_supplies.csv` - Supply data

### Load Seeds

```bash
dbt seed
```

**What this does:**
- Creates tables in your Databricks schema from CSV files
- Tables: `raw_customers`, `raw_orders`, `raw_products`, `raw_stores`, `raw_items`, `raw_supplies`
- These become source tables referenced in `models/staging/sources.yml`

**Expected Output:**
```
Running with dbt=1.10.16
Found 6 seed files:
  - raw_customers.csv
  - raw_orders.csv
  - raw_products.csv
  - raw_stores.csv
  - raw_items.csv
  - raw_supplies.csv
```

---

## Step 5: Run dbt Models

### Run All Models

```bash
dbt run
```

**Execution Order:**
1. **Staging Layer** (views):
   - `stg_customers` - Cleans customer data
   - `stg_orders` - Cleans order data
   - `stg_payments` - Cleans payment data

2. **Marts Layer** (tables):
   - `dim_customers` - Customer dimension
   - `dim_stores` - Store dimension
   - `fct_orders` - Orders fact table
   - `fct_visits` - Visits fact table

3. **Semantic Layer** (views):
   - `time_spine` - Time dimension table (materialized as table)

**Expected Output:**
```
Running with dbt=1.10.16
Found 10 models, 3 sources, 5 tests, 6 seeds, 0 snapshots

1 of 10 START sql view model metricflow_poc.stg_customers ........... [RUN]
1 of 10 OK created sql view model metricflow_poc.stg_customers ..... [SUCCESS]
...
10 of 10 OK created sql table model metricflow_poc.time_spine ...... [SUCCESS]

Completed successfully
```

### Verify Models Created

Check in Databricks:
- Catalog: Your catalog name
- Schema: Your schema name (e.g., `metricflow_poc`)
- Tables/Views: Should see all models listed above

---

## Step 6: Run Tests

```bash
dbt test
```

**Tests Defined:**
- Source tests: `unique`, `not_null` on `raw_customers.id`, `raw_orders.id`
- Relationship tests: `raw_orders.customer` → `raw_customers.id`
- Model tests: Various data quality checks

**Expected Output:**
```
Running with dbt=1.10.16
Found 10 models, 3 sources, 5 tests, 6 seeds, 0 snapshots

1 of 5 START test unique_raw_customers_id .......................... [RUN]
1 of 5 PASS unique_raw_customers_id ................................ [PASS]
...
5 of 5 PASS unique_fct_orders_order_id ............................ [PASS]

Completed successfully
```

---

## Step 7: Compile Semantic Layer

**Critical Step for MetricFlow!**

```bash
dbt parse
```

**What this does:**
- Compiles semantic models from `models/semantic/semantic_models/*.yml`
- Compiles metrics from `models/semantic/metrics/*.yml`
- Creates `target/semantic_manifest.json` - used by MetricFlow

**Verify:**
```bash
ls target/semantic_manifest.json
```

Should show the file exists.

---

## Step 8: Verify MetricFlow Setup

### List Available Metrics

```bash
mf list metrics
```

**Expected Metrics:**
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

### List Semantic Models

```bash
mf list semantic-models
```

**Expected:**
```
Semantic Models:
  - customers
  - orders
  - stores
  - visits
  - time_spine
```

### List Dimensions

```bash
mf list dimensions
```

**Expected Dimensions from orders semantic model:**
- `order__order_date` (day, week, month, quarter, year)
- `order__order_status`
- `order__customer_first_name`
- `order__customer_last_name`

### List Entities

```bash
mf list entities
```

**Expected:**
- `order` (primary)
- `customer` (foreign)
- `store` (foreign)

---

## Step 9: Run Your First Metric Query

### Simple Metric Query

```bash
mf query --metrics total_revenue
```

**Expected Output:**
```
| total_revenue |
|---------------|
| 12345.67      |
```

### Query with Time Grouping

```bash
mf query --metrics total_revenue --group-by order__order_date__month
```

**Expected Output:**
```
| order__order_date__month | total_revenue |
|--------------------------|---------------|
| 2024-09-01               | 1234.56       |
| 2024-10-01               | 2345.67       |
| ...                      | ...           |
```

### Query Multiple Metrics

```bash
mf query --metrics total_revenue,total_orders
```

### Query with Dimension Grouping

```bash
mf query --metrics total_revenue --group-by order__order_status
```

### Query with Multi-hop Join (Automatic!)

```bash
mf query --metrics total_revenue --group-by store__store_type
```

This automatically joins `fct_orders` → `dim_stores` via the `store` entity!

### View Generated SQL

```bash
mf query --metrics total_revenue --group-by store__store_type --explain
```

Shows the SQL that MetricFlow generates for Databricks.

---

## Project Structure Overview

### Directory Layout

```
metricflow_poc/
├── dbt_project.yml              # Project config (profile: metricflow_poc)
├── profiles.yml                  # Databricks connection (create this)
├── packages.yml                  # dbt_utils 1.3.3
├── models/
│   ├── staging/                 # Staging views
│   │   ├── sources.yml          # Source: jaffle_shop.raw_customers, raw_orders
│   │   ├── stg_customers.sql
│   │   ├── stg_orders.sql
│   │   └── stg_payments.sql
│   ├── marts/                   # Mart tables
│   │   ├── dim_customers.sql
│   │   ├── dim_stores.sql
│   │   ├── fct_orders.sql       # Main fact table for metrics
│   │   └── fct_visits.sql
│   └── semantic/                # MetricFlow semantic layer
│       ├── semantic_models/
│       │   ├── orders.yml       # Orders semantic model
│       │   ├── customers.yml
│       │   ├── stores.yml
│       │   └── visits.yml
│       ├── metrics/
│       │   └── revenue.yml      # 13 metrics defined
│       ├── time_spine.sql       # Time dimension (2020-01-01 to 2025-12-31)
│       └── time_spine.yml
├── seeds/                       # Seed data
│   ├── raw_customers.csv
│   ├── raw_orders.csv
│   ├── raw_products.csv
│   ├── raw_stores.csv
│   ├── raw_items.csv
│   └── raw_supplies.csv
└── target/                      # Compiled artifacts
    ├── manifest.json
    └── semantic_manifest.json   # MetricFlow metadata
```

### Key Files

**dbt_project.yml:**
- Project name: `metricflow_poc`
- Profile: `metricflow_poc`
- Staging: views
- Marts: tables
- Semantic: views (except time_spine: table)

**models/staging/sources.yml:**
- Source: `jaffle_shop`
- Tables: `raw_customers`, `raw_orders`
- Uses variables: `{{ var('source_database', target.database) }}`

**models/semantic/semantic_models/orders.yml:**
- Model: `ref('fct_orders')`
- Entities: `order` (primary), `customer` (foreign), `store` (foreign)
- Dimensions: `order_date` (time), `order_status` (categorical)
- Measures: `order_total`, `order_count`, `credit_card_amount`, etc.

**models/semantic/metrics/revenue.yml:**
- 13 metrics defined
- Types: simple, ratio, filtered

**models/semantic/time_spine.yml:**
- Time spine: 2020-01-01 to 2025-12-31
- Daily granularity

---

## Databricks Schema Structure

After running `dbt run`, your Databricks schema will contain:

### Seed Tables (from dbt seed)
- `raw_customers`
- `raw_orders`
- `raw_products`
- `raw_stores`
- `raw_items`
- `raw_supplies`

### Staging Views (from dbt run)
- `stg_customers`
- `stg_orders`
- `stg_payments`

### Mart Tables (from dbt run)
- `dim_customers`
- `dim_stores`
- `fct_orders` ← **Main fact table for metrics**
- `fct_visits`

### Semantic Layer (from dbt run)
- `time_spine` (table) ← Time dimension table

**Full Path Example:**
```
your_catalog.your_schema.fct_orders
your_catalog.your_schema.time_spine
```

---

## Common Workflows

### Daily Development

```bash
# 1. Make changes to models/metrics

# 2. Run specific models
dbt run --select staging
dbt run --select marts

# 3. If semantic layer changed, re-parse
dbt parse

# 4. Test metrics
mf query --metrics total_revenue
```

### Adding a New Metric

1. Edit `models/semantic/metrics/revenue.yml`
2. Add metric definition
3. Run `dbt parse`
4. Verify: `mf list metrics`
5. Test: `mf query --metrics your_new_metric`

### Query Examples

**Revenue by month:**
```bash
mf query --metrics total_revenue --group-by order__order_date__month
```

**Revenue by store type (multi-hop):**
```bash
mf query --metrics total_revenue --group-by store__store_type
```

**Ratio metric:**
```bash
mf query --metrics average_order_value --group-by order__order_date__month
```

**Filtered metric:**
```bash
mf query --metrics completed_revenue --group-by order__order_date__day
```

**View SQL:**
```bash
mf query --metrics total_revenue --group-by store__store_type --explain
```

---

## Quick Reference

### Essential Commands

| Command | Purpose |
|---------|---------|
| `set DBT_PROFILES_DIR=.` | Set profiles directory (Windows) |
| `export DBT_PROFILES_DIR=.` | Set profiles directory (Mac/Linux) |
| `dbt deps` | Install packages |
| `dbt seed` | Load seed data |
| `dbt run` | Run all models |
| `dbt test` | Run tests |
| `dbt parse` | Compile semantic layer |
| `mf list metrics` | List available metrics |
| `mf query --metrics total_revenue` | Query a metric |

### Project Configuration

- **Project Name:** `metricflow_poc`
- **Profile:** `metricflow_poc`
- **Source:** `jaffle_shop` (raw_customers, raw_orders)
- **Main Fact Table:** `fct_orders`
- **Semantic Model:** `orders` (references fct_orders)
- **Time Spine:** 2020-01-01 to 2025-12-31

---

## Next Steps

1. ✅ Explore all metrics: `mf list metrics`
2. ✅ Query different metrics with various dimensions
3. ✅ Test multi-hop joins (orders → stores, orders → customers)
4. ✅ Review semantic models: `models/semantic/semantic_models/*.yml`
5. ✅ Review metrics: `models/semantic/metrics/revenue.yml`
6. ✅ Generate docs: `dbt docs generate && dbt docs serve`
7. ✅ Extract SQL for BI tools using `--explain` flag

---

**Project:** metricflow_poc  
**Last Updated:** 2024

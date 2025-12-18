# MetricFlow POC with Jaffle Shop Data

This is a Proof of Concept (POC) project demonstrating MetricFlow integration with dbt using the Jaffle Shop dataset.

## Project Structure

```
metricflow_poc/
├── dbt_project.yml              # Main dbt configuration
├── packages.yml                  # dbt package dependencies
├── models/
│   ├── staging/                 # Staging layer models
│   │   ├── sources.yml          # Source definitions for raw data
│   │   ├── stg_customers.sql
│   │   ├── stg_orders.sql
│   │   └── stg_payments.sql
│   ├── marts/                   # Business-ready fact tables
│   │   └── fct_orders.sql
│   └── semantic/                # MetricFlow semantic layer
│       ├── semantic_models/
│       │   └── orders.yml       # Orders semantic model
│       ├── metrics/
│       │   └── revenue.yml      # Revenue metrics definitions
│       ├── time_spine.sql       # Time spine table
│       └── time_spine.yml       # Time spine configuration
└── seeds/                       # Seed data (raw tables)
    ├── raw_customers.csv
    ├── raw_orders.csv
    └── raw_payments.csv
```

## Prerequisites

1. **Python** 3.8 or higher
2. **dbt Core** installed
3. **dbt Databricks adapter** installed
4. **dbt MetricFlow** installed
5. A data warehouse connection configured (Databricks, Snowflake, BigQuery, etc.)
6. dbt profile configured (see `profiles_template.yml`)

## Installation

### Step 1: Install dbt Core
```bash
pip install dbt-core
```

### Step 2: Install dbt Databricks Adapter
```bash
pip install dbt-databricks
```

### Step 3: Install dbt MetricFlow
```bash
pip install dbt-metricflow
```

### Step 4: Verify Installation
```bash
# Check dbt version
dbt --version

# Check MetricFlow
mf --version
```

## Setup

### 1. Install dbt packages
```bash
dbt deps
```

### 2. Set up raw data sources
The project uses dbt sources to reference raw data tables. You need to:

**Option A: Use existing raw tables in your database**
- Ensure tables `raw_customers`, `raw_orders`, and `raw_payments` exist in your database
- Update `models/staging/sources.yml` if your source database/schema differs from your target
- The sources.yml uses variables that default to your target database/schema

**Option B: Use dbt seeds**
- Create seed files: `seeds/raw_customers.csv`, `seeds/raw_orders.csv`, `seeds/raw_payments.csv`
- Load them: `dbt seed`
- Note: If using seeds, you may need to adjust sources.yml to reference the seeded tables

**Source table schemas:**
- `raw_customers`: id, first_name, last_name
- `raw_orders`: id, user_id, order_date, status
- `raw_payments`: id, order_id, payment_method, amount

### 3. Run dbt models
```bash
# Run all models
dbt run

# Run specific models
dbt run --select staging
dbt run --select marts
dbt run --select semantic
```

### 4. Validate MetricFlow setup
```bash
# List available metrics
mf list metrics

# List semantic models
mf list semantic-models

# Query a metric
mf query --metrics total_revenue --group-by order_date
```

## Data Model

### Staging Layer
- **stg_customers**: Cleaned customer data
- **stg_orders**: Cleaned order data
- **stg_payments**: Cleaned payment data

### Marts Layer
- **fct_orders**: Fact table combining orders, customers, and payments with aggregated payment amounts by method

### Semantic Layer

#### Semantic Model: `orders`
- **Entities**: order (primary), customer (foreign)
- **Dimensions**: 
  - order_date (time)
  - order_status (categorical)
  - customer_first_name, customer_last_name (categorical)
- **Measures**:
  - order_total (sum of amount)
  - order_count (count distinct orders)
  - credit_card_amount, coupon_amount, bank_transfer_amount

#### Metrics
1. **total_revenue**: Total revenue from all orders
2. **total_orders**: Total number of orders
3. **average_order_value**: Average value per order (ratio metric)
4. **completed_revenue**: Revenue from completed orders only
5. **credit_card_revenue**: Revenue from credit card payments
6. **coupon_revenue**: Revenue from coupon payments
7. **bank_transfer_revenue**: Revenue from bank transfer payments

## Example MetricFlow Queries

```bash
# Total revenue
mf query --metrics total_revenue

# Revenue by date
mf query --metrics total_revenue --group-by orders__order_date

# Revenue by payment method
mf query --metrics credit_card_revenue,coupon_revenue,bank_transfer_revenue

# Average order value over time
mf query --metrics average_order_value --group-by orders__order_date

# Revenue filtered by status
mf query --metrics completed_revenue --group-by orders__order_date
```

## Notes

- The time spine table covers dates from 2020-01-01 to 2025-12-31
- All staging models are materialized as views
- Marts are materialized as tables
- Semantic models are materialized as views


# Databricks Unity Catalog Metric Views - Complete Metrics List

This document lists all metrics implemented in the Databricks semantic layer project.

## Overview

**Total Metric Views:** 7 YAML files  
**Total Measures:** 30+ unique measures across all views

---

## 1. Revenue Metrics (`revenue_metrics.yaml`)

**Source:** `workspace.dbt_poc.fct_orders`  
**Joins:** None

### Measures (6):
1. **total_revenue**
   - Type: Sum (Currency)
   - Expression: `SUM(source.amount)`
   - Format: USD, 2 decimal places

2. **credit_card_revenue**
   - Type: Sum (Currency)
   - Expression: `SUM(source.credit_card_amount)`
   - Format: USD, 2 decimal places

3. **coupon_revenue**
   - Type: Sum (Currency)
   - Expression: `SUM(source.coupon_amount)`
   - Format: USD, 2 decimal places

4. **bank_transfer_revenue**
   - Type: Sum (Currency)
   - Expression: `SUM(source.bank_transfer_amount)`
   - Format: USD, 2 decimal places

5. **total_payment_revenue**
   - Type: Sum (Currency - Composite)
   - Expression: `SUM(source.credit_card_amount + source.coupon_amount + source.bank_transfer_amount)`
   - Format: USD, 2 decimal places

6. **completed_revenue**
   - Type: Sum (Currency - Filtered)
   - Expression: `SUM(CASE WHEN source.status = 'completed' THEN source.amount ELSE 0 END)`
   - Format: USD, 2 decimal places

### Dimensions (5):
- `order_date` (date_time)
- `order_date_month` (date)
- `order_date_quarter` (date)
- `order_date_year` (date)
- `order_status` (categorical)

---

## 2. Revenue Metrics with Stores (`revenue_metrics_with_stores.yaml`)

**Source:** `workspace.dbt_poc.fct_orders`  
**Joins:** `dim_stores` (LEFT JOIN on `store_id`)

### Measures (3):
1. **total_revenue** (same as above)
2. **credit_card_revenue** (same as above)
3. **completed_revenue** (same as above)

### Additional Dimensions (2):
- `store_type` (from dim_stores)
- `store_region` (from dim_stores)

---

## 3. Revenue Metrics with Customers (`revenue_metrics_with_customers.yaml`)

**Source:** `workspace.dbt_poc.fct_orders`  
**Joins:** `dim_customers` (LEFT JOIN on `customer_id`)

### Measures (4):
1. **total_revenue** (same as above)
2. **credit_card_revenue** (same as above)
3. **completed_revenue** (same as above)
4. **total_orders**
   - Type: Count Distinct
   - Expression: `COUNT(DISTINCT source.order_id)`
   - Format: Number, 0 decimal places

### Additional Dimensions (3):
- `customer_region` (from dim_customers)
- `customer_first_name` (from dim_customers)
- `customer_last_name` (from dim_customers)

---

## 4. Order Metrics (`order_metrics.yaml`)

**Source:** `workspace.dbt_poc.fct_orders`  
**Joins:** None

### Measures (4):
1. **total_orders**
   - Type: Count Distinct
   - Expression: `COUNT(DISTINCT source.order_id)`
   - Format: Number, 0 decimal places

2. **completed_orders**
   - Type: Count Distinct (Filtered)
   - Expression: `COUNT(DISTINCT CASE WHEN source.status = 'completed' THEN source.order_id END)`
   - Format: Number, 0 decimal places

3. **unique_customers**
   - Type: Count Distinct
   - Expression: `COUNT(DISTINCT source.customer_id)`
   - Format: Number, 0 decimal places

4. **customers_with_completed_orders**
   - Type: Count Distinct (Filtered)
   - Expression: `COUNT(DISTINCT CASE WHEN source.status = 'completed' THEN source.customer_id END)`
   - Format: Number, 0 decimal places

### Dimensions (2):
- `order_date_month` (date)
- `order_status` (categorical)

---

## 5. Ratio Measures Example (`ratio_measures_example.yaml`)

**Source:** `workspace.dbt_poc.fct_orders`  
**Joins:** None

### Measures (6):
1. **total_revenue** (same as above)
2. **total_orders** (same as above)
3. **conversion_rate**
   - Type: Ratio/Percentage
   - Expression: `COUNT(CASE WHEN source.status = 'completed' THEN 1 END) * 1.0 / NULLIF(COUNT(*), 0)`
   - Format: Percentage, 2 decimal places
   - Description: Percentage of orders that were completed

4. **average_order_value**
   - Type: Ratio (Currency)
   - Expression: `SUM(source.amount) / NULLIF(COUNT(DISTINCT source.order_id), 0)`
   - Format: Currency (USD), 2 decimal places
   - Description: Average revenue per order

5. **credit_card_adoption_rate**
   - Type: Ratio/Percentage
   - Expression: `SUM(source.credit_card_amount) * 1.0 / NULLIF(SUM(source.amount), 0)`
   - Format: Percentage, 2 decimal places
   - Description: Percentage of revenue from credit card payments

6. **coupon_usage_rate**
   - Type: Ratio/Percentage
   - Expression: `COUNT(CASE WHEN source.coupon_amount > 0 THEN 1 END) * 1.0 / NULLIF(COUNT(DISTINCT source.order_id), 0)`
   - Format: Percentage, 2 decimal places
   - Description: Percentage of orders that used a coupon

7. **order_completion_rate**
   - Type: Ratio/Percentage
   - Expression: `COUNT(CASE WHEN source.status = 'completed' THEN 1 END) * 1.0 / NULLIF(COUNT(DISTINCT source.order_id), 0)`
   - Format: Percentage, 2 decimal places
   - Description: Percentage of orders that reached completed status

### Dimensions (2):
- `order_date_month` (date)
- `order_status` (categorical)

---

## 6. Derived Metrics Example (`derived_metrics_example.yaml`)

**Source:** `workspace.dbt_poc.fct_orders`  
**Joins:** None

### Base Measures (4):
1. **total_orders** (same as above)
2. **completed_orders**
   - Type: Count
   - Expression: `COUNT(CASE WHEN source.status = 'completed' THEN 1 END)`
   - Format: Number, 0 decimal places

3. **total_revenue** (same as above)
4. **completed_revenue** (same as above)

### Derived Measures (3) - Using MEASURE() function:
1. **conversion_rate**
   - Type: Derived (Percentage)
   - Expression: `MEASURE(completed_orders) * 1.0 / NULLIF(MEASURE(total_orders), 0)`
   - Format: Percentage, 2 decimal places
   - Description: Derived from completed_orders and total_orders

2. **average_order_value**
   - Type: Derived (Currency)
   - Expression: `MEASURE(total_revenue) / NULLIF(MEASURE(total_orders), 0)`
   - Format: Currency (USD), 2 decimal places
   - Description: Derived from total_revenue and total_orders

3. **completed_revenue_ratio**
   - Type: Derived (Percentage)
   - Expression: `MEASURE(completed_revenue) / NULLIF(MEASURE(total_revenue), 0)`
   - Format: Percentage, 2 decimal places
   - Description: Percentage of revenue from completed orders

### Dimensions (2):
- `order_date_month` (date)
- `order_status` (categorical)

---

## 7. Min/Max Metrics (`min_max_metrics.yaml`)

**Source:** `workspace.dbt_poc.fct_orders`  
**Joins:** None

### Measures (6):
1. **min_order_amount**
   - Type: Min (Currency)
   - Expression: `MIN(source.amount)`
   - Format: Currency (USD), 2 decimal places

2. **max_order_amount**
   - Type: Max (Currency)
   - Expression: `MAX(source.amount)`
   - Format: Currency (USD), 2 decimal places

3. **earliest_order_date**
   - Type: Min (Date/Time)
   - Expression: `MIN(source.order_date)`
   - Format: date_time

4. **latest_order_date**
   - Type: Max (Date/Time)
   - Expression: `MAX(source.order_date)`
   - Format: date_time

5. **min_credit_card_amount**
   - Type: Min (Currency)
   - Expression: `MIN(source.credit_card_amount)`
   - Format: Currency (USD), 2 decimal places

6. **max_credit_card_amount**
   - Type: Max (Currency)
   - Expression: `MAX(source.credit_card_amount)`
   - Format: Currency (USD), 2 decimal places

### Dimensions (2):
- `order_date_month` (date)
- `order_status` (categorical)

---

## Summary by Metric Type

### Sum Metrics (Currency)
- total_revenue
- credit_card_revenue
- coupon_revenue
- bank_transfer_revenue
- total_payment_revenue
- completed_revenue

### Count Metrics
- total_orders
- completed_orders
- unique_customers
- customers_with_completed_orders

### Ratio/Percentage Metrics
- conversion_rate
- credit_card_adoption_rate
- coupon_usage_rate
- order_completion_rate
- completed_revenue_ratio

### Average Metrics
- average_order_value

### Min/Max Metrics
- min_order_amount
- max_order_amount
- earliest_order_date
- latest_order_date
- min_credit_card_amount
- max_credit_card_amount

### Derived Metrics (Using MEASURE())
- conversion_rate (derived)
- average_order_value (derived)
- completed_revenue_ratio (derived)

---

## Query Examples

### Basic Query
```sql
SELECT 
    order_date_month,
    MEASURE(total_revenue),
    MEASURE(total_orders)
FROM catalog.schema.revenue_metrics
GROUP BY order_date_month
ORDER BY order_date_month;
```

### With Joins (Stores)
```sql
SELECT 
    store_type,
    MEASURE(total_revenue),
    MEASURE(completed_revenue)
FROM catalog.schema.revenue_metrics_with_stores
GROUP BY store_type;
```

### With Joins (Customers)
```sql
SELECT 
    customer_region,
    MEASURE(total_revenue),
    MEASURE(total_orders)
FROM catalog.schema.revenue_metrics_with_customers
GROUP BY customer_region;
```

### Ratio Metrics
```sql
SELECT 
    order_date_month,
    MEASURE(conversion_rate),
    MEASURE(average_order_value)
FROM catalog.schema.ratio_measures_example
GROUP BY order_date_month;
```

### Derived Metrics
```sql
SELECT 
    order_date_month,
    MEASURE(conversion_rate),  -- Derived from MEASURE(completed_orders) / MEASURE(total_orders)
    MEASURE(average_order_value)  -- Derived from MEASURE(total_revenue) / MEASURE(total_orders)
FROM catalog.schema.derived_metrics_example
GROUP BY order_date_month;
```

### Min/Max Metrics
```sql
SELECT 
    order_date_month,
    MEASURE(min_order_amount),
    MEASURE(max_order_amount),
    MEASURE(earliest_order_date),
    MEASURE(latest_order_date)
FROM catalog.schema.min_max_metrics
GROUP BY order_date_month;
```

---

## Notes

1. **Format Types Used:**
   - `currency` (USD, 2 decimal places)
   - `percentage` (2 decimal places)
   - `number` (0 decimal places for counts)
   - `date_time` (various formats)
   - `date` (various formats)

2. **Join Types:**
   - All joins are LEFT OUTER JOINs (only supported type in Unity Catalog Metric Views)

3. **Derived Metrics:**
   - Use `MEASURE()` function to reference other measures in the same metric view
   - Must be defined after the base measures they reference

4. **Conversion Metrics:**
   - Implemented as ratio/percentage metrics using SQL expressions
   - Not true time-windowed conversion metrics (not supported in Unity Catalog)

5. **File Organization:**
   - Each YAML file represents a separate metric view
   - Views can be created using the Catalog Explorer UI or SQL scripts


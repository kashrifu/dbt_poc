# Implemented Metrics - Complete List with Test Commands

This document lists all metrics implemented in the MetricFlow POC with example commands to test each one.

---

## Metrics Summary

**Total Metrics Implemented: 12**

- **Simple Metrics**: 8
- **Ratio Metrics**: 4
- **Filtered Metrics**: 1

---

## 1. Simple Metrics

### 1.1 total_revenue
**Type**: Simple  
**Description**: Total revenue from all orders  
**Measure**: `order_total` (sum of amount)

**Test Commands:**
```bash
# Basic query
mf query --metrics total_revenue

# By date
mf query --metrics total_revenue --group-by order__order_date__day

# By month
mf query --metrics total_revenue --group-by order__order_date__month

# By store type (multi-hop join)
mf query --metrics total_revenue --group-by store__store_type

# By customer region (multi-hop join)
mf query --metrics total_revenue --group-by customers__customer_region

# With date range
mf query --metrics total_revenue \
  --start-time "2024-01-01" \
  --end-time "2024-12-31" \
  --group-by order__order_date__day

# View SQL
mf query --metrics total_revenue --group-by order__order_date__day --explain
```

---

### 1.2 total_orders
**Type**: Simple  
**Description**: Total number of orders  
**Measure**: `order_count` (count distinct order_id)

**Test Commands:**
```bash
# Basic query
mf query --metrics total_orders

# By date
mf query --metrics total_orders --group-by order__order_date__day

# By status
mf query --metrics total_orders --group-by order__order_status

# By store type
mf query --metrics total_orders --group-by store__store_type

# Multiple granularities
mf query --metrics total_orders --group-by order__order_date__week
mf query --metrics total_orders --group-by order__order_date__month
mf query --metrics total_orders --group-by order__order_date__quarter
mf query --metrics total_orders --group-by order__order_date__year
```

---

### 1.3 completed_orders
**Type**: Simple  
**Description**: Number of completed orders  
**Measure**: `completed_order_count` (count distinct where status = 'completed')

**Test Commands:**
```bash
# Basic query
mf query --metrics completed_orders

# By date
mf query --metrics completed_orders --group-by order__order_date__day

# By store type
mf query --metrics completed_orders --group-by store__store_type

# View SQL
mf query --metrics completed_orders --explain
```

---

### 1.4 credit_card_revenue
**Type**: Simple  
**Description**: Revenue from credit card payments  
**Measure**: `credit_card_amount` (sum)

**Test Commands:**
```bash
# Basic query
mf query --metrics credit_card_revenue

# By date
mf query --metrics credit_card_revenue --group-by order__order_date__month

# By store type
mf query --metrics credit_card_revenue --group-by store__store_type

# Compare with other payment methods
mf query --metrics credit_card_revenue,coupon_revenue,bank_transfer_revenue \
  --group-by order__order_date__month
```

---

### 1.5 coupon_revenue
**Type**: Simple  
**Description**: Revenue from coupon payments  
**Measure**: `coupon_amount` (sum)

**Test Commands:**
```bash
# Basic query
mf query --metrics coupon_revenue

# By date
mf query --metrics coupon_revenue --group-by order__order_date__month

# By store type
mf query --metrics coupon_revenue --group-by store__store_type
```

---

### 1.6 bank_transfer_revenue
**Type**: Simple  
**Description**: Revenue from bank transfer payments  
**Measure**: `bank_transfer_amount` (sum)

**Test Commands:**
```bash
# Basic query
mf query --metrics bank_transfer_revenue

# By date
mf query --metrics bank_transfer_revenue --group-by order__order_date__month

# By store type
mf query --metrics bank_transfer_revenue --group-by store__store_type
```

---

### 1.7 total_payment_revenue
**Type**: Simple  
**Description**: Sum of all payment method revenues  
**Measure**: `total_payment_amount` (sum of credit_card + coupon + bank_transfer)

**Test Commands:**
```bash
# Basic query
mf query --metrics total_payment_revenue

# By date
mf query --metrics total_payment_revenue --group-by order__order_date__month

# By store type
mf query --metrics total_payment_revenue --group-by store__store_type

# Compare with individual payment methods
mf query --metrics total_payment_revenue,credit_card_revenue,coupon_revenue,bank_transfer_revenue \
  --group-by order__order_date__month
```

---

### 1.8 completed_revenue
**Type**: Simple (with Filter)  
**Description**: Revenue from completed orders only  
**Measure**: `order_total` (sum)  
**Filter**: `order_status = 'completed'`

**Test Commands:**
```bash
# Basic query
mf query --metrics completed_revenue

# By date
mf query --metrics completed_revenue --group-by order__order_date__day

# By month
mf query --metrics completed_revenue --group-by order__order_date__month

# Compare with total revenue
mf query --metrics total_revenue,completed_revenue --group-by order__order_date__month

# View SQL to see filter applied
mf query --metrics completed_revenue --group-by order__order_date__day --explain
```

---

## 2. Ratio Metrics

### 2.1 average_order_value
**Type**: Ratio  
**Description**: Average value per order  
**Formula**: total_revenue / total_orders

**Test Commands:**
```bash
# Basic query
mf query --metrics average_order_value

# By date
mf query --metrics average_order_value --group-by order__order_date__day

# By month
mf query --metrics average_order_value --group-by order__order_date__month

# By store type
mf query --metrics average_order_value --group-by store__store_type

# Compare with revenue and orders
mf query --metrics total_revenue,total_orders,average_order_value \
  --group-by order__order_date__month

# View SQL to see ratio calculation
mf query --metrics average_order_value --group-by order__order_date__month --explain
```

---

### 2.2 revenue_per_customer
**Type**: Ratio  
**Description**: Average revenue per order (simplified)  
**Formula**: total_revenue / total_orders

**Test Commands:**
```bash
# Basic query
mf query --metrics revenue_per_customer

# By date
mf query --metrics revenue_per_customer --group-by order__order_date__month

# By store type
mf query --metrics revenue_per_customer --group-by store__store_type
```

---

### 2.3 credit_card_payment_ratio
**Type**: Ratio  
**Description**: Percentage of revenue from credit card payments  
**Formula**: credit_card_revenue / total_revenue

**Test Commands:**
```bash
# Basic query
mf query --metrics credit_card_payment_ratio

# By date
mf query --metrics credit_card_payment_ratio --group-by order__order_date__month

# By store type
mf query --metrics credit_card_payment_ratio --group-by store__store_type

# Compare with actual revenue amounts
mf query --metrics credit_card_payment_ratio,credit_card_revenue,total_revenue \
  --group-by order__order_date__month
```

---

### 2.4 order_completion_rate
**Type**: Ratio (Conversion-like)  
**Description**: Percentage of orders that were completed  
**Formula**: completed_orders / total_orders

**Test Commands:**
```bash
# Basic query
mf query --metrics order_completion_rate

# By date
mf query --metrics order_completion_rate --group-by order__order_date__day

# By month
mf query --metrics order_completion_rate --group-by order__order_date__month

# By store type
mf query --metrics order_completion_rate --group-by store__store_type

# Compare with component metrics
mf query --metrics order_completion_rate,completed_orders,total_orders \
  --group-by order__order_date__month
```

---

## 3. Advanced Query Examples

### Multiple Metrics Together
```bash
# Revenue and orders together
mf query --metrics total_revenue,total_orders,average_order_value \
  --group-by order__order_date__month

# All payment methods
mf query --metrics credit_card_revenue,coupon_revenue,bank_transfer_revenue,total_payment_revenue \
  --group-by order__order_date__month

# Conversion metrics
mf query --metrics order_completion_rate,credit_card_payment_ratio \
  --group-by order__order_date__month
```

### Multi-Dimensional Analysis
```bash
# Revenue by store type and month
mf query --metrics total_revenue \
  --group-by store__store_type,order__order_date__month \
  --order order__order_date__month,-total_revenue

# Revenue by customer region and store type
mf query --metrics total_revenue \
  --group-by customers__customer_region,store__store_type

# Multiple metrics with multiple dimensions
mf query --metrics total_revenue,total_orders \
  --group-by store__store_type,order__order_date__month
```

### Filtered Queries
```bash
# Revenue with custom filter
mf query --metrics total_revenue \
  --where "{{ Dimension('order__order_status') }} = 'completed'" \
  --group-by order__order_date__day

# Date range filter
mf query --metrics total_revenue \
  --start-time "2024-01-01" \
  --end-time "2024-12-31" \
  --group-by order__order_date__day
```

### SQL Extraction
```bash
# Get SQL for Databricks
mf query --metrics total_revenue --group-by store__store_type --explain

# With dataflow plan
mf query --metrics total_revenue --group-by store__store_type \
  --explain --show-dataflow-plan

# Save to file
mf query --metrics total_revenue --group-by store__store_type --explain > query.sql
```

### Export Results
```bash
# Export to CSV
mf query --metrics total_revenue --group-by order__order_date__month --csv revenue_by_month.csv

# With formatting
mf query --metrics average_order_value --group-by order__order_date__month \
  --csv aov_by_month.csv --decimals 2
```

---

## 4. Metric Categories

### Revenue Metrics
- `total_revenue`
- `completed_revenue`
- `credit_card_revenue`
- `coupon_revenue`
- `bank_transfer_revenue`
- `total_payment_revenue`

### Order Metrics
- `total_orders`
- `completed_orders`

### Calculated Metrics (Ratios)
- `average_order_value`
- `revenue_per_customer`
- `credit_card_payment_ratio`
- `order_completion_rate`

---

## 5. Quick Reference

### List All Metrics
```bash
mf list metrics
```

### Query Single Metric
```bash
mf query --metrics <metric_name>
```

### Query Multiple Metrics
```bash
mf query --metrics <metric1>,<metric2>,<metric3>
```

### Group By Dimension
```bash
mf query --metrics <metric> --group-by <dimension>
```

### View SQL
```bash
mf query --metrics <metric> --explain
```

### Export to CSV
```bash
mf query --metrics <metric> --csv <filename>.csv
```

---

## 6. Metric Dependencies

### Metric Hierarchy
```
Measures (in semantic model)
    ↓
Simple Metrics
    ↓
Ratio Metrics (use simple metrics)
```

**Example:**
- `order_total` (measure) → `total_revenue` (simple metric)
- `order_count` (measure) → `total_orders` (simple metric)
- `total_revenue` + `total_orders` → `average_order_value` (ratio metric)

---

## 7. Testing Checklist

### ✅ Basic Functionality
- [x] All 12 metrics parse successfully
- [x] All metrics can be queried individually
- [x] Multiple metrics can be queried together
- [x] SQL compilation works (`--explain`)

### ✅ Grouping
- [x] Group by time dimensions (day, week, month, quarter, year)
- [x] Group by categorical dimensions (status, store_type, customer_region)
- [x] Group by multiple dimensions
- [x] Multi-hop joins (Orders → Stores, Orders → Customers)

### ✅ Filtering
- [x] Filtered metrics work (`completed_revenue`)
- [x] Custom WHERE clauses
- [x] Date range filters

### ✅ Ratio Metrics
- [x] Ratio metrics calculate correctly
- [x] Can group ratio metrics by dimensions
- [x] Ratio metrics work with time dimensions

---

## 8. Notes

### Conversion Metrics
- **Status**: Not fully implemented
- **Reason**: True conversion metrics require `type: conversion` which needs MetricFlow 0.204+ and proper event tracking
- **Workaround**: Using ratio metrics to represent conversion-like concepts
- **Examples**: `order_completion_rate`, `credit_card_adoption_rate`

### Multi-Hop Joins
- ✅ Working: Orders → Stores, Orders → Customers
- ✅ Automatic join path detection
- ✅ Correct SQL generation

### Time Dimensions
- ✅ Multiple granularities supported
- ✅ Single dimension definition enables all grains
- ✅ Time spine configured correctly

---

## Summary

**Total Metrics**: 12  
**Simple Metrics**: 8  
**Ratio Metrics**: 4  
**Filtered Metrics**: 1  
**Conversion Metrics**: 0 (using ratio metrics as workaround)

All metrics are production-ready and can be queried, grouped, filtered, and exported.


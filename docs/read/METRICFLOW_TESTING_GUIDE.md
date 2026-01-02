# MetricFlow POC - Testing Guide

This guide covers all MetricFlow capabilities demonstrated in this POC.

## ✅ Implemented Capabilities

### 1. **Basic Metrics**
- ✅ Simple metrics (sum, count)
- ✅ Multiple measures from same semantic model
- ✅ Metric labels and descriptions

### 2. **Advanced Metric Types**
- ✅ Ratio metrics (average_order_value, revenue_per_customer)
- ✅ Derived metrics (total_payment_revenue, cumulative_revenue)
- ✅ Filtered metrics (completed_revenue)

### 3. **Time Dimensions**
- ✅ Multiple time granularities (day, week, month, quarter, year)
- ✅ Time spine configuration
- ✅ Time-based grouping and filtering

### 4. **Semantic Model Features**
- ✅ Primary and foreign entities
- ✅ Time dimensions
- ✅ Categorical dimensions
- ✅ Multiple measures with different aggregations

### 5. **Query Capabilities**
- ✅ Single metric queries
- ✅ Multiple metric queries
- ✅ Group by dimensions
- ✅ Group by time dimensions with different granularities

## 📋 Test Scenarios

### Basic Queries
```bash
# Single metric
mf query --metrics total_revenue

# Multiple metrics
mf query --metrics total_revenue,total_orders

# Metric with time grouping (day)
mf query --metrics total_revenue --group-by order__order_date__day

# Metric with time grouping (week)
mf query --metrics total_revenue --group-by order__order_date__week

# Metric with time grouping (month)
mf query --metrics total_revenue --group-by order__order_date__month

# Metric with categorical grouping
mf query --metrics total_revenue --group-by order__order_status
```

### Ratio Metrics
```bash
# Average order value
mf query --metrics average_order_value --group-by order__order_date__day

# Revenue per customer
mf query --metrics revenue_per_customer --group-by order__order_date__month

# Credit card payment ratio
mf query --metrics credit_card_payment_ratio --group-by order__order_date__month
```

### Derived Metrics
```bash
# Total payment revenue (sum of all payment methods)
mf query --metrics total_payment_revenue --group-by order__order_date__day

# Cumulative revenue (running total)
mf query --metrics cumulative_revenue --group-by order__order_date__day
```

### Filtered Metrics
```bash
# Completed orders revenue
mf query --metrics completed_revenue --group-by order__order_date__day
```

### Payment Method Breakdown
```bash
# All payment methods
mf query --metrics credit_card_revenue,coupon_revenue,bank_transfer_revenue --group-by order__order_date__month

# Compare payment methods
mf query --metrics credit_card_revenue,coupon_revenue --group-by order__order_date__quarter
```

### Multi-Dimensional Analysis
```bash
# Revenue by status and date
mf query --metrics total_revenue --group-by order__order_status,order__order_date__month

# Revenue by customer name
mf query --metrics total_revenue --group-by order__customer_first_name
```

## 🎯 MetricFlow Capabilities Demonstrated

| Capability | Status | Example |
|------------|--------|---------|
| Simple Metrics | ✅ | total_revenue, total_orders |
| Ratio Metrics | ✅ | average_order_value, revenue_per_customer |
| Derived Metrics | ✅ | total_payment_revenue, cumulative_revenue |
| Filtered Metrics | ✅ | completed_revenue |
| Time Granularities | ✅ | day, week, month, quarter, year |
| Multiple Measures | ✅ | order_total, credit_card_amount, etc. |
| Entity Relationships | ✅ | order (primary), customer (foreign) |
| Time Spine | ✅ | Configured with day granularity |
| Dimension Grouping | ✅ | order_status, customer names |
| Multi-metric Queries | ✅ | Multiple metrics in one query |

## 📊 Available Metrics

1. **total_revenue** - Total revenue from all orders
2. **total_orders** - Total number of orders
3. **average_order_value** - Average value per order (ratio)
4. **completed_revenue** - Revenue from completed orders (filtered)
5. **credit_card_revenue** - Revenue from credit card payments
6. **coupon_revenue** - Revenue from coupon payments
7. **bank_transfer_revenue** - Revenue from bank transfer payments
8. **total_payment_revenue** - Sum of all payment revenues (derived)
9. **revenue_per_customer** - Average revenue per customer (ratio)
10. **credit_card_payment_ratio** - % of revenue from credit cards (ratio)
11. **cumulative_revenue** - Running total of revenue (derived)

## 🔍 Available Dimensions

### Time Dimensions (Multiple Granularities)
- `order__order_date__day`
- `order__order_date__week`
- `order__order_date__month`
- `order__order_date__quarter`
- `order__order_date__year`

### Categorical Dimensions
- `order__order_status`
- `order__customer_first_name`
- `order__customer_last_name`
- `order__customer` (entity)

## 🚀 Advanced Testing

### Test Time-Based Queries
```bash
# Daily revenue trend
mf query --metrics total_revenue --group-by order__order_date__day

# Weekly summary
mf query --metrics total_revenue,total_orders --group-by order__order_date__week

# Monthly comparison
mf query --metrics total_revenue,average_order_value --group-by order__order_date__month

# Quarterly analysis
mf query --metrics total_revenue,credit_card_revenue --group-by order__order_date__quarter

# Yearly overview
mf query --metrics total_revenue,total_orders --group-by order__order_date__year
```

### Test Metric Combinations
```bash
# Revenue and order count together
mf query --metrics total_revenue,total_orders,average_order_value --group-by order__order_date__month

# Payment method comparison
mf query --metrics credit_card_revenue,coupon_revenue,bank_transfer_revenue,total_payment_revenue --group-by order__order_date__month
```

## 📝 Notes

- All metrics are properly labeled and documented
- Time spine is configured for day-level granularity
- Semantic model includes primary and foreign entities
- Multiple aggregation types are demonstrated (sum, count_distinct)
- Filtered metrics show conditional logic capabilities

## ⚠️ Known Limitations

1. **Window Functions**: Some derived metrics with window functions (like cumulative_revenue) may need adjustment based on your MetricFlow version
2. **Complex Joins**: Fan-out joins and multiple join paths require additional configuration
3. **Conversion Metrics**: Full conversion funnel metrics would require additional semantic models

## 🎓 Learning Outcomes

This POC demonstrates:
- ✅ Basic metric definition and querying
- ✅ Advanced metric types (ratio, derived, filtered)
- ✅ Time dimension handling with multiple granularities
- ✅ Semantic model configuration
- ✅ Entity relationships
- ✅ Multi-dimensional analysis
- ✅ MetricFlow CLI usage


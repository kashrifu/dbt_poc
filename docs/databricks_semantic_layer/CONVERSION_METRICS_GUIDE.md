# Unity Catalog Metric Views - Conversion Metrics Guide

## Overview

Conversion metrics are **fully supported** in Unity Catalog Metric Views! They are defined as measures with calculated expressions that result in percentages or ratios, representing business KPIs that measure the effectiveness of a process.

## What Are Conversion Metrics?

Conversion metrics typically represent:
- **Ratios**: Proportion of one value to another
- **Percentages**: Percentage of items that meet a criteria
- **Rates**: Rate of conversion from one state to another

Examples:
- Order completion rate (completed orders / total orders)
- Credit card adoption rate (credit card revenue / total revenue)
- Coupon usage rate (orders with coupons / total orders)
- Cart-to-purchase rate
- Email open rate

## How to Define Conversion Metrics

### Basic Structure

```yaml
measures:
  - name: conversion_rate
    expr: <numerator_expression> * 1.0 / NULLIF(<denominator_expression>, 0)
    display_name: Conversion Rate
    comment: Description of what this conversion metric measures
    format:
      type: percentage
      decimal_places:
        type: exact
        places: 2
```

### Key Components

1. **Expression**: SQL expression calculating numerator / denominator
2. **NULLIF**: Always use `NULLIF` in denominator to avoid division by zero
3. **Format**: Use `type: percentage` for proper semantic metadata
4. **Display Name**: Clear, business-friendly name
5. **Comment**: Description of what the metric measures

## Examples

### 1. Order Completion Rate

```yaml
- name: order_completion_rate
  expr: COUNT(CASE WHEN source.status = 'completed' THEN 1 END) * 1.0 / NULLIF(COUNT(DISTINCT source.order_id), 0)
  display_name: Order Completion Rate
  comment: Percentage of orders that reached completed status
  format:
    type: percentage
    decimal_places:
      type: exact
      places: 2
```

### 2. Credit Card Adoption Rate

```yaml
- name: credit_card_adoption_rate
  expr: SUM(source.credit_card_amount) * 1.0 / NULLIF(SUM(source.amount), 0)
  display_name: Credit Card Adoption Rate
  comment: Percentage of revenue from credit card payments
  format:
    type: percentage
    decimal_places:
      type: exact
      places: 2
```

### 3. Coupon Usage Rate

```yaml
- name: coupon_usage_rate
  expr: COUNT(CASE WHEN source.coupon_amount > 0 THEN 1 END) * 1.0 / NULLIF(COUNT(DISTINCT source.order_id), 0)
  display_name: Coupon Usage Rate
  comment: Percentage of orders that used a coupon
  format:
    type: percentage
    decimal_places:
      type: exact
      places: 2
```

### 4. Conversion Rate (General)

```yaml
- name: conversion_rate
  expr: COUNT(CASE WHEN source.status = 'completed' THEN 1 END) * 1.0 / NULLIF(COUNT(*), 0)
  display_name: Conversion Rate
  comment: Percentage of orders that were completed
  format:
    type: percentage
    decimal_places:
      type: exact
      places: 2
```

## Best Practices

### 1. Always Use NULLIF

**✅ Correct:**
```yaml
expr: COUNT(CASE WHEN source.status = 'completed' THEN 1 END) * 1.0 / NULLIF(COUNT(*), 0)
```

**❌ Incorrect:**
```yaml
expr: COUNT(CASE WHEN source.status = 'completed' THEN 1 END) * 1.0 / COUNT(*)
```

### 2. Use Percentage Format

Always set `type: percentage` for conversion metrics:

```yaml
format:
  type: percentage
  decimal_places:
    type: exact
    places: 2
```

### 3. Clear Naming and Documentation

```yaml
- name: order_completion_rate
  display_name: Order Completion Rate
  comment: Percentage of orders that reached completed status (conversion metric)
```

### 4. Use Appropriate SQL Functions

- **COUNT**: For counting items that meet criteria
- **SUM**: For summing values that meet criteria
- **CASE WHEN**: For conditional logic
- **DISTINCT**: When counting unique items

## Common Patterns

### Pattern 1: Count-Based Conversion

```yaml
expr: COUNT(CASE WHEN <condition> THEN 1 END) * 1.0 / NULLIF(COUNT(DISTINCT <id_column>), 0)
```

Example: Order completion rate

### Pattern 2: Sum-Based Conversion

```yaml
expr: SUM(CASE WHEN <condition> THEN <value_column> ELSE 0 END) * 1.0 / NULLIF(SUM(<total_column>), 0)
```

Example: Revenue share from specific payment method

### Pattern 3: Existence-Based Conversion

```yaml
expr: COUNT(CASE WHEN <column> > 0 THEN 1 END) * 1.0 / NULLIF(COUNT(DISTINCT <id_column>), 0)
```

Example: Coupon usage rate

## Querying Conversion Metrics

Once defined, query conversion metrics like any other measure:

```sql
SELECT 
    order_date_month,
    MEASURE(conversion_rate) AS conversion_rate,
    MEASURE(credit_card_adoption_rate) AS cc_adoption
FROM workspace.dbt_poc.metric_conversion_metrics
GROUP BY order_date_month;
```

## Comparison with dbt MetricFlow

| Feature | dbt MetricFlow | Databricks Unity Catalog |
|---------|---------------|-------------------------|
| **Conversion Metrics** | ⚠️ Partial (ratio workaround) | ✅ **Fully Supported** |
| **Definition** | Ratio metric type | Percentage measure with expression |
| **Time Windows** | ✅ Supported (advanced) | ⚠️ Must calculate in expression |
| **Flexibility** | ⚠️ Limited to metric references | ✅ Full SQL expression support |
| **Formatting** | ⚠️ Basic | ✅ Rich percentage formatting |

## Key Advantages

1. ✅ **Full SQL Flexibility**: Use any SQL expression for conversion logic
2. ✅ **Rich Formatting**: Native percentage formatting with `type: percentage`
3. ✅ **Business-Friendly**: Clear display names and comments
4. ✅ **No Limitations**: Can calculate any conversion metric with SQL
5. ✅ **Reusable**: Define once, use in any query

## Limitations

1. ⚠️ Cannot reference other measures in expressions (must use raw columns)
2. ⚠️ More verbose than dbt's ratio metric syntax
3. ⚠️ Time-windowed conversions require complex expressions

## Conclusion

Conversion metrics are **fully supported and production-ready** in Unity Catalog Metric Views. They provide powerful, flexible ways to define business KPIs with rich formatting and semantic metadata. Use them for any ratio, percentage, or rate calculation your business needs!


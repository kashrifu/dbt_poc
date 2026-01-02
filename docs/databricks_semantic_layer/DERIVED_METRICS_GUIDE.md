# Unity Catalog Metric Views - Derived Metrics Guide

## Overview

**Derived metrics (also called calculated measures) are fully supported** in Unity Catalog Metric Views! You can define metrics that reference other measures or dimensions within the same metric view using the `MEASURE()` function.

## What Are Derived Metrics?

Derived metrics are measures that are calculated using other measures or dimensions in the same metric view. This enables:
- **Composability**: Build complex metrics from simpler ones
- **Reusability**: Define base measures once, reuse in multiple derived metrics
- **Maintainability**: Update base measures, derived metrics automatically reflect changes

## How to Define Derived Metrics

### Basic Syntax

Use the `MEASURE()` function to reference other measures:

```yaml
measures:
  - name: base_measure
    expr: SUM(source.amount)
    display_name: Base Measure

  - name: derived_measure
    expr: MEASURE(base_measure) * 1.0 / NULLIF(COUNT(*), 0)
    display_name: Derived Measure
```

### Key Rules

1. **Define base measures first**: Measures must be defined before they can be referenced
2. **Use MEASURE() function**: Reference measures using `MEASURE(<measure_name>)`
3. **Reference dimensions directly**: Use dimension names directly in expressions
4. **Always use NULLIF**: Protect against division by zero in derived calculations

## Examples

### Example 1: Conversion Rate

```yaml
measures:
  - name: total_orders
    expr: COUNT(DISTINCT source.order_id)
    display_name: Total Orders

  - name: completed_orders
    expr: COUNT(CASE WHEN source.status = 'completed' THEN 1 END)
    display_name: Completed Orders

  - name: conversion_rate
    expr: MEASURE(completed_orders) * 1.0 / NULLIF(MEASURE(total_orders), 0)
    display_name: Conversion Rate
    comment: Percentage of orders that were completed (derived from completed_orders and total_orders)
    format:
      type: percentage
      decimal_places:
        type: exact
        places: 2
```

### Example 2: Average Order Value

```yaml
measures:
  - name: total_revenue
    expr: SUM(source.amount)
    display_name: Total Revenue

  - name: total_orders
    expr: COUNT(DISTINCT source.order_id)
    display_name: Total Orders

  - name: average_order_value
    expr: MEASURE(total_revenue) / NULLIF(MEASURE(total_orders), 0)
    display_name: Average Order Value
    format:
      type: currency
      currency_code: USD
      decimal_places:
        type: exact
        places: 2
```

### Example 3: Multiple Derived Metrics

```yaml
measures:
  - name: total_revenue
    expr: SUM(source.amount)
    display_name: Total Revenue

  - name: completed_revenue
    expr: SUM(CASE WHEN source.status = 'completed' THEN source.amount ELSE 0 END)
    display_name: Completed Revenue

  - name: total_orders
    expr: COUNT(DISTINCT source.order_id)
    display_name: Total Orders

  - name: completed_orders
    expr: COUNT(CASE WHEN source.status = 'completed' THEN 1 END)
    display_name: Completed Orders

  - name: conversion_rate
    expr: MEASURE(completed_orders) * 1.0 / NULLIF(MEASURE(total_orders), 0)
    display_name: Conversion Rate
    format:
      type: percentage

  - name: completed_revenue_ratio
    expr: MEASURE(completed_revenue) / NULLIF(MEASURE(total_revenue), 0)
    display_name: Completed Revenue Ratio
    format:
      type: percentage

  - name: average_order_value
    expr: MEASURE(total_revenue) / NULLIF(MEASURE(total_orders), 0)
    display_name: Average Order Value
    format:
      type: currency
      currency_code: USD
```

## Best Practices

### 1. Define Base Measures First

**✅ Correct Order:**
```yaml
measures:
  - name: total_orders
    expr: COUNT(DISTINCT source.order_id)

  - name: completed_orders
    expr: COUNT(CASE WHEN source.status = 'completed' THEN 1 END)

  - name: conversion_rate
    expr: MEASURE(completed_orders) / NULLIF(MEASURE(total_orders), 0)
```

**❌ Incorrect Order:**
```yaml
measures:
  - name: conversion_rate
    expr: MEASURE(completed_orders) / NULLIF(MEASURE(total_orders), 0)  # Error: measures not defined yet

  - name: total_orders
    expr: COUNT(DISTINCT source.order_id)

  - name: completed_orders
    expr: COUNT(CASE WHEN source.status = 'completed' THEN 1 END)
```

### 2. Always Use NULLIF for Division

**✅ Correct:**
```yaml
expr: MEASURE(completed_orders) * 1.0 / NULLIF(MEASURE(total_orders), 0)
```

**❌ Incorrect:**
```yaml
expr: MEASURE(completed_orders) / MEASURE(total_orders)  # Division by zero risk
```

### 3. Use Clear Naming

```yaml
- name: conversion_rate
  display_name: Conversion Rate
  comment: Percentage of orders that were completed (derived from completed_orders and total_orders)
```

### 4. Combine with Formatting

```yaml
- name: conversion_rate
  expr: MEASURE(completed_orders) * 1.0 / NULLIF(MEASURE(total_orders), 0)
  display_name: Conversion Rate
  format:
    type: percentage
    decimal_places:
      type: exact
      places: 2
```

## Using Dimensions in Derived Metrics

You can also reference dimensions directly in derived metric expressions:

```yaml
dimensions:
  - name: order_status
    expr: source.status

measures:
  - name: total_orders
    expr: COUNT(DISTINCT source.order_id)

  - name: orders_by_status
    expr: COUNT(CASE WHEN order_status = 'completed' THEN 1 END)  # Reference dimension directly
```

## Comparison: Direct SQL vs. MEASURE() References

### Option 1: Direct SQL Expression
```yaml
- name: conversion_rate
  expr: COUNT(CASE WHEN source.status = 'completed' THEN 1 END) * 1.0 / NULLIF(COUNT(*), 0)
```

**Pros:**
- More flexible for complex logic
- Can use any SQL expression
- No dependency on other measures

**Cons:**
- Less reusable
- Duplicates logic if used in multiple places

### Option 2: MEASURE() Reference
```yaml
- name: conversion_rate
  expr: MEASURE(completed_orders) * 1.0 / NULLIF(MEASURE(total_orders), 0)
```

**Pros:**
- Reusable - define base measures once
- Maintainable - update base measure, derived metric reflects changes
- Clear dependencies
- Better for composability

**Cons:**
- Must define base measures first
- Limited to measures in same metric view

## Common Patterns

### Pattern 1: Ratio from Two Measures
```yaml
expr: MEASURE(numerator) / NULLIF(MEASURE(denominator), 0)
```

### Pattern 2: Percentage from Two Measures
```yaml
expr: MEASURE(part) * 1.0 / NULLIF(MEASURE(total), 0)
format:
  type: percentage
```

### Pattern 3: Average from Two Measures
```yaml
expr: MEASURE(sum) / NULLIF(MEASURE(count), 0)
```

### Pattern 4: Weighted Calculation
```yaml
expr: MEASURE(measure1) * 0.6 + MEASURE(measure2) * 0.4
```

## Limitations

1. ⚠️ Can only reference measures in the **same metric view**
2. ⚠️ Must define base measures **before** derived metrics
3. ⚠️ Cannot reference measures from **other metric views**
4. ⚠️ Cannot use **recursive references** (measure A → measure B → measure A)

## Querying Derived Metrics

Query derived metrics exactly like any other measure:

```sql
SELECT 
    order_date_month,
    MEASURE(conversion_rate) AS conversion_rate,
    MEASURE(average_order_value) AS aov
FROM workspace.dbt_poc.metric_derived_example
GROUP BY order_date_month;
```

## Conclusion

Derived metrics are a powerful feature that enables:
- ✅ Composability and reusability
- ✅ Maintainable metric definitions
- ✅ Clear dependencies between metrics
- ✅ Complex calculations from simple building blocks

Use `MEASURE()` function to reference other measures and build sophisticated metric hierarchies!


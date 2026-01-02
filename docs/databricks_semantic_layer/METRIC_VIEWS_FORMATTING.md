# Unity Catalog Metric Views - Formatting and Display Guide

## Overview

Unity Catalog Metric Views support rich formatting and display metadata for both dimensions and measures. This guide explains how to use these features to create user-friendly, well-documented metric views.

## Dimension Formatting

### Time Dimensions

```yaml
dimensions:
  - name: order_date
    expr: order_date
    display_name: Order Date
    comment: Date and time when the order was placed
    format:
      type: date_time
      date_format: year_month_day
      time_format: locale_hour_minute_second
      leading_zeros: false

  - name: order_date_month
    expr: DATE_TRUNC('month', order_date)
    display_name: Order Month
    comment: Month in which the order was placed
    format:
      type: date
      date_format: locale_short_month
      leading_zeros: false
```

### Format Options for Time Dimensions

- **type**: `date`, `date_time`, `time`
- **date_format**: 
  - `year_month_day`
  - `locale_short_month`
  - `locale_long_month`
  - `year_month`
  - `month_day`
- **time_format**: 
  - `locale_hour_minute_second`
  - `hour_minute`
  - `hour_minute_second`
- **leading_zeros**: `true` | `false`

### Categorical Dimensions

```yaml
  - name: order_status
    expr: status
    display_name: Order Status
    comment: Status of the order (e.g., completed, pending, cancelled)
```

Categorical dimensions typically don't need format specifications, but can include:
- `display_name`: User-friendly name shown in UI
- `comment`: Description of the dimension

## Measure Formatting

### Currency Measures

```yaml
measures:
  - name: total_revenue
    expr: SUM(amount)
    display_name: Total Revenue
    comment: Total revenue from all orders
    format:
      type: currency
      currency_code: USD
      decimal_places:
        type: exact
        places: 2
      abbreviation: compact
```

### Currency Format Options

- **type**: `currency`
- **currency_code**: ISO currency code (e.g., `USD`, `EUR`, `GBP`)
- **decimal_places**:
  - `type`: `exact` | `auto`
  - `places`: Number of decimal places (for `exact`)
- **abbreviation**: `compact` | `none`
  - `compact`: Shows abbreviated format (e.g., "1.2M" instead of "1,200,000")
  - `none`: Shows full number

### Number Measures

```yaml
  - name: total_orders
    expr: COUNT(DISTINCT order_id)
    display_name: Total Orders
    comment: Total number of distinct orders
    format:
      type: number
      decimal_places:
        type: exact
        places: 0
      abbreviation: compact
```

### Number Format Options

- **type**: `number`
- **decimal_places**:
  - `type`: `exact` | `auto`
  - `places`: Number of decimal places
- **abbreviation**: `compact` | `none`

### Percentage Measures

```yaml
  - name: conversion_rate
    expr: COUNT(CASE WHEN source.status = 'completed' THEN 1 END) * 1.0 / COUNT(*)
    display_name: Conversion Rate
    comment: Ratio of completed orders to total orders
    format:
      type: percentage
      decimal_places:
        type: exact
        places: 2
```

### Percentage Format Options

- **type**: `percentage` (not "percent")
- **decimal_places**:
  - `type`: `exact` | `auto`
  - `places`: Number of decimal places

## Display Metadata

### display_name

Provides a user-friendly name that appears in:
- Catalog Explorer
- SQL autocomplete
- BI tools
- Dashboards

```yaml
display_name: Total Revenue
```

### comment

Descriptive text explaining what the dimension or measure represents:

```yaml
comment: Total revenue from all orders, including all payment methods
```

## Complete Example

```yaml
version: 1.1
source: workspace.dbt_poc.fct_orders

dimensions:
  - name: order_date_month
    expr: DATE_TRUNC('month', order_date)
    display_name: Order Month
    comment: Month in which the order was placed
    format:
      type: date
      date_format: locale_short_month
      leading_zeros: false

  - name: order_status
    expr: status
    display_name: Order Status
    comment: Status of the order (e.g., completed, pending, cancelled)

measures:
  - name: total_revenue
    expr: SUM(amount)
    display_name: Total Revenue
    comment: Total revenue from all orders
    format:
      type: currency
      currency_code: USD
      decimal_places:
        type: exact
        places: 2
      abbreviation: compact

  - name: total_orders
    expr: COUNT(DISTINCT order_id)
    display_name: Total Orders
    comment: Total number of distinct orders
    format:
      type: number
      decimal_places:
        type: exact
        places: 0
      abbreviation: compact
```

## Benefits of Formatting

1. **User Experience**: Display names and comments make metrics self-documenting
2. **Consistency**: Standardized formatting across dashboards and reports
3. **Localization**: Locale-aware date and number formatting
4. **Readability**: Compact abbreviations for large numbers (1.2M vs 1,200,000)
5. **Currency Handling**: Automatic currency symbols and formatting

## Best Practices

1. **Always include display_name**: Makes metrics discoverable and user-friendly
2. **Add descriptive comments**: Help users understand what each metric represents
3. **Use appropriate formats**: Currency for money, percentages for rates
4. **Consider abbreviation**: Use `compact` for large numbers in dashboards
5. **Be consistent**: Use the same formatting patterns across related metrics

## Format Support in Tools

- **Catalog Explorer**: Shows display names and comments
- **SQL Editor**: Autocomplete uses display names
- **Dashboards**: Formatting applied automatically
- **BI Tools**: Formatting passed through JDBC/ODBC
- **Databricks Assistant**: Uses comments for context

## Limitations

- Format specifications are hints for UI display
- Actual SQL queries return raw values
- Formatting is applied by consuming tools, not in SQL execution
- Not all format options may be supported in all tools

## References

- [Databricks Metric Views Formatting](https://docs.databricks.com/en/metric-views/format.html)
- [Unity Catalog Business Semantics](https://docs.databricks.com/en/connect/unity-catalog/business-semantics.html)


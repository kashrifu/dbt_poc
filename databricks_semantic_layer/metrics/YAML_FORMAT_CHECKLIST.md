# Unity Catalog Metric Views - YAML Format Checklist

This document verifies that all YAML files follow the enhanced format standard with display names, comments, and formatting.

## Format Standard

All Unity Catalog Metric View YAML files should include:

### ✅ Required for Dimensions:
- [x] `name`: Technical name
- [x] `expr`: SQL expression
- [x] `display_name`: User-friendly name
- [x] `comment`: Description
- [x] `format`: Formatting specification (for time dimensions)

### ✅ Required for Measures:
- [x] `name`: Technical name
- [x] `expr`: SQL aggregation expression
- [x] `display_name`: User-friendly name
- [x] `comment`: Description
- [x] `format`: Formatting specification (currency, number, percentage)

## File Status

### ✅ revenue_metrics.yaml
- **Status**: Complete
- **Dimensions**: 5 (all with display_name, comment, format)
- **Measures**: 6 (all with display_name, comment, currency format)
- **Format**: ✅ Currency formatting (USD, 2 decimals, compact)
- **Date Formatting**: ✅ Time dimensions with proper date formats

### ✅ order_metrics.yaml
- **Status**: Complete
- **Dimensions**: 5 (all with display_name, comment, format)
- **Measures**: 4 (all with display_name, comment, number format)
- **Format**: ✅ Number formatting (0 decimals, compact)
- **Date Formatting**: ✅ Time dimensions with proper date formats

### ✅ revenue_metrics_with_stores.yaml
- **Status**: Complete
- **Joins**: ✅ Multi-hop join to dim_stores
- **Dimensions**: 7 (all with display_name, comment, format)
- **Measures**: 3 (all with display_name, comment, currency format)
- **Format**: ✅ Currency formatting (USD, 2 decimals, compact)
- **Date Formatting**: ✅ Time dimensions with proper date formats

### ✅ revenue_metrics_with_customers.yaml
- **Status**: Complete (NEW)
- **Joins**: ✅ Multi-hop join to dim_customers
- **Dimensions**: 8 (all with display_name, comment, format)
- **Measures**: 4 (all with display_name, comment, proper formats)
- **Format**: ✅ Currency and number formatting
- **Date Formatting**: ✅ Time dimensions with proper date formats

## Format Patterns Used

### Time Dimensions
```yaml
format:
  type: date_time | date
  date_format: year_month_day | locale_short_month
  time_format: locale_hour_minute_second  # for date_time only
  leading_zeros: false
```

### Currency Measures
```yaml
format:
  type: currency
  currency_code: USD
  decimal_places:
    type: exact
    places: 2
  abbreviation: compact
```

### Number Measures
```yaml
format:
  type: number
  decimal_places:
    type: exact
    places: 0
  abbreviation: compact
```

## Verification Checklist

For each YAML file, verify:

- [x] `version: 1.1` specified
- [x] `source` points to correct table
- [x] All dimensions have `display_name` and `comment`
- [x] All measures have `display_name` and `comment`
- [x] Time dimensions have `format` specification
- [x] Currency measures have `format` with `currency_code: USD`
- [x] Number measures have `format` with appropriate decimal places
- [x] Joins (if any) are properly defined with `name`, `source`, `condition`, `type`
- [x] Table aliases used correctly in expressions (e.g., `fct_orders.amount`)

## Consistency Checks

- [x] All revenue measures use same currency format (USD, 2 decimals, compact)
- [x] All count measures use same number format (0 decimals, compact)
- [x] All time dimensions use consistent date formatting
- [x] Display names are user-friendly and consistent
- [x] Comments are descriptive and helpful

## Usage

All YAML files are ready to be:
1. Copied into Catalog Explorer UI when creating metric views
2. Embedded in SQL CREATE VIEW statements
3. Version controlled in git
4. Shared with team members

## Next Steps

1. ✅ All YAML files follow the enhanced format
2. ✅ All files include display names and comments
3. ✅ All files include proper formatting
4. ✅ Multi-hop joins are properly defined
5. Ready for deployment to Databricks Unity Catalog


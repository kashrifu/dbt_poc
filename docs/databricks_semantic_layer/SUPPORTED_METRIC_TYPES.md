# Unity Catalog Metric Views - Supported Metric Types

This document clearly outlines what types of metrics are supported and not supported in Unity Catalog Metric Views YAML definitions.

## ✅ Supported Metric Types

### 1. Simple Aggregation Metrics
**Status**: ✅ Fully Supported

Metrics that aggregate values using standard SQL aggregation functions:
- `SUM()` - Sum of values
- `COUNT()` / `COUNT(DISTINCT)` - Count of items
- `AVG()` - Average of values
- `MIN()` / `MAX()` - Minimum/Maximum values

**Example:**
```yaml
measures:
  - name: total_revenue
    expr: SUM(source.amount)
    display_name: Total Revenue
```

### 2. Filtered Metrics
**Status**: ✅ Fully Supported

Metrics with conditional logic using CASE WHEN expressions:
- Filtered aggregations
- Conditional counts
- Conditional sums

**Example:**
```yaml
measures:
  - name: completed_revenue
    expr: SUM(CASE WHEN source.status = 'completed' THEN source.amount ELSE 0 END)
    display_name: Completed Revenue
```

### 3. Ratio Metrics
**Status**: ✅ Fully Supported

Metrics that calculate ratios between two values:
- Division of two aggregations
- Percentage calculations
- Rate calculations

**Example:**
```yaml
measures:
  - name: average_order_value
    expr: SUM(source.amount) / NULLIF(COUNT(DISTINCT source.order_id), 0)
    display_name: Average Order Value
```

### 4. Conversion Metrics
**Status**: ✅ Fully Supported

Metrics that measure conversion rates, adoption rates, or completion rates:
- Order completion rate
- Credit card adoption rate
- Coupon usage rate
- Cart-to-purchase rate

**Example:**
```yaml
measures:
  - name: conversion_rate
    expr: COUNT(CASE WHEN source.status = 'completed' THEN 1 END) * 1.0 / NULLIF(COUNT(*), 0)
    display_name: Conversion Rate
    format:
      type: percentage
      decimal_places:
        type: exact
        places: 2
```

### 5. Combined Expression Metrics
**Status**: ✅ Fully Supported

Metrics that combine multiple columns or use arithmetic operations:
- Sum of multiple columns
- Weighted averages
- Complex calculations using SQL expressions

**Example:**
```yaml
measures:
  - name: total_payment_revenue
    expr: SUM(source.credit_card_amount + source.coupon_amount + source.bank_transfer_amount)
    display_name: Total Payment Revenue
```

### 6. Derived Metrics (Calculated Measures)
**Status**: ✅ Fully Supported

Metrics that reference other measures or dimensions in the same metric view:
- Use `MEASURE(<measure_name>)` to reference other measures
- Reference dimensions directly by name
- Enables composability and reusability

**Example:**
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
    format:
      type: percentage
      decimal_places:
        type: exact
        places: 2
```

**Key Points:**
- ✅ Define base measures before derived metrics in YAML
- ✅ Use `MEASURE(<measure_name>)` to reference measures
- ✅ Use dimension names directly in expressions
- ✅ Can combine multiple measures in calculations

## ❌ Not Supported Features (December 2025)

### 1. Non-Aggregate (Row-Level) Metrics
**Status**: ❌ Not Supported

Metrics that operate on individual rows without aggregation:
- Row-level calculations
- Per-row transformations
- Non-aggregated expressions
- Simple column references

**Why**: Unity Catalog Metric Views require aggregation functions. All measures must use aggregation functions like SUM, COUNT, AVG, etc.

**Workaround**: Use business views or regular SQL views for row-level metrics.

**Example:**
```yaml
# ❌ NOT Supported
measures:
  - name: order_amount
    expr: source.amount  # Error: Must be aggregated

# ✅ Supported
measures:
  - name: total_revenue
    expr: SUM(source.amount)  # Aggregated
```

### 2. Multi-Step Logic / Procedural Logic
**Status**: ❌ Not Supported

Metrics requiring procedural or iterative calculations:
- Multi-step calculations with intermediate results
- Iterative algorithms
- Recursive calculations
- Stored procedures
- Loops (WHILE, FOR)
- IF/ELSE statements (outside CASE expressions)
- Scripting languages (Python, Scala, R)

**Why**: Metric views support single SQL expressions, not multi-step procedural logic.

**Workaround**: Use business views or materialized views with multiple CTEs.

**Note**: CASE WHEN expressions ARE supported for conditional logic.

### 3. External API/Data Sources / Non-SQL Data Sources
**Status**: ❌ Not Supported

Metrics that pull data from external sources:
- REST API calls
- External databases (outside Unity Catalog)
- File systems (S3, ADLS, etc.) directly
- Streaming sources
- Non-SQL data formats

**Why**: Metric views only support SQL-based tables, views, and metric views in Unity Catalog as sources.

**Workaround**: Ingest external data into Unity Catalog tables first, then create metric views.

### 4. Advanced Statistical Metrics / Custom UDFs
**Status**: ❌ Not Supported

Metrics requiring advanced statistical functions or custom functions:
- Median
- Mode
- Percentiles (beyond basic SQL)
- Custom statistical models
- Machine learning predictions
- Custom user-defined functions (UDFs)
- Python/Scala UDFs
- Non-standard SQL functions

**Why**: Limited to standard SQL aggregation functions available in Databricks SQL. Custom UDFs are not supported.

**Workaround**: 
1. Use business views with custom SQL or Databricks ML functions
2. Create views that apply UDFs to source data, then reference in metric view

### 5. Dynamic Parameters / Variables
**Status**: ❌ Not Supported

Metrics with runtime or user input parameters:
- User-defined date ranges
- Runtime filters
- Parameterized calculations
- Interactive metrics
- Template variables
- Runtime variables

**Why**: Metric views are static definitions without runtime parameters.

**Workaround**: Use queries with WHERE clauses or create parameterized business views.

**Example:**
```sql
-- Dynamic filtering in query (not in metric view)
SELECT 
    order_date_month,
    MEASURE(total_revenue) AS revenue
FROM workspace.dbt_poc.metric_revenue_metrics
WHERE order_date_month >= '2024-01-01'  -- Dynamic filter
GROUP BY order_date_month;
```

## Support Matrix

| Metric Type | Supported in YAML? | Notes |
|------------|-------------------|-------|
| **Simple Aggregation** | ✅ Yes | SUM, COUNT, AVG, MIN, MAX |
| **Filtered Metrics** | ✅ Yes | CASE WHEN expressions |
| **Ratio Metrics** | ✅ Yes | Division of aggregations |
| **Conversion Metrics** | ✅ Yes | Percentage/rate calculations |
| **Combined Expressions** | ✅ Yes | Multiple columns, arithmetic |
| **Derived Metrics** | ✅ Yes | MEASURE() function to reference other measures |
| **Non-Aggregate (Row-Level)** | ❌ No | Requires aggregation |
| **Multi-Step/Procedural Logic** | ❌ No | Single expression only (CASE WHEN supported) |
| **External API/Data Sources** | ❌ No | Unity Catalog SQL sources only |
| **Advanced Stats/Custom UDFs** | ❌ No | Standard SQL functions only |
| **Dynamic Parameters** | ❌ No | Static definitions only |
| **Multi-Table Fact Sources** | ❌ No | Single source only (use unified views) |
| **Non-LEFT Joins** | ❌ No | LEFT OUTER JOIN only |
| **Row-Level Security** | ❌ No | Implement at table/view level |
| **Advanced Semantic Metadata** | ⚠️ Limited | Basic formatting only |
| **Complex Window Functions** | ❌ Limited | Specific syntax only |

## Best Practices

### ✅ Do Use Metric Views For:
- Standard business metrics (revenue, counts, averages)
- Conversion rates and adoption metrics
- Ratio calculations
- Filtered aggregations
- Time-based aggregations
- Derived metrics that reference other measures (using MEASURE())

### ❌ Don't Use Metric Views For:
- Row-level calculations (use business views)
- Complex multi-step/procedural logic (use business views or materialized views)
- External data integration (ingest first, then metric view)
- Advanced statistics/custom UDFs (use business views with custom SQL)
- Dynamic/interactive metrics (use queries with parameters)
- Multi-table fact sources (create unified views first)
- Non-LEFT joins (use LEFT joins only)
- Row-level security (implement at table/view level)
- Complex window functions (use business views)
- Custom UDFs (apply in views first)

## Workarounds

### For Non-Supported Types:

1. **Row-Level Metrics**: Create business views with row-level calculations
2. **Multi-Step Logic**: Use business views with CTEs or materialized views
3. **External Data**: Ingest into Unity Catalog tables first
4. **Advanced Stats**: Use business views with Databricks SQL/ML functions
5. **Dynamic Parameters**: Use SQL queries with WHERE clauses or parameterized views

## Examples

### ✅ Supported: Conversion Rate
```yaml
measures:
  - name: conversion_rate
    expr: COUNT(CASE WHEN source.status = 'completed' THEN 1 END) * 1.0 / NULLIF(COUNT(*), 0)
    display_name: Conversion Rate
    format:
      type: percentage
```

### ❌ Not Supported: Row-Level Metric
```yaml
# This will NOT work - no aggregation
measures:
  - name: order_profit_margin
    expr: (source.amount - source.cost) / source.amount  # Missing aggregation
```

**Workaround**: Create business view first, then aggregate in metric view:
```sql
-- Business view
CREATE VIEW business_order_margins AS
SELECT 
    order_id,
    (amount - cost) / amount AS profit_margin
FROM fct_orders;

-- Then in metric view
measures:
  - name: avg_profit_margin
    expr: AVG(source.profit_margin)  # Now aggregated
```

## Conclusion

Unity Catalog Metric Views excel at:
- ✅ Standard business metrics
- ✅ Aggregated calculations
- ✅ Conversion and ratio metrics
- ✅ Filtered aggregations

For advanced use cases, combine metric views with:
- Business views for complex logic
- Materialized views for performance
- Custom SQL queries for dynamic needs


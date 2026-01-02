# Unity Catalog Metric Views - Limitations (December 2025)

This document lists all features and capabilities that are **NOT supported** in Unity Catalog Metric Views as of December 2025.

## Not Supported Features

### 1. Non-Aggregate Measures

**Status**: ❌ Not Supported

All measures must be aggregate expressions (e.g., SUM, COUNT, AVG). You cannot define measures that are simple column references or non-aggregated calculations.

**Example of what's NOT supported:**
```yaml
measures:
  - name: order_amount  # ❌ Error: Not an aggregation
    expr: source.amount  # Must use SUM(source.amount) instead
```

**Workaround**: Use business views for row-level calculations, then aggregate in metric view.

---

### 2. Complex Window Functions Beyond Supported Syntax

**Status**: ❌ Limited Support

Only specific windowing options are supported for measures (e.g., trailing/leading/cumulative windows). Arbitrary SQL window functions (like ROW_NUMBER, RANK, etc.) are not supported in the metric view YAML.

**Not Supported:**
- `ROW_NUMBER()`
- `RANK()`
- `DENSE_RANK()`
- `LAG()` / `LEAD()` (beyond supported syntax)
- Complex window frame specifications

**Workaround**: Use business views with window functions, then aggregate in metric view.

**See**: `WINDOWED_METRICS_NOTE.md` for details and workarounds.

---

### 3. Custom SQL Functions or UDFs

**Status**: ❌ Not Supported

You cannot use custom user-defined functions (UDFs) or non-standard SQL functions in measure or dimension expressions.

**Not Supported:**
- Custom UDFs
- Python/Scala UDFs
- Non-standard SQL functions
- External function libraries

**Workaround**: 
1. Create a view that applies UDFs to source data
2. Reference that view in the metric view
3. Use standard SQL functions only

---

### 4. Multi-Table Fact Sources

**Status**: ❌ Not Supported

The `source` property must be a single table, view, or SELECT query. You cannot define a metric view that natively combines multiple fact tables.

**Not Supported:**
```yaml
source: 
  - workspace.dbt_poc.fct_orders
  - workspace.dbt_poc.fct_returns  # ❌ Error: Multiple sources not allowed
```

**Workaround**: 
1. Create a unified view that combines multiple fact tables
2. Reference that unified view in the metric view
3. Use JOINs within the unified view definition

**Example:**
```sql
CREATE VIEW unified_facts AS
SELECT * FROM fct_orders
UNION ALL
SELECT * FROM fct_returns;

-- Then in metric view:
source: workspace.dbt_poc.unified_facts
```

---

### 5. Non-LEFT Joins

**Status**: ❌ Not Supported

Only LEFT OUTER JOINs are supported for dimension tables. Other join types (INNER, RIGHT, FULL) are not supported in the metric view YAML.

**Not Supported:**
```yaml
joins:
  - name: stores
    source: workspace.dbt_poc.dim_stores
    on: source.store_id = stores.store_id
    type: inner  # ❌ Error: Only 'left' is supported
```

**Supported:**
```yaml
joins:
  - name: stores
    source: workspace.dbt_poc.dim_stores
    on: source.store_id = stores.store_id
    # type defaults to 'left' - this is the only option
```

**Workaround**: 
1. Use LEFT joins (recommended for fact tables anyway)
2. Pre-filter dimension tables to ensure referential integrity
3. Use business views with different join types if needed

---

### 6. Dynamic Parameters or Variables

**Status**: ❌ Not Supported

Metric views do not support dynamic parameters, runtime variables, or user input for filtering or calculation logic.

**Not Supported:**
- Parameterized date ranges
- User-defined filters
- Runtime variables
- Template variables
- Dynamic calculation logic

**Workaround**: 
1. Use SQL queries with WHERE clauses for dynamic filtering
2. Create multiple metric views for different scenarios
3. Use business views with parameters if needed

**Example:**
```sql
-- Query with dynamic filter
SELECT 
    order_date_month,
    MEASURE(total_revenue) AS revenue
FROM workspace.dbt_poc.metric_revenue_metrics
WHERE order_date_month >= '2024-01-01'  -- Dynamic filter in query
GROUP BY order_date_month;
```

---

### 7. Advanced Semantic Metadata

**Status**: ⚠️ Limited Support

While display names, synonyms, and basic formatting are supported, more advanced metadata is not natively supported.

**Supported:**
- ✅ `display_name` - User-friendly names
- ✅ `comment` - Descriptions
- ✅ `format` - Currency, percentage, number formatting
- ✅ Basic date/time formatting

**Not Supported:**
- ❌ Hierarchical relationships between dimensions
- ❌ Custom tooltips or extended descriptions
- ❌ Conditional formatting rules
- ❌ Data quality indicators
- ❌ Certification badges (must use Unity Catalog)
- ❌ Custom metadata schemas

**Workaround**: Use Unity Catalog's native features for advanced metadata (certifications, tags, etc.).

---

### 8. Row-Level Security or Data Masking

**Status**: ❌ Not Supported

Metric views do not provide built-in row-level security or data masking features. These must be handled at the table/view level in Unity Catalog.

**Not Supported:**
- Row-level security in metric view definition
- Data masking in metric view
- Column-level security in metric view
- Dynamic data filtering based on user

**Workaround**: 
1. Implement row-level security at the source table/view level
2. Use Unity Catalog's native access control
3. Create filtered views for different user groups
4. Use business views with security logic

**Example:**
```sql
-- Create secure view with RLS
CREATE VIEW secure_orders AS
SELECT * FROM fct_orders
WHERE region = CURRENT_USER_REGION();  -- RLS at view level

-- Then create metric view on secure view
source: workspace.dbt_poc.secure_orders
```

---

### 9. Non-SQL Data Sources

**Status**: ❌ Not Supported

Only SQL-based tables, views, and metric views in Unity Catalog are supported as sources. You cannot reference external APIs, files, or non-SQL data sources.

**Not Supported:**
- External REST APIs
- File systems (S3, ADLS, etc.) directly
- Streaming sources
- External databases (outside Unity Catalog)
- Non-SQL data formats

**Workaround**: 
1. Ingest external data into Unity Catalog tables first
2. Use Databricks ingestion pipelines
3. Create views on ingested data
4. Reference those views in metric views

---

### 10. Procedural Logic or Scripting

**Status**: ❌ Not Supported

You cannot use procedural SQL (e.g., loops, IF statements outside of CASE expressions) or scripting languages in metric view definitions.

**Not Supported:**
- Loops (WHILE, FOR)
- IF/ELSE statements (outside CASE)
- Stored procedures
- Scripting languages (Python, Scala, R)
- Control flow logic

**Supported:**
- ✅ CASE WHEN expressions (conditional logic)
- ✅ SQL aggregate functions
- ✅ Standard SQL expressions

**Workaround**: 
1. Use CASE WHEN for conditional logic
2. Create business views with procedural logic
3. Use Databricks notebooks for complex transformations
4. Materialize results in tables/views

---

## Summary Table

| Feature | Status | Workaround |
|---------|--------|------------|
| **Non-Aggregate Measures** | ❌ Not Supported | Business views |
| **Complex Window Functions** | ❌ Limited | Business views, materialized views |
| **Custom UDFs** | ❌ Not Supported | Views with UDFs applied |
| **Multi-Table Fact Sources** | ❌ Not Supported | Unified views |
| **Non-LEFT Joins** | ❌ Not Supported | Use LEFT joins only |
| **Dynamic Parameters** | ❌ Not Supported | Query-level filters |
| **Advanced Semantic Metadata** | ⚠️ Limited | Unity Catalog features |
| **Row-Level Security** | ❌ Not Supported | Table/view level RLS |
| **Non-SQL Data Sources** | ❌ Not Supported | Ingest into Unity Catalog first |
| **Procedural Logic** | ❌ Not Supported | Business views, notebooks |

## Best Practices

### ✅ Do Use Metric Views For:
- Standard aggregated business metrics
- Metrics with standard SQL aggregations
- Metrics that reference Unity Catalog tables/views
- Metrics with LEFT joins to dimensions
- Metrics with basic formatting needs

### ❌ Don't Use Metric Views For:
- Row-level calculations (use business views)
- Complex window functions (use business views)
- Multi-table fact sources (create unified views first)
- Dynamic parameters (use query-level filters)
- Row-level security (implement at table/view level)
- External data sources (ingest first)
- Procedural logic (use business views or notebooks)

## Workaround Patterns

### Pattern 1: Business Views for Complex Logic
```sql
-- Create business view with complex logic
CREATE VIEW business_complex_metrics AS
SELECT 
    order_id,
    CASE 
        WHEN amount > 1000 THEN 'high_value'
        ELSE 'standard'
    END AS order_tier,
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date) AS order_sequence
FROM fct_orders;

-- Then create metric view on business view
source: workspace.dbt_poc.business_complex_metrics
```

### Pattern 2: Unified Views for Multi-Table Sources
```sql
-- Create unified view
CREATE VIEW unified_facts AS
SELECT 'orders' AS source_type, * FROM fct_orders
UNION ALL
SELECT 'returns' AS source_type, * FROM fct_returns;

-- Then create metric view
source: workspace.dbt_poc.unified_facts
```

### Pattern 3: Query-Level Dynamic Filtering
```sql
-- Use WHERE clauses in queries for dynamic filtering
SELECT 
    order_date_month,
    MEASURE(total_revenue) AS revenue
FROM workspace.dbt_poc.metric_revenue_metrics
WHERE order_date_month >= CURRENT_DATE - INTERVAL 30 DAYS  -- Dynamic
GROUP BY order_date_month;
```

## Conclusion

Unity Catalog Metric Views are designed for **standard aggregated business metrics** with **standard SQL expressions**. For advanced use cases, use the workaround patterns above:

1. **Business Views** - For complex logic, window functions, row-level calculations
2. **Unified Views** - For multi-table sources
3. **Query-Level Filters** - For dynamic parameters
4. **Table/View Level** - For security and data masking
5. **Ingestion Pipelines** - For external data sources

This design keeps metric views simple, performant, and maintainable while providing flexibility through the broader Databricks platform.


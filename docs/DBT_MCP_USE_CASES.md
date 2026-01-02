# dbt MCP Server - Use Cases for MetricFlow POC

This document provides specific, practical examples of how an AI assistant with dbt MCP server access would help with your Jaffle Shop MetricFlow POC.

---

## Use Case 1: Natural Language Metric Queries

### Scenario
**User asks:** "What was our total revenue last month?"

### What MCP Server Does
1. **Understands intent**: User wants `total_revenue` metric filtered by last month
2. **Discovers available metrics**: Queries MCP `list_metrics()` → finds `total_revenue`
3. **Finds time dimensions**: Queries `get_semantic_model('orders')` → finds `order__order_date__month`
4. **Generates correct query**: 
   ```bash
   mf query --metrics total_revenue --group-by order__order_date__month --where "{{ TimeDimension('order__order_date__month') }} = '2024-12'"
   ```
5. **Executes and formats**: Returns formatted result with currency formatting

### Result
```
Total Revenue (December 2024): $45,230.50
```

---

## Use Case 2: Multi-Dimensional Analysis

### Scenario
**User asks:** "Show me completed revenue by store type and customer region for Q4"

### What MCP Server Does
1. **Identifies metric**: `completed_revenue` (filtered metric)
2. **Finds dimensions**: 
   - `store__store_type` (from stores semantic model via multi-hop join)
   - `customer__customer_region` (from customers semantic model via multi-hop join)
   - `order__order_date__quarter` (time dimension)
3. **Validates join paths**: Confirms multi-hop joins are possible via `order` → `store` and `order` → `customer` entities
4. **Generates query**:
   ```bash
   mf query --metrics completed_revenue \
     --group-by store__store_type,customer__customer_region,order__order_date__quarter \
     --where "{{ TimeDimension('order__order_date__quarter') }} = '2024-Q4'"
   ```
5. **Explains the query**: Shows dataflow plan if user asks

### Result
```
Store Type    | Customer Region | Quarter | Completed Revenue
--------------|-----------------|---------|------------------
Premium       | West            | 2024-Q4 | $12,450.00
Premium       | East            | 2024-Q4 | $10,230.00
Standard      | West            | 2024-Q4 | $8,920.00
...
```

---

## Use Case 3: Conversion Metric Analysis

### Scenario
**User asks:** "What's our visit-to-order conversion rate for the last 30 days?"

### What MCP Server Does
1. **Finds conversion metric**: `visit_to_order_conversion_rate_30d`
2. **Understands metric structure**: 
   - Base: `visit_count` from `visits` semantic model
   - Conversion: `order_count` from `orders` semantic model
   - Entity: `customer` (links both)
   - Window: 30 days
3. **Checks time dimensions**: Both semantic models have time dimensions (`visit_date`, `order_date`)
4. **Generates query**:
   ```bash
   mf query --metrics visit_to_order_conversion_rate_30d \
     --group-by visit__visit_date__day \
     --where "{{ TimeDimension('visit__visit_date__day') }} >= '2024-12-01'"
   ```
5. **Explains the metric**: "This tracks the percentage of visitors who place an order within 30 days of their visit, grouped by customer."

### Result
```
Visit Date   | Conversion Rate (30d)
-------------|----------------------
2024-12-01   | 12.5%
2024-12-02   | 13.2%
...
```

---

## Use Case 4: Metric Discovery and Comparison

### Scenario
**User asks:** "What revenue metrics do we have? Show me the difference between total_revenue and completed_revenue"

### What MCP Server Does
1. **Lists all revenue metrics**: 
   - `total_revenue` (simple metric, sum of all orders)
   - `completed_revenue` (filtered metric, only completed orders)
   - `credit_card_revenue`, `coupon_revenue`, `bank_transfer_revenue`
   - `total_payment_revenue` (sum of all payment methods)
2. **Explains differences**: 
   - `total_revenue`: Includes all orders regardless of status
   - `completed_revenue`: Only orders with status = 'completed'
3. **Suggests comparison query**:
   ```bash
   mf query --metrics total_revenue,completed_revenue \
     --group-by order__order_date__month
   ```
4. **Calculates gap**: Shows the difference (revenue from non-completed orders)

### Result
```
Month        | Total Revenue | Completed Revenue | Difference
-------------|---------------|-------------------|------------
2024-12      | $45,230.50   | $42,100.00       | $3,130.50
```

---

## Use Case 5: Creating New Metrics

### Scenario
**User asks:** "I need a metric for average revenue per customer by region"

### What MCP Server Does
1. **Checks existing metrics**: Finds `revenue_per_customer` but it's revenue per order, not per customer
2. **Analyzes semantic models**: 
   - `orders` has `order_total` measure and `customer` entity
   - `customers` has `customer_region` dimension
3. **Suggests approach**: Create a ratio metric:
   - Numerator: `total_revenue` (sum of all order amounts)
   - Denominator: Need customer count metric
4. **Checks if customer_count metric exists**: If not, suggests creating it first
5. **Generates YAML**:
   ```yaml
   - name: revenue_per_customer_by_region
     label: "Revenue Per Customer by Region"
     description: "Average revenue per distinct customer, grouped by region"
     type: ratio
     type_params:
       numerator: total_revenue
       denominator: total_customers  # Would need to create this metric first
   ```
6. **Validates**: Checks that `customer__customer_region` dimension is available for grouping

### Result
Creates the metric definition with proper syntax and validation.

---

## Use Case 6: Impact Analysis Before Changes

### Scenario
**User asks:** "What will break if I change the `order_total` measure definition?"

### What MCP Server Does
1. **Traces dependencies**: 
   - Finds all metrics using `order_total`:
     - `total_revenue` (direct)
     - `completed_revenue` (uses `order_total` with filter)
     - `average_order_value` (ratio using `total_revenue`)
     - `revenue_per_customer` (ratio using `total_revenue`)
     - `credit_card_payment_ratio` (indirect, uses `total_revenue` as denominator)
2. **Checks exposures**: Finds any dashboards or reports using these metrics
3. **Lists downstream impact**:
   ```
   Direct Dependencies:
   - total_revenue (simple metric)
   - completed_revenue (filtered metric)
   
   Indirect Dependencies (via total_revenue):
   - average_order_value
   - revenue_per_customer
   - credit_card_payment_ratio
   
   Exposures:
   - revenue_dashboard (uses total_revenue, completed_revenue)
   - monthly_report (uses average_order_value)
   ```
4. **Suggests testing**: Run `dbt test` and `mf query` on affected metrics

### Result
Complete impact analysis showing what needs to be tested after the change.

---

## Use Case 7: Debugging Metric Queries

### Scenario
**User gets error:** "The given input does not match any of the available group-by-items for SimpleMetric('completed_revenue')"

### What MCP Server Does
1. **Analyzes the error**: Dimension reference issue
2. **Checks semantic model**: Finds `orders` semantic model has entity `order` (singular)
3. **Identifies problem**: User likely used `orders__order_status` instead of `order__order_status`
4. **Suggests correct syntax**: 
   - ❌ Wrong: `Dimension('orders__order_status')`
   - ✅ Correct: `Dimension('order__order_status')`
5. **Lists available dimensions**: Shows all valid dimension references:
   ```
   Available dimensions for completed_revenue:
   - order__order_date (time, multiple grains)
   - order__order_status (categorical)
   - store__store_type (via multi-hop join)
   - customer__customer_region (via multi-hop join)
   ```

### Result
Identifies the issue and provides the correct syntax.

---

## Use Case 8: Explaining Complex Metrics

### Scenario
**User asks:** "How does the visit_to_order_conversion_rate_7d metric work?"

### What MCP Server Does
1. **Reads metric definition**: Gets YAML from `revenue.yml`
2. **Explains structure**:
   ```
   Type: Conversion Metric
   Base Event: Customer visits (visits semantic model)
   Conversion Event: Orders placed (orders semantic model)
   Linking Entity: customer (customer_id)
   Time Window: 7 days
   Calculation: Percentage of visitors who place an order within 7 days
   ```
3. **Shows the logic**:
   - For each customer visit, checks if they placed an order within 7 days
   - Counts how many visits resulted in conversions
   - Calculates: (converted visits / total visits) × 100
4. **Explains why it needs separate semantic models**: Base and conversion measures must come from different tables
5. **Shows example query**: Demonstrates how to query it

### Result
Clear explanation of how the conversion metric works with your specific data model.

---

## Use Case 9: Optimizing Queries

### Scenario
**User asks:** "This query is slow. Can you optimize it?"

### What MCP Server Does
1. **Analyzes the query**: 
   ```bash
   mf query --metrics total_revenue,completed_revenue,average_order_value \
     --group-by store__store_type,customer__customer_region,order__order_date__day
   ```
2. **Gets execution plan**: Uses `--explain --show-dataflow-plan` to see the SQL
3. **Identifies issues**:
   - Multiple metrics with different filters
   - Multiple dimensions requiring joins
   - Daily granularity (large result set)
4. **Suggests optimizations**:
   - Use monthly granularity instead of daily
   - Query metrics separately if they're used in different contexts
   - Add filters to reduce data scanned
   - Consider materializing intermediate results
5. **Provides optimized query**:
   ```bash
   mf query --metrics total_revenue,completed_revenue \
     --group-by store__store_type,order__order_date__month \
     --where "{{ TimeDimension('order__order_date__month') }} >= '2024-10'"
   ```

### Result
Optimized query with explanation of improvements.

---

## Use Case 10: Documentation Generation

### Scenario
**User asks:** "Generate documentation for all our conversion metrics"

### What MCP Server Does
1. **Finds all conversion metrics**:
   - `visit_to_order_conversion_rate_7d`
   - `visit_to_order_conversion_rate_30d`
   - `visit_to_order_conversions_7d`
   - `order_completion_rate` (conversion-like ratio)
   - `credit_card_adoption_rate` (conversion-like ratio)
2. **Reads definitions**: Gets YAML for each metric
3. **Generates markdown documentation**:
   ```markdown
   # Conversion Metrics
   
   ## True Conversion Metrics
   
   ### visit_to_order_conversion_rate_7d
   - **Type**: Conversion (time-windowed)
   - **Base**: Customer visits
   - **Conversion**: Orders placed
   - **Window**: 7 days
   - **Entity**: customer
   - **Description**: Tracks the percentage of visitors who place at least one order within 7 days of their visit.
   
   ### visit_to_order_conversion_rate_30d
   - **Type**: Conversion (time-windowed)
   - **Base**: Customer visits
   - **Conversion**: Orders placed
   - **Window**: 30 days
   - **Entity**: customer
   - **Description**: Tracks the percentage of visitors who place at least one order within 30 days of their visit.
   
   ## Conversion-Like Metrics (Ratio-based)
   
   ### order_completion_rate
   - **Type**: Ratio (represents conversion)
   - **Calculation**: completed_orders / total_orders
   - **Description**: Percentage of orders that were completed
   
   ...
   ```
4. **Includes examples**: Adds query examples for each metric

### Result
Complete documentation file ready for your team.

---

## Use Case 11: Validating Metric Definitions

### Scenario
**User asks:** "I just added a new metric. Can you check if it's correct?"

### What MCP Server Does
1. **Reads the new metric definition** from YAML
2. **Validates syntax**: Checks YAML structure, required fields
3. **Validates references**:
   - Checks if referenced measures exist
   - Checks if referenced metrics exist (for ratio/derived metrics)
   - Validates dimension references in filters
4. **Checks semantic model compatibility**:
   - Verifies measures come from valid semantic models
   - For conversion metrics, verifies base and conversion measures are from different semantic models
5. **Runs dbt parse**: Executes `dbt parse` to catch any errors
6. **Tests the metric**: Runs `mf query` to ensure it compiles correctly
7. **Provides feedback**:
   ```
   ✅ Syntax: Valid
   ✅ Measure reference: order_total exists
   ✅ Filter syntax: Correct dimension reference
   ✅ Semantic model: Compatible
   ⚠️  Warning: Consider adding a description for better documentation
   ```

### Result
Comprehensive validation report with actionable feedback.

---

## Use Case 12: Multi-Hop Join Explanation

### Scenario
**User asks:** "How can I query revenue by customer region? I don't see customer_region in the orders table."

### What MCP Server Does
1. **Explains multi-hop joins**:
   - `orders` semantic model has `customer` entity (foreign key)
   - `customers` semantic model has `customer` entity (primary key)
   - MetricFlow automatically joins via the shared entity
2. **Shows the relationship**:
   ```
   orders (fact) → customer_id → customers (dimension) → customer_region
   ```
3. **Validates the join path**: Confirms `customer` entity exists in both semantic models
4. **Provides correct query**:
   ```bash
   mf query --metrics total_revenue --group-by customer__customer_region
   ```
5. **Explains why it works**: MetricFlow detects the relationship and generates the join automatically
6. **Shows the SQL**: Uses `--explain` to show the generated SQL with the join

### Result
Clear explanation of multi-hop joins with your specific data model.

---

## Summary: Key Benefits for Your POC

1. **Context-Aware**: AI understands your specific semantic models (orders, customers, stores, visits)
2. **Metric Discovery**: Knows all 15+ metrics you've defined
3. **Correct Syntax**: Uses proper entity names (`order__`, not `orders__`)
4. **Multi-Hop Awareness**: Understands how to join across semantic models
5. **Conversion Metrics**: Knows how your visit-to-order conversion metrics work
6. **Error Prevention**: Catches common mistakes before they cause errors
7. **Documentation**: Generates docs specific to your project structure
8. **Impact Analysis**: Traces dependencies in your actual project

---

## Next Steps

To implement dbt MCP server integration:

1. **Install MCP Server**: Set up the dbt MCP server package
2. **Configure Cursor**: Add MCP server to Cursor settings
3. **Test Queries**: Try the use cases above with your actual project
4. **Customize**: Add project-specific tools and capabilities

Would you like me to create a setup guide for integrating the dbt MCP server with your MetricFlow POC?


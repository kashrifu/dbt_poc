-- Query Examples for Unity Catalog Metric Views
-- These examples show how to query metric views using the MEASURE() function

-- Example 1: Query revenue by month
SELECT 
    order_date_month,
    MEASURE(total_revenue) AS revenue
FROM workspace.dbt_poc.metric_revenue_metrics
GROUP BY order_date_month
ORDER BY order_date_month DESC;

-- Example 2: Query revenue by store type
SELECT 
    store_type,
    MEASURE(total_revenue) AS revenue,
    MEASURE(credit_card_revenue) AS cc_revenue
FROM workspace.dbt_poc.metric_revenue_with_stores
GROUP BY store_type;

-- Example 3: Query multiple measures
SELECT 
    order_date_month,
    order_status,
    MEASURE(total_revenue) AS revenue,
    MEASURE(completed_revenue) AS completed_rev
FROM workspace.dbt_poc.metric_revenue_metrics
GROUP BY order_date_month, order_status
ORDER BY order_date_month DESC, revenue DESC;

-- Example 4: Query orders by status
SELECT 
    order_status,
    MEASURE(total_orders) AS orders,
    MEASURE(completed_orders) AS completed
FROM workspace.dbt_poc.metric_order_metrics
GROUP BY order_status;

-- Example 5: Revenue by store region
SELECT 
    store_region,
    MEASURE(total_revenue) AS revenue
FROM workspace.dbt_poc.metric_revenue_with_stores
GROUP BY store_region
ORDER BY revenue DESC;

-- Example 6: Time series analysis
SELECT 
    order_date_month,
    MEASURE(total_revenue) AS revenue,
    MEASURE(total_orders) AS orders,
    MEASURE(total_revenue) / NULLIF(MEASURE(total_orders), 0) AS avg_order_value
FROM workspace.dbt_poc.metric_revenue_metrics
GROUP BY order_date_month
ORDER BY order_date_month DESC;

-- Note: 
-- - Always use MEASURE() function to aggregate measures
-- - Must GROUP BY dimensions
-- - No SELECT * allowed - must specify dimensions and measures explicitly
-- - Joins must be predefined in the metric view YAML


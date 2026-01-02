-- Business View: Order Metrics
-- This view provides order-level aggregations and statistics

CREATE OR REPLACE VIEW workspace.dbt_poc.business_order_metrics AS
SELECT
    -- Time dimensions
    DATE_TRUNC('day', o.order_date) AS order_day,
    DATE_TRUNC('week', o.order_date) AS order_week,
    DATE_TRUNC('month', o.order_date) AS order_month,
    DATE_TRUNC('quarter', o.order_date) AS order_quarter,
    DATE_TRUNC('year', o.order_date) AS order_year,
    
    -- Store dimensions
    s.store_type,
    s.region AS store_region,
    
    -- Customer dimensions
    c.region AS customer_region,
    
    -- Order status
    o.status AS order_status,
    
    -- Order counts
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT CASE WHEN o.status = 'completed' THEN o.order_id END) AS completed_orders,
    COUNT(DISTINCT CASE WHEN o.status = 'returned' THEN o.order_id END) AS returned_orders,
    COUNT(DISTINCT CASE WHEN o.status = 'shipped' THEN o.order_id END) AS shipped_orders,
    
    -- Customer counts
    COUNT(DISTINCT o.customer_id) AS unique_customers,
    COUNT(DISTINCT CASE WHEN o.status = 'completed' THEN o.customer_id END) AS customers_with_completed_orders,
    
    -- Revenue metrics
    SUM(o.amount) AS total_revenue,
    SUM(CASE WHEN o.status = 'completed' THEN o.amount ELSE 0 END) AS completed_revenue,
    
    -- Average metrics
    AVG(o.amount) AS avg_order_amount,
    SUM(o.amount) / NULLIF(COUNT(DISTINCT o.order_id), 0) AS average_order_value,
    SUM(o.amount) / NULLIF(COUNT(DISTINCT o.customer_id), 0) AS revenue_per_customer

FROM workspace.dbt_poc.fct_orders o
LEFT JOIN workspace.dbt_poc.dim_stores s ON o.store_id = s.store_id
LEFT JOIN workspace.dbt_poc.dim_customers c ON o.customer_id = c.customer_id
GROUP BY
    DATE_TRUNC('day', o.order_date),
    DATE_TRUNC('week', o.order_date),
    DATE_TRUNC('month', o.order_date),
    DATE_TRUNC('quarter', o.order_date),
    DATE_TRUNC('year', o.order_date),
    s.store_type,
    s.region,
    c.region,
    o.status;

-- Grant permissions (adjust as needed)
-- GRANT SELECT ON VIEW workspace.dbt_poc.business_order_metrics TO `account users`;


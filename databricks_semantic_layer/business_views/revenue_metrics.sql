-- Business View: Revenue Metrics
-- This view provides pre-aggregated revenue metrics for easy consumption
-- Assumes base tables exist: fct_orders, dim_stores, dim_customers

CREATE OR REPLACE VIEW workspace.dbt_poc.business_revenue_metrics AS
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
    s.store_name,
    
    -- Customer dimensions
    c.region AS customer_region,
    
    -- Order dimensions
    o.status AS order_status,
    
    -- Revenue metrics
    SUM(o.amount) AS total_revenue,
    SUM(o.credit_card_amount) AS credit_card_revenue,
    SUM(o.coupon_amount) AS coupon_revenue,
    SUM(o.bank_transfer_amount) AS bank_transfer_revenue,
    SUM(CASE WHEN o.status = 'completed' THEN o.amount ELSE 0 END) AS completed_revenue,
    
    -- Order counts
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT CASE WHEN o.status = 'completed' THEN o.order_id END) AS completed_orders,
    
    -- Calculated metrics
    SUM(o.amount) / NULLIF(COUNT(DISTINCT o.order_id), 0) AS average_order_value,
    SUM(o.credit_card_amount) / NULLIF(SUM(o.amount), 0) AS credit_card_payment_ratio,
    COUNT(DISTINCT CASE WHEN o.status = 'completed' THEN o.order_id END) / 
        NULLIF(COUNT(DISTINCT o.order_id), 0) AS order_completion_rate

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
    s.store_name,
    c.region,
    o.status;

-- Grant permissions (adjust as needed)
-- GRANT SELECT ON VIEW workspace.dbt_poc.business_revenue_metrics TO `account users`;


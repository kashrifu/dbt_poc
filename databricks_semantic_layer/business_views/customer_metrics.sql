-- Business View: Customer Metrics
-- This view provides customer-level aggregations and metrics

CREATE OR REPLACE VIEW workspace.dbt_poc.business_customer_metrics AS
SELECT
    -- Customer dimensions
    c.customer_id,
    c.first_name,
    c.last_name,
    c.name AS customer_name,
    c.region AS customer_region,
    
    -- Time dimensions (latest order)
    MAX(o.order_date) AS last_order_date,
    MIN(o.order_date) AS first_order_date,
    
    -- Order metrics
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT CASE WHEN o.status = 'completed' THEN o.order_id END) AS completed_orders,
    
    -- Revenue metrics
    SUM(o.amount) AS total_revenue,
    SUM(CASE WHEN o.status = 'completed' THEN o.amount ELSE 0 END) AS completed_revenue,
    SUM(o.credit_card_amount) AS credit_card_revenue,
    SUM(o.coupon_amount) AS coupon_revenue,
    SUM(o.bank_transfer_amount) AS bank_transfer_revenue,
    
    -- Average metrics
    AVG(o.amount) AS avg_order_value,
    SUM(o.amount) / NULLIF(COUNT(DISTINCT o.order_id), 0) AS average_order_value,
    
    -- Customer lifetime value
    SUM(o.amount) AS customer_lifetime_value,
    
    -- Payment method preferences
    CASE 
        WHEN SUM(o.credit_card_amount) > COALESCE(SUM(o.coupon_amount), 0) 
             AND SUM(o.credit_card_amount) > COALESCE(SUM(o.bank_transfer_amount), 0)
        THEN 'Credit Card'
        WHEN SUM(o.coupon_amount) > COALESCE(SUM(o.bank_transfer_amount), 0)
        THEN 'Coupon'
        ELSE 'Bank Transfer'
    END AS preferred_payment_method

FROM workspace.dbt_poc.dim_customers c
LEFT JOIN workspace.dbt_poc.fct_orders o ON c.customer_id = o.customer_id
GROUP BY
    c.customer_id,
    c.first_name,
    c.last_name,
    c.name,
    c.region;

-- Grant permissions (adjust as needed)
-- GRANT SELECT ON VIEW workspace.dbt_poc.business_customer_metrics TO `account users`;


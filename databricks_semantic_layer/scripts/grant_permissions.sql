-- Grant Permissions Script
-- This script grants access to business views and metrics
-- Adjust catalog, schema, and user/group names as needed

-- Grant permissions on business views
GRANT SELECT ON VIEW workspace.dbt_poc.business_revenue_metrics TO `account users`;
GRANT SELECT ON VIEW workspace.dbt_poc.business_order_metrics TO `account users`;
GRANT SELECT ON VIEW workspace.dbt_poc.business_customer_metrics TO `account users`;

-- Grant permissions on metrics
-- Note: Metric permissions are managed through Unity Catalog
-- You may need to grant SELECT on the underlying tables first
GRANT SELECT ON TABLE workspace.dbt_poc.fct_orders TO `account users`;
GRANT SELECT ON TABLE workspace.dbt_poc.dim_customers TO `account users`;
GRANT SELECT ON TABLE workspace.dbt_poc.dim_stores TO `account users`;

-- For specific users or groups, replace `account users` with:
-- - A specific user: `user@example.com`
-- - A group: `analysts@example.com`
-- - A service principal: `service-principal-name`

-- Example for specific groups:
-- GRANT SELECT ON VIEW workspace.dbt_poc.business_revenue_metrics TO `analysts@company.com`;
-- GRANT SELECT ON VIEW workspace.dbt_poc.business_order_metrics TO `analysts@company.com`;
-- GRANT SELECT ON VIEW workspace.dbt_poc.business_customer_metrics TO `analysts@company.com`;


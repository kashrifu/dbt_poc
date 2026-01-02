-- Setup Script: Create Base Tables (if they don't exist from dbt)
-- This script is optional - only needed if tables aren't created by dbt run

-- Note: In most cases, you'll run `dbt run` from the main project
-- to create these tables. This script is provided as a reference
-- or for manual setup scenarios.

-- Verify tables exist
-- If tables don't exist, you can create them manually or run dbt:

-- Option 1: Run dbt (recommended)
-- From the dbt project root:
--   dbt run --select marts

-- Option 2: Create tables manually (not recommended, but possible)
-- This would require recreating the logic from:
--   - models/marts/fct_orders.sql
--   - models/marts/dim_customers.sql
--   - models/marts/dim_stores.sql

-- Check if tables exist
SHOW TABLES IN workspace.dbt_poc;

-- Expected tables:
-- - fct_orders
-- - dim_customers
-- - dim_stores

-- If tables are missing, ensure you've run:
--   dbt run --select marts
-- from the main dbt project directory


-- SQL Script to Create Unity Catalog Metric Views
-- This script creates metric views by embedding YAML definitions
-- Alternative: Use Catalog Explorer UI to create metric views

-- Method 1: Create metric view using CREATE VIEW with YAML embedded
-- Note: The exact syntax may vary by Databricks version
-- Check Databricks documentation for the current syntax

-- Revenue Metrics Metric View
-- Note: For full formatting and display metadata, use the YAML file directly in Catalog Explorer UI
-- This SQL version includes basic structure; see revenue_metrics.yaml for complete definition
CREATE OR REPLACE VIEW workspace.dbt_poc.metric_revenue_metrics AS
$$
version: 1.1
source: workspace.dbt_poc.fct_orders
dimensions:
  - name: order_date
    expr: order_date
    display_name: Order Date
    comment: Date and time when the order was placed
  - name: order_date_month
    expr: DATE_TRUNC('month', order_date)
    display_name: Order Month
    comment: Month in which the order was placed
  - name: order_date_quarter
    expr: DATE_TRUNC('quarter', order_date)
    display_name: Order Quarter
    comment: Quarter in which the order was placed
  - name: order_date_year
    expr: DATE_TRUNC('year', order_date)
    display_name: Order Year
    comment: Year in which the order was placed
  - name: order_status
    expr: status
    display_name: Order Status
    comment: Status of the order (e.g., completed, pending, cancelled)
measures:
  - name: total_revenue
    expr: SUM(amount)
    display_name: Total Revenue
    comment: Total revenue from all orders
  - name: credit_card_revenue
    expr: SUM(credit_card_amount)
    display_name: Credit Card Revenue
    comment: Revenue from credit card payments
  - name: coupon_revenue
    expr: SUM(coupon_amount)
    display_name: Coupon Revenue
    comment: Revenue from coupon payments
  - name: bank_transfer_revenue
    expr: SUM(bank_transfer_amount)
    display_name: Bank Transfer Revenue
    comment: Revenue from bank transfer payments
  - name: total_payment_revenue
    expr: SUM(credit_card_amount + coupon_amount + bank_transfer_amount)
    display_name: Total Payment Revenue
    comment: Sum of all payment method revenues
  - name: completed_revenue
    expr: SUM(CASE WHEN status = 'completed' THEN amount ELSE 0 END)
    display_name: Completed Revenue
    comment: Revenue from completed orders only
$$;

-- Order Metrics Metric View
CREATE OR REPLACE VIEW workspace.dbt_poc.metric_order_metrics AS
$$
version: 1.1
source: workspace.dbt_poc.fct_orders
dimensions:
  - name: order_date
    expr: order_date
    type: time
  - name: order_date_month
    expr: DATE_TRUNC('month', order_date)
    type: time
  - name: order_status
    expr: status
    type: categorical
measures:
  - name: total_orders
    expr: COUNT(DISTINCT order_id)
    description: "Total number of distinct orders"
  - name: completed_orders
    expr: COUNT(DISTINCT CASE WHEN status = 'completed' THEN order_id END)
    description: "Count of completed orders"
  - name: unique_customers
    expr: COUNT(DISTINCT customer_id)
    description: "Number of unique customers"
$$;

-- Revenue Metrics with Store Dimensions (Multi-hop Join)
CREATE OR REPLACE VIEW workspace.dbt_poc.metric_revenue_with_stores AS
$$
version: 1.1
source: workspace.dbt_poc.fct_orders
joins:
  - name: stores
    source: workspace.dbt_poc.dim_stores
    on: fct_orders.store_id = stores.store_id
dimensions:
  - name: order_date_month
    expr: DATE_TRUNC('month', fct_orders.order_date)
    type: time
  - name: store_type
    expr: stores.store_type
    type: categorical
  - name: store_region
    expr: stores.region
    type: categorical
measures:
  - name: total_revenue
    expr: SUM(fct_orders.amount)
    description: "Total revenue from all orders"
  - name: credit_card_revenue
    expr: SUM(fct_orders.credit_card_amount)
    description: "Revenue from credit card payments"
$$;

-- Usage Examples:
-- SELECT order_date_month, MEASURE(total_revenue) 
-- FROM workspace.dbt_poc.metric_revenue_metrics 
-- GROUP BY order_date_month;
--
-- SELECT store_type, MEASURE(total_revenue) 
-- FROM workspace.dbt_poc.metric_revenue_with_stores 
-- GROUP BY store_type;


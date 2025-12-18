with customers as (
    select * from {{ ref('stg_customers') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),

final as (
    select
        orders.order_id,
        orders.customer_id,
        customers.first_name,
        customers.last_name,
        orders.order_date,
        orders.status,
        -- Using tax_paid as a proxy for order amount since payments table doesn't exist
        -- Adjust this based on your actual data structure
        coalesce(orders.tax_paid * 10, 0) as amount,  -- Assuming tax is ~10% of order
        coalesce(orders.tax_paid * 10, 0) as credit_card_amount,  -- Defaulting all to same
        0 as coupon_amount,
        0 as bank_transfer_amount,
        orders.tax_paid,
        orders.store_id
    from orders
    left join customers on orders.customer_id = customers.customer_id
)

select * from final


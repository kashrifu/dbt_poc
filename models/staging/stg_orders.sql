with orders as (
    select * from {{ source('jaffle_shop', 'raw_orders') }}
),

final as (
    select
        id as order_id,
        customer as customer_id,
        ordered_at as order_date,
        'completed' as status,
        tax_paid,
        store_id
    from orders
)

select * from final


{{
  config(
    materialized='table'
  )
}}

with customers as (
    select * from {{ ref('stg_customers') }}
),

final as (
    select
        customer_id,
        first_name,
        last_name,
        name,
        -- Add a region for multi-hop demo using hash of UUID
        -- In a real scenario, this would come from your customer data
        case 
            when abs(hash(customer_id)) % 3 = 0 then 'North'
            when abs(hash(customer_id)) % 3 = 1 then 'South'
            else 'East'
        end as region
    from customers
)

select * from final


with customers as (
    select * from {{ source('jaffle_shop', 'raw_customers') }}
),

final as (
    select
        id as customer_id,
        name,
        -- Extract first name (everything before first space)
        trim(regexp_extract(name, '^([^ ]+)', 1)) as first_name,
        -- Extract last name (everything after last space)
        trim(regexp_extract(name, ' ([^ ]+)$', 1)) as last_name
    from customers
)

select * from final


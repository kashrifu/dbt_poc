{{ config(materialized='table') }}

-- Visits table for conversion metrics
-- Base event: Customer visits to the Jaffle Shop website
-- Conversion event: Orders placed (fct_orders)
-- Linked by customer_id entity

with customer_first_orders as (
    select 
        customer_id,
        min(order_date) as first_order_date
    from {{ ref('fct_orders') }}
    group by customer_id
),

-- Generate visits: 2-4 visits per customer, 1-30 days before first order
visit_numbers as (
    select 1 as n
    union all select 2
    union all select 3
    union all select 4
),

visits_generated as (
    select
        cfo.customer_id,
        dateadd(day, 
            -(abs(hash(concat(cfo.customer_id, '_', vn.n))) % 30 + 1),
            cfo.first_order_date
        ) as visit_date,
        concat('visit_', cfo.customer_id, '_', vn.n) as visit_id,
        case (abs(hash(concat(cfo.customer_id, '_page_', vn.n))) % 4)
            when 0 then 'home'
            when 1 then 'products'
            when 2 then 'product_detail'
            else 'checkout'
        end as page_type,
        case (abs(hash(concat(cfo.customer_id, '_ref_', vn.n))) % 4)
            when 0 then 'direct'
            when 1 then 'google'
            when 2 then 'facebook'
            else 'email'
        end as referrer,
        abs(hash(concat(cfo.customer_id, '_', vn.n))) % 3 as visit_selector
    from customer_first_orders cfo
    cross join visit_numbers vn
),

customer_info as (
    select distinct
        customer_id,
        first_name,
        last_name
    from {{ ref('fct_orders') }}
)

select
    vg.visit_id,
    vg.customer_id,
    vg.visit_date,
    vg.page_type,
    vg.referrer,
    ci.first_name,
    ci.last_name
from visits_generated vg
left join customer_info ci on vg.customer_id = ci.customer_id
left join customer_first_orders cfo_check on vg.customer_id = cfo_check.customer_id
where vg.visit_date is not null
  and vg.visit_selector < 3
  and vg.visit_date < cfo_check.first_order_date
order by vg.customer_id, vg.visit_date

{{
  config(
    materialized='table'
  )
}}

-- Create a stores dimension table
-- In real scenario, this would come from your stores source
select
    store_id,
    'Store ' || substring(store_id, 1, 8) as store_name,
    case 
        when abs(hash(store_id)) % 2 = 0 then 'Premium'
        else 'Standard'
    end as store_type,
    case 
        when abs(hash(store_id)) % 3 = 0 then 'North'
        when abs(hash(store_id)) % 3 = 1 then 'South'
        else 'East'
    end as region
from (
    select distinct store_id 
    from {{ ref('stg_orders') }}
    where store_id is not null
) stores


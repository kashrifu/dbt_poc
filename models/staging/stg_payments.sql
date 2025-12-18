-- Payments table doesn't exist in this dataset
-- Creating empty payments table structure for compatibility
select
    cast(null as int) as payment_id,
    cast(null as int) as order_id,
    cast(null as string) as payment_method,
    cast(null as decimal(10,2)) as amount
where 1=0


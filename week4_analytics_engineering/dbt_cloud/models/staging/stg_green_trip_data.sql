-- create views so we don't have the need to refresh constantly but still have the latest data loaded
{{ config(materialized='view') }}

-- de-duplicate data in case our primary key tripid is not unique
with tripdata as 
(
  select 
    *,
    row_number() over(partition by vendorid, lpep_pickup_datetime) as rn
  from {{ source('staging', 'green_trip_data') }}
  where vendorid is not null 
)

{# SELECT * FROM {{ source([source name from schema.yml], [table name from schema.yml]) }} #}
select
    -- identifiers
    -- 1.0.0 version of dbt utilis, `dbt_utils.surrogate_key` has been replaced by `dbt_utils.generate_surrogate_key`
    {{ dbt_utils.surrogate_key(['vendorid', 'lpep_pickup_datetime']) }} as tripid,
    cast(vendorid as integer) as vendorid,
    cast(ratecodeid as integer) as ratecodeid,
    cast(pulocationid as integer) as  pickup_locationid,
    cast(dolocationid as integer) as dropoff_locationid,
    
    -- timestamps
    cast(lpep_pickup_datetime as timestamp) as pickup_datetime,
    cast(lpep_dropoff_datetime as timestamp) as dropoff_datetime,
    
    -- trip info
    store_and_fwd_flag,
    cast(passenger_count as integer) as passenger_count,
    cast(trip_distance as numeric) as trip_distance,
    cast(trip_type as integer) as trip_type,
    
    -- payment info
    cast(fare_amount as numeric) as fare_amount,
    cast(extra as numeric) as extra,
    cast(mta_tax as numeric) as mta_tax,
    cast(tip_amount as numeric) as tip_amount,
    cast(tolls_amount as numeric) as tolls_amount,
    cast(ehail_fee as numeric) as ehail_fee,
    cast(improvement_surcharge as numeric) as improvement_surcharge,
    cast(total_amount as numeric) as total_amount,
    cast(payment_type as integer) as payment_type,
    {{ get_payment_type_description('payment_type') }} as payment_type_description,  {# macro #}
    cast(congestion_surcharge as numeric) as congestion_surcharge
-- from {{ source('staging', 'green_trip_data') }}
-- where vendorid is not null
from tripdata
where rn = 1

-- dbt build -m [model.sql] --var 'is_test_run: false'
{% if var('is_test_run', default=true) %}
    
    limit 100

{% endif %}
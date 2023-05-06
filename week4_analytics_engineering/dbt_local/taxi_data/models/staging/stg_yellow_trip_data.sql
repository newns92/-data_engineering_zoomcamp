-- create views so we don't have the need to refresh constantly but still have the latest data loaded
{{ config(materialized='view') }}

{# SELECT * FROM {{ source([source name from schema.yml], [table name from schema.yml]) }} #}
select
    -- identifiers
    -- 1.0.0 version of dbt utilis, `dbt_utils.surrogate_key` has been replaced by `dbt_utils.generate_surrogate_key`
    {{ dbt_utils.surrogate_key(['"VendorID"', 'tpep_pickup_datetime']) }} as tripid,
    cast("VendorID" as integer) as vendorid,
    cast("RatecodeID" as integer) as ratecodeid,
    cast("PULocationID" as integer) as pickup_locationid,
    cast("DOLocationID" as integer) as dropoff_locationid,
    
    -- timestamps
    cast(tpep_pickup_datetime as timestamp) as pickup_datetime,
    cast(tpep_dropoff_datetime as timestamp) as dropoff_datetime,
    
    -- trip info
    store_and_fwd_flag,
    cast(passenger_count as integer) as passenger_count,
    cast(trip_distance as numeric) as trip_distance,
    -- yellow cabs are always street-hail
    -- cast(trip_type as integer) as trip_type,
    1 as trip_type,
    
    -- payment info
    cast(fare_amount as numeric) as fare_amount,
    cast(extra as numeric) as extra,
    cast(mta_tax as numeric) as mta_tax,
    cast(tip_amount as numeric) as tip_amount,
    cast(tolls_amount as numeric) as tolls_amount,
    -- cast(ehail_fee as numeric) as ehail_fee,
    cast(0 as numeric) as ehail_fee,    
    cast(improvement_surcharge as numeric) as improvement_surcharge,
    cast(total_amount as numeric) as total_amount,
    cast(payment_type as integer) as payment_type,
    {{ get_payment_type_description('payment_type') }} as payment_type_description,  {# macro #}
    cast(congestion_surcharge as numeric) as congestion_surcharge
from {{ source('staging', 'yellow_trip_data') }}
where "VendorID" is not null

-- dbt build -m [model.sql] --var 'is_test_run: false'
{% if var('is_test_run', default=true) %}
    
    limit 100

{% endif %}
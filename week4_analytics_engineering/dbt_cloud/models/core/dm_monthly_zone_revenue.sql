{{
    config(
        materialized='table'
    )
}}

with trips_data as (
    select
        trip_id,
        vendor_id,
        service_type,
        rate_code_id,
        pickup_location_id,
        pickup_borough,
        pickup_zone,
        dropoff_location_id,
        dropoff_borough,
        dropoff_zone,
        pickup_datetime,
        dropoff_datetime,
        store_and_fwd_flag,
        passenger_count,
        trip_distance,
        trip_type,
        fare_amount,
        extra,
        mta_tax,
        tip_amount,
        tolls_amount,
        -- ehail_fee,
        improvement_surcharge,
        total_amount,
        payment_type,
        payment_type_description,
        congestion_surcharge        
    from {{ ref('fact_trips') }}
)

select 
    -- Revenue grouping 
    pickup_zone as revenue_zone,    
    {{ dbt.date_trunc("month", "pickup_datetime") }} as revenue_month, -- Cross-database macro

    service_type, 

    -- Revenue calculation 
    sum(fare_amount) as revenue_monthly_fare,
    sum(extra) as revenue_monthly_extra,
    sum(mta_tax) as revenue_monthly_mta_tax,
    sum(tip_amount) as revenue_monthly_tip_amount,
    sum(tolls_amount) as revenue_monthly_tolls_amount,
    -- sum(ehail_fee) as revenue_monthly_ehail_fee,
    sum(improvement_surcharge) as revenue_monthly_improvement_surcharge,
    sum(total_amount) as revenue_monthly_total_amount,

    -- Additional calculations
    count(trip_id) as total_monthly_trips,
    avg(passenger_count) as avg_montly_passenger_count,
    avg(trip_distance) as avg_montly_trip_distance

from trips_data
-- group by 1,2,3
group by
    revenue_zone,
    revenue_month,
    service_type
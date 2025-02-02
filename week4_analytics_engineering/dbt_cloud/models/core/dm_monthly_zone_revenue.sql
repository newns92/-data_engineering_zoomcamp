{{
    config(materialized='table') }}

WITH trips_data AS (
    SELECT
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
        ehail_fee,
        improvement_surcharge,
        congestion_surcharge,
        total_amount,
        payment_type,
        payment_type_description
    FROM {{ ref('fact_trips') }}
)

SELECT
    -- Revenue grouping 
    pickup_zone as revenue_zone,
    {{ dbt.date_trunc("month", "pickup_datetime") }} as revenue_month, 

    service_type, 

    -- Revenue calculation 
    SUM(fare_amount) as revenue_monthly_fare,
    SUM(extra) as revenue_monthly_extra,
    SUM(mta_tax) as revenue_monthly_mta_tax,
    SUM(tip_amount) as revenue_monthly_tip_amount,
    SUM(tolls_amount) as revenue_monthly_tolls_amount,
    SUM(ehail_fee) as revenue_monthly_ehail_fee,
    SUM(improvement_surcharge) as revenue_monthly_improvement_surcharge,
    SUM(congestion_surcharge) as revenue_monthly_congestion_surcharge,
    SUM(total_amount) as revenue_monthly_total_amount,

    -- Additional calculations
    COUNT(trip_id) as total_monthly_trips,
    AVG(passenger_count) as avg_monthly_passenger_count,
    AVG(trip_distance) as avg_monthly_trip_distance

FROM trips_data
GROUP BY -- 1, 2, 3
    revenue_zone,
    revenue_month,
    service_type

{{
    config(
        materialized='table'
    )
}}

-- Four CTE's: Two for data, one for UNION ALL, one for zones data
WITH green_data AS (
    SELECT
        trip_id,
        vendor_id,
        rate_code_id,
        pu_location_id,
        do_location_id,
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
        payment_type_description,
        -- Create new field
        'green' AS service_type
    FROM {{ ref('stg_green_trip_data') }}
)
,

yellow_data AS (
    SELECT
        trip_id,
        vendor_id,
        rate_code_id,
        pu_location_id,
        do_location_id,
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
        payment_type_description,
        -- Create new field
        'yellow' AS service_type
    FROM {{ ref('stg_yellow_trip_data') }}
)
,

trips_unioned as (
    SELECT
        trip_id,
        vendor_id,
        rate_code_id,
        pu_location_id,
        do_location_id,
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
        payment_type_description,
        service_type
    FROM green_data
    
    -- We already removed duplicates, so we can UNION ALL
    UNION ALL

    SELECT
        trip_id,
        vendor_id,
        rate_code_id,
        pu_location_id,
        do_location_id,
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
        payment_type_description,
        service_type
    FROM yellow_data
)
,

dim_zones AS (
    SELECT
        location_id,
        borough,
        zone,
        service_zone
    FROM {{ ref('dim_zones') }}
    WHERE borough != 'Unknown'
)

SELECT
    trips_unioned.trip_id,
    trips_unioned.vendor_id,
    trips_unioned.service_type,
    trips_unioned.rate_code_id,
    trips_unioned.pu_location_id AS pickup_location_id,
    pickup_zone.borough AS pickup_borough,
    pickup_zone.zone AS pickup_zone,
    trips_unioned.do_location_id AS dropoff_location_id,
    dropoff_zone.borough AS dropoff_borough,
    dropoff_zone.zone AS dropoff_zone,
    trips_unioned.pickup_datetime,
    trips_unioned.dropoff_datetime,
    trips_unioned.store_and_fwd_flag,
    trips_unioned.passenger_count,
    trips_unioned.trip_distance,
    trips_unioned.trip_type,
    trips_unioned.fare_amount,
    trips_unioned.extra,
    trips_unioned.mta_tax,
    trips_unioned.tip_amount,
    trips_unioned.tolls_amount,
    trips_unioned.ehail_fee,
    trips_unioned.improvement_surcharge,
    trips_unioned.congestion_surcharge,
    trips_unioned.total_amount,
    trips_unioned.payment_type,
    trips_unioned.payment_type_description
FROM trips_unioned
-- Inner JOINs to remove NULL records
INNER JOIN dim_zones AS pickup_zone
    ON trips_unioned.pu_location_id = pickup_zone.location_id
INNER JOIN dim_zones AS dropoff_zone
    ON trips_unioned.do_location_id = dropoff_zone.location_id

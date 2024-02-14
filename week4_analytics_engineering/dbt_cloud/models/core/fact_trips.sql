{{
    config(
        materialized='table'
    )
}}

-- Select everything from green staging data
with green_data as (
    select 
        trip_id,
        vendor_id,
        rate_code_id,
        pickup_location_id,
        dropoff_location_id,
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
        congestion_surcharge,
        -- New field
        'Green' as service_type
    from {{ ref('stg_green_trip_data') }}
), 

-- Select everything from yellow staging data
yellow_data as (
    select 
        trip_id,
        vendor_id,
        rate_code_id,
        pickup_location_id,
        dropoff_location_id,
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
        congestion_surcharge,
        -- New field
        'Yellow' as service_type
    from {{ ref('stg_yellow_trip_data') }}
), 

-- UNION our two types of trips togther
trips_unioned as (
    select
        trip_id,
        vendor_id,
        service_type,
        rate_code_id,
        pickup_location_id,
        dropoff_location_id,
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
    from green_data
    union all
    select
        trip_id,
        vendor_id,
        service_type,
        rate_code_id,
        pickup_location_id,
        dropoff_location_id,
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
    from yellow_data
), 

-- From our dimension table, get the zones for all KNOWN boroughs
dim_zones as (
    select * 
    from {{ ref('dim_zones') }}
    where borough != 'Unknown'
)

-- Select specific fields, not SELECT *
select 
    trips_unioned.trip_id,
    trips_unioned.vendor_id,
    trips_unioned.service_type,
    trips_unioned.rate_code_id,
    trips_unioned.pickup_location_id,
    pickup_zone.borough as pickup_borough,
    pickup_zone.zone as pickup_zone,
    trips_unioned.dropoff_location_id,
    dropoff_zone.borough as dropoff_borough,
    dropoff_zone.zone as dropoff_zone,
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
    -- trips_unioned.ehail_fee,
    trips_unioned.improvement_surcharge,
    trips_unioned.total_amount,
    trips_unioned.payment_type,
    trips_unioned.payment_type_description,
    trips_unioned.congestion_surcharge
from trips_unioned
-- Want both pickup and dropoff zones, so JOIN twice
inner join dim_zones as pickup_zone
    on pickup_location_id = pickup_zone.location_id
inner join dim_zones as dropoff_zone
    on dropoff_location_id = dropoff_zone.location_id

{{
    config(
        materialized='table'
    )
}}

-- Select everything from FHV staging data
with fhv_data as (
    select 
        trip_id,
        dispatching_base_num,
        affiliated_base_number,
        pickup_location_id,
        dropoff_location_id,
        pickup_datetime,
        dropoff_datetime,
        sr_flag,
        'FHV' as service_type
    from {{ ref('stg_fhv_trip_data') }}
),

-- From our dimension table, get the zones for all KNOWN boroughs
dim_zones as (
    select * 
    from {{ ref('dim_zones') }}
    where borough != 'Unknown'
)

-- Select specific fields, not SELECT *
select
    fhv_data.trip_id,
    fhv_data.dispatching_base_num,
    fhv_data.affiliated_base_number,
    fhv_data.pickup_location_id,
    pickup_zone.borough as pickup_borough,
    pickup_zone.zone as pickup_zone,    
    fhv_data.dropoff_location_id,
    dropoff_zone.borough as dropoff_borough,
    dropoff_zone.zone as dropoff_zone,    
    fhv_data.pickup_datetime,
    fhv_data.dropoff_datetime,
    fhv_data.sr_flag,
    fhv_data.service_type
from fhv_data
-- Want both pickup and dropoff zones, so JOIN twice
inner join dim_zones as pickup_zone
    on pickup_location_id = pickup_zone.location_id
inner join dim_zones as dropoff_zone
    on dropoff_location_id = dropoff_zone.location_id

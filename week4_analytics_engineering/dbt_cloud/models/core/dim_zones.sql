{{
    config(
        materialized='table'
    )
}}

SELECT
    locationid AS location_id,
    borough,
    zone,
    REPLACE(service_zone, 'Boro', 'Green') as service_zone
FROM {{ ref('taxi_zone_lookup') }}

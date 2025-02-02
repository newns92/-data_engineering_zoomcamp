-- Create a view so we don't have the need to refresh constantly but still have the latest data loaded
{{ config(materialized = 'view') }}

WITH source AS (
    /* {# SELECT * FROM {{ source(<'source-name-from-schema.yml>', '<table-name-from-schema.yml>') }} #} */
    SELECT * FROM {{ source('staging', 'green_trip_data') }}
    LIMIT 100
)
,

renamed AS (
    SELECT
        {{ dbt_utils.generate_surrogate_key(['vendor_id', 'lpep_pickup_datetime']) }} AS trip_id,
        vendor_id,
        lpep_pickup_datetime,
        lpep_dropoff_datetime,
        store_and_fwd_flag,
        rate_code_id,
        pu_location_id,
        do_location_id,
        passenger_count,
        trip_distance,
        fare_amount,
        extra,
        mta_tax,
        tip_amount,
        tolls_amount,
        ehail_fee,
        improvement_surcharge,
        total_amount,
        payment_type,
        {{ get_payment_type_description('payment_type') }} AS payment_type_description,  {# custom macro #}
        trip_type,
        congestion_surcharge
    FROM source
)

SELECT
    *
FROM renamed
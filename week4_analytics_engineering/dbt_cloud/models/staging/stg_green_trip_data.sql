-- Create a view so we don't have the need to refresh constantly but still have the latest data loaded
{{
    config(
        materialized = 'view'
    ) 
}}

-- Generate row numbers to find duplicates records (vendor_id and lpep_pickup_datetime)
WITH trip_data AS (
    /* {# SELECT * FROM {{ source(<'source-name-from-schema.yml>', '<table-name-from-schema.yml>') }} #} */
    SELECT
        ROW_NUMBER() OVER(PARTITION BY vendor_id, lpep_dropoff_datetime) AS row_num,
    FROM {{ source('staging', 'green_trip_data') }}
    -- Remove null data
    WHERE vendor_id IS NOT NULL
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
    FROM trip_data
    -- Retrieve only one of any duplicate records
    WHERE row_num = 1
)

SELECT
    *
FROM renamed
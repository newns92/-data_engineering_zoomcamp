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
        trip_type,
        congestion_surcharge        
    FROM {{ source('staging', 'green_trip_data') }}
    -- Remove null data
    WHERE vendor_id IS NOT NULL
)

-- Use dbt.safe_case() function to make sure all INTEGER data fields are correct
-- https://docs.getdbt.com/reference/dbt-jinja-functions/cross-database-macros#safe_cast
SELECT
    -- Identifiers
    {{ dbt_utils.generate_surrogate_key(['vendor_id', 'lpep_pickup_datetime']) }} AS trip_id,
    {{ dbt.safe_cast('vendor_id', api.Column.translate_type('integer')) }} AS vendor_id,
    {{ dbt.safe_cast('rate_code_id', api.Column.translate_type('integer')) }} AS rate_code_id,
    {{ dbt.safe_cast('pu_location_id', api.Column.translate_type('integer')) }} AS pu_location_id,
    {{ dbt.safe_cast('do_location_id', api.Column.translate_type('integer')) }} AS do_location_id,

    -- Datetimes
    CAST(lpep_pickup_datetime AS TIMESTAMP) AS pickup_datetime,
    CAST(lpep_dropoff_datetime AS TIMESTAMP) AS dropoff_datetime,

    -- Trip information
    store_and_fwd_flag,
    {{ dbt.safe_cast('passenger_count', api.Column.translate_type('integer')) }} AS passenger_count,
    CAST(trip_distance AS NUMERIC) AS trip_distance,
    {{ dbt.safe_cast('trip_type', api.Column.translate_type('integer')) }} AS trip_type,

    -- Payment information
    CAST(fare_amount AS NUMERIC) AS fare_amount,
    CAST(extra AS NUMERIC) AS extra,
    CAST(mta_tax AS NUMERIC) AS mta_tax,
    CAST(tip_amount AS NUMERIC) AS tip_amount,
    CAST(tolls_amount AS NUMERIC) AS tolls_amount,
    CAST(ehail_fee AS NUMERIC) AS ehail_fee,
    CAST(improvement_surcharge AS NUMERIC) AS improvement_surcharge,
    CAST(congestion_surcharge AS NUMERIC) AS congestion_surcharge,
    CAST(total_amount AS NUMERIC) AS total_amount,
    {{ dbt.safe_cast('payment_type', api.Column.translate_type('integer')) }} AS payment_type,
    {{ get_payment_type_description('payment_type') }} AS payment_type_description  {# custom macro #}    

FROM trip_data
-- Retrieve only one of any duplicate records
WHERE row_num = 1

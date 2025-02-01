-- Create a view so we don't have the need to refresh constantly but still have the latest data loaded
{{ config(materialized = 'view') }}

/* {# SELECT * FROM {{ source(<'source-name-from-schema.yml>', '<table-name-from-schema.yml>') }} #} */
SELECT * FROM {{ source('staging', 'green_trip_data') }}
LIMIT 100

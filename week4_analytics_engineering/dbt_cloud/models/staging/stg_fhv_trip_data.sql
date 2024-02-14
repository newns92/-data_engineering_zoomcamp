-- Create a view so we don't have the need to refresh constantly but still have the latest data loaded
{{ config(materialized = 'view') }}


select
    -- identifiers
    -- 1.0.0 version of dbt utils, `dbt_utils.surrogate_key` has been replaced by `dbt_utils.generate_surrogate_key`
    {{ dbt_utils.generate_surrogate_key(['dispatching_base_num', 'pickup_datetime']) }} as trip_id,
    cast(dispatching_base_num as string) as dispatching_base_num,
    cast(affiliated_base_number as string) as affiliated_base_number,
    cast(pu_location_id as integer) as pickup_location_id,
    cast(do_location_id as integer) as dropoff_location_id,
    
    -- timestamps
    cast(pickup_datetime as timestamp) as pickup_datetime,
    cast(dropoff_datetime as timestamp) as dropoff_datetime,
    
    -- trip info
    cast(sr_flag as integer) as sr_flag,
    
from {{ source('staging', 'fhv_trip_data') }}
where extract(year from pickup_datetime) = 2019
-- from trip_data
-- where rn = 1

-- dbt build -select <model-name> --vars '{'is_test_run': 'false'}'
{% if var('is_test_run', default=true) %}
    
    limit 100

{% endif %}
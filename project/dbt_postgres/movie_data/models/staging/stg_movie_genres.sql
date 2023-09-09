-- create views so we don't have the need to refresh constantly but still have the latest data loaded
{{ config(materialized='view') }}


{# This is a comment block #}
{# SELECT * FROM {{ source('[source name from `schema.yml`]', '[table name from `schema.yml`]') }} #}
select
    -- IDENTIFIERS
    -- Create a surrogate key, if desired
    -- 1.0.0 version of dbt utilis, `dbt_utils.surrogate_key` has been replaced by `dbt_utils.generate_surrogate_key`

    -- cast(index as integer) as record_id,
    cast(genre_id as integer) as genre_id,
   
    -- GENRE INFORMATION
    cast(genre_name as text) as genre_name
    
from {{ source('staging', 'movie_genres_info') }}


-- -- dbt build -m [model.sql] --var 'is_test_run: false'
-- {% if var('is_test_run', default=true) %}
    
--     limit 100

-- {% endif %}
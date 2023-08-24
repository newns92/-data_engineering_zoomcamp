-- create views so we don't have the need to refresh constantly but still have the latest data loaded
{{ config(materialized='view') }}


{# This is a comment block #}
{# SELECT * FROM {{ source('[source name from `schema.yml`]', '[table name from `schema.yml`]') }} #}
select
    -- IDENTIFIERS
    -- Create a surrogate key, if desired
    -- 1.0.0 version of dbt utilis, `dbt_utils.surrogate_key` has been replaced by `dbt_utils.generate_surrogate_key`

    cast(index as integer) as record_id,
    cast(id as integer) as movie_id,
    cast(title as text) as title,
    
    -- TIMESTAMPS
    cast(release_date as timestamp) as release_date,
    
    -- MOVIE INFORMATION
    cast(original_language as text) as original_language,
    
    -- MOVIE METRICS
    cast(popularity as double precision) as popularity_score,
    cast(vote_average as double precision) as average_rating,
    cast(vote_count as integer) as rating_count

from {{ source('staging', 'movie_data_info') }}


-- -- dbt build -m [model.sql] --var 'is_test_run: false'
-- {% if var('is_test_run', default=true) %}
    
--     limit 100

-- {% endif %}
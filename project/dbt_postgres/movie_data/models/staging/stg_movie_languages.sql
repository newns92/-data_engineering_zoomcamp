-- create views so we don't have the need to refresh constantly but still have the latest data loaded
{{ config(materialized='view') }}


{# This is a comment block #}
{# SELECT * FROM {{ source('[source name from `schema.yml`]', '[table name from `schema.yml`]') }} #}
select
    -- Create a surrogate key, if desired
    -- 1.0.0 version of dbt utilis, `dbt_utils.surrogate_key` has been replaced by `dbt_utils.generate_surrogate_key`

    cast(index as integer) as language_record_id,
    cast(full_language_name as text) as full_language_name,
    cast(language_abbrev as text) as language_key

from {{ source('staging', 'movie_language_info') }}


-- -- dbt build -m [model.sql] --var 'is_test_run: false'
-- {% if var('is_test_run', default=true) %}
    
--     limit 100

-- {% endif %}
-- create views so we don't have the need to refresh constantly but still have the latest data loaded
{{ config(materialized='view') }}


{# This is a comment block #}
{# SELECT * FROM {{ source('[source name from `schema.yml`]', '[table name from `schema.yml`]') }} #}
select
    -- IDENTIFIERS
    -- Create a surrogate key, if desired
    -- 1.0.0 version of dbt utilis, `dbt_utils.surrogate_key` has been replaced by `dbt_utils.generate_surrogate_key`

    -- cast(index as integer) as record_id,
	-- Remove {} from string and replace commas, all with blanks
	-- https://stackoverflow.com/questions/17691579/removing-a-set-of-letters-from-a-string
    case
		when translate(genre_ids, '{},', '') = ''
		then null
		else cast(translate(genre_ids, '{},', '') as bigint)
	end as genre_key,
    cast(translate(
		unnest(
			case
				when translate(genre_ids, '{},', '') = ''
				then null
				else string_to_array(genre_ids, ',')
			end
		), 
	'{},', '') as integer) as genre_id
    
from {{ source('staging', 'movie_data_info') }}


-- -- dbt build -m [model.sql] --var 'is_test_run: false'
-- {% if var('is_test_run', default=true) %}
    
--     limit 100

-- {% endif %}
{{ config(materialized='table') }}

-- select everything from movie staging data
with movie_languages as (
    select 
        language_record_id,
        full_language_name,
        language_key

    from {{ ref('stg_movie_languages') }}
)

-- select only specific fields
select 
    movie_languages.language_record_id,
    movie_languages.full_language_name,
    movie_languages.language_key

from movie_languages
-- JOINs to genre dimension table?
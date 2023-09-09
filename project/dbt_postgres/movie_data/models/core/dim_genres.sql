{{ config(materialized='table') }}

-- select everything from movie staging data
with movie_languages as (
    select 
        genre_id,
        genre_name

    from {{ ref('stg_movie_genres') }}
)

-- select only specific fields
select 

    movie_languages.genre_id,
    movie_languages.genre_name

from movie_languages
-- JOINs to genre dimension bridge table?
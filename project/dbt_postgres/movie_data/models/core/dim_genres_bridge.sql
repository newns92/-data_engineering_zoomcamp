{{ config(materialized='table') }}

-- select everything from movie staging data
with movie_genre_keys as (
    select 
        
        genre_key,
        genre_id

    from {{ ref('stg_movie_genres_bridge') }}
)

-- select only specific fields
select 

    movie_genre_keys.genre_key,
    movie_genre_keys.genre_id

from movie_genre_keys
-- JOINs to genre dimension bridge table?
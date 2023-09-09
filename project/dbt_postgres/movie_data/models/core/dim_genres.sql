{{ config(materialized='table') }}

-- select everything from movie staging data
with movie_genres as (

    select 
        genre_id,
        genre_name

    from {{ ref('stg_movie_genres') }}
)

-- select only specific fields
select 

    movie_genres.genre_id,
    movie_genres.genre_name

from movie_genres
-- JOINs to genre dimension bridge table?
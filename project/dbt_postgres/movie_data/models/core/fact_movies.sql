{{ config(materialized='table') }}

-- select everything from movie staging data
with movie_data as (
    select 
        record_id,
        movie_id,
        title,
        release_date,
        language_key,
        popularity_score,
        average_rating,
        rating_count

    from {{ ref('stg_movie_data_info') }}
)

-- select only specific fields
select 
    movie_data.record_id,
    movie_data.movie_id,
    movie_data.title,
    movie_data.release_date,
    movie_data.language_key,
    movie_data.popularity_score,
    movie_data.average_rating,
    movie_data.rating_count

from movie_data
-- JOINs to genre dimension table?
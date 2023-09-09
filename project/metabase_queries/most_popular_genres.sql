SELECT
	public.dim_genres.genre_name,
	COUNT(public.dim_genres.genre_name) AS genre_count
FROM public.dim_genres_bridge
LEFT JOIN public.dim_genres ON
	public.dim_genres_bridge.genre_id = public.dim_genres.genre_id
GROUP BY public.dim_genres.genre_name
ORDER BY genre_count DESC
;
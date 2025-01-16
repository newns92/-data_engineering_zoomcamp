-- SELECT * FROM public.green_taxi_data
-- LIMIT 100

-- QUESTION 3
-- During the period of October 1st 2019 (inclusive) and November 1st 2019 (exclusive), how many trips, **respectively**, happened:
-- 1. Up to 1 mile
SELECT COUNT(*)
FROM public.green_taxi_data
WHERE
	(lpep_pickup_datetime >= '2019-10-01' AND lpep_pickup_datetime < '2019-11-01')
	AND (lpep_dropoff_datetime >= '2019-10-01' AND lpep_dropoff_datetime < '2019-11-01')
	AND trip_distance <= 1.0
;

-- 2. In between 1 (exclusive) and 3 miles (inclusive),
SELECT COUNT(*)
FROM public.green_taxi_data
WHERE
	(lpep_pickup_datetime >= '2019-10-01' AND lpep_pickup_datetime < '2019-11-01')
	AND (lpep_dropoff_datetime >= '2019-10-01' AND lpep_dropoff_datetime < '2019-11-01')
	AND (trip_distance > 1.0 AND trip_distance <= 3.0)
;

-- 3. In between 3 (exclusive) and 7 miles (inclusive),
SELECT COUNT(*)
FROM public.green_taxi_data
WHERE
	(lpep_pickup_datetime >= '2019-10-01' AND lpep_pickup_datetime < '2019-11-01')
	AND (lpep_dropoff_datetime >= '2019-10-01' AND lpep_dropoff_datetime < '2019-11-01')
	AND (trip_distance > 3.0 AND trip_distance <= 7.0)
;

-- 4. In between 7 (exclusive) and 10 miles (inclusive),
SELECT COUNT(*)
FROM public.green_taxi_data
WHERE
	(lpep_pickup_datetime >= '2019-10-01' AND lpep_pickup_datetime < '2019-11-01')
	AND (lpep_dropoff_datetime >= '2019-10-01' AND lpep_dropoff_datetime < '2019-11-01')
	AND (trip_distance > 7.0 AND trip_distance <= 10.0)
;

-- 5. Over 10 miles
SELECT COUNT(*)
FROM public.green_taxi_data
WHERE
	(lpep_pickup_datetime >= '2019-10-01' AND lpep_pickup_datetime < '2019-11-01')
	AND (lpep_dropoff_datetime >= '2019-10-01' AND lpep_dropoff_datetime < '2019-11-01')
	AND trip_distance > 10.0
;


-- QUESTION 4
-- Which was the pick up day with the longest trip distance? Use the pick up time for your calculations.
-- Tip: For every day, we only care about one single trip with the longest distance.
-- SELECT * FROM public.green_taxi_data
-- LIMIT 10
-- ;
SELECT
	CAST(lpep_pickup_datetime AS DATE) AS pickup_date,
	MAX(trip_distance) AS max_trip_distance
FROM public.green_taxi_data
GROUP BY pickup_date
ORDER BY max_trip_distance DESC
;


-- QUESTION 5
-- Which were the top pickup locations with over 13,000 in `total_amount` (across all trips) for 2019-10-18?
-- Consider only `lpep_pickup_datetime` when filtering by date.
-- SELECT * FROM public.green_taxi_data
-- LIMIT 10
-- SELECT * FROM public.zones
-- LIMIT 10
SELECT
	taxi."PULocationID",
	zones."Zone",
	SUM(taxi.total_amount)
FROM public.green_taxi_data AS taxi
LEFT JOIN public.zones AS zones
	ON taxi."PULocationID" = zones."LocationID"
WHERE CAST(lpep_pickup_datetime AS DATE) = '2019-10-18'
GROUP BY taxi."PULocationID", zones."Zone"
HAVING SUM(taxi.total_amount) > 13000



-- QUESTION 6
-- For the passengers picked up in October 2019 in the zone name "East Harlem North" which was the drop off zone that had the largest tip?
-- Note: it's `tip` , not `trip`
-- We need the name of the zone, not the ID.
SELECT
	do_zones."Zone",
	MAX(taxi.tip_amount) AS max_tip
FROM public.green_taxi_data AS taxi
LEFT JOIN public.zones AS pu_zones
	ON taxi."PULocationID" = pu_zones."LocationID"
LEFT JOIN public.zones AS do_zones
	ON taxi."DOLocationID" = do_zones."LocationID"	
WHERE LOWER(pu_zones."Zone") = 'east harlem north'
	AND (lpep_pickup_datetime >= '2019-10-01' AND lpep_pickup_datetime < '2019-11-01')
GROUP BY do_zones."Zone"
ORDER BY max_tip DESC

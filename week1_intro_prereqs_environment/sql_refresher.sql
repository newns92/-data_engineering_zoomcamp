-- Implicit JOIN
SELECT
	taxi.tpep_pickup_datetime,
	taxi.tpep_dropoff_datetime,
	taxi.total_amount,
	-- capitalized fields must be in quotes in Postgres
	CONCAT(zones_pickup."Borough", ' / ', zones_pickup."Zone") AS pickup_location,
	CONCAT(zones_dropoff."Borough", ' / ', zones_dropoff."Zone") AS dropoff_location
FROM public.yellow_taxi_data AS taxi,
	public.zones AS zones_pickup,
	public.zones AS zones_dropoff
WHERE
	taxi."PULocationID" = zones_pickup."LocationID"
	AND taxi."DOLocationID" = zones_dropoff."LocationID"
LIMIT 100
;


-- Explicit JOIN
SELECT
	taxi.tpep_pickup_datetime,
	taxi.tpep_dropoff_datetime,
	taxi.total_amount,
	-- capitalized fields must be in quotes in Postgres
	CONCAT(zones_pickup."Borough", ' / ', zones_pickup."Zone") AS pickup_location,
	CONCAT(zones_dropoff."Borough", ' / ', zones_dropoff."Zone") AS dropoff_location
FROM public.yellow_taxi_data AS taxi
	JOIN public.zones AS zones_pickup
		ON taxi."PULocationID" = zones_pickup."LocationID"
	JOIN public.zones AS zones_dropoff
		ON taxi."DOLocationID" = zones_dropoff."LocationID"
LIMIT 100
;


-- Checking for LocationIDs that *are* in the Taxi data that are *not* in the Zones data
SELECT
	taxi.tpep_pickup_datetime,
	taxi.tpep_dropoff_datetime,
	taxi.total_amount,
	-- capitalized fields must be in quotes in Postgres
	taxi."PULocationID",
	taxi."DOLocationID"
FROM public.yellow_taxi_data AS taxi
WHERE
	taxi."DOLocationID" NOT IN (SELECT "LocationID" FROM public.zones)
	OR taxi."PULocationID" NOT IN (SELECT "LocationID" FROM public.zones)
LIMIT 100
;

SELECT
	taxi.tpep_pickup_datetime,
	taxi.tpep_dropoff_datetime,
	taxi.total_amount,
	taxi."PULocationID",
	taxi."DOLocationID"
FROM public.yellow_taxi_data AS taxi
WHERE
	-- taxi."DOLocationID" = 142
	taxi."DOLocationID" NOT IN (SELECT "LocationID" FROM public.zones WHERE "LocationID" <> 142)
	OR taxi."PULocationID" NOT IN (SELECT "LocationID" FROM public.zones)
LIMIT 100
;


-- GROUP BY to get total trips per day
SELECT
	CAST(taxi.tpep_dropoff_datetime AS DATE) AS dropoff_date,
	COUNT(*) AS total_trips,
	MAX(taxi.total_amount) AS max_trip_amount,
	MAX(taxi.passenger_count) AS max_passengers
FROM public.yellow_taxi_data AS taxi
GROUP BY dropoff_date
-- ORDER BY dropoff_date ASC
ORDER BY total_trips DESC
LIMIT 100
;


-- Multiple-field GROUP BY
SELECT
	CAST(taxi.tpep_dropoff_datetime AS DATE) AS dropoff_date,
	taxi."DOLocationID",
	COUNT(*) AS total_trips,
	MAX(taxi.total_amount) AS max_trip_amount,
	MAX(taxi.passenger_count) AS max_passengers
FROM public.yellow_taxi_data AS taxi
GROUP BY 
	dropoff_date,
	taxi."DOLocationID"
ORDER BY 
	dropoff_date ASC,
	taxi."DOLocationID" ASC
-- ORDER BY taxi."DOLocationID", total_trips DESC
LIMIT 100
;

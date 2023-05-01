-- get pickup and dropoff locations
SELECT 
	taxi.*
	-- ***** fields that start with capitals must be in quotes *****
	-- ,pickup."Borough" AS pickup_borough
	--,pickup."Zone" AS pickup_zone
	,pickup."service_zone" AS pickup_service_zone
	,CONCAT(pickup."Borough", ' - ', pickup."Zone") AS pickup_location
	--,dropoff."Borough" AS dropoff_borough
	-- ,dropoff."Zone" AS dropoff_zone
	,dropoff."service_zone" AS dropoff_service_zone
	,CONCAT(dropoff."Borough", ' - ', dropoff."Zone") AS dropoff_location
FROM public.yellow_taxi_data AS taxi
	LEFT JOIN public.zones AS pickup
		ON taxi."PULocationID" = pickup."LocationID"
	LEFT JOIN public.zones AS dropoff
		ON taxi."DOLocationID" = dropoff."LocationID"
LIMIT 100;


-- get pickup and dropoff locations
SELECT 
	taxi.tpep_pickup_datetime
	,CAST(DATE_TRUNC('DAY', taxi.tpep_pickup_datetime) AS DATE) AS pickup_day
	,taxi.tpep_dropoff_datetime
	,CAST(DATE_TRUNC('DAY', taxi.tpep_dropoff_datetime) AS DATE) AS dropoff_day
	,taxi.total_amount
	,taxi."PULocationID"
	,taxi."DOLocationID"
	-- ***** fields that start with capitals must be in quotes *****
	-- ,pickup."Borough" AS pickup_borough
	--,pickup."Zone" AS pickup_zone
	,pickup."service_zone" AS pickup_service_zone
	,CONCAT(pickup."Borough", ' - ', pickup."Zone") AS pickup_location
	--,dropoff."Borough" AS dropoff_borough
	-- ,dropoff."Zone" AS dropoff_zone
	,dropoff."service_zone" AS dropoff_service_zone
	,CONCAT(dropoff."Borough", ' - ', dropoff."Zone") AS dropoff_location
FROM public.yellow_taxi_data AS taxi
	LEFT JOIN public.zones AS pickup
		ON taxi."PULocationID" = pickup."LocationID"
	LEFT JOIN public.zones AS dropoff
		ON taxi."DOLocationID" = dropoff."LocationID"
-- WHERE
-- 	taxi."PULocationID" IS NULL -- no records of this
-- 	taxi."DOLocationID" IS NULL -- no records of this
LIMIT 100;


-- get ID's that are NOT in the trips database (Should return no data)
SELECT 
	* 
FROM public.zones AS zones 
WHERE 
	zones."LocationID" NOT IN (SELECT "PULocationID" from public.yellow_taxi_data)
	OR zones."LocationID" NOT IN (SELECT "DOLocationID" from public.yellow_taxi_data)


-- Count the number of trips per day
SELECT 
	CAST(DATE_TRUNC('DAY', taxi.tpep_dropoff_datetime) AS DATE) AS dropoff_day
	,COUNT(1) AS trip_count
FROM 
	public.yellow_taxi_data AS taxi
GROUP BY
	dropoff_day
ORDER BY
	dropoff_day -- ASC
LIMIT 100;


-- Get most trips per day
SELECT 
	CAST(DATE_TRUNC('DAY', taxi.tpep_dropoff_datetime) AS DATE) AS dropoff_day
	,COUNT(1) AS trip_count
    ,MAX(taxi.total_amount) AS max_trip_amount
FROM 
	public.yellow_taxi_data AS taxi
GROUP BY
	dropoff_day
ORDER BY
	trip_count DESC
LIMIT 100;


-- GROUP BY MULTIPLE FIELDS
SELECT 
	CAST(DATE_TRUNC('DAY', taxi.tpep_dropoff_datetime) AS DATE) AS dropoff_day
	,taxi."DOLocationID" AS DOLocationID
	,COUNT(1) AS trip_count
    ,MAX(taxi.total_amount) AS max_trip_amount
	,MAX(taxi.passenger_count) AS max_passengers
FROM 
	public.yellow_taxi_data AS taxi
GROUP BY
	1, 2 -- groups by the 1st 2 fields/columns in the SELECT statement
ORDER BY -- ASC by default
	dropoff_day
	,DOLocationID
LIMIT 100;
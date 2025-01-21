-- 3) How many rows are there for the `Yellow` Taxi data for the year 2020?
SELECT COUNT(*) FROM public.yellow_tripdata WHERE EXTRACT(YEAR FROM tpep_pickup_datetime) = 2020

-- 4) How many rows are there for the `Green` Taxi data for the year 2020?
SELECT COUNT(*) FROM public.green_tripdata WHERE EXTRACT(YEAR FROM lpep_pickup_datetime) = 2020

-- 5) How many rows are there for the `Yellow` Taxi data for March 2021?
SELECT COUNT(*) FROM public.yellow_tripdata WHERE EXTRACT(YEAR FROM tpep_pickup_datetime) = 2021 AND EXTRACT(MONTH FROM tpep_pickup_datetime) = 03
CREATE OR REPLACE EXTERNAL TABLE `<project-id>.<dataset-name>.external_yellow_trip_data_homework3`
OPTIONS (
    format = 'PARQUET',
    uris = ['gs://<bucket-name>/data/yellow/yellow_tripdata_2024-*.parquet']
)
;

CREATE OR REPLACE TABLE `<project-id>.<dataset-name>.yellow_trip_data_homework3`
AS
SELECT * FROM '<project-id>.<dataset-name>.external_yellow_trip_data_homework3';

-- Question 1:
SELECT COUNT(*) FROM '<project-id>.<dataset-name>.yellow_trip_data_homework3';

-- Question 2:
SELECT
  COUNT(DISTINCT pu_location_id)
FROM '<project-id>.<dataset-name>.external_yellow_trip_data_homework3'
;

SELECT
  COUNT(DISTINCT pu_location_id)
FROM '<project-id>.<dataset-name>.yellow_trip_data_homework3'
;

-- Question 4:
SELECT
  COUNT(*)
FROM '<project-id>.<dataset-name>.yellow_trip_data_homework3'
WHERE fare_amount = 0
;

-- Question 5
-- Creating a partition and cluster table
CREATE OR REPLACE TABLE `<project-id>.<dataset-name>.yellow_taxi_data_homework_partitioned_clustered`
PARTITION BY DATE(tpep_dropoff_datetime)
CLUSTER BY vendor_id
AS
SELECT * FROM '<project-id>.<dataset-name>.yellow_trip_data_homework3'
;


-- Question 6
SELECT DISTINCT
  vendor_id
FROM '<project-id>.<dataset-name>.yellow_trip_data_homework3'
WHERE tpep_dropoff_datetime BETWEEN '2024-03-01' AND '2024-03-15'
;

SELECT DISTINCT
  vendor_id
FROM '<project-id>.<dataset-name>.yellow_taxi_data_homework_partitioned_clustered'
WHERE tpep_dropoff_datetime BETWEEN '2024-03-01' AND '2024-03-15'
;


-- Bonus
SELECT COUNT(*) FROM '<project-id>.<dataset-name>.yellow_trip_data_homework3';




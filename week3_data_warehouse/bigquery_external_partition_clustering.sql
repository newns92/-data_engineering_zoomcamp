-- SELECT COUNT(*) FROM `de-zoomcamp-384821.ny_trips.external_yellow_trip_data` LIMIT 1000
-- TRUNCATE TABLE `de-zoomcamp-384821.ny_trips.external_yellow_trip_data` 

-- 1) EXTERNAL TABLES
-- - Create (or replace) external table referring to a GCS path (gsutil URI)
CREATE OR REPLACE EXTERNAL TABLE `de-zoomcamp-384821.ny_trips.external_yellow_trip_data`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://prefect-de-zoomcamp-384821/data/yellow/yellow_tripdata_2019-*.parquet', 'gs://prefect-de-zoomcamp-384821/data/yellow/yellow_tripdata_2020-*.parquet']
);

SELECT * FROM `de-zoomcamp-384821.ny_trips.external_yellow_trip_data` limit 10;


-- 2) PARTITIONING
-- - Create a NON-partitioned table from the external table above
-- - Should see 38,231,366 rows, 4.91 GB of data, and 583.35 MB Total and Active physical bytes
CREATE OR REPLACE TABLE `de-zoomcamp-384821.ny_trips.yellow_trip_data_non_partitioned`
AS
SELECT * FROM `de-zoomcamp-384821.ny_trips.external_yellow_trip_data`;

-- - Create a partitioned table from the external table above
-- - Should see 38,231,366 rows, 4.91 GB of data, and 0 MB Total and Active physical bytes
CREATE OR REPLACE TABLE `de-zoomcamp-384821.ny_trips.yellow_trip_data_non_partitioned`
PARTITION BY
  DATE(tpep_pickup_datetime) AS
SELECT * FROM `de-zoomcamp-384821.ny_trips.external_yellow_trip_data`;

-- Check how much data is processed
-- - 1st, run on the non-partitioned dataset
-- - Should get 583.36 MB Bytes processed, 583 MB Bytes billed
SELECT DISTINCT(VendorID)
FROM de-zoomcamp-384821.ny_trips.yellow_trip_data_non_partitioned
WHERE DATE(tpep_pickup_datetime) BETWEEN '2019-01-01' AND '2019-03-31';

-- - 2nd, run on the partitioned dataset
-- - Should get 343.61 MB Bytes processed, 344 MB Bytes billed
SELECT DISTINCT(VendorID)
FROM de-zoomcamp-384821.ny_trips.yellow_trip_data_partitioned
WHERE DATE(tpep_pickup_datetime) BETWEEN '2019-01-01' AND '2019-03-31';

-- - Can look directly into the partitons to see how many rows are in each partition
SELECT table_name, partition_id, total_rows
FROM `ny_trips.INFORMATION_SCHEMA.PARTITIONS`
WHERE table_name = 'yellow_trip_data_partitioned'
ORDER BY total_rows DESC;


-- 2) CLUSTERING
-- - Create a partitioned AND clustered table
CREATE OR REPLACE TABLE de-zoomcamp-384821.ny_trips.yellow_tripdata_partitoned_clustered
PARTITION BY DATE(tpep_pickup_datetime)
CLUSTER BY VendorID AS
SELECT * FROM de-zoomcamp-384821.ny_trips.external_yellow_trip_data;

-- - See the drop in processed data
-- - This will process 583.35 MB of data
SELECT COUNT(*) as trips
FROM de-zoomcamp-384821.ny_trips.yellow_trip_data_partitioned
WHERE 
  DATE(tpep_pickup_datetime) BETWEEN '2019-01-01' AND '2020-03-31'
  AND VendorID=1;

-- - This will process 448.91 MB of data
SELECT COUNT(*) as trips
FROM de-zoomcamp-384821.ny_trips.yellow_tripdata_partitoned_clustered
WHERE 
  DATE(tpep_pickup_datetime) BETWEEN '2019-01-01' AND '2020-03-31'
  AND VendorID=1;
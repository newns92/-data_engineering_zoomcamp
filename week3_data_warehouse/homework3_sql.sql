-- Create an external table using the Green Taxi Trip Records Data for 2022. 
CREATE OR REPLACE EXTERNAL TABLE `<project-id>.ny_taxi.external_nyc_green_taxi_data`
  OPTIONS (
    format = 'PARQUET',
    uris = ['gs://<bucket-name>/data/green/green_tripdata_2022-*.parquet']
  )
;

-- Create a table in BQ using the Green Taxi Trip Records for 2022 (do not partition or cluster this table).
CREATE OR REPLACE TABLE `<project-id>.ny_taxi.green_taxi_data`
AS
SELECT * FROM <project-id>.ny_taxi.external_nyc_green_taxi_data
;


-- Question 1: What is count of records for the 2022 Green Taxi Data??
SELECT COUNT(*) FROM <project-id>.ny_taxi.green_taxi_data;


-- Question 2: Write a query to count the distinct number of PULocationIDs for the entire dataset on both the tables.
-- What is the estimated amount of data that will be read when this query is executed on the External Table and the Table?
SELECT
  DISTINCT pu_location_id
FROM <project-id>.ny_taxi.external_nyc_green_taxi_data
;

SELECT
  DISTINCT pu_location_id
FROM <project-id>.ny_taxi.green_taxi_data
;


-- Question 3: How many records have a fare_amount of 0?
SELECT
  COUNT(*)
FROM <project-id>.ny_taxi.green_taxi_data
WHERE fare_amount = 0
;


-- Question 4: What is the best strategy to make an optimized table in Big Query if your query will always order the results by PUlocationID and filter based on lpep_pickup_datetime? (Create a new table with this strategy)
CREATE OR REPLACE TABLE <project-id>.ny_taxi.green_taxi_data_partitioned_clustered
PARTITION BY DATE(lpep_pickup_datetime)
CLUSTER BY pu_location_id
AS
SELECT * FROM <project-id>.ny_taxi.external_nyc_green_taxi_data;


-- Question 5: Write a query to retrieve the distinct PULocationID between lpep_pickup_datetime 06/01/2022 and 06/30/2022 (inclusive)
-- Use the materialized table you created earlier in your from clause and note the estimated bytes. Now change the table in the from clause to the partitioned table you created for question 4 and note the estimated bytes processed. What are these values?
-- Choose the answer which most closely matches.
SELECT
  DISTINCT pu_location_id
FROM <project-id>.ny_taxi.green_taxi_data
WHERE lpep_pickup_datetime BETWEEN '2022-06-01' AND '2022-06-30'
;

SELECT
  DISTINCT pu_location_id
FROM <project-id>.ny_taxi.green_taxi_data_partitioned_clustered
WHERE lpep_pickup_datetime BETWEEN '2022-06-01' AND '2022-06-30'
;

-- (Bonus: Not worth points) Question 8: Write a `SELECT count(*)` query FROM the materialized table you created. How many bytes does it estimate will be read? Why?
SELECT COUNT(*) FROM <project-id>.ny_taxi.green_taxi_data;


DROP TABLE <project-id>.ny_taxi.green_taxi_data_partitioned_clustered;
DROP TABLE <project-id>.ny_taxi.green_taxi_data;
DROP TABLE <project-id>.ny_taxi.external_nyc_green_taxi_data;
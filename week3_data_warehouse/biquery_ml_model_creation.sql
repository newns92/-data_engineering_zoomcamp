--SELECT  FROM `de-zoomcamp-384821.ny_trips.yellow_trip_data_partitioned` WHERE DATE(tpep_pickup_datetime) = "2023-05-02" LIMIT 1000

-- 1) SELECT THE COLUMNS TO POTENTIALLY HELP PREDICT TIP AMOUNT
SELECT COUNT(*)
FROM de-zoomcamp-384821.ny_trips.yellow_trip_data_partitioned 
WHERE fare_amount != 0
;
-- 38,216,838 rows out of 38,231,366 total

SELECT 
  passenger_count,
  trip_distance,
  PULocationID,
  DOLocationID,
  payment_type,
  fare_amount,
  tolls_amount,
  tip_amount
FROM de-zoomcamp-384821.ny_trips.yellow_trip_data_partitioned 
WHERE fare_amount != 0
;


-- 2) CREATE A TABLE FOR ML AUTOMATIC PREPROCESSING WITH APPROPRIATE DATA TYPES
CREATE OR REPLACE TABLE de-zoomcamp-384821.ny_trips.yellow_trip_data_ml (
  `passenger_count` INTEGER,
  `trip_distance` FLOAT64,
  `PULocationID` STRING,
  `DOLocationID` STRING,
  `payment_type` STRING,
  `fare_amount` FLOAT64,
  `tolls_amount` FLOAT64,
  `tip_amount` FLOAT64
) 
AS 
(
  SELECT 
    passenger_count,
    trip_distance,
    cast(PULocationID AS STRING),
    CAST(DOLocationID AS STRING),
    CAST(payment_type AS STRING),
    fare_amount,
    tolls_amount,
    tip_amount
  FROM de-zoomcamp-384821.ny_trips.yellow_trip_data_partitioned 
  WHERE fare_amount != 0
)
;


-- 3. CREATE LINEAR REGRESSION ML MODEL WITH DEFAULT SETTING
CREATE OR REPLACE MODEL `de-zoomcamp-384821.ny_trips.taxi_tip_model`
OPTIONS
(
  model_type='linear_reg',
  input_label_cols=['tip_amount'], -- what we want to predict
  DATA_SPLIT_METHOD='AUTO_SPLIT') -- for training and evaluation
AS
  SELECT
  *
  FROM `de-zoomcamp-384821.ny_trips.yellow_trip_data_ml`
  WHERE tip_amount IS NOT NULL
;


-- 4. CHECK FEATURES
SELECT * FROM ML.FEATURE_INFO(MODEL `de-zoomcamp-384821.ny_trips.taxi_tip_model`);


-- 5. EVALUATE THE MODEL
SELECT
  *
FROM 
  ML.EVALUATE(MODEL `de-zoomcamp-384821.ny_trips.taxi_tip_model`,
    -- TABLE/DATASET
    (
      SELECT
      *
      FROM
      `de-zoomcamp-384821.ny_trips.yellow_trip_data_ml`
      WHERE
        tip_amount IS NOT NULL
    )
  )
;


-- 6. PREDICT TIP AMOUNT USING THE MODEL
SELECT
  *
FROM 
  ML.PREDICT(MODEL `de-zoomcamp-384821.ny_trips.taxi_tip_model`,
    -- TABLE/DATASET
    (
      SELECT
      *
      FROM
      `de-zoomcamp-384821.ny_trips.yellow_trip_data_ml`
      WHERE
        tip_amount IS NOT NULL
    )
  )
;


-- 7. PREDICT AND EXPLAIN
SELECT
  *
FROM 
  ML.EXPLAIN_PREDICT(MODEL `de-zoomcamp-384821.ny_trips.taxi_tip_model`,
    -- TABLE/DATASET
    (
      SELECT
      *
      FROM
      `de-zoomcamp-384821.ny_trips.yellow_trip_data_ml`
      WHERE
        tip_amount IS NOT NULL
    )
    -- look only at top 3 most "important" features
  , STRUCT(3 as top_k_features)
  )
;


-- 8. HYPERPARAMETER TUNNING
CREATE OR REPLACE MODEL `de-zoomcamp-384821.ny_trips.taxi_tip_model_tuned`
  OPTIONS (
    model_type='linear_reg',
    input_label_cols=['tip_amount'],
    DATA_SPLIT_METHOD='AUTO_SPLIT',
    num_trials=5,
    max_parallel_trials=2,
    l1_reg=hparam_range(0, 20),
    l2_reg=hparam_candidates([0, 0.1, 1, 10])
  ) 
AS
  SELECT
    *
  FROM
    `de-zoomcamp-384821.ny_trips.yellow_trip_data_ml`
  WHERE
    tip_amount IS NOT NULL
;
# ML in Google BigQuery

- We will know talk about ML in BigQuery, as well as build a model, export it, and run it via Docker

## Why ML in BigQuery
- Introduction: https://cloud.google.com/bigquery/docs/bqml-introduction
- Tutorials: https://cloud.google.com/bigquery-ml/docs/tutorials
- Target audience = Data analysts, managers
- Idea: No need for Python or Java knowledge, just SQL and some ML algorithms
- Advantage: No need to export data into a different system
    - Generally when training an ML model, you export the data from some data warehouse, build a model, train it, then deploy it
    - BigQuery allows us to build the model in the data warehouse itself, removing that extra export step
- ML BigQuery Pricing:
    - Free tier
        - Free 10 GB per month of data storage
        - Free 1 TB per month of queries processed
        - ML Create model step = 1st 10 GB per month is free
    - After the free tier, you'd pay about $250 per TB (for logistic or linear regression, K-means clustering, or time series model creation), or $5 per Tb, plus Vertex AI training cost for AutoML Tables model, DNN model, and Boosted tree model creation

## Steps of ML Development
- ML model development is expert-driven to address some need
- 1\. Collect Data
- 2\. Process the data (dava evaluation, cleaning, feature engineering, normalization, optimization)
- 3\. Splitting data into Test and Train sets
- 4\. Building the ML model (choosing the correct algorithm, optimizing parameters via hyperparamter tuning, training)
    - Multiple, likely iterative, steps
- 5\. Validate and optimize ML model (evaluation on validation and/or testing sets) with the goal of generalization/reproducibility
    - Multiple, likely iterative, steps
- 6\. Deployment of optimized ML model
    - Multiple, likely iterative, steps
- BigQuery helps us in all of these steps
    - Manual *and* automatic feature engineering
    - Splitting the data
    - Allows the choice of different algorithms and do hyperparameter tuning
    - Provides hidden matrices to do model validation against
    - Deployment of models via a Docker image

## Algorithms to Choose
- This is based on use case
- Predict Values (stock prices, sales figures) = Linear regression, Boosted tree regressor, AutoML Table regressor, DNN regressor, Wide & Deep regressor
- Predict betwen categories (SPAM emails, tumor types) = Logistic regression, Boosted tree classifier, AutoML Table classifier, DNN classifier, Wide & Deep classifier
- Generate recommendations (products, personalized content) = Wide & Deep classifier, Matrix factorization
- Reduce data dimensionality (analysis of written text or DNA data) = PCA, Auto-encoder
- Find anomolies (identify fraud, predict credit risk) = PCA, Auto-encoder, K-means, ARIMA-PLUS
- Clustering (customer segmentation) = K-means
- Time Series forecasting (predict housing prices based on historical data) = ARIMA-PLUS

## Building a Linear Regression Model
- In BigQuery, re-create the yellow taxi partitioned and partitioned + clustered tables if needed
- We will be trying to predict tip amount based on some specific columns
- F or the partitioned table, in a query editor, investigate some rows
    ```bash
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
        WHERE fare_amount != 0;
    ```
- BigQuery gives us the ability to do some feature engineering
    - https://cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-syntax-preprocess-overview
    - **Feature preprocessing** = one of the most important steps in developing a ML model, and it consists of the creation of features (**Feature engineering**) *as well as* the cleaning of the data
    - Feature preprocessing in BigQuery ML is divided into 2 parts:
        - **Automatic preprocessing** = BigQuery ML performs automatic preprocessing during training (https://cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-auto-preprocessing)
            - Missing data imputation
            - Feature transformations
                - Ex: Standardization of numeric fields (`NUMERIC`, `INT64`, `BIGNUMERIC`, `FLOAT64`), one-hot encoding (converting category feature into a **sparse vector**) of category fields (`BOOL`, `STRING`, `BYTES`, `DATE`, `DATETIME`, `TIME`), *multi*-hot encoding of `ARRAY`'s
            - `TIMESTAMP` feature transformation
            - Category feature encoding (`ONE_HOT_ENCODING` or `DUMMY_ENCODING`) 
        - **Manual preprocessing** = BigQuery ML provides the `TRANSFORM` clause for you to define custom preprocessing using the manual preprocessing functions, and you can also use these functions (*outside*) the `TRANSFORM` clause (https://cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-preprocessing-functions)
            - `CREATE MODEL`:
                - 2 types of manual preprocessing functions, **scalar** and **analytic**:
                    - Scalar functions operate on a single row (for example, `ML.BUCKETIZE`)
                    - Analytic functions operate on *all* rows (for example, `ML.QUANTILE_BUCKETIZE`) and output the result for each row based on the statistics collected across all rows
            - There's also `ML.BUCKETIZE`, `ML.POLYNOMIAL_EXPAND`, `ML.FEATURE_CROSS`, `ML.NGRAMS`, `ML.QUANTILE_BUCKETIZE`, `ML.HASH_BUCKETIZE`, `ML.MIN_MAX_SCALER`, `ML.STANDARD_SCALER`, `ML.MAX_ABS_SCALER`, `ML.ROBUST_SCALER`, `ML.NORMALIZER`, `ML.IMPUTER`, `ML.ONE_HOT_ENCODER`, and `ML.LABEL_ENCODER`, ``, ``, ``, ``, ``, ``, ``, ``, ``, ``, ``, ``, ``
    - **BigQuery ML supports automatic preprocessing in the model export but does NOT include manual preprocessing**
    - Can use the `ML.FEATURE_INFO` function to retrieve statistics of all input feature columns
- For this example, we won't have to use any manual pre-processing
- Some our features are not in the right datatype for automatic preprocessing (`PULocationID` and `DOLocationID` are `INTEGER`'s right now, but they're actually categories, same with `payment_type`)
- To deal with this, we convert them to `STRING` in a new table specifically for ML
    ```bash
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
        ```
- Then we build a linear regression model with auto-splitting into training and evaluation sets (this will take a couple of minutes)
    ```bash
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
    ```
- Clicking on the model, we can see its type and that the training and evaluation sets are *temporary*
- In the "Training" tab, we can already see the loss and the duration it took
- In the "Evaluation" tab, we can see some metrics like mean absolute error, mean squeare error, R squared, etc.
- We can then check the features statistics (min, max, mean, median, stddev, category_count, null_count, dimension) via
    ```bash
        SELECT * FROM ML.FEATURE_INFO(MODEL `de-zoomcamp-384821.ny_trips.taxi_tip_model`);
    ```
- For evaluation metrics calculated during model creation, you can use evaluation functions such as `ML.EVALUATE` (https://cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-syntax-evaluate) on the model with no input data specified (https://cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-syntax-evaluate-overview)
    ```bash
        -- 5. EVALUATE THE MODEL
        SELECT
        *
        FROM 
        ML.EVALUATE(MODEL `de-zoomcamp-384821.ny_trips.taxi_tip_model`,
            -- TABLE
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
    ```
    - You will get back various metrics: `mean_absolute_error`, `mean_squared_error`, `mean_squared_log_error`, `median_absolute_error`, `r2_score`, `explained_variance`
- Next, we can predict using the model
    - https://cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-syntax-predict
    - https://cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-syntax-inference-overview
    ```bash
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
    ```
    - You will get all records with all columns back, along with a new column for the predicted value of the target column, `predicted_tip_amount`
- The `ML.EXPLAIN_PREDICT` function generates a predicted value and a set of feature attributions per instance of the input data
    - **Feature attributions** indicate how much each feature in your model contributed to the final prediction for each given instance
    - `ML.EXPLAIN_PREDICT` can be viewed as an extended version of `ML.PREDICT`
    - https://cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-syntax-explain-predict
    - We will look at the top 3 most "important" features in our dataset (which end up being our 3 category features)
        ```bash
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
        ```
    - You get back a lot of metrics, multiple columns with rows for each predicted value of each of the 3 input features for that predicted value
        - https://cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-syntax-explain-predict#mlexplain_predict_output
- We've seen thus far that out model has not been "optimal", so we can do some hyperparameter tuning via arguments within `CREATE OR REPLACE MODEL`
    - https://cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-hyperparameter-tuning
    - https://cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-syntax-create-glm
    - We will use `num_trials=5`, `max_parallel_trials=2`, `l1_reg=hparam_range(0, 20)`, and `l2_reg=hparam_candidates([0, 0.1, 1, 10])`
        ```bash
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
        ```


## ML Deployment in BigQuery
- 
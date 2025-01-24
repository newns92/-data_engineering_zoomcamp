# Machine Learning in BigQuery

- We will now talk about machine learning (ML) in BigQuery, as well as building a model, exporting it, and running it via Docker


## BigQuery Machine Learning


### Why Do Machine Learning in BigQuery
- Introduction: https://cloud.google.com/bigquery/docs/bqml-introduction
- Tutorials: https://cloud.google.com/bigquery-ml/docs/tutorials
- The target audience for the output of ML is data analysts, managers, and more
- The idea behind doing ML *in* BigQuery is that there's no need for Python or Java knowledge, just knowledge of SQL and some ML algorithms
- Another BigQuery ML advantage is that there is no need to export data into a *different system*
    - Generally when training an ML model, you export the data from some data warehouse, build a model, train it, then deploy it to some other system
    - BigQuery allows us to build the model *in the data warehouse itself*, removing that extra export step


### ML BigQuery Pricing
- Pricing is the main condition you'd have to consider between choosing to do ML in BigQuery or to build your model separately
- As of 2022, the free tier consists of:
    - Free 10 GB per month of data storage
    - Free 1 TB per month of queries processed
    - If using the ML "Create model" step, the first 10 GB per month is free
- Beyond the free tier, you'd pay about $250 per TB (for logistic or linear regression, K-means clustering, or time series model creation), or $5 per Tb, plus Vertex AI training cost (for AutoML Tables models, DNN models, and Boosted Tree model creation)


### Steps of ML Development
- ML model development is expert-driven to address some need
- Steps:
    - 1\. Collect Data
    - 2\. Process the data (dava evaluation, cleaning, **feature engineering**, normalization, optimization)
    - 3\. Splitting data into Test and Train sets
    - 4\. Building the ML model (choosing the correct algorithm, optimizing parameters via **hyperparamter tuning**, training)
        - This step consists of multiple (likely iterative) steps
    - 5\. Validate and optimize ML model (evaluation on validation and/or testing sets) with the goal of generalization and/or reproducibility
        - This step consists of multiple (likely iterative) steps
    - 6\. Deployment of optimized ML model
        - This step consists of multiple (likely iterative) steps
- BigQuery helps us in all of these steps:
    - Allows us to do manual *and* automatic feature engineering
    - Allows us to do split the data
    - Allows the choice of different algorithms and do hyperparameter tuning
    - Provides hidden matrices to do model validation against
    - Allows deployment of models via a Docker image


### Algorithms to Choose
- See: https://cloud.google.com/bigquery/docs/bqml-introduction#model_selection_guide
- *The choice of ML algorithm is based on use case*
- To **predict values** (stock prices, sales figures), go with: Linear regression, Boosted tree regressor, AutoML Table regressor, DNN regressor, Wide & Deep regressor
- To **predict between *categories*** (SPAM emails, tumor types), go with: Logistic regression, Boosted tree classifier, AutoML Table classifier, DNN classifier, Wide & Deep classifier
- To **generate recommendations** (products, personalized content), go with: Wide & Deep classifier, Matrix factorization
- To **reduce data dimensionality** (analysis of written text or DNA data), go with: PCA, Auto-encoder
- To **find anomolies** (identify fraud, predict credit risk), go with: PCA, Auto-encoder, K-means, ARIMA-PLUS
- For **clustering** (customer segmentation), go with: K-means
- For **time series forecasting** (predict housing prices based on historical data), go with: ARIMA-PLUS


## Building a Linear Regression Model in BigQuery
- In BigQuery, re-create the yellow taxi partitioned and partitioned + clustered tables, if needed
- We will be trying to **predict tip amount based on some specific columns**
- For the partitioned table, in a query editor, let's first investigate some rows:
    ```SQL
        SELECT 
            passenger_count,
            trip_distance,
            pu_location_id,
            do_location_id,
            payment_type,
            fare_amount,
            tolls_amount,
            tip_amount
        FROM <project-id>.de_zoomcamp.yellow_taxi_data_partitioned
        WHERE fare_amount != 0
        ;
    ```
- BigQuery gives us the ability to do some **feature engineering**
    - See: https://cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-syntax-preprocess-overview
    - **Feature pre-processing** is one of the *most important* steps in developing a ML model, and it consists of the creation of features (**Feature engineering**) *as well as* the **cleaning** of the data
    - Feature pre-processing in BigQuery ML is divided into 2 parts:
        - ***Automatic* pre-processing**, wherein BigQuery ML performs automatic pre-processing *during training* (https://cloud.google.com/bigquery/docs/auto-preprocessing)
            - It performs **missing data imputation**
            - It also performs **feature transformations**
                - **Standardization** of numeric fields (`NUMERIC`, `INT64`, `BIGNUMERIC`, `FLOAT64`)
                - **One-hot encoding** (converting a category feature into a **sparse vector**) of non-numerical (other than `TIMESTAMP`) category fields (`BOOL`, `STRING`, `BYTES`, `DATE`, `DATETIME`, `TIME`)
                - ***Multi*-hot encoding** of non-numerical `ARRAY`'s
                - `TIMESTAMP` transformations
                - ***NOTE:*** Category feature encoding involves `ONE_HOT_ENCODING` or `DUMMY_ENCODING`
        - ***Manual* pre-processing**, wherein BigQuery ML provides the `TRANSFORM` clause for you to define *custom* pre-processing using specific manual pre-processing functions
            - You can also use these functions *outside* of the `TRANSFORM` clause (https://cloud.google.com/bigquery/docs/manual-preprocessing)
                - There are several types of manual pre-processing functions:
                    - **Scalar** functions operate on a single row (for example, `ML.BUCKETIZE`)
                    - **Analytic** functions operate on *all* rows (for example, `ML.QUANTILE_BUCKETIZE`) and output the result for each row based on the statistics collected across all rows
                    - **Table-valued** functions operate on all rows and output a table (for example, `ML.FEATURES_AT_TIME`)
    - **BigQuery ML supports automatic pre-processing in the model export but does *NOT* include manual pre-processing**
    - We can use the `ML.FEATURE_INFO` function to retrieve statistics of all input feature columns
- For this example, we won't have to use any *manual* pre-processing
- Some of our features are not the right data type for automatic preprocessing (`pu_location_id` and `do_location_id` are `INTEGER`'s right now, but they're actually *categories*, and the same goes for `payment_type`)
- To deal with this, we convert them to `STRING` in a *new* table *specifically* for ML
    ```SQL
        -- 2) CREATE A TABLE FOR ML AUTOMATIC PREPROCESSING WITH APPROPRIATE DATA TYPES
        CREATE OR REPLACE TABLE <project-id>.de_zoomcamp.yellow_taxi_data_ml (
            `passenger_count` INTEGER,
            `trip_distance` FLOAT64,
            `pu_location_id` STRING,
            `do_location_id` STRING,
            `payment_type` STRING,
            `fare_amount` FLOAT64,
            `tolls_amount` FLOAT64,
            `tip_amount` FLOAT64
        ) 
        AS (
            SELECT
                passenger_count,
                trip_distance,
                -- Convert to categories
                CAST(pu_location_id AS STRING),
                CAST(do_location_id AS STRING),
                CAST(payment_type AS STRING),
                fare_amount,
                tolls_amount,
                tip_amount
            FROM `<project-id>.de_zoomcamp.yellow_taxi_data_partitioned`
            WHERE fare_amount != 0
        )
        ;
        ```
- Then, we build a linear regression model with **auto-splitting** into training and evaluation sets (This will take a couple of minutes)
    ```SQL
        -- 3. CREATE LINEAR REGRESSION ML MODEL WITH DEFAULT SETTINGS
        CREATE OR REPLACE MODEL `<project-id>.de_zoomcamp.taxi_tip_model`
        OPTIONS (
            model_type='linear_reg',
            input_label_cols=['tip_amount'], -- what we want to predict
            DATA_SPLIT_METHOD='AUTO_SPLIT' -- for training and evaluation
        )
        AS
            SELECT
                passenger_count,
                trip_distance,
                pu_location_id,
                do_location_id,
                payment_type,
                fare_amount,
                tolls_amount,
                tip_amount
            FROM `<project-id>.de_zoomcamp.yellow_taxi_data_ml`
            WHERE tip_amount IS NOT NULL
        ;
    ```
- Clicking on the model in the BigQuery UI once completed to open up its details UI, we can see its type and that the training and evaluation sets are *temporary*, and that no optimization was done
    - In the "Training" tab, we can already see the loss and the duration it took
    - In the "Evaluation" tab, we can see some metrics like mean absolute error, mean squeare error, R squared, etc.
- We can then check the features statistics (min, max, mean, median, standard deviation, `category_count`, `null_count`, dimension)  for each feature via:
    ```SQL
        -- CHECK FEATURES
        SELECT * FROM ML.FEATURE_INFO(MODEL `<project-id>.de_zoomcamp.taxi_tip_model`);
    ```
- For evaluation metrics calculated during model creation, we can use **evaluation functions** such as `ML.EVALUATE` (https://cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-syntax-evaluate) on the model *with no input data specified* (https://cloud.google.com/bigquery/docs/evaluate-overview)
    - This will evaluate our model against our training data
        ```SQL
            -- 5. EVALUATE THE MODEL
            SELECT
            *
            FROM 
            ML.EVALUATE(MODEL `<project-id>.de_zoomcamp.taxi_tip_model`,
                -- TABLE/DATASET
                (
                    SELECT
                    *
                    FROM
                    `<project-id>.de_zoomcamp.yellow_taxi_data_ml`
                    WHERE
                    tip_amount IS NOT NULL
                )
            )
            ;
        ```
    - You will get back various metrics: `mean_absolute_error`, `mean_squared_error`, `mean_squared_log_error`, `median_absolute_error`, `r2_score`, `explained_variance`
        - *We can use these metrics to optimize our models*
- Next, we can **predict** using the model
    - https://cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-syntax-predict
    - https://cloud.google.com/bigquery/docs/inference-overview
        ```SQL
            -- 6. PREDICT TIP AMOUNT USING THE MODEL
            SELECT
            *
            FROM 
            ML.PREDICT(MODEL `<project-id>.de_zoomcamp.taxi_tip_model`,
                -- TABLE/DATASET
                (
                    SELECT
                    *
                    FROM
                    `<project-id>.de_zoomcamp.yellow_taxi_data_ml`
                    WHERE tip_amount IS NOT NULL
                )
            )
            ;
        ```
    - You will get all records with all columns back, along with a *new* column for the predicted value of the target column, `predicted_tip_amount`
    - The resulting columns can be used for manual evaluation
- The `ML.EXPLAIN_PREDICT` function, used to explain and predict different models, generates a predicted value *and* a set of **feature attributions** per instance of the input data
    - **Feature attributions** indicate how much each feature in your model contributed to the final prediction for each given instance
    - `ML.EXPLAIN_PREDICT` can be viewed as an extended version of `ML.PREDICT`
        - https://cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-syntax-explain-predict
    - We will look at the top 3 most "important" features in our dataset (which end up being our 3 category features)
        ```SQL
            -- 7. PREDICT AND EXPLAIN THE MODEL
            SELECT
            *
            FROM 
            ML.EXPLAIN_PREDICT(MODEL `<project-id>.de_zoomcamp.taxi_tip_model`,
                -- TABLE/DATASET
                (
                    SELECT
                    *
                    FROM
                    `<project-id>.de_zoomcamp.yellow_taxi_data_ml`
                    WHERE tip_amount IS NOT NULL
                )
            -- Look only at top 3 most "important" features
            , STRUCT(3 as top_k_features)
            )
            ;
        ```
    - Note that you get back a *lot* of metrics in the form of multiple columns with rows for each predicted value of each of the 3 input features for that predicted value
        - https://cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-syntax-explain-predict#mlexplain_predict_output
- We've seen thus far that our model has not been "optimal", so we can do some **hyperparameter tuning** via arguments within our `CREATE OR REPLACE MODEL` statement
    - https://cloud.google.com/bigquery/docs/hp-tuning-overview
    - https://cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-syntax-create-glm
    - We will use `num_trials=5`, `max_parallel_trials=2`, `l1_reg=hparam_range(0, 20)`, and `l2_reg=hparam_candidates([0, 0.1, 1, 10])` as our hyperparameters
        ```SQL
            -- 8. HYPERPARAMETER TUNNING
            CREATE OR REPLACE MODEL `<project-id>.de_zoomcamp.taxi_tip_model_tuned`
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
                    `<project-id>.de_zoomcamp.yellow_taxi_data_ml`
                WHERE tip_amount IS NOT NULL
            ;
        ```
    - This will process *much* more data, so be aware of that, and it will take much more time


## BigQuery Machine Learning Deployment
- See:
    - https://cloud.google.com/bigquery/docs/export-model-tutorial
    - https://cloud.google.com/bigquery/docs/bq-command-line-tool
    - https://cloud.google.com/bigquery/docs/exporting-data#bq
- First, enable the **AI Platform Training and Prediction API** and the **Compute Engine API**, if needed
- *Then, make sure you have a `de_zoomcamp.taxi_tip_model_tuned` model in BigQuery, and create one if not*
- Then, create a `<project-id>-taxi-data` GCS Bucket with default permissions, if needed
- Then, in an Anaconda or Git command prompt, run `gcloud auth login`
    - Authenticate in a web browser, if prompted
    - If the the current project is not the right project for this use case as displayed in the welcome message in the command prompt, choose the correct project via `gcloud config set project <project-id>`
- Then, *in the shell where you ran `gcloud auth login`*, run `bq --project_id <project-id> extract -m de_zoomcamp.taxi_tip_model_tuned gs://<project-id>-taxi-data/tip_model_tuned` to *export* our model to our GCS bucket (`<project-id>-taxi-data`)
    - The `-m` argument is for model
    - The destination format is `gs://<bucket-name>/<model-name>`
    - This command will take 1-3 minutes to execute, but then you will see a `tip_model_tuned/` directory in the above bucket with various files within it
- In your command prompt, make a *temporary* directory for the model in the *host* machine's `C:/` drive locally via `mkdir \tmp\model`
- In your command prompt, bring down the model locally with the copy `cp` commands via `gsutil cp -r gs://<project-id>-taxi-data/tip_model_tuned \tmp\model`
    - The `-r` argument means to copy an *entire* directory tree
- *In Git bash*, in your local `week3/` sub-directory for the course, run `mkdir -p serving_dir/tip_model/1` to make a **serving directory**
    - `-p` stands for the *parent* argument, meaning the command will create all the directories necessaries to fulfill your request, not returning any error in case that directory exists
- *In the same Git bash command prompt*, copy everything from `\tmp\model` to there via:
    - Git bash: `cp -r C:/tmp/model/tip_model_tuned/* serving_dir/tip_model/1`
    - Anaconda prompt: `copy -r \tmp\model\tip_model\* serving_dir\tip_model\1`
- *In the same Git bash* in the local `week3/` sub-directory, run `docker pull tensorflow/serving` to get a specific Docker image
- Then, *in Git bash and in the directory where we ran `docker pull`*, run that Docker image on port 8501 via ```docker run -p 8501:8501 --mount type=bind,source=`pwd`/serving_dir/tip_model,target=/models/tip_model -e MODEL_NAME=tip_model -t tensorflow/serving &```
- Then go to http://localhost:8501/v1/models/tip_model in a browser, and note that we see something we can make HTTP requests to
    - In this JSON, we see that we are in model version 1, that there's no error, and that the `state` is `AVAILABLE`
- Then, in the *same* Git bash window, run `curl -d '{"instances": [{"passenger_count":1, "trip_distance":12.2, "pu_location_id":"193", "do_location_id":"264", "payment_type":"2", "fare_amount":20.4, "tolls_amount":0.0}]}' -X POST http://localhost:8501/v1/models/tip_model:predict` to make a request for a prediction for these specified field values/parameters
    - We should recieve some JSON like `"predictions": [[0.79005508736825658]]]`
    - We can play around with these parameters values
- When done, you can stop the Docker image via `docker stop <container-id>`


## References
- BigQuery Machine Learning Tutorials: https://cloud.google.com/bigquery-ml/docs/tutorials
- BigQuery Machine Learning Reference Parameter: https://cloud.google.com/bigquery-ml/docs/analytics-reference-patterns
- Hyper Parameter tuning: https://cloud.google.com/bigquery-ml/docs/reference/standard-sql/bigqueryml-syntax-create-glm
- Feature preprocessing: https://cloud.google.com/bigquery-ml/docs/reference/standard-sql/bigqueryml-syntax-preprocess-overview
- Steps to extract and deploy model with docker: https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/03-data-warehouse/extract_model.md

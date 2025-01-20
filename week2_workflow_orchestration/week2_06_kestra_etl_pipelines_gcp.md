# ETL Pipelines in Kestra: Google Cloud Platform


## Intro
- We will take our existing ETL pipeline (currently feeding into a local Postgres database) and move it over to GCP using Google Cloud Storage (GCS) and BigQuery
- We will use a very similar flow to the Postgres one, but will instead be loading our CSV's into a **data lake** (GCS)
- Then, BigQuery can automatically use that CSV file and create a table off of it
- From then onwards, we can start to process data and run queries
- Then, we can add in schedules and backfills like we did for the Postgres flow
- But first, we have to get set up in GCP


## Setup GCP with a Flow
- In order to run GCP Kestra tasks, we need a couple of things:
  - GCP service account
  - GCP project ID
  - Location region
  - GCS **bucket** name
- We will write a separate flow to create these things, and in this flow, we will use Kestra's **key-value store**
  - In Kestra, we can create key-value pairs that we can later use (sort of like local environment variables)
  - While they can be accessed by a flow, they are not seen directly in it, which is good because we don't want to expose secrets or other sensitive information
  - In this flow, for example, we can create a biolerplate `GCP_CREDS` key-value store (that we will edit later)
    ```YML
    id: gcp_key_value
    namespace: zoomcamp

    tasks:
      - id: gcp_creds
        type: io.kestra.plugin.core.kv.Set
        key: GCP_CREDS
        value: |
          {
            type: 'service_account',
            project_id: '<your_project_id>'
          }
    ```
 - We can then create more key-value stores for the GCP project ID, GCP location, GCS bucket name, and our dataset
    ```YML
      - id: gcp_project_id
        type: io.kestra.plugin.core.kv.Set
        key: GCP_PROJECT_ID
        kvType: STRING
        value: '<your_project_id>'

      - id: gcp_location
        type: io.kestra.plugin.core.kv.Set
        key: GCP_LOCATION
        kvType: STRING
        value: 'northamerica-northeast2'

      - id: gcp_bucket_name
        type: io.kestra.plugin.core.kv.Set
        key: GCP_BUCKET_NAME
        kvType: STRING
        # Need a globally-unique value
        value: '<your_project_id>-ny-taxi'

      - id: gcp_dataset
        type: io.kestra.plugin.core.kv.Set
        key: GCP_DATASET
        kvType: STRING
        value: 'de_zoomcamp'
    ```
  - In order to use this flow, if you have not done so already, create a GCP service account with the "Storage Admin" and "BigQuery Admin" roles
  - Then, generate a private JSON key (again, if you have not done so already) and keep it somewhere on your local machine
  - Next, open the JSON for the key, and copy and paste the values into the `gcp_creds` task in the `values: {}` dictionary
  - Save the flow, then execute it
  - We can then see the the values added to the "KV Store" tab in the "Namespace" section of the UI (on the left-hand side) for our namespace, `zoomcamp`
- Next, create a new flow that will set up GCP for us, using the key-value stores via the `kv()` function in Kestra
  ```YML
  id: gcp_setup
  namespace: zoomcamp

  tasks:
    - id: create_gcs_bucket
      type: io.kestra.plugin.gcp.gcs.CreateBucket
      ifExists: SKIP
      storageClass: REGIONAL
      # Make sure the following is globally unique
      name: '{{ kv(''GCP_BUCKET_NAME'') }}'

    - id: create_bq_dataset
      type: io.kestra.plugin.gcp.bigquery.CreateDataset
      ifExists: SKIP
      name: '{{ kv(''GCP_DATASET'') }}'

  pluginDefaults:
    - type: io.kestra.plugin.gcp
      values:
        serviceAccount: '{{ kv(''GCP_CREDS'') }}'
        projectId: '{{ kv(''GCP_PROJECT_ID'') }}'
        location: '{{ kv(''GCP_LOCATION'') }}'
        bucket: '{{ kv(''GCP_BUCKET_NAME'') }}'
  ```
- Once executed, we can see the bucket in GCS and the dataset in BigQuery


## Uploading CSV's to GCS
- GCS is typically used for **object storage**, usually storing *unstructured* data files
- But we will be using it to store *structured* CSV's that our **data warehouse** (BigQuery) can access
- We will be storing the raw data into a **data lake**, then pass it over to the data warehouse to process it
- So, create yet another flow, this time to upload a CSV file to our GCS bucket, that will look similar to the Postgres flow to load in data, but with new dynamic variables and a new `upload_to_gcs` task to upload to a data lake (GCS) rather than straight to a database/data warehouse
  ```YML
  variables:
    file: '{{ inputs.taxi }}_tripdata_{{ inputs.year }}-{{ inputs.month }}.csv'
    gcs_file: 'gs://{{ kv(''GCP_BUCKET_NAME'' )}}/{{ vars.file }}'
    table: '{{ kv(''GCP_DATASET'' )}}.{{ inputs.taxi }}_tripdata_{{ inputs.year }}-{{ inputs.month }}'
    data: '{{ outputs.extract.outputFiles[inputs.taxi ~ ''_tripdata_'' ~ inputs.year ~ ''-'' ~ inputs.month ~ ''.csv''] }}'
  ```
  ```YML
  - id: upload_to_gcs
    type: io.kestra.plugin.gcp.gcs.Upload
    from: '{{ render(vars.data) }}'
    to: '{{ render(vars.gcs_file) }}'
  ```
- Remember to have your default plugins at the bottom of the flow, and execute this flow for January 2019 green taxi data
- You should then see the CSV in your GCS bucket


## Creating a Table in BigQuery
- Next, we can pass over this CSV file to BigQuery to make a table from it
- We do this via a new task in the current flow that will define the table via SQL and also give the columns descriptions that we can view in the BigQuery documentation
- Also, note that we are partitioning on the date of `lpep_pickup_datetime`
  ```YML
  - id: bq_green_tripdata
    type: io.kestra.plugin.gcp.bigquery.Query
    sql:
      CREATE TABLE IF NOT EXISTS `{{ kv('GCP_PROJECT_ID') }}.{{ kv('GCP_DATASET') }}.green_tripdata` (
        unique_row_id BYTES OPTIONS (description = 'A unique identifier for the trip, generated by hashing key trip attributes.'),
        filename STRING OPTIONS (description = 'The source filename from which the trip data was loaded.'),      
        VendorID STRING OPTIONS (description = 'A code indicating the LPEP provider that provided the record. 1= Creative Mobile Technologies, LLC; 2= VeriFone Inc.'),
        lpep_pickup_datetime TIMESTAMP OPTIONS (description = 'The date and time when the meter was engaged'),
        lpep_dropoff_datetime TIMESTAMP OPTIONS (description = 'The date and time when the meter was disengaged'),
        store_and_fwd_flag STRING OPTIONS (description = 'This flag indicates whether the trip record was held in vehicle memory before sending to the vendor, aka "store and forward," because the vehicle did not have a connection to the server. Y= store and forward trip N= not a store and forward trip'),
        RatecodeID STRING OPTIONS (description = 'The final rate code in effect at the end of the trip. 1= Standard rate 2=JFK 3=Newark 4=Nassau or Westchester 5=Negotiated fare 6=Group ride'),
        PULocationID STRING OPTIONS (description = 'TLC Taxi Zone in which the taximeter was engaged'),
        DOLocationID STRING OPTIONS (description = 'TLC Taxi Zone in which the taximeter was disengaged'),
        passenger_count INT64 OPTIONS (description = 'The number of passengers in the vehicle. This is a driver-entered value.'),
        trip_distance NUMERIC OPTIONS (description = 'The elapsed trip distance in miles reported by the taximeter.'),
        fare_amount NUMERIC OPTIONS (description = 'The time-and-distance fare calculated by the meter'),
        extra NUMERIC OPTIONS (description = 'Miscellaneous extras and surcharges. Currently, this only includes the $0.50 and $1 rush hour and overnight charges'),
        mta_tax NUMERIC OPTIONS (description = '$0.50 MTA tax that is automatically triggered based on the metered rate in use'),
        tip_amount NUMERIC OPTIONS (description = 'Tip amount. This field is automatically populated for credit card tips. Cash tips are not included.'),
        tolls_amount NUMERIC OPTIONS (description = 'Total amount of all tolls paid in trip.'),
        ehail_fee NUMERIC,
        improvement_surcharge NUMERIC OPTIONS (description = '$0.30 improvement surcharge assessed on hailed trips at the flag drop. The improvement surcharge began being levied in 2015.'),
        total_amount NUMERIC OPTIONS (description = 'The total amount charged to passengers. Does not include cash tips.'),
        payment_type INTEGER OPTIONS (description = 'A numeric code signifying how the passenger paid for the trip. 1= Credit card 2= Cash 3= No charge 4= Dispute 5= Unknown 6= Voided trip'),
        trip_type STRING OPTIONS (description = 'A code indicating whether the trip was a street-hail or a dispatch that is automatically assigned based on the metered rate in use but can be altered by the driver. 1= Street-hail 2= Dispatch'),
        congestion_surcharge NUMERIC OPTIONS (description = 'Congestion surcharge applied to trips in congested zones')
      )
      PARTITION BY DATE(lpep_pickup_datetime)
      ;
  ```
- We should then be able to see the `green_tripdata` table in BigQuery
- Now we can start to load all the data into BigQuery, but only after creating our staging table(s) to load into our final table from
- In BigQuery, we use **external tables** as our staging tables, telling the external tables to use the CSV in our GCS bucket for its data
  ```YML
    - id: bq_green_tripdata_external
      type: io.kestra.plugin.gcp.bigquery.Query
      sql:
          # Tell the external table to use the data from the CSV file in GCS in the `OPTIONS = ()` section
          CREATE OR REPLACE EXTERNAL TABLE `{{ kv('GCP_PROJECT_ID') }}.{{ render(vars.table) }}_external` (   
            VendorID STRING OPTIONS (description = 'A code indicating the LPEP provider that provided the record. 1= Creative Mobile Technologies, LLC; 2= VeriFone Inc.'),
            lpep_pickup_datetime TIMESTAMP OPTIONS (description = 'The date and time when the meter was engaged'),
            lpep_dropoff_datetime TIMESTAMP OPTIONS (description = 'The date and time when the meter was disengaged'),
            store_and_fwd_flag STRING OPTIONS (description = 'This flag indicates whether the trip record was held in vehicle memory before sending to the vendor, aka "store and forward," because the vehicle did not have a connection to the server. Y= store and forward trip N= not a store and forward trip'),
            RatecodeID STRING OPTIONS (description = 'The final rate code in effect at the end of the trip. 1= Standard rate 2=JFK 3=Newark 4=Nassau or Westchester 5=Negotiated fare 6=Group ride'),
            PULocationID STRING OPTIONS (description = 'TLC Taxi Zone in which the taximeter was engaged'),
            DOLocationID STRING OPTIONS (description = 'TLC Taxi Zone in which the taximeter was disengaged'),
            passenger_count INT64 OPTIONS (description = 'The number of passengers in the vehicle. This is a driver-entered value.'),
            trip_distance NUMERIC OPTIONS (description = 'The elapsed trip distance in miles reported by the taximeter.'),
            fare_amount NUMERIC OPTIONS (description = 'The time-and-distance fare calculated by the meter'),
            extra NUMERIC OPTIONS (description = 'Miscellaneous extras and surcharges. Currently, this only includes the $0.50 and $1 rush hour and overnight charges'),
            mta_tax NUMERIC OPTIONS (description = '$0.50 MTA tax that is automatically triggered based on the metered rate in use'),
            tip_amount NUMERIC OPTIONS (description = 'Tip amount. This field is automatically populated for credit card tips. Cash tips are not included.'),
            tolls_amount NUMERIC OPTIONS (description = 'Total amount of all tolls paid in trip.'),
            ehail_fee NUMERIC,
            improvement_surcharge NUMERIC OPTIONS (description = '$0.30 improvement surcharge assessed on hailed trips at the flag drop. The improvement surcharge began being levied in 2015.'),
            total_amount NUMERIC OPTIONS (description = 'The total amount charged to passengers. Does not include cash tips.'),
            payment_type INTEGER OPTIONS (description = 'A numeric code signifying how the passenger paid for the trip. 1= Credit card 2= Cash 3= No charge 4= Dispute 5= Unknown 6= Voided trip'),
            trip_type STRING OPTIONS (description = 'A code indicating whether the trip was a street-hail or a dispatch that is automatically assigned based on the metered rate in use but can be altered by the driver. 1= Street-hail 2= Dispatch'),
            congestion_surcharge NUMERIC OPTIONS (description = 'Congestion surcharge applied to trips in congested zones')
          )        
          OPTIONS (
            format = 'CSV',
            uris = ['{{ render(vars.gcs_file) }}'],
            skip_leading_rows = 1,
            ignore_unknown_values = TRUE
          )
          ;
  ```
- After this, in BigQuery, we should see our two tables
- Click on the external table (January 2019 green taxi data), and see in the "Details" pane that the "Source URI(s)" field has a value corresponding to the CSV in our GCS bucket
- You could then query this external table to see that it is indeed populated with data (say, via `SELECT * FROM <project_id>.<dataset>.green_tripdata_2019_01_external LIMIT 10;`)
- Next, we need to add our two fields like we did in Postgres and then merge this data into the final table


## Adding Fields to the External Table
- We do this in a new task in the flow, creating a temp table based off of this external table (using a `CREATE TABLE AS` statement), adding in our two new fields, `unique_row_id` and `filename`
  ```YML
    - id: bq_green_table_temp
      type: io.kestra.plugin.gcp.bigquery.Query
      sql:
        CREATE OR REPLACE TABLE `{{ kv('GCP_PROJECT_ID') }}.{{ render(vars.table) }}`
        AS
        SELECT
          MD5(CONCAT(
            COALESCE(CAST(VendorID AS STRING), ''),
            COALESCE(CAST(lpep_pickup_datetime AS STRING), ''),
            COALESCE(CAST(lpep_dropoff_datetime AS STRING), ''),
            COALESCE(CAST(PULocationID AS STRING), ''),
            COALESCE(CAST(DOLocationID AS STRING), '')
          )) AS unique_row_id,
          '{{ render(vars.file) }}' AS filename,
          *
        FROM `{{ kv('GCP_PROJECT_ID') }}.{{ render(vars.table) }}_external`
        ;
  ```
- We should now see a third table, that we can query to see if we have our two new columns and that they are populated with data
  - `SELECT * FROM <project_id>.<dataset>.green_tripdata_2019_01 LIMIT 10;`


## Merge Data into Main Table
- Next, we need to merge this data into our final table, and then get rid of those external and temp tables
- Back in Kestra, we make a new task in our flow to do this in SQL via a `MERGE INTO WHEN NOT MATCHED THEN INSERT VALUES` statement
  ```YML
    - id: bq_green_merge
      type: io.kestra.plugin.gcp.bigquery.Query
      sql:
        MERGE INTO `{{ kv('GCP_PROJECT_ID') }}.{{ kv('GCP_DATASET') }}.green_tripdata` AS table
        USING `{{ kv('GCP_PROJECT_ID') }}.{{ render(vars.table) }}` AS staging
        ON table.unique_row_id = staging.unique_row_id
        WHEN NOT MATCHED THEN
          INSERT (
            unique_row_id, filename, VendorID, lpep_pickup_datetime, lpep_dropoff_datetime,
            store_and_fwd_flag, RatecodeID, PULocationID, DOLocationID, passenger_count, trip_distance,
            fare_amount, extra, mta_tax, tip_amount, tolls_amount, ehail_fee, improvement_surcharge,
            total_amount, payment_type, trip_type, congestion_surcharge
          )
          VALUES (
            staging.unique_row_id, staging.filename, staging.VendorID, staging.lpep_pickup_datetime,
            staging.lpep_dropoff_datetime, staging.store_and_fwd_flag, staging.RatecodeID, staging.PULocationID,
            staging.DOLocationID, staging.passenger_count, staging.trip_distance, staging.fare_amount,
            staging.extra, staging.mta_tax, staging.tip_amount, staging.tolls_amount, staging.ehail_fee,
            staging.improvement_surcharge, staging.total_amount, staging.payment_type, staging.trip_type,
            staging.congestion_surcharge
          )
        ;
  ```
- Once the execution is completed, we should be able to preview (or query) the main table in BigQuery and see data
- Make note of the number of rows (630,918), and then execute the flow again but this time for green February 2019 data
- Then, check to make sure we have increased the number of rows in the main table (up to 1,206,603 rows), as well as seeing a temp table and external table for February 2019 green taxi data


## Add Condition for Yellow Vs. Green Datasets
- Just like we did for the Postgres version, we can add conditions to our flow that will run certain tasks depending on if we choose the yellow or green taxi data at execution time
  ```YML
    - id: if_green
      type: io.kestra.plugin.core.flow.If
      condition: '{{ inputs.taxi == ''green'' }}'
      then:

      - id: bq_green_tripdata
        type: io.kestra.plugin.gcp.bigquery.Query
        sql:
            CREATE TABLE IF NOT EXISTS `{{ kv('GCP_PROJECT_ID') }}.{{ kv('GCP_DATASET') }}.green_tripdata` (
  ```
  ```YML
    - id: if_yellow
      type: io.kestra.plugin.core.flow.If
      condition: '{{ inputs.taxi == ''yellow'' }}'
      then:

      - id: bq_yellow_tripdata
        type: io.kestra.plugin.gcp.bigquery.Query
        sql:
            CREATE TABLE IF NOT EXISTS `{{ kv('GCP_PROJECT_ID') }}.{{ kv('GCP_DATASET') }}.yellow_tripdata` (
  ```
- Then, be sure to once again add in a task to purge the files from Kestra
  ```YML
    - id: purge_files
      type: io.kestra.plugin.core.storage.PurgeCurrentExecutionFiles
      description: If you'd like to explore Kestra outputs, disable it.
      disabled: false
  ```
- Then, execute this flow for January 2019 yellow taxi data, and once successful, note that the CSV is in our GCS bucket and we have three new tables, one main yellow taxi data table, and the temp and external tables for January 2019 yellow taxi data
- You can then double-check that the merge is working by executing this flow for February 2019 yellow taxi data
- Next, we will create a schedule to automatically run this flow as data comes in, as well as running backfills to get past data

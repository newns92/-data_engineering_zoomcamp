# ETL Pipelines with Postgres in Kestra


## Create a Workflow
- Create a new flow via the "+ Create" or "+ Create Flow" button at the top-right of the UI of the "Flows" or "Dashboard" pages
- Give it a new `id` and `namespace`:
    ```YML
    id: postgres_taxi
    namespace: zoomcamp
    ```
- Next, we need to create **tasks** in order to do our ETL
    - E: We will use a request to the GitHub repository containing the data
    - T: We will do transforms on the data (if needed)
    - L: Then we merge and load all the data into one table in a Postgres database
- Before creating the Postgres database, we first get set up to extract the data


## Add Inputs
- First, we create a `SELECT`-type input that allows us to filter between green and yellow taxis, with a default-selected value of "Yellow:
    ```YML
    inputs:
    - id: taxi
      type: SELECT
      displayName: 'Select taxi type'
      values: ['yellow', 'green']
      defaults: 'yellow'
    ```
- Then, when we execute, we get the a drop-down that allows us to choose which set of taxis we want to get data for, with "Yellow" selected by default
- Replicate this to select the month and the year of each specific dataset:
```YML
  - id: month
    type: SELECT
    displayName: 'Select the month'
    values: ['01', '02', '03', '04', '05', '06', '07', 
      '08', '09', '10', '11', '12']
    defaults: '01'

  - id: year
    type: SELECT
    displayName: 'Select the year'
    values: ['2019', '2020']
    defaults: '2019'
```
- Next, we create a request to get the exact data that we want/input in Kestra


## Creating a Dynamic Variable
- To make creating our requests easier, we will create variables that are dynamically-generated based on our Kestra inputs
```YML
variables:
  # File to download
  file: '{{ inputs.taxi }}_tripdata_{{ inputs.year }}-{{ inputs.month }}.csv'
  # Monthly data table
  staging_table: 'public.{{ inputs.taxi }}_tripdata_staging'
  # Full data table
  table: 'public.{{ inputs.taxi }}_tripdata'
  # The data itself, generated based on the output from the extract task
  data: '{{ outputs.extract.outputFiles[inputs.taxi ~ ''_tripdata_'' ~ inputs.year ~ ''-'' ~ inputs.month ~ ''.csv'' ]}}'
```
- Next, we must create the Extract task which will use the `file` variable
- But first, create a `set_label` task to make it easier to to identify if the executoin is for green or yellow taxi data
```YML
tasks:
  - id: set_label
    type: io.kestra.plugin.core.execution.Labels
    labels:
      file: '{{ render(vars.file) }}'
      taxi: '{{ inputs.taxi }}'
```


## Downloading and Uncompressing CSV Files
- Next, create the `extract` task, using a shell command `type` of `wget`:
    ```YML
    - id: extract
        type: io.kestra.plugin.scripts.shell.Commands
        outputFiles:
        - '*.csv'
        taskRunner:
        type: io.kestra.plugin.core.runner.Process
        commands:
            # Download in "quiet mode" (-q) and specify the output (-O)
            # Use gunzip to decompress .gz files
            - wget -qO- https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{{ inputs.taxi }}/{{ render(vars.file) }}.gz | gunzip > {{ render(vars.file) }}
    ```
- This will return a CSV file for us to use
- We can execute this flow now, say for green taxis in 01/2019, and then the "Outputs" tab of the execution, within the `extract` task page on the left-hand side, we can see `outputFiles` has 1 item, our CSV, which we can then preview in Kestra itself
- Before putting this into our table, we must first create our Postgres database


## Set Up Postgres Database
- Kestra itself runs on a Postgres database, but we can spin up one using Docker
    ```YML
    # version: '3.8'  # obselete line

    services:
    postgres:
        image: postgres
        container_name: postgres_db
        environment:
        - POSTGRES_USER=kestra
        - POSTGRES_PASSWORD=k3str4
        - POSTGRES_DB=postgres-zoomcamp
        ports:
        - '5432:5432'
        volumes:
        - 'postgres-data:/var/lib/postgresql/data'

    volumes:
    postgres-data:
    ```
- After spinning it up via `docker-compose up -d`, we can connect this database to Kestra and start reading and writing data to it
- We do this via a Postgres `Queries` task in Kestra
    ```YML
    - id: green_create_table
      type: io.kestra.plugin.jdbc.postgresql.Queries
      # In the SQL, create a unique row ID generated via a 
      #   MD5 hash and note which file the row came from
      sql:
        CREATE TABLE IF NOT EXISTS {{ render(vars.table) }} (
            unique_row_id          text,
            filename               text,
            VendorID               text,
            lpep_pickup_datetime   timestamp,
            lpep_dropoff_datetime  timestamp,
            store_and_fwd_flag     text,
            RatecodeID             text,
            PULocationID           text,
            DOLocationID           text,
            passenger_count        integer,
            trip_distance          double precision,
            fare_amount            double precision,
            extra                  double precision,
            mta_tax                double precision,
            tip_amount             double precision,
            tolls_amount           double precision,
            ehail_fee              double precision,
            improvement_surcharge  double precision,
            total_amount           double precision,
            payment_type           integer,
            trip_type              integer,
            congestion_surcharge   double precision
            )
            ;
    ```
- The SQL also needs a `url` argument and the database information (`username`, `password`, etc.)
- Since we're going to end up making numerous queries, we will take advantage of **plugin defaults** to allows us to set the URL, username, and password for *all* Posgres tasks, without having to constantly copy-and-paste them
    - This is useful if using a different database with a different connection URL
    ```YML
    pluginDefaults:
    - type: io.kestra.plugin.jdbc.postgresql
        values:
        url: jdbc:postgresql://host.docker.internal:5432/postgres-zoomcamp
        username: kestra
        password: k3str4
    ```
- Next, we create a task to create the staging table, which will be used to add in our two additional columns (`unique_row_id` and `filename`) and to merge the data into our final table
- We will truncate this table each time we run the flow with a different month and store the new month's data
    ```YML
    - id: green_create_staging_table
      type: io.kestra.plugin.jdbc.postgresql.Queries
      # In the SQL, create a unique row ID generated via a 
      #   MD5 hash and note which file the row came from
      sql:
        CREATE TABLE IF NOT EXISTS {{ render(vars.staging_table) }} (
            unique_row_id          text,
            filename               text,
            VendorID               text,
            lpep_pickup_datetime   timestamp,
            lpep_dropoff_datetime  timestamp,
            store_and_fwd_flag     text,
            RatecodeID             text,
            PULocationID           text,
            DOLocationID           text,
            passenger_count        integer,
            trip_distance          double precision,
            fare_amount            double precision,
            extra                  double precision,
            mta_tax                double precision,
            tip_amount             double precision,
            tolls_amount           double precision,
            ehail_fee              double precision,
            improvement_surcharge  double precision,
            total_amount           double precision,
            payment_type           integer,
            trip_type              integer,
            congestion_surcharge   double precision
            )
            ;
    ```
- We can then see if the tables were created by using PGAdmin locally, or by accessing Postgres via `winpty pgcli -h localhost -p 5432 -u kestra -d postgres-zoomcamp` and executing `\dt` to view all the tables in the database
- Next, we will load the data into our database from the downloaded CSV files


## Load Data into the Table
- We need a new task for this
```YML
  - id: green_copy_into_staging_table
    type: io.kestra.plugin.jdbc.postgresql.CopyIn
    format: CSV
    from: '{{ render(vars.data) }}'
    table: '{{ render(vars.staging_table) }}'
    header: true
    columns: [VendorID, lpep_pickup_datetime, lpep_dropoff_datetime, store_and_fwd_flag,
      RatecodeID, PULocationID, DOLocationID, passenger_count, trip_distance, fare_amount,
      extra, mta_tax, tip_amount, tolls_amount, ehail_fee, improvement_surcharge,
      total_amount, payment_type, trip_type, congestion_surcharge]
```
- Once executed, you can connect back to Postgres and run `SELECT COUNT(*) FROM public.green_tripdata_staging`, and you should see a result of 630,918
- When running `SELECT * FROM public.green_tripdata_staging LIMIT 10` however, we notice that our first two columns are full of NULLs, since we haven't transformed the data yet to create those values
- We do this via an `UPDATE` SQL command in a new task
    ```YML
    - id: green_add_unique_id_and_filename
      type: io.kestra.plugin.jdbc.postgresql.Queries
      sql:
        UPDATE {{ render(vars.staging_table )}}
        SET
            unique_row_id = md5(
            COALESCE(CAST(VendorID AS text), '') ||
            COALESCE(CAST(lpep_pickup_datetime AS text), '') ||
            COALESCE(CAST(lpep_dropoff_datetime AS text), '') ||
            COALESCE(PULocationID, '') ||
            COALESCE(DOLocationID, '') ||
            COALESCE(CAST(fare_amount AS text), '') ||
            COALESCE(CAST(trip_distance AS text), '')
            ),
            filename = '{{ render(vars.file )}}'
    ```
- Now running `SELECT * FROM public.green_tripdata_staging LIMIT 10` will return data in those two columns
- However, note that we have now doubled the size of our table, since we did not truncate it before copying in the data again with these 2 new columns
- So, we need *another* task in order to clean this up


## Truncating Tables
- We create a new SQL-based task in order to truncate our table before loading data into it
    ```YML
    - id: green_truncate_staging_table
      type: io.kestra.plugin.jdbc.postgresql.Queries
      sql:
        TRUNCATE TABLE {{ render(vars.staging_table )}}
    ```
- Next, we must merge the staging table data into our final table in order to get a full dataset in the future


## Merging Data
- Once again, we need a new task
    ```YML
    - id: green_merge_data
      type: io.kestra.plugin.jdbc.postgresql.Queries
      sql:
        MERGE INTO {{ render(vars.table) }} AS final
        USING {{ render(vars.staging_table) }} AS staging
        ON final.unique_row_id = staging.unique_row_id
        WHEN NOT MATCHED THEN
            INSERT (
            unique_row_id, filename, VendorID, lpep_pickup_datetime, lpep_dropoff_datetime,
            store_and_fwd_flag, RatecodeID, PULocationID, DOLocationID, passenger_count,
            trip_distance, fare_amount, extra, mta_tax, tip_amount, tolls_amount, ehail_fee,
            improvement_surcharge, total_amount, payment_type, trip_type, congestion_surcharge
            )
            VALUES (
            staging.unique_row_id, staging.filename, staging.VendorID,
            staging.lpep_pickup_datetime, staging.lpep_dropoff_datetime,
            staging.store_and_fwd_flag, staging.RatecodeID, staging.PULocationID,
            staging.DOLocationID, staging.passenger_count, staging.trip_distance,
            staging.fare_amount, staging.extra, staging.mta_tax, staging.tip_amount,
            staging.tolls_amount, staging.ehail_fee, staging.improvement_surcharge,
            staging.total_amount, staging.payment_type, staging.trip_type,
            staging.congestion_surcharge
            )
        ;
    ```
- Then check that everything ran as planned by checking `SELECT * FROM public.green_tripdata LIMIT 10` and/or `SELECT COUNT(*) FROM public.green_tripdata`
- Next, we execute the flow again, but this time for the *February* 2019 green taxi data
    - Now, the staging table will be truncated of its January 2019 green taxi data, and then the February data will be merged into the final table, since it does not match anything currently in said table (which now, consists only of January data)
- We can check our results via `SELECT COUNT(*) FROM public.green_tripdata` and `SELECT COUNT(*) FROM public.green_tripdata_staging`


## Purging Output Files
- Since we don't want to run out of storage, we need to purge our execution output files
    ```YML
    - id: purge_files
      type: io.kestra.plugin.core.storage.PurgeCurrentExecutionFiles
      description: This will remove output files. If you'd like to explore Kestra outputs, disable this task.
      # disable: true
    ```


## Yellow Data
- Next, in order to load in *all* of our data, we need to copy various tasks and edit them to work for the yellow taxi dataset
- Such tasks are `green_merge_data`, `green_truncate_staging_table`, `green_add_unique_id_and_filename`, `green_copy_into_staging_table`, `green_create_staging_table`, and `green_create_table`
- Most of these tasks are quite similar whether it is yellow or green taxi data, but since the two datasets have different fields, that must be updated in most of these tasks
    ```YML
    - id: yellow_create_table
      type: io.kestra.plugin.jdbc.postgresql.Queries
      # In the SQL, create a unique row ID generated via a 
      #   MD5 hash and note which file the row came from
      sql:
        CREATE TABLE IF NOT EXISTS {{ render(vars.table) }} (
            unique_row_id          text,
            filename               text,
            VendorID               text,
            tpep_pickup_datetime   timestamp,
            tpep_dropoff_datetime  timestamp,
            passenger_count        integer,
            trip_distance          double precision,
            RatecodeID             text,
            store_and_fwd_flag     text,
            PULocationID           text,
            DOLocationID           text,
            payment_type           integer,
            fare_amount            double precision,
            extra                  double precision,
            mta_tax                double precision,
            tip_amount             double precision,
            tolls_amount           double precision,
            improvement_surcharge  double precision,
            total_amount           double precision,
            congestion_surcharge   double precision
            )
        ;

    - id: yellow_create_staging_table
      type: io.kestra.plugin.jdbc.postgresql.Queries
      # In the SQL, create a unique row ID generated via a 
      #   MD5 hash and note which file the row came from
      sql:
        CREATE TABLE IF NOT EXISTS {{ render(vars.staging_table) }} (
            unique_row_id          text,
            filename               text,
            VendorID               text,
            tpep_pickup_datetime   timestamp,
            tpep_dropoff_datetime  timestamp,
            passenger_count        integer,
            trip_distance          double precision,
            RatecodeID             text,
            store_and_fwd_flag     text,
            PULocationID           text,
            DOLocationID           text,
            payment_type           integer,
            fare_amount            double precision,
            extra                  double precision,
            mta_tax                double precision,
            tip_amount             double precision,
            tolls_amount           double precision,
            improvement_surcharge  double precision,
            total_amount           double precision,
            congestion_surcharge   double precision
            )
        ;

    - id: yellow_truncate_staging_table
      type: io.kestra.plugin.jdbc.postgresql.Queries
      sql:
        TRUNCATE TABLE {{ render(vars.staging_table )}};

    - id: yellow_copy_into_staging_table
      type: io.kestra.plugin.jdbc.postgresql.CopyIn
      format: CSV
      from: '{{ render(vars.data) }}'
      table: '{{ render(vars.staging_table) }}'
      header: true
      columns: [VendorID, tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count,
        trip_distance, RatecodeID, store_and_fwd_flag, PULocationID, DOLocationID,
        payment_type, fare_amount, extra, mta_tax, tip_amount, tolls_amount,
        improvement_surcharge, total_amount, congestion_surcharge]

    - id: yellow_add_unique_id_and_filename
      type: io.kestra.plugin.jdbc.postgresql.Queries
      sql:
        UPDATE {{ render(vars.staging_table )}}
        SET
            unique_row_id = md5(
            COALESCE(CAST(VendorID AS text), '') ||
            COALESCE(CAST(tpep_pickup_datetime AS text), '') ||
            COALESCE(CAST(tpep_dropoff_datetime AS text), '') ||
            COALESCE(PULocationID, '') ||
            COALESCE(DOLocationID, '') ||
            COALESCE(CAST(fare_amount AS text), '') ||
            COALESCE(CAST(trip_distance AS text), '')
            ),
            filename = '{{ render(vars.file )}}'
        ;

    - id: yellow_merge_data
      type: io.kestra.plugin.jdbc.postgresql.Queries
      sql:
        MERGE INTO {{ render(vars.table) }} AS final
        USING {{ render(vars.staging_table) }} AS staging
        ON final.unique_row_id = staging.unique_row_id
        
        WHEN NOT MATCHED THEN
            INSERT (
            unique_row_id, filename, VendorID, tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count, trip_distance, RatecodeID, store_and_fwd_flag, PULocationID,
            DOLocationID, payment_type, fare_amount, extra, mta_tax, tip_amount, tolls_amount,
            improvement_surcharge, total_amount, congestion_surcharge
            )
            VALUES (
            staging.unique_row_id, staging.filename, staging.VendorID,
            staging.tpep_pickup_datetime, staging.tpep_dropoff_datetime,
            staging.passenger_count, staging.trip_distance, staging.RatecodeID,
            staging.store_and_fwd_flag, staging.PULocationID, staging.DOLocationID,
            staging.payment_type, staging.fare_amount, staging.extra, staging.mta_tax,
            staging.tip_amount, staging.tolls_amount, staging.improvement_surcharge,
            staging.total_amount, staging.congestion_surcharge
            )
        ;
    ```


## Kestra IF Statements
- Next, we need to make sure our flow runs correctly depending on if we want the yellow or the green taxi dataset(s)
- We *could* add `runIf: '{{ inputs.taxi == ''green'' }}'` to our tasks, but we'd have to add this to *every* task
- Instead, we will use an IF statement, and group all the green taxi tasks together, and then all the yellow taxi tasks together
- We then must indent all of our green taxi tasks underneath the `then:` argument of the If statement task:
    ```YML
    - id: if_green
      type: io.kestra.plugin.core.flow.If
      condition: '{{ inputs.taxi == ''green'' }}'
      then:
        - id: green_create_table
          type: io.kestra.plugin.jdbc.postgresql.Queries
          # In the SQL, create a unique row ID generated via a 
          #   MD5 hash and note which file the row came from
          sql:
            CREATE TABLE IF NOT EXISTS {{ render(vars.table) }} (
                unique_row_id          text,
    # AND SO ON
    ```
- You should then be able to see all these tasks grouped together by color in the topology view
- Then we do the same for the yellow taxi data
    ```YML
    - id: if_yellow
      type: io.kestra.plugin.core.flow.If
      condition: '{{ inputs.taxi == ''yellow'' }}'
      then:
        - id: yellow_create_table
          type: io.kestra.plugin.jdbc.postgresql.Queries
          # In the SQL, create a unique row ID generated via a 
          #   MD5 hash and note which file the row came from
          sql:
            CREATE TABLE IF NOT EXISTS {{ render(vars.table) }} (
                unique_row_id          text,
    # AND SO ON
    ```
- Now, finally run the flow for January 2019 for the yellow taxi dataset to create two new tables, staging and final tables for the yellow taxi dataset, which you can check in Postgres via `\dt`
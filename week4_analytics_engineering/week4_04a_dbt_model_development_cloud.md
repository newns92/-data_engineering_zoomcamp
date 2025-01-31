# dbt Model Development

## Anatomy of a dbt Model
- dbt sits on top of our data warehouse (BigQuery, Postgres, etc.), which contains *raw* data
- Next, via dbt, we perform **development**, **testing** plus **documentation**, and finally **deployment** of **dbt models**
- Once deployed, we can use the transformed **datasets** as input to business intelligence (BI) tools, machine learning (ML) models, operational analytics, and more
- We will be using a ***modular* data modeling** approach in order to get our final **fact** and **dimension** tables
    - We start with the raw data tables we loaded (our **sources**)
    - We then create SQL scripts (our **models**) in order to:
        - Perform transformations (clean, de-duplicate, re-name, re-cast, etc.)
        - Implement business logic (creating fact and dimension tables, etc.)
        - Create **data marts** to serve finalized data to stakeholders
- Concerning dbt models:
    - They are SQL scripts, so they are written in `.sql` files
    - dbt will be running the Data Definition Language (DDL) and (Data Manipulation Language) DML *for us*, so all we need to do is write a good `SELECT` statement
        - But, we must *tell* dbt *how* to create that DDL and DML via **materilization** strategies defined at the top of the model `.sql` script
        - These are written in **Jinja**, a Pythonic templating language:
            ```Jinja
                {{
                    config(materialized = 'table')
                }}
            ```
        - There are several materialization strategies, such as:
            - **Tables**: *Physical* representations of data that are created and stored in the data warehouse
                - **NOTE**: Every time we run `dbt run`, the specified table in the command is *dropped* and *re*-created
            - **Views**: *Virtual* tables that materialize in the data warehouse and can be queried just like "regular" tables
                - A view *doesn't* store data like a table does, but instead it defines the logic that you need in order to fetch the underlying data
            - **Incremental**: A powerful physical materialization that allows for efficient updates to existing tables, reducing the need for full data refreshes
                - This strategy can be used to drop and re-create tables, *or* insert only *new* records into the table
            - **Ephemeral**: A temporary materialization that doesn't *really* materialize in physical storage, and exists only for the duration of a single `dbt run` call
                - It's model that can only live within *other* models
                - They're similar to CTE's in typical SQL
            - See more at: https://docs.getdbt.com/docs/build/materializations
        - These Jinja statements tell dbt how we want to compile our code in the data warehouse when we run the `dbt run` command

## Modular Data Modeling
- In our dbt project, we will define the *existing tables in our data warehouse* as dbt **sources** for our dbt models
    - See more at: https://docs.getdbt.com/docs/build/sources
    - The configuration for sources is defined in `schema.yml` files in the `models/` directory (or within subdirectories within the `models/` directory, say one named `core/` or `staging/` for core or staging models), wherein we tell dbt where to find the sources:
        ```YML
            sources:
            - name: staging
                database: ny_taxi  # i.e., the Postgres database or BigQuery dataset name
                schema: staging  # the Postgres or BigQuery schema

                tables:
                    - name: green_trip_data
                    - name: yellow_trip_data
        ```
        - This allows us to define the location *just once*, as well as define all of the tables in that location
        - This also allows us to abstract a little bit the complexity of where the source is physically stored
    - Sources are used with the source **macro** within the `FROM` clause in a model's `.sql` file
        - This function will resolve the name to the right schema, as well as build the dependencies automatically
            ```SQL
                from {{ source('staging', 'green_trip_data') }}
            ```
        - This will compile the SQL code and therefore build the resulting model to the database and schema defined in the respective `schema.yml` file
    - Source **freshness** can be defined and tested, as well
    - We can also do a lot of **testing** *within* sources
        - For example, we can define a threshold to test the freshness of our source and alert us if it is *not* fresh
            - This would be very helpful when we have a pipeline in production and we need to know that our data is not fresh *before the stakeholders are aware of this*
        - *By checking and testing the sources, we can ensure better data quality for our models*
- We can also define specific CSV files called **seeds** in our dbt project subdirectory `seeds/` to be used to load in data
    - See more at: https://docs.getdbt.com/docs/build/seeds
    - Seeds give us the benefit of *version control*
    - They are equivalent to a `COPY INTO` command
    - Seeds are recommended for *data that doesn't change frequently*
    - They can be ran via `dbt seed -s <file-name>`
    - They can also be referenced via the `ref` macro:
        ```SQL
            from {{ ref('taxi_zone_lookup') }}
        ```
        - Apart from seeds, `ref` can *also* reference the underlying tables and views that were building the data warehouse
            ```SQL
                from {{ ref('stg_green_trip_data') }}
            ```
            - We can run the same code in *any* environment, and it will resolve the correct schema for you
            - Dependencies are built automatically


## Defining a Source and Developing a First Model
- First, load in all the data that we'll need into BigQuery:
    - Run the `upload_all_data_parquet_gcs.py` script in this repo to get all the data into a GCS Bucket
    - Then, in BigQuery, create the external tables via:
        ```SQL
            CREATE OR REPLACE EXTERNAL TABLE `<project-id>.ny_taxi.external_yellow_trip_data`
            OPTIONS (
            format = 'PARQUET',
            uris = ['gs://<bucket-name>/data/yellow/yellow_tripdata_2019-*.parquet', 'gs://<bucket-name>/data/yellow/yellow_tripdata_2020-*.parquet']
            );

            CREATE OR REPLACE EXTERNAL TABLE `<project-id>.ny_taxi.external_green_trip_data`
            OPTIONS (
            format = 'PARQUET',
            uris = ['gs://<bucket-name>/data/green/green_tripdata_2019-*.parquet', 'gs://<bucket-name>/data/green/green_tripdata_2020-*.parquet']
            );

            CREATE OR REPLACE EXTERNAL TABLE `<project-id>.ny_taxi.external_fhv_trip_data`
            OPTIONS (
            format = 'PARQUET',
            uris = ['gs://<bucket-name>/data/fhv/fhv_tripdata_2019-*.parquet']
            );        
        ```
    - Then, in BigQuery, create *non*-external, *materialized* tables via
        ```SQL
            CREATE OR REPLACE TABLE `<project-id>.ny_taxi.yellow_trip_data`
            AS
            SELECT * FROM `<project-id>.ny_taxi.external_yellow_trip_data`;

            CREATE OR REPLACE TABLE `<project-id>.ny_taxi.green_trip_data`
            AS
            SELECT * FROM `<project-id>.ny_taxi.external_green_trip_data`;

            CREATE OR REPLACE TABLE `<project-id>.ny_taxi.fhv_trip_data`
            AS
            SELECT * FROM `<project-id>.ny_taxi.external_fhv_trip_data`;
        ```
    - Then, check the row counts via
        ```SQL
            SELECT COUNT(*) FROM `<project-id>.ny_taxi.fhv_trip_data`;
            --- 43,244,696

            SELECT COUNT(*) FROM `<project-id>.ny_taxi.yellow_trip_data`;
            --- 109,247,536

            SELECT COUNT(*) FROM `<project-id>.ny_taxi.green_trip_data`;
            --- 8,035,161
        ```        
- Now, back in the dbt Cloud IDE, in the `models/` directory, create a new directory called `staging/`
    - This is where we take in the raw data and apply some transforms if needed
- Then, create a `core/` subdirectory under the `models/` directory
    - This is where we'll create models to expose to a BI tool, to an ML model, to stakeholders, etc.
- In the `staging/` directory, create 2 files:
    1. A staging model, `stg_green_trip_data.sql`
        ```SQL
            -- Create views so we don't have the need to refresh constantly but still have the latest data loaded
            {{ config(materialized = 'view') }}

            /* {# SELECT * FROM {{ source(<'source-name-from-schema.yml>', '<table-name-from-schema.yml>') }} #} */
            select * from {{ source('staging', 'green_trip_data') }}
            limit 100        
        ```
    2. A `schema.yml` file
        - **First, create an environment variable in your system in a command prompt via `export DBT_GCP_PROJECT_ID='<your-gcp-project-id>'`**
            - Can check this via `echo $DBT_GCP_PROJECT_ID`
        - Then, use the `env_var()` dbt macro/function to incorporate your Google Cloud Platform project ID in this YML file instead of hard-coding it
            - See more at: https://docs.getdbt.com/reference/dbt-jinja-functions/env_var
        ```YML
            version: 2

            sources:
            - name: staging
                database: "{{ env_var('DBT_GCP_PROJECT_ID') }}"  # i.e., the dataset (Project ID) in BigQuery
                schema: ny_taxi  # the dataset itself

                tables:
                - name: green_trip_data
                - name: yellow_trip_data            
        ```
- In the dbt Cloud IDE terminal (at the bottom of the page), run:
    1. `dbt build`
        - See: https://docs.getdbt.com/reference/commands/build
        - This will grab *all* models *and* tests, seeds, and snapshots in a project and run them all
    2. `dbt run -m stg_green_trip_data`
        - See: https://docs.getdbt.com/reference/commands/run
        - `dbt run` will execute compiled SQL model files against the current `target` database defined in the `profiles.yml` file
        - The `--m` flag is an alias for `--models`, wherein afterwards we specify the model to execute
- Then, change the `SELECT` statement to run with the new column definitions to make all column names consistent
    - ***NOTE***: You can also run `dbt run --select stg_green_trip_data`, which is equivalent to `dbt run -m stg_green_trip_data`
- You should then see the new view under `ny_taxi_dev` in BigQuery (since *that's what we named the dataset to be when we defined the project*)
- You can also see compiled SQL code in the `target/compiled/` directory in the dbt Cloud IDE

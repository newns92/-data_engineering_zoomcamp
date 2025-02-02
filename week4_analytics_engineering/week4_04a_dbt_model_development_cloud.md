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
        - Create **data marts** to serve aggregated and finalized data to stakeholders in some form
- Concerning dbt models themselves:
    - They are SQL scripts, so they are written in `.sql` files
    - dbt will be running the Data Definition Language (DDL) and (Data Manipulation Language) DML *for us*, so all we need to do is write a good `SELECT` statement
        - But, we must *tell* dbt *how* to create that DDL and DML via **materilization** strategies defined at the top of the model `.sql` script
        - These are written in **Jinja**, a Pythonic templating language:
            ```SQL
                {{
                    config(materialized = 'table')
                }}
            ```
            - This materializes as:
                ```SQL
                CREATE TABLE myschema.my_model AS (
                    ........
                )
                ```
        - There are several materialization strategies, such as:
            - **Ephemeral**: A temporary materialization that doesn't *really* materialize in physical storage, and exists only for the duration of a single `dbt run` call
                - It's model that can only live within *other* models
                - They're similar to CTE's in typical SQL            
            - **Views**: *Virtual* tables that materialize in the data warehouse and can be queried just like "regular" tables
                - A view *doesn't* store data like a table does, but instead it defines the logic that you need in order to fetch the underlying data            
            - **Tables**: *Physical* representations of data that are created and stored in the data warehouse
                - **NOTE**: Every time we run `dbt run`, the specified table in the command is *dropped* and *re*-created
            - **Incremental**: A powerful (and arguable, advanced) physical materialization that allows for efficient updates to existing tables, reducing the need for full data refreshes
                - This strategy can be used to drop and re-create tables, *or* insert only *new* records into the table
            - See more at: https://docs.getdbt.com/docs/build/materializations
        - These Jinja statements tell dbt how we want to compile our code in the data warehouse when we run the `dbt run` command

## Modular Data Modeling: The FROM Clause of a dbt Model
- In our dbt project, we will define the *existing tables in our data warehouse* and *any other external data, such as files*, as dbt **sources** for our dbt models
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
        - This allows us to define the location *just once*, as well as define all of the tables within that location
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
            - This would be very helpful when we have a pipeline in production and we need to know that our data is *not* fresh *before the stakeholders are aware of this*
        - *By checking and testing the sources, we can ensure better data quality for our models*
- We can also define specific CSV files called **seeds** in our dbt project subdirectory `seeds/` to be used to load in data
    - See more at: https://docs.getdbt.com/docs/build/seeds
    - Seeds give us the benefit of *version control*, kept in the repository that contains the rest of your dbt project
    - They are equivalent to a `COPY INTO` command
    - Seeds are recommended for *data that doesn't change frequently*
    - They can be ran via `dbt seed -s <file-name>`
    - They too can be documented, tested, and ran alongside the entire dbt project
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
    - Manually upload all the parquet files to your GCS bucket, or run a script (like the `upload_all_data_parquet_gcs.py` script in this repo) to get all the data into the cloud, available to BigQuery
    - Then, in BigQuery, create the external tables via:
        ```SQL
            CREATE OR REPLACE EXTERNAL TABLE `<project-id>.<dataset-name>.external_yellow_trip_data`
            OPTIONS (
            format = 'PARQUET',
            uris = ['gs://<bucket-name>/data/yellow/yellow_tripdata_2019-*.parquet', 'gs://<bucket-name>/data/yellow/yellow_tripdata_2020-*.parquet']
            );

            CREATE OR REPLACE EXTERNAL TABLE `<project-id>.<dataset-name>.external_green_trip_data`
            OPTIONS (
            format = 'PARQUET',
            uris = ['gs://<bucket-name>/data/green/green_tripdata_2019-*.parquet', 'gs://<bucket-name>/data/green/green_tripdata_2020-*.parquet']
            );

            CREATE OR REPLACE EXTERNAL TABLE `<project-id>.<dataset-name>.external_fhv_trip_data`
            OPTIONS (
            format = 'PARQUET',
            uris = ['gs://<bucket-name>/data/fhv/fhv_tripdata_2019-*.parquet']
            );        
        ```
    - Then, in BigQuery, create *non*-external, *materialized* tables via
        ```SQL
            CREATE OR REPLACE TABLE `<project-id>.<dataset-name>.yellow_trip_data`
            AS
            SELECT * FROM `<project-id>.<dataset-name>.external_yellow_trip_data`;

            CREATE OR REPLACE TABLE `<project-id>.<dataset-name>.green_trip_data`
            AS
            SELECT * FROM `<project-id>.<dataset-name>.external_green_trip_data`;

            CREATE OR REPLACE TABLE `<project-id>.<dataset-name>.fhv_trip_data`
            AS
            SELECT * FROM `<project-id>.<dataset-name>.external_fhv_trip_data`;
        ```
    - Then, check the row counts in the details portion of the UI or via SQL:
        ```SQL
            SELECT COUNT(*) FROM `<project-id>.<dataset-name>.fhv_trip_data`;
            --- 43,244,696

            SELECT COUNT(*) FROM `<project-id>.<dataset-name>.yellow_trip_data`;
            --- 109,047,518

            SELECT COUNT(*) FROM `<project-id>.<dataset-name>.green_trip_data`;
            --- 7,778,101
        ```        
- Now, back in the dbt Cloud IDE, in the `models/` directory, create a new directory called `staging/`
    - This is where we will take in raw data (and apply some transforms if needed)
- Then, create a `core/` subdirectory under the same `models/` directory
    - This is where we'll create models to expose to a BI tool, to an ML model, to stakeholders, etc.
- In the `staging/` subdirectory, create 2 files:
    1. A `schema.yml` file (You can also get a step ahead and create another (but blank for now) `schema.yml` in the `core/` subdirectory)        
        - **First, make sure to create an environment variable in dbt Cloud if you have not done so already**
            - When using dbt Cloud, you *must* adhere to the naming conventions for environment variables: they *must* be prefixed with `DBT_` 
            - Environment variables keys are *uppercased* and *case-sensitive*
            - When referencing something like `{{env_var('DBT_KEY')}}` in a dbt project's code, the key must match *exactly* the variable defined in dbt Cloud's UI        
                - ***NOTE***: `env_var()` also accepts a second, optional argument a default value                
            - To create the environment variables, on the left-hand side of the dbt Cloud UI, click "Deploy", and then "Environments"
            - Click the "Environment variables" tab
            - Then, enter your key and value (both "Project default" and "Development" values) pairs for `DBT_GCP_PROJECT_ID` and `DBT_BIGQUERY_SCHEMA` environment variables
            - See more at: https://docs.getdbt.com/reference/dbt-jinja-functions/env_var
            - Then, head back to the dbt Cloud IDE and restart it to set the new (or updated) environment variables
            - You can click the `</> Compile` button at the bottom of the dbt Cloud IDE when you have `stg_green_trip_data.sql` open to see if the environment variables are working
        - Example code:
            ```YML
                version: 2

                sources:
                    - name: staging
                      database: "{{ env_var('DBT_GCP_PROJECT_ID') }}"  # i.e., the "dataset" (Project ID) in BigQuery
                      schema: "{{ env_var('DBT_BIGQUERY_SCHEMA', 'de_zoomcamp') }}"  # the dataset itself

                      tables:
                        - name: green_trip_data
                        - name: yellow_trip_data            
            ```    
    2. A staging model, `stg_green_trip_data.sql`
        - Basic starter code for testing:
            ```SQL
                -- Create a view so we don't have the need to refresh constantly but still have the latest data loaded
                {{ config(materialized = 'view') }}

                /* {# SELECT * FROM {{ source(<'source-name-from-schema.yml>', '<table-name-from-schema.yml>') }} #} */
                SELECT * FROM {{ source('staging', 'green_trip_data') }}
                LIMIT 100
            ```
- In the dbt Cloud IDE terminal (at the bottom of the page), run either:
    - A. `dbt build`
        - See: https://docs.getdbt.com/reference/commands/build
        - This will grab *all* models *and* tests, seeds, and snapshots in a project and run them all
            - The models will be processed according to their lineage and dependencies
            - Tests will be executed as follows:
                1. Unit tests are run on a SQL model
                2. The model is materialized
                3. Data tests are run on the model
            - This saves on warehouse spend as the model will only be materialized if the unit tests pass successfully.
    - B. `dbt run -m stg_green_trip_data`
        - See: https://docs.getdbt.com/reference/commands/run
        - `dbt run` will execute specified, compiled SQL model files against the current `target` database defined in the `profiles.yml` file
        - The `--m` flag is an alias for `--models`, wherein afterwards we specify the model to execute
    - See the differences between `build` and `run` here: https://www.castordoc.com/blog/dbt-build-vs-dbt-run
- Then, change the `SELECT` statement to run with the new column definitions to make all column names consistent
    - ***NOTE***: You can also run `dbt run --select stg_green_trip_data`, which is equivalent to `dbt run -m stg_green_trip_data`
- *\***NOTE**: If trying to run "Preview" in the dbt Cloud IDE, remove any `LIMIT` statement at the end of the query, as dbt Cloud will add a `LIMIT 500` automatically, which will break the code*
- You should then see the new view under your dataset name (*that you specified in your project's development credentials*) in BigQuery (since *that's what we named the dataset to be when we defined the project*)
- You can also see compiled SQL code in the `target/compiled/` directory in the dbt Cloud IDE


## Macros
- You can think of dbt **macros** as *functions* that are written in Jinja (again, a Pythonic templating language) and SQL (They are written in `.sql` files)
- The goal is to turn abstract snippets of SQL into these *reusable* macros
- dbt has many built-in macros (`config()`, `source()`, `env_var()`, etc.), but we can also *define our own*
- Macros return code, and are in the style of: 
    ```Jinja
        {% macro <macro-name>(<parameter(s)>) -%}   
            # some code
        {%- end macro %}
    ```
- They are helpful if we want to maintain (i.e. re-use) the same type of transformation in several different models (Do Not Repeat Yourself principle)
- They can use **control structures** (e.g., IF statements and FOR loops in SQL)
- They can also use environment variables in a dbt project for production deployments
- They operate on the results on one query to generate *another* query
    - In other words, their "output" is generated code
- See more at https://docs.getdbt.com/docs/build/jinja-macros
- In our dbt project:
    - Create the `get_payment_type_description` macro under the `macros/` subdirectory of the project in a `get_payment_type_description.sql` file:
        ```Jinja
            {#
                This macro returns the description of the payment_type 
            #}

            {% macro get_payment_type_description(payment_type) -%}

                case {{ payment_type }}
                    when 1 then 'Credit card'
                    when 2 then 'Cash'
                    when 3 then 'No charge'
                    when 4 then 'Dispute'
                    when 5 then 'Unknown'
                    when 6 then 'Voided trip'
                    else 'EMPTY'
                end

            {%- endmacro %}
        ```
    - We then use it in our `stg_green_trip_data.sql` model file, which we can then run again via `dbt run --select stg_green_trip_data`

        ```Jinja
            -- Create a view so we don't have the need to refresh constantly but still have the latest data loaded
            {{ config(materialized = 'view') }}

            WITH source AS (
                /* {# SELECT * FROM {{ source(<'source-name-from-schema.yml>', '<table-name-from-schema.yml>') }} #} */
                SELECT * FROM {{ source('staging', 'green_trip_data') }}
                LIMIT 100
            )
            ,

            renamed AS (
                SELECT
                    vendor_id,
                    lpep_pickup_datetime,
                    lpep_dropoff_datetime,
                    store_and_fwd_flag,
                    rate_code_id,
                    pu_location_id,
                    do_location_id,
                    passenger_count,
                    trip_distance,
                    fare_amount,
                    extra,
                    mta_tax,
                    tip_amount,
                    tolls_amount,
                    ehail_fee,
                    improvement_surcharge,
                    total_amount,
                    payment_type,
                    {{ get_payment_type_description('payment_type') }} as payment_type_description,  {# macro #}
                    trip_type,
                    congestion_surcharge
                FROM source
            )

            SELECT
                *
            FROM renamed
        ```
        - We can click "Compile" at the bottom of the page in the dbt Cloud IDE to see the compiled result without running it
    - We will then see the updated compiled code in the `target/compiled/` directory and the updated staging table in BigQuery's dataset that you specified (as a schema)


## Packages
- You can think of dbt **packages** like libraries in other programming languages
    - You can call them similar to library functions: `{{ <dbt-package>.<macro-name>(<parameter(s)>) }}`
- Packages are "downloaded" via the `packages.yml` file, *which you create*, in the main directory of the project, and then imported via the `dbt deps` command
- They are basically standalone dbt projects, with models and macros that tackle specific problems
- By adding a package to your own project, said package's models and macros become a part of *your* dbt project
- You can see a list of useful packages at https://hub.getdbt.com/
- A good thing to note is that dbt will update and change the compiled code depending on your connection adapter (code might be different for BigQuery than for Postgres), as it abstracts away that complexity for the end user
- We will be importing the package `dbt_utils` from dbt Labs
    - First, we create the `packages.yml` file in the same directory level as `dbt_project.yml`:
        ```YML
            packages:
            - package: dbt-labs/dbt_utils
            version: 1.3.0
        ```
    - Then we run `dbt deps` in the terminal at the bottom of the dbt Cloud IDE to install the packages
    - We can then view installed packages in the `dbt_packages/` subdirectory of the project, and look inside its *own* `macros/` subdirectory to see all of its macros
    - We will then create a **surrogate key** via `{{ dbt_utils.generate_surrogate_key(['vendor_id', 'lpep_pickup_datetime']) }} as trip_id,` in our staging table model
    - Run the model again via `dbt run --select stg_green_trip_data`, and again see the updated compiled code in the `target/compiled/` directory and the updated staging table your BigQuery schema


## Variables
- dbt **variables** are the same as any other programming language: useful for defining values that should be used *across* a project
- With a macro, dbt allows us to provide data *via* variables to models for translation during compilation
- To use a variables, use the `{{ var('...')}}` function/macro
    ```Jinja
        -- Use dbt Variable to LIMIT dataset when testing
        -- `dbt build --select <model_name> --vars '{'is_test_run': 'false'}'`
        {% if var('is_test_run', default=true) %}

            LIMIT 100

        {% endif %}
    ```
    - *Add the above to the end of the `stg_green_trip_data.sql` model*
- We can do this in the dbt Cloud CLI (where we can change the value on-the-fly) via:
    ```bash
        dbt build -select <model-name> --vars '{'is_test_run': 'false'}'
    ```

- We can also define variables in the `dbt_project.yml` file:
    ```YML
        vars:
            payment_type_values = [1, 2, 3, 4, 5, 6]
    ```
- We can run our model and change the value of `is_test_run` using the command `dbt run --select stg_green_trip_data.sql --var 'is_test_run: false'` and you should *NOT* see `LIMIT 100` in the compiled code
- Just running `dbt run --select stg_green_trip_data` should give the default value of `true` and you should see `limit 100` in the compiled code
- ***We can then repeat everything above, with some small code changes, for a `stg_yellow_trip_data` model***
    - Commands:
        - `dbt run --select stg_green_trip_data --vars '{'is_test_run': 'false'}'`
        - `dbt run --select stg_yellow_trip_data --vars '{'is_test_run': 'false'}'`


## Seeds
- These are CSV files that we can have in our repo and then run to use as tables via a `ref` macro
- These are meant to be used for *smaller* files that contain **data that won't change often**
- ***NOTE***: They cannot be *directly* loaded in the Cloud UI
    - If done locally, you can just copy the CSV to the `seeds/` subdirectory of the project
    - In *dbt Cloud*, you can add the file to the GitHub repo and then pull it into the dbt Cloud UI
        - *Or you can just create the CSV in the Cloud UI and paste in the exact contents*
- Once the CSV is loaded into the repo (or the Cloud UI), run `dbt seed`, which will create the specified table in the data warehouse (BigQuery) and will define, for each of the fields, the data type that it corresponds to
- *However, we can also define the data types ourselves in the `dbt_project.yml` file*
    - Here's an example of explicilty defining one column's data type, leaving the rest as defaults:
        ```YML
            seeds:
                taxi_data:
                    taxi_zone_lookup:
                        +column_types:
                            location_id: numeric
        ```
    - Run `dbt seed` again, you should see the updated table in BigQuery
- Now let's say we want to change some value in our data, like changing "EWR" to "NEWR"
    - `dbt seed` will by default *append* to things we've already created
    - So, to avoid this, you instead add a CLI argument and run `dbt seed --full-refresh` to *drop* and *recreate* the table
- Now, we can create a **dimension model** based on this seed
    - Under `models/core/`, create a file `dim_zones.sql`
    - Here, we will first define the configiguration as a materialized *table* rather than a view, like we have been doing thus far in our staging models
        - Ideally we want everything in `models/core/` to be a *table*, since this is what's exposed to BI tools and/or to stakeholders
- After adding the SQL to create such a dimension table, and before runnning this model, create a *second* new model called `fact_trips.sql`
    - In this model, we'll take both the staging yellow and staging green data and `UNION` them into a *table*
        - This will allow our queries to be more efficient and performant, since this will have a lot more data than our previous tables
        - The closer to the BI layer that we get, the more we want performant queries so that things run faster for the stakeholders
- Once `fact_trips.sql` is complete, we can see the lineage graph in the dbt Cloud IDE and we should see our staging sources creatin two staging models, our seed creating a dimension model, and those three models creating a fact model
    - dbt automatically identifies all of these dependencies
    - We can tell dbt to run all model but *also* specify to run all of its parent models
- Now, we can run `dbt run` which will run all of our models, *but not the seed*
    - In order to run the seed as well, run `dbt build` to build everything that we have, *along with running some tests*
    - Say we just want to run `fact_trips.sql`, we'd run `dbt build --select fact_trips`
        - *But to run everything that `fact_trips.sql` depends on first*, we can run `dbt build --select +fact_trips`
        - Command:
            - `dbt build --select +fact_trips+ --vars '{'is_test_run': 'false'}'`
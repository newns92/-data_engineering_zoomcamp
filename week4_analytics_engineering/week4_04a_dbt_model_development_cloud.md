# dbt Model Development

## Anatomy of a dbt Model
- dbt sits on top of our data warehouse (BigQuery, Postgres, etc.), which contains *raw* data
- Next, we perform **development**, **testing** & **documentation**, and finally **deployment** of dbt models
- Once deployed, we can use the transformed **datasets** as input to BI tools, ML models, operational analytics, and more
- We will be using a **modular data modeling** approach in order to get our final fact and dimension tables
    - We start with the raw data tables we loaded (our **sources**)
    - We then create SQL scripts (our **models**) in order to:
        - Perform transformations (clean, de-duplicate, re-name, re-cast)
        - Implement business logic (creating fact and dimension tables)
        - Create **data marts** to serve finalized data to stakeholders
- Concerning dbt models:
    - They are SQL scripts, so they are written in `.sql` files
    - dbt will be doing the DDL and DML *for us*, so all we need to do is write a good `SELECT` statement
        - But, we must *tell* dbt how to create that DDL and DML via **materilization** strategies defined at the top of the model script
        - These are written in **Jinja**, a Pythonic templating language:
            ```Jinja
                {{
                    config(materialized = 'table')
                }}
            ```
        - There are several materialization strategies, such as:
            - **Tables**: Physical representations of data that are created and stored in the data warehouse
                - Every time we run `dbt run`, the table is *dropped* and re-created
            - **Views**: *Virtual* tables that materialize in the data warehouse and can be queries like "regular" tables
                - A view doesn’t store data, like a table does, but it defines the logic that you need to fetch the underlying data.
            - **Incremental**: A powerful physical materialization that allows for efficient updates to existing tables, reducing the need for full data refreshes
                - This strategy can be used to drop and re-create tables, *or* insert only *new* records into the table
            - **Ephemeral**: A temporary materialization that doesn't *really* materialize in physical storage and exists only for the duration of a single `dbt run` call
                - It's model that can only live within *other* models
                - They're similar to CTE's in SQL
            - https://docs.getdbt.com/docs/build/materializations
        - These statements tell dbt how we want to compile our code in the data warehouse when we run `dbt run`

## Modular Data Modeling
- In our dbt project, we will define the existing tables in our data warehouse as dbt **sources** for our models
    - https://docs.getdbt.com/docs/build/sources
    - The configuration for sources is defined in the `schema.yml` files in the `models/` directory, wherein we tell dbt where to find the sources
        ```YML
            sources:
            - name: staging
                database: ny_taxi  # i.e., the Postgres or BigQuery database
                schema: staging  # the schema

                tables:
                    - name: green_trip_data
                    - name: yellow_trip_data
        ```
        - This allows us to define the location *just once*, as well as all the tables in that location
        - This also allows us to abstract a little bit the complexity of where the source is physically stored
    - Sources are used with the source **macro** within the `FROM` clause that will resolve the name to the right schema, plus build the dependencies automatically
        ```SQL
            from {{ source('staging', 'green_trip_data') }}
        ```
        - This will compile the SQL code and therefore the resulting model to the database and schema defined in the `schema.yml` file
    - Source **freshness** can be defined and tested
    - We can also do a lot of **testing** within sources
        - For example, we can define a threshold to test the freshness of our source and alert us if it is not fresh
            - This would be very helpful when we have a pipeline in production and we need to know that our data is not fresh *before the stakeholders are aware of this*
        - *By checking and testing the sources, we can ensure better data quality for our models*
- We can also define specific CSV files in our dbt project subdirectory `seeds/` to be used to load in data, and these are called **seeds**
    - https://docs.getdbt.com/docs/build/seeds
    - This gives us the benefit of *version control*
    - It is equivalent to a `COPY INYO` command
    - It's recommended for *data that doesn't change frequently*
    - They can be ran via `dbt seed -s <file-name>`
    - They can be referenced via the `ref` macro:
        ```SQL
            from {{ ref('taxi_zone_lookup') }}
        ```
        - `ref` can also reference the underlying tables and views that were building the data warehouse
            ```SQL
                from {{ ref('stg_green_trip_data') }}
            ```
            - We can run the same code in *any* environment, and it will resolve the correct schema for you
            - Dependencies are built automatically


## Defining a Source and Developing a First Model
- First, load in all the data that we'll need into BigQuery:
    - Run the `upload_all_data_parquet.py` to get all the data into a GCS Bucket
    - Then, in BigQuery, create the external tables via:
        ```SQL
            CREATE OR REPLACE EXTERNAL TABLE `<project-id>.ny_trips.external_yellow_trip_data`
            OPTIONS (
            format = 'PARQUET',
            uris = ['gs://<bucket-name>/data/yellow/yellow_tripdata_2019-*.parquet', 'gs://<bucket-name>/data/yellow/yellow_tripdata_2020-*.parquet']
            );

            CREATE OR REPLACE EXTERNAL TABLE `<project-id>.ny_trips.external_green_trip_data`
            OPTIONS (
            format = 'PARQUET',
            uris = ['gs://<bucket-name>/data/green/green_tripdata_2019-*.parquet', 'gs://<bucket-name>/data/green/green_tripdata_20209-*.parquet']
            );

            CREATE OR REPLACE EXTERNAL TABLE `<project-id>.ny_trips.external_fhv_trip_data`
            OPTIONS (
            format = 'PARQUET',
            uris = ['gs://<bucket-name>/data/fhv/fhv_tripdata_2019-*.parquet']
            );        
        ```
    - Then, in BigQuery, create *non*-external, materialized tables via
        ```SQL
            CREATE OR REPLACE TABLE `<project-id>.ny_trips.yellow_trip_data`
            AS
            SELECT * FROM `<project-id>.ny_trips.external_yellow_trip_data`;

            CREATE OR REPLACE TABLE `<project-id>.ny_trips.green_trip_data`
            AS
            SELECT * FROM `<project-id>.ny_trips.external_green_trip_data`;

            CREATE OR REPLACE TABLE `<project-id>.ny_trips.fhv_trip_data`
            AS
            SELECT * FROM `<project-id>.ny_trips.external_fhv_trip_data`;
        ```
    - Then, check the row counts via
        ```SQL
            SELECT COUNT(*) FROM `<project-id>.ny_trips.fhv_trip_data`;
            --- 43,244,696

            SELECT COUNT(*) FROM `<project-id>.ny_trips.yellow_trip_data`;
            --- 109,047,518

            SELECT COUNT(*) FROM `<project-id>.ny_trips.green_trip_data`;
            --- 7,778,101
        ```        
- Now, back in the dbt Cloud IDE, in the `models/` directory, create a new directory called `staging/`
    - This is where we take in the raw data and apply some transforms if needed
- Then, create a `core/` subdirectory under the `models/` directory
    - This is where we'll create models to expose to a BI tool, to stakeholders, etc.
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
        ```YML
            version: 2

            sources:
            - name: staging
                database: <project-id>  # i.e., the dataset (Project ID) in BigQuery
                schema: ny_trips  # the dataset itself

                tables:
                - name: green_trip_data
                - name: yellow_trip_data            
        ```
- In the dbt Cloud IDE terminal (at the bottom of the page), run:
    1. `dbt build`
        - https://docs.getdbt.com/reference/commands/build
        - This will grab *all* models *and* tests, seeds, and snapshots in a project and run them all
    2. `dbt run -m stg_green_trip_data`
        - https://docs.getdbt.com/reference/commands/run
        - `dbt run` will executes compiled sql model files against the current `target` database defined in the `profiles.yml` file
- Then, change the `SELECT` statement to run with the new column definitions to make all column names consistent
    - You can also run `dbt run --select stg_green_trip_data`, which is equivalent to `dbt run -m stg_green_trip_data`
- You should then see the new view under `ny_trips_dev` in BigQuery (since *that's what we named the dataset to be when we defined the project*)
- You can also see compiled SQL code in the `target/compiled/` directory

 
## Macros
- You can think of these as *functions* that are written in Jinja (a Pythonic templating language) and SQL
- The goal is to turn abstract snippets of SQL into these *reusable* macros
- dbt has many built-in macros (`config()`, `source()`), but we can also define our own
- Macros return code, and are in the style 
    ```Jinja
        {% macro <macro-name>(<parameter(s)>) -%}   
            # some code
        {%- end macro %}
    ```
- They are helpful if we want to maintain (re-use) the same type of transformation in several different models
- They can use **control structures** (e.g., IF statements and FOR loops in SQL)
- They can use environment variables in a dbt project for production deployments
- They operate on the results on one query to generate another query
- See more at https://docs.getdbt.com/docs/build/jinja-macros
- In our project:
    - We create the `get_payment_type_description` macro under the `macros/` subdirectory of the project in a `get_payment_type_description.sql` file:
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
                end

            {%- endmacro %}
        ```
    - We then use it in our `stg_green_trip_data.sql` model file, which we can then run again via `dbt run --select stg_green_trip_data`
        ```Jinja
            {{ get_payment_type_description('payment_type') }} as payment_type_description,  {# macro #}
        ```
        - We can also click "Compile" at the bottom of the page in the dbt Cloud IDE to see the compiled result without running it
    - We will then see the updated compiled code in the `target/compiled/` directory and the updated staging table in BigQuery's `ny_trips_dev` schema


## Packages
- Think of these like libraries in other programming languages
    - You can call them similar to library functions: `{{ <dbt-package>.<macro-name>(<parameter(s)>) }}`
- Packages are "downloaded" via the `packages.yml` file, *which you create*, in the main directory of the project, and then imported via the `dbt deps` command
- They are basically standalone dbt projects, with models and macros that tackle specific problems
- By adding a package to your own project, such a package's models and macros become a part of *your* project
- You can see a list of useful packages at https://hub.getdbt.com/
- A good thing to note is that dbt will update and change the compiled code depending on your connection adapter (code might be different for BigQuery than for Postgres), as it abstracts away that complexity for the end user
- We are importing the package `dbt_utils` from dbt labs
    - First, we create the `packages.yml` file in the same directory level as `dbt_project.yml`:
        ```YML
            packages:
            - package: dbt-labs/dbt_utils
                version: 1.1.1
        ```
    - Then we run `dbt deps` in the terminal at the bottom of the dbt Cloud IDE to install the packages
    - We can then view installed packages in the `dbt_packages/` subdirectory of the project, and see its *own* `macros/` subdirectory to see all of its macros
    - We will then create a **surrogate key** via `{{ dbt_utils.surrogate_key(['vendor_id', 'lpep_pickup_datetime']) }} as trip_id,` in our staging table model
    - Run the model again via `dbt run --select stg_green_trip_data`, and again see the updated compiled code in the `target/compiled/` directory and the updated staging table in BigQuery's `ny_trips_dev` schema
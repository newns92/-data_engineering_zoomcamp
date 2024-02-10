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
- In the Cloud IDE, in the `models/` directory, create a new directory called `staging/`
    - This is where we take in the raw data and apply some transforms if needed
- Then, create a `core/` subdirectory under the `models` directory
    - This is where we'll create models to expose to a BI tool, to stakeholders, etc.
- In the 

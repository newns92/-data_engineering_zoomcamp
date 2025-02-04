# dbt Testing and Documentation


## Testing
- dbt **Tests** are *assumptions* that we make about our data
- Tests in dbt are essentially a `SELECT` statement in a SQL query that selects the data that we "don't want"
    - i.e., Our assumptions get compiled to SQL that *returns the amount of failing records*
- Child models will *not* be built if a test fails (for the most part)
    - Those tests with `severity: [severity-option]` will ask if dbt should keep running if it fails or not, or should it stop entirely
        - `severity: warn` means everything will run but it will give warnings at the end
        - `severity: never` means it will stop immediately    
- Tests are defined on a per-column-basis in `schema.yml` files
    - For example:
        ```YML
            columns:
                - name: trip_id
                description: Primary key for this table, generated with a concatenation of vendor_id and pickup_datetime
                tests:
                    - unique:
                        severity: warn
                    - not_null:
                        severity: warn    
        ```
- dbt provides 4 basic, built-in tests to check if the column values are:
    - Unique
    - Not NULL
    - Accepted values:
        ```YML
            - name: payment_type
            description: >
              A numeric code signifying how the passenger paid for the trip.
            tests: 
              - accepted_values:
                  # Test against variable in dbt_project.yml
                  values: "{{ var('payment_type_values') }}"
                  severity: warn
                  quote: false        
        ```
    - A foreign key to another table ("relationships"):
        ```YML
            - name: pickup_location_id 
            description: location_id where the meter was engaged.
            # Check if this field is located in the zone lookup table
            tests:
              - relationships:
                  to: ref('taxi_zone_lookup')
                  field: location_id        
            - name: dropoff_location_id 
            description: location_id where the meter was disengaged.
            # Check if this field is located in the zone lookup table
            tests:
              - relationships:
                  to: ref('taxi_zone_lookup')
                  field: location_id
        ```
- You can also create your own, custom tests via queries
- To start, create the `dm_monthly_zone_revenue.sql` file in `models/core`
    ```SQL
        {{
            config(
                materialized='table'
            )
        }}

        WITH trips_data AS (
            SELECT
                *
            FROM {{ ref('fact_trips') }}
        )

        SELECT
            -- Revenue grouping 
            pickup_zone as revenue_zone,
            {{ dbt.date_trunc("month", "pickup_datetime") }} as revenue_month, 

            service_type, 

            -- Revenue calculation 
            SUM(fare_amount) as revenue_monthly_fare,
            SUM(extra) as revenue_monthly_extra,
            SUM(mta_tax) as revenue_monthly_mta_tax,
            SUM(tip_amount) as revenue_monthly_tip_amount,
            SUM(tolls_amount) as revenue_monthly_tolls_amount,
            SUM(ehail_fee) as revenue_monthly_ehail_fee,
            SUM(improvement_surcharge) as revenue_monthly_improvement_surcharge,
            SUM(congestion_surcharge) as revenue_monthly_congestion_surcharge,
            SUM(total_amount) as revenue_monthly_total_amount,

            -- Additional calculations
            COUNT(trip_id) as total_monthly_trips,
            AVG(passenger_count) as avg_monthly_passenger_count,
            AVG(trip_distance) as avg_monthly_trip_distance

        FROM trips_data
        GROUP BY -- 1, 2, 3
            revenue_zone,
            revenue_month,
            service_type
    ```
    - This is a **data mart** based off of our fact table that contains a bunch of revenue information and aggregations, ready to be exposed to stakeholders 
    - NOTE: This also contains a **cross-database macro**, `dbt.date_trunc()`:
        - https://docs.getdbt.com/reference/dbt-jinja-functions/cross-database-macros
        - Basically, they use the flavor of underlying SQL that we are currently using (BigQuery vs. Postgres)
    - NOTE: We can also add the `codegen` package to our `packages.yml` file
        ```YML
            - package: dbt-labs/codegen
                version: 0.12.1        
        ```
        - See more at:
            - https://hub.getdbt.com/dbt-labs/codegen/latest/
            - https://github.com/dbt-labs/dbt-codegen/
        - This package contains macros that generate dbt code for us, and also log it to the CLI
            - i.e., We already generated our YML file for our sources, but this could do it *for us*
        - After adding the `codegen` package to its respective YML file, run `dbt deps` to install it
        - We will be using this package to generate the YML for *base models* (our staging models)
            - In a separate and blank file, enter:
            ```Jinja
                {% set models_to_generate = codegen.get_models(directory='staging', prefix='stg_') %}
                {{ codegen.generate_model_yaml(
                    model_names = models_to_generate
                ) }}            
            ```
            - Then click "Compile" in the dbt Cloud IDE UI
            - This generates a YML file with every field in the model, as well as its data type and a placeholder for its description
                ```YML
                    version: 2

                    models:
                    - name: stg_yellow_trip_data
                        description: ""
                        columns:
                        - name: trip_id
                            data_type: string
                            description: ""

                        - name: vendor_id
                            data_type: int64
                            description: ""            
                ```
            - We can then copy and paste this to the `schema.yml` file for the `staging/` subdirectory, and then update the descriptions if desired
- After generating the YML (if needed) and adding the four tests noted above (two reference test, one primary key test, and an accepted values test, if needed), run the entire pipeline/workflow *with these new test* via `dbt build`
- ***NOTE***: **dbt_expectations** is another good package for utilizing a lot of dbt tests
    - https://hub.getdbt.com/calogica/dbt_expectations/latest/
    - https://github.com/calogica/dbt-expectations/


## Documentation
- dbt provides a way to *generate* documentation for a dbt project and render it as a website
- The documentation for a project includes:
    - *Information about the project*: 
        - Model code (both from the `.SQL` model files and *compiled* SQL files)
        - Model dependencies
        - Sources
        - An auto-generated DAG from the `ref` and `source` macros
        - Descriptions (from `.yml` files) and tests 
    - *Information about the data warehouse* (`information_schema`):
        - Column names and data types
        - Table stats (like size and number of rows, for example)
- dbt documentation can be hosted in dbt Cloud, as well generated locally
    - For a dbt Cloud documentation generation, just run `dbt docs generate` in the dbt Cloud IDE terminal
        - For a local documentation generation, just run `dbt docs generate` in your local CLI
            - This generates all the necessary files
            - Then, we can run `dbt docs serve` with various arguments in order to start a web server to serve the documentation locally
                ```bash
                    dbt docs serve [--profiles-dir PROFILES_DIR]
                                [--profile PROFILE] [--target TARGET]
                                [--port PORT]
                                [--no-browser]        
                ```
    - See more at https://docs.getdbt.com/reference/commands/cmd-docs
- It pulls data from our YML files (like `schema.yml` files), as well as the lineage of our current workflow(s)
- For the dbt Cloud environment, once `dbt docs generate` completes successfully, we can open the documentation via the "View Docs" icon next to the branch name on the right-hand side of the dbt Cloud IDE
    - You can also see the files generated for documentation in the `target/` directory of the project, such as `catalog.json`, `manifest.json`, and `index.html`***
    - This will show all the descriptions and metadata that we defined ourselves (or with the help from packages), along with the code (source *and* compiled) and dependencies for any models
    - NOTE: dbt documentation will look different once you deploy it

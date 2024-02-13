# dbt Testing and Documentation


## Testing
- **Tests** are *assumptions* that we make about our data
- Tests in dbt are essentially a `SELECT` statement in a SQL query that selects the data that we "don't want"
    - i.e., Our assumptions get compiled to SQL that *returns the amount of failing records*
- Child models will not be built if a test fails (for the most part)
    - Those tests with `severity: [severity]` will ask if dbt should keep running if it fails or not, or should it stop entirely
        - `severity: warn` means everything will run but it will give warnings at the end
        - `severity: never` means it will stop immediately    
- Tests are defined on a per-column-basis in the `schema.yml` file:
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
    - Accepted values
        ```YML
            - name: payment_type
            description: >
              A numeric code signifying how the passenger paid for the trip.
            tests: 
              - accepted_values:
                  values: "{{ var('payment_type_values') }}"
                  severity: warn
                  quote: false        
        ```
    - A foreign key to another table ("relationships")
        ```YML
            - name: pickup_location_id 
            description: location_id where the meter was engaged.
            # check if this field is located in the zone lookup table            
            tests:
              - relationships:
                  to: ref('taxi_zone_lookup')
                  field: location_id        
            - name: dropoff_location_id 
            description: location_id where the meter was disengaged.
            # check if this field is located in the zone lookup table            
            tests:
              - relationships:
                  to: ref('taxi_zone_lookup')
                  field: location_id
        ```
- You can also create your custom tests as queries
- To start, check out the `dm_monthly_zone_revenue.sql` file in `models/core`
    - This is a **data mart** based off of our fact table that contains a bunch of revenue information and aggregations, ready to be exposed to stakeholders 
    - NOTE: This also contains a **cross-database macro**:
        - https://docs.getdbt.com/reference/dbt-jinja-functions/cross-database-macros
        - Basically, they use the flavor of underlying SQL that we are currently using (BigQuery vs. Postgres)
    - NOTE: Also add the `codegen` package to our `packages.yml` file
        ```YML
            - package: dbt-labs/codegen
                version: 0.12.1        
        ```
        - See more at:
            - https://hub.getdbt.com/dbt-labs/codegen/latest/
            - https://github.com/dbt-labs/dbt-codegen/
        - This package contains macros that generate dbt code for us, and also log it to the CLI
            - i.e., We already generated our YML file for our sources, but this could do it for us
        - We will be using this package to generate the YML for a base model
            - In a separate file, add:
            ```Jinja
                {% set models_to_generate = codegen.get_models(directory='staging', prefix='stg_') %}
                {{ codegen.generate_model_yaml(
                    model_names = models_to_generate
                ) }}            
            ```
            - This generates a YML file with every field in the model, as well as its data type and a placeholder for its description
        - After adding the package to its respective YML file, run `dbt deps` to install it
- After generating the YML (if needed) and adding the 4 tests noted above (if needed), run the entire pipeline/workflow via `dbt build`
- **dbt_expectations** is another good package for utilizing a lot of dbt tests
    - https://hub.getdbt.com/calogica/dbt_expectations/latest/
    - https://github.com/calogica/dbt-expectations/


## Documentation
- dbt provides a way to *generate* documentation for a dbt project and render it as a website
- The documentation for a project includes:
    - *Information about the project*: 
        - Model code (both from the `.SQL` model files and *compiled* SQL files)
        - Model dependencies
        - Sources
        - Auto generated DAG from the ref and source macros
        - Descriptions (from .yml file) and tests 
    - *Information about the data warehouse* (`information_schema`):
        - Column names and data types
        - Table stats (like size and number of rows)
- dbt documentation can be hosted in dbt Cloud, as well generated as locally
    - For a local documentation generation, just run `dbt docs generate`
        - This generates all the necessary files
    - Then, we can run `dbt docs serve` with various arguments in order to start a web server to serve the documentation locally
        ```bash
            dbt docs serve [--profiles-dir PROFILES_DIR]
                        [--profile PROFILE] [--target TARGET]
                        [--port PORT]
                        [--no-browser]        
        ```
    - See more at https://docs.getdbt.com/reference/commands/cmd-docs
- It pulls data from our YML files (like `schema.yml`) as well as the lineage of our current workflow(s)
- 

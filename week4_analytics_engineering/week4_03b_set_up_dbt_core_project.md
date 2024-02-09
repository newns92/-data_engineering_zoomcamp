# Starting a dbt Project Locally

## Creating a dbt Project
- dbt provides a starter project with all basic files and folders at https://github.com/dbt-labs/dbt-starter-project
- A dbt **project** includes the following files:
    - `dbt_project.yml`: a file used to *configure* the dbt project
        - *If using dbt locally*, make sure the profile here matches the one setup during installation in `~/.dbt/profiles.yml`
    - `*.yml` files under folders `models/data/macros`: documentation files
    - CSV files in the `data/` folder: these will be our sources, files described above
    - Files inside `folder/` models: The SQL files contain the scripts to run our models, this will cover staging, core, and a datamarts models
        - At the end, these models will follow a specific structure (https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/week_4_analytics_engineering/taxi_rides_ny/README.md)
- In `dbt_project.yml`, you're able to define global settings (like project name, profile file, models, global variables), along with different configurations
    - So, we can set the project name to something like `taxi_data` and profile name `taxi_data`
    - We could have one dbt project, and by changing the profile, we could change where we run the project (from Postgres to BigQuery or vice versa, for example)
    - Every model will be a view or a table, unless indicated otherwise
- There are 2 ways to use dbt:
    1. With the CLI
        - After having installed dbt locally and setup the `profiles.yml` files, in a terminal, run `dbt init` *within the path that we want to start the project in order to clone the starter project*
    2. With dbt Cloud
        - After having set up dbt Cloud credentials (repo and data warehouse), start the project from the web-based IDE
- In BigQuery, we should have at least 2 schemas:
    - A DEV schema (`ny_trips`?), something like a sandbox
    - A PROD one (`ny_trips_prod`?), which is where we will run models after deployment
        - Potentially a STAGING schema/environment?
- ***In local Postgres, we should also have these schemas***:
- Once you have initialized the dbt project in the cloud, in `dbt_project.yml`, change the project name to `taxi_data`, but keep the profile `default` and leave the defaults for where our different files are located (under the `# These configurations specify where dbt...` section/comment)
    - The `profile` will define/configure which data warehouse dbt will use to create the project
    - Again, we could have one dbt project, and by changing the profile, we could change where we run the project (from Postgres to BigQuery or vice versa, for example)
- Then, under `models:` near the bottom of `dbt_project.yml`, change it's value from `my_new_project` to `taxi_data`
- Then, since we're not using it yet, delete the `example: +materiliazed: view` part of the YAML file
- Can also note that in the `models/` directory, we can see some sample models with basic DAGs already set up
    - But we don't worry about this, as we will create our own models
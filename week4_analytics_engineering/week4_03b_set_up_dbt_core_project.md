# Starting a dbt Project Locally

## Creating a dbt Project
- dbt provides a starter project with all basic files and folders at https://github.com/dbt-labs/dbt-starter-project
- A dbt **project** includes the following files:
    - `dbt_project.yml`: a file used to *configure* the dbt project
        - Defines things like the project name, different connections, where to store files, and other global configurations
            - So, we can set the project name to something like `taxi_data` and profile name `taxi_data`
        - We could have a dbt project, and by changing the *profile*, we could change *where* we run the project (from Postgres to BigQuery or vice versa, for example)
    - **Models**
        - Includes staging, core, and a datamarts models
        - Every model will be a view or a table, *unless indicated otherwise*
    - **Snapshots**, which are a way to capture the state of your mutable tables so you can refer to it later.
    - **Macros** that contain blocks of code that you can reuse multiple times
    - **Seeds**, which are CSV files with static data that you can load into your data platform with dbt
    - **Test**, which are SQL queries that you can write to test the models and resources in a dbt project
    - CSV files in the `data/` folder, which will be our **Sources**
    - For more information, see: https://docs.getdbt.com/docs/build/projects

- There are 2 ways to use dbt:
    1. With the CLI
        - After having installed dbt locally and setup the `profiles.yml` files, in a terminal, run `dbt init` *within the path that we want to start the project in order to clone the starter project*
    2. With dbt Cloud
        - After having set up dbt Cloud credentials (consisting of a GitHub repo and a data warehouse), start the project from the web-based IDE


## Setting up a dbt Core Project Locally
- 

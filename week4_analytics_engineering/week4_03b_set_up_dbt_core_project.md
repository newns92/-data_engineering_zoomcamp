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
        - After having installed dbt locally and setup the `profiles.yml` file, in a terminal, run `dbt init` *within the path that we want to start the project in order to clone the starter project to the correct location*
    2. With dbt Cloud
        - After having set up dbt Cloud credentials (consisting of a GitHub repo and a data warehouse), start the project from the web-based IDE


## Setting up a dbt Core Project Locally
- In a `week4/dbt_local` directory, copy over the `docker-compose.yml` file from week 1 of the course
- In a CLI prompt, spin up the Postgres database and pgAdmin in detached mode via `docker-compose up -d`
    - If needed, create a new server named `ny_taxi_data` by right-clicking on "Servers" and clic,ing "Register", then "Server"
    - You then need to specify the host address in the "Connection" tab, which should be `pgdatabase`, and the port is `5432` while username and password are both `root`
    - You will then see the `ny_taxi` database that was specified via the `docker-compose.yml` file
    - Create two new schemas, `dev` and `prod`
- Next, to install our packages and dependencies, open an Anaconda command prompt, activate the `zoom` Conda environement, and run `pip install dbt-bigquery` and `pip install dbt-postgres`
    - Installing `dbt-bigquery` *or* `dbt-postgres` will install `dbt-core` and any other dependencies
- Then, to initialize the project, `cd` into the `dbt_local` directory and run `dbt init`
- When prompted by the CLI, name the project `ny_taxi_data` and select the `postgres` option for the database
- NOTE that `profiles.yml` will be created in wherever your `.dbt/` directory is, say something like at `C:\Users\<username>\.dbt\` on Windows
    - It should be updated with stock **outputs** like:
        ```YML
        ny_taxi_data:
            outputs:

                dev:
                type: postgres
                threads: [1 or more]
                host: [host]
                port: [port]
                user: [dev_username]
                pass: [dev_password]
                dbname: [dbname]
                schema: [dev_schema]

                prod:
                type: postgres
                threads: [1 or more]
                host: [host]
                port: [port]
                user: [prod_username]
                pass: [prod_password]
                dbname: [dbname]
                schema: [prod_schema]

            target: dev
        ```
    - Update these outputs to be the correct root username, password, host, port, etc. for the Postgres database
- Next, `cd` into `ny_taxi_data/` and run `dbt debug --profiles-dir ../`
    - This will find the `profiles.yml` file in the current parent of the working directory of the dbt project, check the database connection, display any errors or warnings that it finds
    - **`profiles.yml` *should* live outside of your project directory, since it can have information for various dbt projects**

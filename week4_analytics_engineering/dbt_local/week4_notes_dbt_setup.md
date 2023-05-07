## Local setup for Postgres
- In the `week4/` directory, spin up the Postgres database via `docker-compose up -d`
    - If needed, create a new server: `taxi_data` by right-clicking on "Servers" and hit "Register" --> "Server"
    - Need to specify the host address in the "Connection" tab, which should be `pgdatabase`, port is `5432`, username and password is `root`
- In the `zoom` Conda environment, run `pip install dbt-bigquery` and `pip install dbt-postgres`
    - Installing `dbt-bigquery` or `dbt-postgres` will install `dbt-core` and any other dependencies
- Create a `dbt_local/` directory, `cd` into it, and run `dbt init`
- Name the project `taxi_data` and select the Postgres option of a database
- `profiles.yml` should be updated with stock **outputs**.
- Update these outputs to be the correct root username, password, host, port, etc. for the Postgres database
- Run `dbt debug --profiles-dir ../`
    - This will find the `profiles.yml` file in the parent directory of the dbt project and check the database connection and display any errors or warnings that it finds
- Copy in the green staging SQL file, the `schema.yml` file, the macros file
- Create the `packages.yml` file
- Then run `dbt deps --profiles-dir=../`
- Then attempt `dbt run -m stg_green_trip_data --profiles-dir=../`
- This *should* work, and you should see the View in the `public` schema of Postgres
    - ***If needed, create `staging` and `prod` schemas now***
- Then create the yellow staging SQL file
- Then attempt `dbt run -m stg_yellow_trip_data --profiles-dir=../`
- You should see the second View in the `public` schema of Postgres

## Seeds
- Create the seed CSV, then add it to the `dbt_project.yml`
- Then run `dbt seed --profiles-dir=../`
- You should see a new table in Postgres
- Now, we can create a model based on this seed
    - Under `models/core/`, create a file `dim_zones.sql`
    - Here, we will first define the config as a materialized *table* rather than a view like we have been doing thus far in our models
        - Ideally we want everything in `models/core` to be a table, since this is what's exposed (to BI tools and/or to stakeholders)
    - Add the SQL to create the dim table
    - Before runnning this model, create a new one called `fact_trips.sql`
        - In here, we'll take both the staging yellow and staging green data and UNION them
    - Once `fact_trips.sql` is done, we can run `dbt run --profiles-dir=../` which will run all of our models, *but not the seed*
        - To run the seed as well, run `dbt build --profiles-dir=../` to build everything that we have, along with running some tests
    - Say we just want to run `fact_trips.sql`, we'd run `dbt build --select fact_trips.sql --profiles-dir=../`
        - But to run everything that `fact_trips.sql` depends on first, we can run `dbt build --select +fact_trips.sql --profiles-dir=../`

## Testing
- Then add all the tests and the correct `schema.yml` files and the `dm_montly_zone_revenue.sql` core model
- Run `dbt build --profiles-dir=../`


## Deployment
- Add the PROD code to the `profiles.yml` file
- Then run `dbt build -t prod --profiles-dir=../` to change the target (`-t`) to PROD
- We could then `git checkout` into `master` and use it to deploy models in PROD once done development
- We could also use a CRON job to indicate the command and the target
    - The Windows equivalent to a CRON job is a **scheduled task**
    - A scheduled task can be in **Task Scheduler** (or just run `Win+R` then execute `taskschd.msc`)
    - But it can also be done via CLI with `schtasks` (if you, for instance, need to script it or add it to version control)
        - Ex: `schtasks /create /tn calculate /tr calc /sc weekly /d MON /st 06:05 /ru "System"`
            - This creates the task "calculate", which starts the calculator(calc) every Monday at 6:05 (should you ever need that)
        - All available commands:
            - https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/schtasks
            - https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/schtasks-create
    - There's also `pycron`
        - https://pypi.org/project/python-crontab/
    - Other options (Airflow, Prefect, Dagster, Databricks, etc.):
        - https://docs.getdbt.com/docs/deploy/deployment-tools
            - https://prefecthq.github.io/prefect-dbt/
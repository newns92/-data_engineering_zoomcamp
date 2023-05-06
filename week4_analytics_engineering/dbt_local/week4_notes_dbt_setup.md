## Local setup for Postgres
- In the `week4/` directory, spin up the Postgres database via `docker-compose up -d`
    - If needed, create a new server: `taxi_data` by right-clicking on "Servers" and hit "Register" --> "Server"
    - Need to specify the host address in the "Connection" tab, which should be `pgdatabase`, port is `5432`, username and password is `root`
- In the `zoom` Conda environment, run `pip install dbt-bigquery` and `pip install dbt-postgres`
    - Installing `dbt-bigquery` or `dbt-postgres` will install `dbt-core` and any other dependencies
- 
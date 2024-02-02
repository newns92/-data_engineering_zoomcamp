# ETL: From API to Postgres

## Configuring Postgres
- Now, we will configure out Postgres client so that we can connect to the local Postgres database in our Docker container
- Notice that in `docker-compose.yml`, our credentials and environment variables are stored in that `.env` file
- After configuring our Postgres instance, we will make sure we're connected to it before writing data to it in Mage
- The Mage connections are managed in the `io_config.yaml` file in the `magic-zoomcamp` directory/project
    - There is a default profile in this file, but we can also add other profiles, such as ones for development and production environments
    - We can create a development profile `dev` and use **Jinja** templating in order to interpolate environment variables in Mage with the `env_var()` syntax:
        ```bash
        dev:
            # PostgresSQL
            POSTGRES_CONNECT_TIMEOUT: 10
            POSTGRES_DBNAME: "{{ env_var('POSTGRES_DBNAME') }}"
            POSTGRES_SCHEMA: "{{ env_var('POSTGRES_SCHEMA') }}"
            POSTGRES_USER: "{{ env_var('POSTGRES_USER') }}"
            POSTGRES_PASSWORD: "{{ env_var('POSTGRES_PASSWORD') }}"
            POSTGRES_HOST: "{{ env_var('POSTGRES_HOST') }}"
            POSTGRES_PORT: "{{ env_var('POSTGRES_PORT') }}"
        ```
    - These Postgres configuration settings are being pulled in from Docker (where we are actually defining to Postgres instance)
- Then, navigate to "Pipelines" in Mage and create a new **batch** pipeline and name it `test_config`
- Open this pipeline and go to "Edit pipeline" on the left-hand side
- Then, add in a simple SQL data loader block named `test_postgres`
- In the Mage UI for the block, make sure the connection is to "PostgreSQL", and select the "dev" profile from the drop-down menus, and select the "Use raw SQL" checkbox
- For the block, just enter `SELECT 1;`, and Mage should connect to our Postgres database in our Docker container and run this statement *in Postgres*, and *not* in Mage
- We should get back a single column with one row with the value `1` in the output when running the block
- Now that we have our Postgres connection, we can now move forward with creating a pipeline

## Writing an ETL Pipeline
- We will be taking data from an API in the form of a compressed CSV file, doing some transforms, and loading it to our local Postgres database (in Docker)
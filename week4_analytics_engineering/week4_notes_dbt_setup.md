## Cloud setup
- First, upload the data to a GCS bucket via the `upload_all_data.py` file in the `week4/` directory
- Then, in BigQuery, create the external tables via:
    ```bash
        CREATE OR REPLACE EXTERNAL TABLE `de-zoomcamp-384821.ny_trips.external_yellow_trip_data`
        OPTIONS (
        format = 'PARQUET',
        uris = ['gs://de-zoomcamp-384821-taxi-data/data/yellow/yellow_tripdata_2019-*.parquet', 'gs://de-zoomcamp-384821-taxi-data/data/yellow/yellow_tripdata_2020-*.parquet']
        );

        CREATE OR REPLACE EXTERNAL TABLE `de-zoomcamp-384821.ny_trips.external_green_trip_data`
        OPTIONS (
        format = 'PARQUET',
        uris = ['gs://de-zoomcamp-384821-taxi-data/data/green/green_tripdata_2019-*.parquet', 'gs://de-zoomcamp-384821-taxi-data/data/green/green_tripdata_20209-*.parquet']
        );

        CREATE OR REPLACE EXTERNAL TABLE `de-zoomcamp-384821.ny_trips.external_fhv_trip_data`
        OPTIONS (
        format = 'PARQUET',
        uris = ['gs://de-zoomcamp-384821-taxi-data/data/fhv/fhv_tripdata_2019-*.parquet']
        );        
    ```
- Then, in BigQuery, create *non*-external tables via
    ```bash
        CREATE OR REPLACE TABLE `de-zoomcamp-384821.ny_trips.yellow_trip_data`
        AS
        SELECT * FROM `de-zoomcamp-384821.ny_trips.external_yellow_trip_data`;

        CREATE OR REPLACE TABLE `de-zoomcamp-384821.ny_trips.green_trip_data`
        AS
        SELECT * FROM `de-zoomcamp-384821.ny_trips.external_green_trip_data`;

        CREATE OR REPLACE TABLE `de-zoomcamp-384821.ny_trips.fhv_trip_data`
        AS
        SELECT * FROM `de-zoomcamp-384821.ny_trips.external_fhv_trip_data`;
    ```
- Then, check the row counts via
    ```bash
        SELECT COUNT(*) FROM `de-zoomcamp-384821.ny_trips.fhv_trip_data`;
        --- 43,244,696

        SELECT COUNT(*) FROM `de-zoomcamp-384821.ny_trips.yellow_trip_data`;
        --- 109,047,518

        SELECT COUNT(*) FROM `de-zoomcamp-384821.ny_trips.green_trip_data`;
        --- 7,778,101
    ```
- Then, create a free dbt Cloud account via https://www.getdbt.com/signup/
- Then, follow the instructions at https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/week_4_analytics_engineering/dbt_cloud_setup.md and https://www.youtube.com/watch?v=uF76d5EmdtU&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=31docker 
    - **Create a BigQuery service account**
        - First, create a client ID and secret key for authentication with BigQuery
            - This client ID and secret key will be stored in dbt Cloud to manage the OAuth connection between dbt Cloud users and BigQuery
        - Do this via by creating a BigQuery service account via the BigQuery credential wizard (https://console.cloud.google.com/apis/credentials/wizard) to create a service account in the taxi project
            - Select the BigQuery API as the API to use, then "application data", then "No, I'm not using them" for the last option
            - Name the service acccount `dbt-service-account`
            - Can either grant the specific roles the account will need (BigQuery Data Editor, Big Query Job User, BigQuery User) or simply use BigQuery Admin, as you'll be the sole user of both accounts and data
            - Ignore the last section, and click "Done"
        - Now that the service account has been created we need to add and download a JSON key
            - Go to the "Keys" section, and select "Add key", then "Create new key" 
            - Select key type "JSON", click "Create", and recieve a downloaded JSON file
    - **Create a dbt cloud project**
        - Create a dbt cloud account from their website (it's free for solo developers)
        - Once you have logged in into dbt cloud you will be prompt to create a new project
        - Name your project "Taxi Data" and under "Advanced Settings", set the directory to where we want to work with dbt (`week4_analytics_engineering/dbt_cloud`)
        - Choose BigQuery as the data warehouse
        - Upload the key JSON file you just downloaded under the "Upload from file" section for "Settings"
            - This will fill out most fields related to the production credentials
        - Scroll down to the end of the page and set up your development credentials
            - Enter your personal development credentials here (*not* deployment credentials!). 
            - dbt will use these credentials to connect to the database on your behalf
            - When ready to deploy a dbt project to production, you'll be able to supply your production credentials separately
            - The dataset you'll see under "Development Credentials" is the one you'll use to run and build models during development
            - Since BigQuery's default location may not match the one you used for your source data, it's recommended to create this schema manually to avoid multiregion errors
            - Name the dataset "ny_trips_dev", and set the target to "ny_trips"
        - Click "Test connection" to make sure we can connect
        - For "Setup a repository", select "Git Clone"
            - Add the SSH for the GitHub repo you are using and click "Import"
            - You will get a **deploy key**
            - Go to the GitHub repo and go to the "Settings" tab
            - Under "Security", you'll see the menu "Deploy keys" on the left
            - Click on "Add deploy key" and paste in the deploy key provided by dbt Cloud, while **making sure to check on "write access"**
            - *You could simplify the process of adding and creating repositories by linking your GitHub account* (https://docs.getdbt.com/docs/cloud/git/connect-github)
    - **Review your project settings**
        - Checkout the `dbt` branch in the project within the dbt Cloud IDE
        - Click "Initialize dbt project"
        - Commit the changes
        - Open a PR


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
- Copy/Cut the `profiles.yml` file into the `taxi_data` directory that `dbt init` created
- Run `dbt debug`
    - This will check the database connection and display any errors or warnings that it finds


## Local setup for BigQuery with Docker
- https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/week_4_analytics_engineering/docker_setup/README.md
- Create the `Dockerfile` and `docker-compose.yaml` and `profiles.yaml` files in the `dbt_local_docker/` directory
- In a `zoom` Anaconda terminal, run `docker compose build` to build the `dbt/bigquery` Docker image
- Then run `docker compose run dbt-bq-dtc init`
    - **Note**: We are essentially running `dbt init` above because the `ENTRYPOINT` in the `Dockerfile` is ['dbt']
    - Input the required values, such as project name as "taxi_data", select the BigQuery database when prompted, enter the path to the credentials JSON, enter the GCP project ID, the BigQuery dataset, 4 threads, 300 timeout seconds, then select "US" at the desired location
    - This should create `dbt/taxi_data/` and you should see `dbt_project.yml` in there.
    - In `dbt_project.yml`, replace `profile: 'taxi_rides_ny'` with `profile: 'bq-dbt-workshop'` as we have a profile with the latter name in our `profiles.yml`
- Get your credentials file in the right directory, then run `docker compose run --workdir="//usr/app/dbt/taxi_rides_ny" dbt-bq-dtc debug` to test your connection

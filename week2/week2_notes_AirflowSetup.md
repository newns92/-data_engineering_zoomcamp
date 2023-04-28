# Airflow Setup
## Pre-Reqs
- For the sake of standardization across the workshop config, rename the `gcp-service-accounts-credentials` file to `google_credentials.json` & store it in your $HOME directory
    - `cd ~ && mkdir -p ~/.google/credentials/`
    - `cp [path/to/service-account-authkeys].json ~/.google/credentials/google_credentials.json`
- May need to upgrade `docker-compose` to version v2.x+ and set the memory for your Docker Engine to minimum 4GB (ideally 8GB)
    - If enough memory is not allocated, it might lead to `airflow-webserver` continuously restarting
- Make sure Python is at least v3.7

## Airflow Setup
- `mkdir airflow` in the week 2 directory for the course
- Set the Airflow user:
    - In Git Bash, `cd` into `airflow` and run `mkdir -p ./dags ./logs ./plugins`
    - Then run `echo -e "AIRFLOW_UID=$(id -u)" >> .env`
        - To get rid of the warning `("AIRFLOW_UID is not set")`, edit `.env` file to have this: `AIRFLOW_UID=50000`
- Import the official Docker setup file from the latest Airflow version:
    - Run `curl -LfO 'https://airflow.apache.org/docs/apache-airflow/stable/docker-compose.yaml'`
    - It could be overwhelming to see a lot of services in here, but this is only a quick-start template, and as you proceed you'll figure out which unused services can be removed
    - **Can use the "no-frills" version from the zoomcamp Github**
        - Also use the `.env_example` instead of `.env` and copy the `entrypoint.sh` file
            - Changes: 
                - Removal of `redis` queue, `worker`, `triggerer`, `flower` & `airflow-init` services, and changing from `CeleryExecutor (multi-node)` mode to `LocalExecutor (single-node)` mode in `docker-compose.yaml`
                - Inclusion of a new `.env` for better parametrization & flexibility
                - Inclusion of simple `entrypoint.sh` to the webserver container, responsible to initialize the database and create login-user (admin).
                - Updated `Dockerfile` to grant permissions on executing `scripts/entrypoint.sh`
        - `mkdir scripts` and add `entrypoint.sh` to it
        - ***DO NOT USE LATEST VERSION OF AIRFLOW, PIP INSTALL ERROR***
- Docker Build
    - When you want to run Airflow locally, you might want to use an extended image, containing some additional dependencies (like add new Python packages, or upgrade Airflow providers to a later version)
    - Create a `requirements.txt` for what to `pip install` in the `Dockerfile`
    - Create a `Dockerfile` pointing to the latest Airflow version, such as apache/airflow:2.2.3, for the base image
    - Customize this `Dockerfile` by:
        - Adding custom packages to be installed
            - The one we'll need the most is `gcloud` to connect with the GCS bucket/Data Lake.
        - Integrate `requirements.txt` to install libraries via `pip install`
- In `.env`:
    - Set environment variables `AIRFLOW_UID`, `GCP_PROJECT_ID` & `GCP_GCS_BUCKET`, as per your config.
        - ***SET `AIRFLOW_UID=50000` so that Airflow actually runs***
        - **Spin up the VM and `terraform apply` up a Bucket to get an ID for `GCP_GCS_BUCKET**
    - Optionally, if your `google-credentials.json` is stored somewhere else than mentioned above, modify the env-vars (`GOOGLE_APPLICATION_CREDENTIALS`, `AIRFLOW_CONN_GOOGLE_CLOUD_DEFAULT`) and volumes path in `docker-compose.yaml`

## Running everything
- Run `docker-compose build`, and it should take about 5-10 minutes to build
- Kick up the all the services from the container (no need to specially initialize): via `docker-compose -f docker-compose.yaml up`
- In *another* terminal, run `docker ps` to see which containers are up & running (there should be 3, matching with the services in your `docker-compose.yaml` file)
- Login to the Airflow web UI on `localhost:8080` with creds: admin/admin (explicit creation of admin user was required)

    
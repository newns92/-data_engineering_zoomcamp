# Dockerizing the Ingestion Script


## The Ingestion Script
- If you have the ingestion script as a Jupyter notebook, convert it to a script by `cd`-ing into the directory with the notebook and run `jupyter nbconvert --to=script [notebook name].ipynb`
- Next, add in the `argparse` Python library to the `load_data.py` file in order to take in command line arguments
- Start both the Postgres database and pgAdmin containers via Docker Desktop, or delete the containers and re-create and run them via their respective `docker run` commands
    - Or, if the containers are running, stop them via `docker stop [container-name]`
    - Then can start them from the CLI via `docker start [container-name]`
    - You can check the statuses via `docker ps`
- Once running both containers, re-run the `load_data.py` script with the arguments:
    ```
        python load_data.py \
        --user=root \
        --password=root \
        --host=localhost \
        --port=5432 \
        --database=ny_taxi \
        --yellow_taxi_table_name=yellow_taxi_data \
        --yellow_taxi_url=https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz
    ```
- Double-check the row count, which should be 1,369,765 rows


## Docker-izing load_data.py
- To start, add `RUN apt-get install wget` to the `Dockerfile` to install `wget` in the container
- Then, add `sqlalchemy` and `psycopg2` to the `pip install pandas` line in the `Dockerfile`
    - `psycopg2` is a Python library for interacting with Postgres through Python
- Then change all instances of `pipeline.py` to `load_data.py`
    ```
    # copy pipeline file from current working directory to docker image
    COPY load_data.py load_data.py

    # override the entry point
    # ENTRYPOINT [ "bash" ]
    ENTRYPOINT [ "python", "load_data.py" ]
    ```
- We can then run `docker build -t taxi_ingest:v001 .` to specify that we are building the first version of the `taxi_ingest` image in the current directory (via the `.` at the end of the command)
- After the image has been built, we can build the container via this image using the same CLI arguments as we used for the Python file:
    ```
        docker run -it taxi_ingest:v001 \
        --user=root \
        --password=root \
        --host=localhost \
        --port=5432 \
        --database=ny_taxi \
        --yellow_taxi_table_name=yellow_taxi_data \
        --yellow_taxi_url=https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz
    ```
- ***This should give an error, since there is no `localhost` in this container, and we need to instead run this command in the `pg-network` that we created earlier***
- We do this via the Docker `--network` argument, which is *specified before the image name*, and by *updating the host name to `pgdatabase`*:
    ```
        docker run -it \
        --network=pg-network \
        taxi_ingest:v001 \
        --user=root \
        --password=root \
        --host=pgdatabase \
        --port=5432 \
        --database=ny_taxi \
        --yellow_taxi_table_name=yellow_taxi_data \
        --yellow_taxi_url=https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz
    ```
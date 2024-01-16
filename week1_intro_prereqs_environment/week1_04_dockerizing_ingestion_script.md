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

## Docker Compose
- **Docker Compose** lets us define and run *multiple* containers and link them in a network
- It lets us codify the Docker shell commands into a YML file so that we don't have to remember the correct sequence to run network commands, along with all of the flags and environment variables
- https://docs.docker.com/compose/
- Create the `docker-compose.yml` file
    - Don't need to write the full path for the volumes
    - Docker provides `restart` policies to control whether your containers start automatically when they exit, or when Docker restarts, and these that linked containers are started in the correct order
    - The containers automatically become part of a network, so we don't have to specify it here
- To begin, 
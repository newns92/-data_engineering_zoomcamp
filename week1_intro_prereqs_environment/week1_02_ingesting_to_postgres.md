# Ingesting Data into Postgres

## Running Postgres in Docker
- To start up Postgres in Docker via Git bash, run the following command:
    ```
    winpty docker run -it -e POSTGRES_USER="root" -e POSTGRES_PASSWORD="root" -e POSTGRES_DB="ny_taxi" -v .//ny_taxi_postgres_data:/var/lib/postgresql/data:rw -p 5432:5432 postgres:13`
    ```
    - `winpty` 
- To start up Postgres in Docker via an Anaconda prompt on Windows, run the following command:
    ```
    docker run -it -e POSTGRES_USER="root" -e POSTGRES_PASSWORD="root" -e POSTGRES_DB="ny_taxi" -v C://Users//[rest-of-path]//ny_taxi_postgres_data:/var/lib/postgresql/data:rw -p 5432:5432 postgres:13`
    ```
    - We are running in interactive mode via the `-it` flag
    - The `-e` flag is used to set environment variables, the `-v` flag is used to **bind mount** a volume (share a directory from the host's filesystem into the container), and the `-p` flag is meant to specify ports (maps a container port to a port on the Docker host to the outside world)
    - Then, finally, we name the image that we want to use as a template for our container (`postgres:13`)
- Once completed, the command should result in a line in the prompt window saying `database system is ready to accept connections` and the `\ny_taxi_postgres_data\` directory should be populated with many folders

## pgcli
- Next, we will look at a CLI client to access our Postgres database called **pgcli**
- Install via `pip install pgcli`
- Then test via `pgcli --help`
    - If you get an `Exception has occurred: ImportError no pq wrapper available` error, run `pip install "psycopg[binary,pool]"`
- Then, start up the container with the Postgres database like above
- To connect to a Postgres database, ***in a separate command prompt***, run `pgcli -h localhost -p 5432 -u root -d ny_taxi` where `-d` specifices the database, `-u` specifices the user, `-p` specifies the port, and `-h` specifies the host
    - If there *were* tables in the database, we could see them by running `\dt`
    - You can also test by running `SELECT 1`
- You can then exit the database connection via `CTRL + D`

## Ingesting the data
- Install pandas via `pip install pandas` and `sqlalchemy` via `pip install sqlalchemy` and then run `load_data.py` in an Anaconda prompt via `python load_data.py`
- You can then check the schema in a Postgres-connected Anaconda prompt via `\d yellow_taxi_data`
- You can test the row counts with `SELECT COUNT(*) FROM yellow_taxi_data` (should be 1369765)
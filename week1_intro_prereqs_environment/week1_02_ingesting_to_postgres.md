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

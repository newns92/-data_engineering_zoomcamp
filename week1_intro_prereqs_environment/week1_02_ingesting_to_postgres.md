# Ingesting Data into Postgres


## Running Postgres in Docker
- To start up Postgres *in Docker* via Git bash, run the following command:
    ```
    winpty docker run -it -e POSTGRES_USER="root" -e POSTGRES_PASSWORD="root" -e POSTGRES_DB="ny_taxi" -v /${PWD}/ny_taxi_postgres_data:/var/lib/postgresql/data:rw -p 5432:5432 postgres:13
    ```
    - `winpty` is a Windows software package providing an interface similar to a Unix pty-master for communicating with Windows console programs
        - *Note that we preface the path to host directory (volume) that we are mounting with a `/` because MINGW has an odd conversion*
            - Thus, instead of using `.` to denote the current working directory, we must use `${PWD}`
            - For more, see: https://stackoverflow.com/questions/50608301/docker-mounted-volume-adds-c-to-end-of-windows-path-when-translating-from-linux
    - We are running in interactive mode via the `-it` flag
    - The `-e` flag is used to set environment variables (such as username, password, and database for Postgres), the `-v` flag is used to **bind mount** a volume (share a directory from the host's filesystem into the container via the format `<host-directory>:<docker-container-directory>`), and the `-p` flag is meant to specify ports (maps a container port to a port on the Docker host in the outside world)
    - Again, finally, we name the image that we want to use as a template for our container (`postgres:13`)
    - The `:rw` at the end of the volume specifies it to be READ/WRITE mode
- To start up Postgres in Docker *via an Anaconda prompt on Windows*, run the following command:
    ```
    docker run -it -e POSTGRES_USER="root" -e POSTGRES_PASSWORD="root" -e POSTGRES_DB="ny_taxi" -v C://Users//<rest-of-path>//ny_taxi_postgres_data:/var/lib/postgresql/data:rw -p 5432:5432 postgres:13
    ```
    - *Note that a Windows prompt (Anaconda in this case) needs the FULL path to the host directory*
    - Again, we are running in interactive mode via the `-it` flag
    - Again, the `-e` flag is used to set environment variables (such as username, password, and database for Postgres), the `-v` flag is used to **bind mount** a volume (share a directory from the host's filesystem into the container via the format `<host-directory>:<docker-container-directory>`), and the `-p` flag is meant to specify ports (maps a container port to a port on the Docker host in the outside world)
    - Again, finally, we name the image that we want to use as a template for our container (`postgres:13`)
    - The `:rw` at the end of the volume specifies it to be READ/WRITE mode
- Once completed, the command should result in a line in the prompt window saying `database system is ready to accept connections` and the `ny_taxi_postgres_data\` directory should be populated with many sub-directories


## pgcli Client
- Next, we will look at a CLI client to access our Postgres database called **pgcli**
- Install this client via `pip install pgcli`
- Then test that it was installed correctly via `pgcli --help`
    - If you get an `Exception has occurred: ImportError no pq wrapper available` error, run `pip install "psycopg[binary,pool]"`
- Then, start up the container with the Postgres database like in the above command(s)
- To connect to a Postgres database, ***in a separate command prompt***, run `pgcli -h localhost -p 5432 -u root -d ny_taxi` (or `winpty pgcli -h localhost -p 5432 -u root -d ny_taxi`) where `-d` specifices the database, `-u` specifices the user, `-p` specifies the port, and `-h` specifies the host
    - If you are prompted for a password, use the one specified in the `docker run` command at the top of this page
    - If there *were* tables in the database, we could see them by running `\dt`
    - You can also test that the database connection is working by running `SELECT 1`
- You can then exit the database connection via `CTRL + D`


## Ingesting the data
- If needed, install pandas via `pip install pandas` and `sqlalchemy` via `pip install sqlalchemy`
- Then run the script `load_data.py` in a prompt window separate from the Postgres command prompt via `python load_data.py` with passed in args, like for example: 
    ```bash
    URL1="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz"

    python load_data.py \
    --user=root \
    --password=root \
    --host=localhost \
    --port=5432 \
    --database=ny_taxi \
    --yellow_taxi_table_name=yellow_taxi_data \
    --yellow_taxi_url=${URL1}    
    ```
- You can then check the schema in a Postgres-connected prompt (Anaconda or Git bash) via `\d yellow_taxi_data`
- You can test the row counts with `SELECT COUNT(*) FROM yellow_taxi_data`, which should be 1,369,765 rows
- Once done, you can exit the database via `CTRL + D` and then shut down the database in the other command prompt via 
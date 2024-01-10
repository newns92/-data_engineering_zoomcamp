# pgAdmin and Docker Networks

## Refresher
- Activate the conda environment
- `cd` to the correct directory
- Make sure Docker Desktop is running
- To start up Postgres in Docker via an Anaconda prompt on Windows, run the following command:
    ```
    docker run -it -e POSTGRES_USER="root" -e POSTGRES_PASSWORD="root" -e POSTGRES_DB="ny_taxi" -v C://Users//[rest-of-path]//ny_taxi_postgres_data:/var/lib/postgresql/data:rw -p 5432:5432 postgres:13`
    ```
- ***In a separate command prompt***, run `load_data.py` in an Anaconda prompt via `python load_data.py`
- To connect to the Postgres database, ***in a separate command prompt***, run `pgcli -h localhost -p 5432 -u root -d ny_taxi` where `-d` specifices the database, `-u` specifices the user, `-p` specifies the port, and `-h` specifies the host
- Can test that the data was loaded via `SELECT COUNT(*) FROM yellow_taxi_data` (should be 1,369,765 rows) or `SELECT MAX(tpep_pickup_datetime), MIN(tpep_pickup_datetime), MAX(total_amount) FROM yellow_taxi_data`

## pgAdmin
- It’s not very convenient to use `pgcli` for data exploration and querying
- `pgAdmin` = the standard web-based GUI for Postgres database exploration and querying (both local and remote servers)
- We don't need to install it since we have Docker, so we can just **pull** an image that contains this tool
- Google search for `pgadmin docker`, and select the first link (to the container): https://www.pgadmin.org/download/pgadmin-4-container/
- Click the documentation link for how to run this container: https://www.pgadmin.org/docs/pgadmin4/latest/container_deployment.html
- We will use `docker pull dpage/pgadmin4:<tag name>` where `<tag name>` can be a specific release, such as `latest`, `7.4`, `snapshot`, etc.
- The full command will be `docker run -it -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" -e PGADMIN_DEFAULT_PASSWORD="root" -p 8080:80 dpage/pgadmin4`
    - *Notice that we connect port 8080 on our local machine to port 80 in the container*
- Disconnect from `pgcli` and, after running the above command, once you see `Listening at: http://[::]:80 (1)`, open a browser window and go to `http://localhost:8080/` to see the landing page for pgAdmin
- On this page, sign in with the credentials from the above command
- Create a new server: `Local Docker` by right-clicking on "Servers" and hit "Register" --> "Server"
- You need to specify the host address in the "Connection" tab, which should be `localhost`, port is `5432`, username and password is `root`
- You will see an error of "Unable to connect to server: connection failed"
- This is because we're running pgAdmin *inside of a container*, and this is trying to find the Postgres localhost *within this container*, though it is running in *another, separate* container
- We need to link these two containers (one containing the Postgres database, the other containing pgAdmin), which we can do via a **Docker Network**

## Docker Networks
- "Container networking refers to the ability for containers to connect to and communicate with each other, or to non-Docker workloads"
    - https://docs.docker.com/network/
- To start, shut down both containers (pgAdmina and Postgres) in their respective command prompts
- Create a **Docker Network** via:
    1) Creating the network itself with `docker network create pg-network` being ran in a command prompt
        - Should return a SHA
    2) Run Postgres, specifying it should be run in the network, with `winpty docker run -it -e POSTGRES_USER="root" -e POSTGRES_PASSWORD="root" -e POSTGRES_DB="ny_taxi" -v C://Users//[rest of path]//ny_taxi_postgres_data:/var/lib/postgresql/data:rw -p 5432:5432 --name pgdatabase --network=pg-network postgres:13`
        - Check that the data has persisted with `SELECT COUNT(*) FROM yellow_taxi_data` (1,369,765)
    3) In a separate command window, run pgAdmin again, specifying it should be run within the network, with `docker run -it -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" -e PGADMIN_DEFAULT_PASSWORD="root" -p 8080:80 --name pgadmin --network=pg-network dpage/pgadmin4`
        - *Notice the commands are similar but we added `--name` and `--network` arguments*
- Then, reload pgAdmin in the browser window, log back in, and attempt to create the server again as described above, *BUT* the host name/address should be `pgdatabase`, the port is still `5432`, and the username and password are both still `root`
- You should have been able to connect and see "Local Docker" under "Servers" on the left side of the pgAdmin UI
- We an see our tables under "Local Docker" --> "Databases (2)" --> "ny_taxi" --> "Schemas (1)" --> "Tables (2)"
- We can view some of the data with `SELECT * FROM public.yellow_taxi_data LIMIT 100`
    - Can write the same query by going to "Tools" --> "Query Tool"
- Next, we will put those two `docker run -it` commands from above into a single YML file to run both containers in a single terminal via `docker compose`
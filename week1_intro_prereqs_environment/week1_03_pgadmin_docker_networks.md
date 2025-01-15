# pgAdmin and Docker Networks


## Refresher
- Make sure Docker Desktop is running
- `cd` to the correct directory in a command prompt
    - To start up Postgres in Docker via an Anaconda prompt on Windows, run the following command:
        ```bash
        docker run -it -e POSTGRES_USER="root" -e POSTGRES_PASSWORD="root" -e POSTGRES_DB="ny_taxi" -v C://Users//[rest-of-path]//ny_taxi_postgres_data:/var/lib/postgresql/data:rw -p 5432:5432 postgres:13
        ```
    - To start up Postgres in Docker via Git bash, run the following command:
        ```bash
        winpty docker run -it -e POSTGRES_USER="root" -e POSTGRES_PASSWORD="root" -e POSTGRES_DB="ny_taxi" -v /${PWD}/ny_taxi_postgres_data:/var/lib/postgresql/data:rw -p 5432:5432 postgres:13
        ```    
- ***In a separate command prompt***, run `load_data.py` via `python load_data.py`
- To connect to the Postgres database, ***in a third separate command prompt***, run `pgcli -h localhost -p 5432 -u root -d ny_taxi` (or `winpty pgcli -h localhost -p 5432 -u root -d ny_taxi`) where `-d` specifices the database, `-u` specifices the user, `-p` specifies the port, and `-h` specifies the host
- Can test that the data was loaded via `SELECT COUNT(*) FROM yellow_taxi_data` (should be 1,369,765 rows) or `SELECT MAX(tpep_pickup_datetime), MIN(tpep_pickup_datetime), MAX(total_amount) FROM yellow_taxi_data`


## pgAdmin
- It’s not very convenient to use `pgcli` for data exploration and querying
- `pgAdmin` is the standard web-based GUI for Postgres database exploration and querying (for both local and remote servers)
- We don't need to install it since we have Docker, so we can just **pull** an image that contains this tool
- Google search for `pgadmin docker`, and select the first link (to the container): https://www.pgadmin.org/download/pgadmin-4-container/
- Click the documentation link for information on how to run this container: https://www.pgadmin.org/docs/pgadmin4/latest/container_deployment.html
- We will use `docker pull dpage/pgadmin4:<tag name>` where `<tag name>` can be a specific release, such as `latest`, `7.4`, `snapshot`, etc.
- The full command (without a tag) will be `docker run -it -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" -e PGADMIN_DEFAULT_PASSWORD="root" -p 8080:80 dpage/pgadmin4`
    - *Notice that we connect port 8080 on our local machine to port 80 in the container*
- Disconnect from `pgcli` in its command prompt and, after running the above command in said command prompt, once you see `Listening at: http://[::]:80 (1)`, open a browser window and go to `http://localhost:8080/` to see the landing page for pgAdmin
- On this page, sign in with the credentials from the above command (email and password)
- Create a new server called `Local Docker` by right-clicking on "Servers" on the left-hand sidebar
    - Then click "Register", then click "Server"
- You need to specify the host address in the "Connection" tab, which should be `localhost`, port is `5432`, username and password is `root`
- You will see an error of `Unable to connect to server: connection failed`
- This is because we're running pgAdmin *inside of a container*, and it's trying to find the Postgres localhost *within this container*, but the Postgres localhost database is running in *another, separate* container
- We need to *link* these two containers (one containing the Postgres database, the other containing pgAdmin), which we can do via a **Docker Network**


## Docker Networks
- Definition: "Container networking refers to the ability for containers to connect to and communicate with each other, or to non-Docker workloads"
    - See: https://docs.docker.com/network/
- To start, shut down both containers (pgAdmin and the Postgres database) in their respective command prompts
- Create a **Docker Network** by:
    1) After shutting down pgAdmin and the Postgres database, create the network itself with `(winpty) docker network create pg-network` being ran in a command prompt
        - This should return a SHA if successful
    2) Run Postgres in its own separate command prompt, specifying it should be run *in the network we just created*, with
        ```bash
        docker run -it -e POSTGRES_USER="root" -e POSTGRES_PASSWORD="root" -e POSTGRES_DB="ny_taxi" -v C://Users//[rest of path]//ny_taxi_postgres_data:/var/lib/postgresql/data:rw -p 5432:5432 --name pgdatabase --network=pg-network postgres:13
        ```
        Or
        ```bash
        winpty docker run -it -e POSTGRES_USER="root" -e POSTGRES_PASSWORD="root" -e POSTGRES_DB="ny_taxi" -v /${PWD}/ny_taxi_postgres_data:/var/lib/postgresql/data:rw -p 5432:5432 --name pgdatabase --network=pg-network postgres:13
        ```
        - *NOTE*: If you get an error that the container name is already in use by another container, then
            - Run `docker ps -a` to see all containers in this case
            - Find the container with the container ID specified from the error message, and note the container name from the `docker ps -a` output in the "NAMES" column
            - Run `docker rm <container-name>`
            - Try the above command again
    3) Check that the data has persisted via pgcli with a `SELECT COUNT(*) FROM yellow_taxi_data` command (should return 1,369,765 rows)
    4) In a separate command window from the `docker run` command prompt (say, the pgcli command prompt after exiting pgcli), spin up pgAdmin again, *specifying it should be run within the network*, via `(winpty) docker run -it -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" -e PGADMIN_DEFAULT_PASSWORD="root" -p 8080:80 --name pgadmin --network=pg-network dpage/pgadmin4`
        - *Notice the commands are similar but we added `--name` and `--network` arguments*
- Once the network has been created and Postgres and pgAdmin are up and running again, reload pgAdmin in the browser window, log back in, and attempt to create the server again as described above, *BUT this time* the host name/address should be `pgdatabase`, while the port is still `5432` and the username and password are both still `root`
- You should have been able to connect and see "Local Docker" under "Servers" on the left-hand side of the pgAdmin UI
- We an see our tables under "Local Docker" --> "Databases (2)" --> "ny_taxi" --> "Schemas (1)" --> "Tables (2)"
- We can view some of the data with `SELECT * FROM public.yellow_taxi_data LIMIT 100`
- Next, we will put those two `docker run -it` commands from above (one for pgAdmin, one for the Postgres database) into a single YML file to run both containers in a single terminal via `docker compose`

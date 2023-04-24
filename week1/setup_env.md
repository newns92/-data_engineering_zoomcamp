# Docker: 
- https://docs.docker.com/desktop/install/windows-install/
- https://medium.com/@verazabeida/zoomcamp-2023-week-1-f4f94cb360ae
- Check for running containers with `docker ps`
# Docker Compose
- way of running multiple Docker images
# Postgres
- `winpty docker run -it -e POSTGRES_USER="root" -e POSTGRES_PASSWORD="root" -e POSTGRES_DB="ny_taxi" -v C://Users//[rest of path]//ny_taxi_postgres_data:/var/lib/postgresql/data:rw -p 5432:5432 postgres:13`
- Install a client for Postgres: `conda install -c conda-forge pgcli`
- Add to the system path: `C:\ProgramData\Miniconda3\Scripts`
- Test with `pgcli --help`
- Install keyring with `conda install keyring`
- Connect to Postgres IN A SEPARATE COMMAND WINDOW with `pgcli -h localhost -p 5432 -u root -d ny_taxi` where -d = database, -u = user, -p = port, -h = host
- Test by checking for tables with `\dt` and also doing `SELECT 1`
- Exit with CTRL+D
- See `load_data.py` to load in data
- Test with `SELECT COUNT(*) FROM yellow_taxi_data` (1369765) and `SELECT COUNT(*) FROM zones` (265)
- Test again with `SELECT MAX(tpep_pickup_datetime), MIN(tpep_pickup_datetime), max(total_amount) FROM yellow_taxi_data`
    - should get `2021-02-22 16:52:16`, `2008-12-31 23:05:16`, and `7661.28`
# pgAdmin
- It’s not convenient to use `pgcli` for data exploration and querying
- `pgAdmin` - the standard web-based GUI for Postgres data exploration and querying (both local and remote servers)
- Don't need to install it since we have Docker, so we can just pull an image that contains this tool
- Google `pgadmin docker`, select the first link (to the container)
- Click the "instructions on Dockerhub" link
- Will have to use `docker pull dpage/pgadmin4`
- Full command: `docker run -it -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" -e PGADMIN_DEFAULT_PASSWORD="root" -p 8080:80 dpage/pgadmin4`
    - notice we port 8080 on our machine to 80 in the container
- Once you see `Listening at: http://[::]:80 (1)`, open browser and go to `http://localhost:8080/` to see the landing page for pgAdmin
- Sign in with the credentials from the command above
- Create a new server: `Local Docker` by right-clicking on "Servers" and hit "Register" --> "Server"
- Need to specify the host address in the "Connection" tab, which should be `localhost`, port is `5432`, username and password is `root`
- Will see an error of unable to connect to this server because we're running pgAdmin inside of a container, and this is trying to find postgres localhost within this container, though it is in *another* container
# Docker Networks
- In other words, this pgAdmin Docker container cannot access the Postgres container, and we need to **link them** via a **Docker network**
- Shut down both containers
- Create a network with:
    - 1) Create the network itself with `docker network create pg-network`
    - 2) Run Postgres, specifying it should be run in the network, with `winpty docker run -it -e POSTGRES_USER="root" -e POSTGRES_PASSWORD="root" -e POSTGRES_DB="ny_taxi" -v C://Users//nimz//Dropbox//de_zoomcamp//week1//ny_taxi_postgres_data:/var/lib/postgresql/data:rw -p 5432:5432 --name pgdatabase --network=pg-network postgres:13`
        - a) Check that the data has persisted with `SELECT COUNT(*) FROM yellow_taxi_data` (1369765)
    - 3) In a separate command window, run pgAdmin, specifying it should be run in the network, with `docker run -it -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" -e PGADMIN_DEFAULT_PASSWORD="root" -p 8080:80 --name pgadmin --network=pg-network dpage/pgadmin4`
    - *Notice the commands are similar but we added `--name` and `--net` arguments*
- Create the server again in same manner as above, BUT host name/address should be `pgdatabase`, port is `5432`, username and password is `root`
- Should have been able to connect and see "Local Docker" under "Servers" on the left of pgAdmin
- Can see our tables under "Local Docker" --> "Databases (2)" --> "ny_taxi" --> "Schemas (1)" --> "Tables (2)"
- Can view data with `SELECT * FROM public.yellow_taxi_data LIMIT 100`
- Can write the same query by going to "Tools" --> "Query Tool"
- Next, we will put those two `docker run -it` commands into a single YAML file to run both containters with one terminal via `docker compose`
# Dockerize Data Load Script
- See 
# Docker Compose
- Docker Compose lets us run multiple containers and link them in a network
- Docker compose lets us codify the Docker shell commands into a YAML file so that we don't have to remember the correct sequence to run network commands, + all of the flags and environment variables
- Create the `docker-compose.yml` file
    - Don't need to write the full path for the volumes\
    - Docker provides `restart` policies to control whether your containers start automatically when they exit, or when Docker restarts, and these that linked containers are started in the correct order
    - The containers automatically become part of a network, so we don't have to specify it here
- Check that nothing is running with `docker ps`
- Then run `docker-compose up`
    - will have to create a new instance of the database server in the browser since we didn't do volumes mappings
- Or run in detached mode with `docker-compose up -d` to get control of the terminal back once things are spun up
- Shut it down with `docker-compose down`
- **To make pgAdmin configuration persistent**, create a folder `data_pgadmin`
    - Change its permission potentially (on Linux, `sudo chown 5050:5050 data_pgadmin`)
    - Mount it to the `/var/lib/pgadmin` folder under `volumes` in the `pgadmin1` service in `docker-compose.yml`
# Terraform
- Install chocolatey
    - Run `Get-ExecutionPolicy` in Windows Powershell. If it returns `Restricted`, then run `Set-ExecutionPolicy AllSigned` or `Set-ExecutionPolicy Bypass -Scope Process`
    - Run `Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))`
- Install with `choco install terraform`
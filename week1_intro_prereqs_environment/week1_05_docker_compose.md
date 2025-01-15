# Docker Compose


## Docker Compose Intro
- **Docker Compose** lets us define and run *multiple* containers and link them in a network
- It lets us codify the Docker shell commands into a YML file so that we don't have to remember the correct sequence to run network commands, along with all of the flags and environment variables needed
- For more, see: https://docs.docker.com/compose/
- To start, create the `docker-compose.yml` file containing 2 **services** (the Postgres database and pgAdmin), with their respective images `postgres:13` and `dpage/pgadmin4` and their respective environment variables:
    ```YML
    services:
        pgdatabase:
            ## Specify image to pull
            image: postgres:13
            restart: always
            ## Specify environment variables
            environment:
                - POSTGRES_USER=root
                - POSTGRES_PASSWORD=root
                - POSTGRES_DB=ny_taxi
            volumes:
                - "./ny_taxi_postgres_data:/var/lib/postgresql/data:rw"
            ports:
                - "5432:5432"
            networks:
                - pg-network
        pgadmin:
            ## Specify image to pull
            image: dpage/pgadmin4
            # restart: always
            ## Specify environment variables
            environment:
                - PGADMIN_DEFAULT_EMAIL=admin@admin.com
                - PGADMIN_DEFAULT_PASSWORD=root
            volumes:
                - ./data_pgadmin:/var/lib/pgadmin
            ports:
                - "8080:80"
            networks:
                - pg-network
    networks:
        pg-network:
            name: pg-network
    ```
    - We don't need to write the full path for the volumes in this case
    - *Note*: Docker provides `restart` policies to control whether your containers start automatically when they exit, or when Docker restarts, and these that linked containers are started in the correct order
    - The containers automatically become part of a network, so we don't have to specify it here


## Using Docker Compose
- Docker Compose should have come with your Windows installation of Docker Desktop
    - If on Linux, you might have to install it separately
- You can test that it's there via `docker compose` in a CLI window
- Next, stop the two contaners for `pgdatabase` and `pgadmin` if they are running via two `docker stop [container-name]` commands
- We can now run `docker-compose up` while in the directory containing the `docker-compose.yml` file
    - *We can also run in detached mode via `docker-compose up -d`*
- ***NOTE***: You *will* have to re-register the server with the name `Local Docker`, host name `pgdatabase`, and username and password both being `root` before seeing the table again
    - You can then run the `load_data.py` script if you have also added in the Zones table (*after* rebuilding the `taxi_ingest:v001` image if need be)
- We can then exit the CLI via `CTRL + C` if not in detached mode, and then run `docker-compose down`

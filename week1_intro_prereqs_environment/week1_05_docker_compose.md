# Docker Compose

## Docker Compose Intro
- **Docker Compose** lets us define and run *multiple* containers and link them in a network
- It lets us codify the Docker shell commands into a YML file so that we don't have to remember the correct sequence to run network commands, along with all of the flags and environment variables
- https://docs.docker.com/compose/
- Create the `docker-compose.yml` file
    - Don't need to write the full path for the volumes
    - Docker provides `restart` policies to control whether your containers start automatically when they exit, or when Docker restarts, and these that linked containers are started in the correct order
    - The containers automatically become part of a network, so we don't have to specify it here

## Using Docker Compose
- It should have come with your Windows installation of Docker Desktop
    - If on Linux, you might have to install it separately
- You can test that it's there via `docker compose` in a CLI window
- Create a `docker-compose.yml` file, and add our 2 **services**: `pgdatabase` and `pgadmin`, with their respective images `postgres:13` and `dpage/pgadmin4`
- Then add their respective environment variables:
    - `pgdatabase`:
        ```
        environment:
            - POSTGRES_USER=root
            - POSTGRES_PASSWORD=root
            - POSTGRES_DB=ny_taxi
        ```
    - `pgadmin`:
        ```
        environment:
            - PGADMIN_DEFAULT_EMAIL=admin@admin.com
            - PGADMIN_DEFAULT_PASSWORD=root
        ```
- Then add their respective volumes, ports, and (*if not already created*) the network `pg-network`:
    - `pgdatabase`:
        ```
        volumes:
        - "./ny_taxi_postgres_data:/var/lib/postgresql/data:rw"
        ports:
        - "5432:5432"
        # networks:
        # - pg-network
        ```
    - `pgadmin`:
        ```
        volumes:
        - ./data_pgadmin:/var/lib/pgadmin
        ports:
        - "8080:80"
        # networks:
        # - pg-network
        ```
- Next up, stop the two contaners for `pgdatabase` and `pgadmin`, if they are running via `docker stop [container-name]` commands
- We can now run `docker compose up` while in the directory containing the `docker-compose.yml` file
- *We can also run in detached mode via `docker-compose up -d`*
- You *will* have to re-register the server with the name `Docker Localhost`, host name `pgdatabase`, and username and password both being `root` before seeing the table again
- We can then exit the CLI via `CTRL + C` if not in detached mode, and then run `docker compose down`
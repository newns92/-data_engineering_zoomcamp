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
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
# pgAdmin
- It’s not convenient to use `pgcli` for data exploration and querying
- `pgAdmin` - the standard graphical tool for postgres for data exploration and querying
# Terraform
- Install chocolatey
    - Run `Get-ExecutionPolicy` in Windows Powershell. If it returns `Restricted`, then run `Set-ExecutionPolicy AllSigned` or `Set-ExecutionPolicy Bypass -Scope Process`
    - Run `Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))`
- Install with `choco install terraform`
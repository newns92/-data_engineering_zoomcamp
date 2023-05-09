# PipeRider: Maximizing Confidence in Your Data Model Changes with dbt and PipeRider

## DuckDB
- First, install DuckDB in the `zoom` Anaconda environment via `pip install duckdb==0.7.1`
- When to use DuckDB
    - Processing and storing tabular datasets (e.g. from CSV or Parquet files)
    - Interactive data analysis (e.g. Joining & aggregate multiple large tables)
    - Concurrent large changes, to multiple large tables (e.g. appending rows, adding/removing/updating columns)
    - Large result set transfer to client
- Download the DuckDB database file: `wget https://dtc-workshop.s3.ap-northeast-1.amazonaws.com/nyc_taxi.duckdb`
- Copy in all dirs/files from `https://github.com/InfuseAI/taxi_rides_ny_duckdb`
- Install the neccessary dbt packages and PipeRider: `pip install dbt-core dbt-duckdb 'piperider[duckdb]'`
- Create a new branch to work on: `git switch -c duckdb`
- Install dbt deps and build dbt models via: `dbt deps`, then `dbt build`

- 

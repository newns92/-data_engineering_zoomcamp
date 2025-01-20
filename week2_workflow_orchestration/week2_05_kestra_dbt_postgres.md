# Orchestrate dbt Models with Postgres in Kestra


## Intro
- We will be using **dbt** to transform our data after extracting it and for some automation
- We will extract the data from GitHub, load it into a table, and then perform transformations on it via dbt


## Create dbt Workflow
- We can pass different dbt commands into a Kestra flow's code
    ```YML
    inputs:
    - id: dbt_command
      type: SELECT
      allowCustomValue: true
      defaults: dbt build
      values:
        - dbt build
        - dbt debug # Use when running the first time to validate the database connection
    ```
- Then, we clone and synch the GitHub repo containing the dbt project we are trying to run
    ```YML
    tasks:
    # Clone and sync the git repository containing the dbt project
    - id: sync
      type: io.kestra.plugin.git.SyncNamespaceFiles
      url: https://github.com/DataTalksClub/data-engineering-zoomcamp/
      branch: main
      namespace: '{{ flow.namespace }}'
      gitDirectory: 04-analytics-engineering/taxi_rides_ny
      dryRun: false
      # This Git Sync is only needed when running the first time
      # Afterwards, the task can be disabled
      # disabled: true  
    ```
- Then, we actually perform dbt operations (via flow code), while also making sure that we are connected to the correct Postgres database (from earlier in the lesson)
    ```YML
    # Perform dbt operations
    - id: dbt-build
      type: io.kestra.plugin.dbt.cli.DbtCLI
      env:
      DBT_DATABASE: postgres-zoomcamp
      DBT_SCHEMA: public
      namespaceFiles:
      enabled: true
      containerImage: ghcr.io/kestra-io/dbt-postgres:latest
      taskRunner:
      type: io.kestra.plugin.scripts.runner.docker.Docker
      commands:
        # Install packages/updates
        - dbt deps
        - '{{ inputs.dbt_command }}'
      storeManifest:
      key: manifest.json
      namespace: '{{ flow.namespace }}'
      profiles: |
        default:
          outputs:
           dev:
              type: postgres
              host: host.docker.internal
              user: kestra
              password: k3str4
              port: 5432
              dbname: postgres-zoomcamp
              schema: public
              threads: 8
              connect_timeout: 10
              priority: interactive
          target: dev
    ```


## Run the Workflow and View Results
- Once done with the flow code, we can execute the flow, which will run our two tasks.
- Notice that new tables are created in the database: `dim_zones`, `dm_monthly_zone_revenue`, `fact_trips`, and `taxi_zone_lookup`
- We can then view the data in the Postgres database, say by running `SELECT * FROM public.dm_monthly_zone_revenue LIMIT 10`

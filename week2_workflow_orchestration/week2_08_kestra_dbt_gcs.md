# Orchestrate dbt Models in BigQuery in Kestra


## Intro
- We will be using **dbt** to transform our data after extracting it and for some automation
- We will extract the data from GitHub, load it into a table, and then perform transformations on it via dbt
- First, load in all of the green and yellow taxi data from 2019 and 2020 into BigQuery

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
- Then, we actually perform dbt operations (via flow code), while also making sure that we are connected to the correct BigQuery dataset (from earlier in the lesson)
    ```YML
    # Perform dbt operations
    - id: dbt-build
      type: io.kestra.plugin.dbt.cli.DbtCLI
      env:
        DBT_DATABASE: '{{ kv(''GCP_PROJECT_ID'') }}'
        DBT_SCHEMA: '{{ kv(''GCP_DATASET'') }}'
      namespaceFiles:
        enabled: true
      containerImage: ghcr.io/kestra-io/dbt-bigquery:latest
      taskRunner:
        type: io.kestra.plugin.scripts.runner.docker.Docker
      inputFiles:
        sa.json: '{{ kv(''GCP_CREDS'') }}'
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
              type: bigquery
              dataset: '{{ kv(''GCP_DATASET'') }}'
              project: '{{ kv(''GCP_PROJECT_ID'') }}'
              location: '{{ kv(''GCP_LOCATION'') }}'
              keyfile: sa.json
              method: service-account
              priority: interactive
              threads: 16
              timeout_seconds: 300
              fixed_retries: 1
          target: dev
    ```


## Run the Workflow and View Results
- Once done with the flow code, we can execute the flow, which will run our two tasks.
- Notice that new tables are created in BigQuery: `dim_zones`, `dm_monthly_zone_revenue`, `fact_trips`, and `taxi_zone_lookup`
- We can then preview the data in BigQuery, or query it say by running `SELECT * FROM <project-id>.<dataset>.dm_monthly_zone_revenue LIMIT 10`

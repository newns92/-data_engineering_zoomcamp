# Manage Scheduling and Backfills in BigQuery in Kestra


## Introduction
- We can use scheduling and backfills (for schedules that were missed in the past) to automate Kestra pipelines in BigQuery just as we did in Postgres


## Modifying Inputs and Variables
- Like before, we will create a trigger to automatically add the year and month for the selected taxi dataset (green or yellow)
    ```YML
    inputs:
    - id: taxi
      type: SELECT
      displayName: 'Select taxi type'
      values: ['yellow', 'green']
      defaults: 'yellow'

    variables:
      # File to download
      file: '{{ inputs.taxi }}_tripdata_{{ trigger.date | date(''yyyy-MM'') }}.csv'
      # Monthly data table in GCS
      gcs_file: 'gs://{{ kv(''GCP_BUCKET_NAME'') }}/{{ vars.file }}'
      # Full data table
      table: '{{ kv(''GCP_DATASET'') }}.{{ inputs.taxi }}_tripdata_{{ trigger.date | date(''yyyy_MM'') }}'
      # The data itself, generated based on the output from the extract task
      data: '{{ outputs.extract.outputFiles[inputs.taxi ~ ''_tripdata_'' ~ (trigger.date | date(''yyyy-MM'')) ~ ''.csv'' ]}}'
    ```


## Adding Schedules
- Again, at the bottom of the flow code, we add in our triggers, making sure our CRON jobs run on the first of the month, at 9AM for green taxi data, and 10AM for yellow taxi data
    ```YML
    triggers:
    - id: green_schedule
      type: io.kestra.plugin.core.trigger.Schedule
      cron: '0 9 1 * *'
      inputs:
      taxi: green

    - id: yellow_schedule
      type: io.kestra.plugin.core.trigger.Schedule
      cron: '0 10 1 * *'
      inputs:
      taxi: yellow
    ```
- We still need to use **backfills** to get the data from the past (2019, 2020, 2021)


## Backfills
- Again, at the top of the UI for the flow, go to the "Triggers" tab to set up our backfill execution, which will "go back in time" and execute for the dates that we don't have
- Click "Backfill executions" for the `green_schedule`, select "green" for the taxi type, and then and set the Start Date to be January 1, 2019, and set the End Date to December 31, 2019
- Under "Advanced configuration", you can also add labels to the backfill execution to note which executions of the flow were backfills or were real-time executions
- Then, click "Execute backfill"
- In the "Executions" tab, you can then see the file the execution is using, the input taxi color, and the backfill label
- Once January completes, the execution moves onto February, and so on
- Then, check the table for the green taxi data in Postgres, which should contain 6,044,050 rows
- Then, to prevent multiple flows from running at the same time and trying to write to the table at the same time (or truncating a table while we are writing to it, for example), we need to set `concurrency` to a value of "1" near the top of the flow code:
    ```YML
    id: gcp_taxi_scheduled
    namespace: zoomcamp
    description: Best to add a label `backfill:true` in the UI to track executions created via a backfill

    concurrency:
      limit: 1
    ```

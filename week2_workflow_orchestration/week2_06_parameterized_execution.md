# Parameterized Execution
- By now you're familiar with building pipelines, but *what about adding **parameters***? 
- Now we'll discuss some built-in runtime variables that exist in Mage and go over how to define your own
- We'll also cover how to use these variables to **parameterize** pipelines
- Finally, we'll talk about what it means to **backfill** a pipeline and how to do it in Mage

## Parameterized Execution
- We so far have been loading full datasets, but not loading *partial* datasets, nor datasets that depend on some *parameter* (hence the name **parameterized execution**)
    - For example, having a pipeline/a DAG that executes depending on some variable supplied to it
- Mage has various types of variables, like runtime variables and global variables
    - See: https://docs.mage.ai/development/variables/overview
- We will be working with **runtime variables** to create specific files for each day that our NYC taxi job is being run
    - This can come in handy when you're, say, calling an API and you want to write to a *specific* Parquet file by date (like in incremental payloads, for example)
- To start, right-click on the `api_to_gcp` pipeline and clone it, then rename it to `api_to_gcp_paramaterized`
- We still see all the same blocks when we open this copy pipeline, **because in Mage, blocks are *shared* across resources/pipelines**
- In order to edit these blocks *without affecting other pipelines*, there are some thing we must do
    - To start, delete the partitioning exporter block (This only deletes it from *this* pipeline/workflow, *not* from the entire project)
    - Then, create a new generic Python data exporter block, `export_to_gcp_parameter` and copy the code from the `taxi_to_gcs_parquet` block into this *new*, empty block
    - Then, in order to remove the `taxi_to_gcs_parquet` block from this pipeline, we must first remove the dependency to the transformer block in the dependency graph on the right-hand side of the UI
    - After doing so, we can delete the block from this pipeline
- Next, you may have noticed that every Mage block function has the **keywords argument** argument, `**kwargs`
    - This contains a number of parameters
    - Any variable that we declare and pass into a pipeline is going to stored in this `**kwargs` argument
    - There are some that we can access by default
        - For example, we can access the execution date by storing in a variable via a line like: `now = kwargs.get('execution_date')`, followed by a `print(now)` line
            - If we were running a pipeline and we wanted to write to some location that was dependent on the execution date, we can use this variable
                - For example, say we're loading incremental data that we want to fetch based on the date, we can supply the date of this `now` variable via `now.date()`, or via a custom date format like `now.strftime('%Y/%m/%d')`
        - Then, to write incremental data, we can write `now_fpath = now.strftime('%Y/%m/%d')`
            - Then, for our `object_key`, we can add this into it via `object_key = f'{now_fpath}/daily-trips.parquet'` and it will write to some file path in the GCS Bucket like `2024/01/03/daily-trips.parquet`
    - We can also a number of *custom* ways to do parameterized execution
        - Say you're triggering pipelines for an API in Mage, you can supply parameters that way
        - You can also pipeline variables from the pipeline editor view on the right-hand side of the UI when in the "Edit pipeline" view
            - Say you're defining some downstream step that relies on some upstream result, you could fetch data from some API, set a variable, and then later on down the line, reference that variable without having to explicitly pass data between blocks
        - Similarly, if we're defining a Mage trigger, if running on a schedule, we can add runtime variables from the UI in the "Run settings" window
- So, parameterized execution is another way to write data for data that's changing or to locations that are changing based on time or state
- Parameterized execution can be a very useful pattern in data engineering work

## Backfills
- 
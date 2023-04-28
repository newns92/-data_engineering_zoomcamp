# DE Zoomcamp - Week 2 - Workflow Orchestration

## Introduction to Workflow Orchestration (2023 Cohort - Prefect)
- **Workflow Orchestration** = governing your data flow in such a way that respects orchestration rules and your business logic
- **Data flow** = binds an otherwise disparate set of applications together
- Workflow orchestration tools allow us to turn any code into a workflow that we can schedule, run, and observe
- Delivery system analogy:
    - Each order in a shopping cart is the workflow, and each delivery is a workflow run
    - It's easy to add things to a cart, just like it's easy to add functions to a workflow
    - Within each order, may have several products packed into boxes
        - Think of the boxes as (various different) tasks within the workflow (dbt data transformation, pandas data cleansing, an ML use case, etc.)
    - Products within these boxes may come from different vendors
    - Boxes can be as big or small as you wish (workflow *design*)
    - The different delivery addresses specified could be different workflow destinations like data warehouses, databases, etc.
    - When checking out, you can decide to have an order delivered all at once, or sequentially
        - This is like as configuring the order of execution for tasks inside of a workflow
    - Can also choose if a delivery is "gift wrapped"
        - This is like packaging a workflow into a subprocess, or a Docker container, or a Kubernetes job
    - Can also choose delivery type
        - "Express" is like using Ray, or Das
    - Can choose to have multiple trucks delivering the packages
        - Like having sped-up execution with a single thread using concurrency and async (1 driver who's faster and more efficient)
    - Workflow Orchestration = the actual taking care of the delivery = execution of the workflow run
        - Ensuring products are packaged as desired, shipped at the desired schedule, and with the correct delivery type
    - A good orchestration service should **scale** and be highly available
        - An order should be shipped and the package delivery system should run even if suppliers are sick, or there's a weather storm delay, etc.
    - **Things can, of course, go wrong**
        - Packages damaged and should be returned = retrying or restarting a workflow
        - Entire delivery may be need to be rescheduled
    - Workflow orchestration is all about data flow and ensuring you can rely on its execution by giving visibility into how long a workflow (i.e., delivery) took, providing "shipment" updates (i.e., workflow execution logs), and letting you know if something was successfully shipped (the end state of the workflow)
    - The delivery service should also respect privacy and only be able to operate only on metadata
        - The workflow orchestration tool is responsible for the transport and execution of the data flow, but *not* what's "inside the box" (the data)
- **Core features of workflow orchestration:**
    - Remote execution
    - Scheduling
    - Retries
    - Caching
    - Integration with external systems (API's, databases, etc.)
    - Triggering ad-hoc runs
    - Allowing parameterization
    - Alert you when something fails
- Differnt workflow orchestration tools = Airflow, FLyte, Prefect, Dagster, Luigi, Astronomer, and more
- A workflow orchestration tool gives you the ability to orchestrate dataflow a variety of different tools

## Data Pipelines and Workflows (2022 Cohort - Airflow)
- **Data pipeline** = script/scripts/job that takes in 1+ data sources, does something to the data, and produces 1+ datasets
- The `load_data.py` was a pipeline from Week 1 used `wget` to download the data as a CSV, did some transforms, and then wrote the data to our Postgres database
     - This is a bad strategy, it's only 2 steps = downloading + transforming and then loading
     - **It's better to have each step separated, such that in case one step fails, the entire pipeline doesn't fail**
        - Say the internet goes out after we downloaded the data --> we can't connect to the database, so the entire script will fail
        - Should split out the downloading of the data into a local CSV and the ingestion of the data into a Postgres database
        - And we should make sure the we do not run the ingest step if the download step fails
- A slightly more complex data flow/pipeline would be:
    - 1) `wget` the data and store locally as CSV
    - 2) Parquet-erize the data as parquet is a somewhat more effective way of storing data on disk
    - 3a) Store the parquet file in GCP Storage bucket
    - 3b) Store the partuet file in AWS S3 (run in parallel to the GCP step)
    - 4) Take the parquet file from the Storage bucket and upload it to a table in BigQuery
- Each step above takes in some data as input, and outputs some data, and there's some dependency between the tasks
- The tasks are **jobs** and the **dependencies** are the files
- Can refer to this workflow as a **Directed Acyclic Graph (DAG)**
    - *Directed*: data flows from one step to the next
    - *Acyclic*: there are no cycles, data flows in one direction only
    - *Graph*: processing steps/jobs/tasks are the nodes, and data products/dependencies/files are the edges
- **Workflows can have parameters overall, and each job can have their own set of parameters**
- Workflow orchestration tools (Airflow, Prefect, etc.) can be used to define these DAGs and conduct the workflow in such a way that we have an easy way of retrying things if something fails



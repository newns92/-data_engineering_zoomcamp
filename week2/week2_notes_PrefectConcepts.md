# Introduction to Prefect Concepts

## Prefect
- **Prefect** = a modern open source dataflow automation platform that allows one to add observability and orchestration by utilizing Python to write code as **workflows** in order to build, run, and monitor pipelines at scale.

## Creating the environment
- Create a conda environment: `conda create -n zoom python=3.9`
- *In an Anaconda command window*, activate the environment: `conda activate zoom`
- Install the requirements found in `requirements.txt` via `pip install -r requirements.txt`
- Check `prefect version`
- Spin up the Postgres database via `docker-compose up -d` in the `week1/` directory
- Run the `load_data.py` file to load in a 2nd copy of the tables
- Notice that the new tables should have been loaded in the PgAdmin `localhost:8080` web address

## Prefect Flow
- That was great but, we had to manually trigger this python script via a `python` command
- Using a **workflow orchestration** tool will allow us to add a **scheduler** so that we won’t have to trigger this script manually
- Additionally, we’ll get all the functionality that comes with workflow orchestation such as visibility, additional resilience to the dataflow with automatic retries or caching, and more
- Let’s transform this into a **Prefect flow**
- A **flow** is the most basic Prefect Python **object** that is a **container** for workflow logic and allows you to interact with and understand the state of the workflow
    - Flows are like functions: they take inputs, perform work, and return outputs
- First, mport prefect with `from prefect import flow, task`
- We can start by using the `@flow` decorator to a `main_flow` function
- Add `@flow(name="Ingest Flow")` above a new `main_flow()` function, right above the `if __name__ == '__main__':` call
- Add add the code beneath the `if __name__ == '__main__':` call into `main()`
- Now, we have a **flow** wrapped around `main_flow()`
- Flows can contain **tasks**, so we transform `load_data()` *into* a task by adding the `@task` decorator
- Tasks are not *required* for flows, but tasks are special because they receive metadata about upstream dependencies and the state of those dependencies before the function is run, which gives you the opportunity to have a task wait on the completion of *another* task before executing
- Can also edit `task()` to be `@task(log_prints=True, retries=3)` for debugging and in order to add resilience via automatic retries in case the downloading of the external data fails for some reason
- Drop the tables that were loaded earlier and run this new script in the *Anaconda command prompt* to see if it works
- You should see output saying that this is a flow with an auto-generated name in purple text before the script actually starts running, and it will give an error when it finishes
- We can do some transformation do deal with taxi rides with `passenger_count` of 0
- First, we notice that the `load_data()` function does a lot of things, so we can break it up into smaller tasks in order to get more visibility into each of the steps
    - Add a new Task with `task()` and `def extract_data` to take the URL downloading part
    - Make sure this returns the desired dataframes
    - Can also create a caching key function    
        - One of the benefits of tasks if if we're running a workflow with heavy computation over and over that we *know* was continually successful, we can pull from the cache results to make execution more efficient and faster
        - Do `from prefect.tasks import task_input_hash`, then within the `extract_data()` `@task` decorator, add `cache_key_fn=task_input_hash`
        - Also add a chache expiration within this `@task` decorator via `cache_expiration=timedelta(days=1)`
            - Also `from datetime import timedelta` so this works
- Next up is to build a transform task to get rid of those `passenger_count` values of 0
    - We do:
    ```bash
    @task(log_prints=True)
    def transform_data(df):
        print(f"pre: missing passenger count: {df['passenger_count'].isin([0]).sum()}")
        df = df[df['passenger_count'] != 0]
        print(f"post: missing passenger count: {df['passenger_count'].isin([0]).sum()}")
        return df
    ```
- Now, to simplify `load_data()`
    ```bash
        @task(log_prints=True, retries=3)
        def load_data(user, password, host, port, database, taxi_table_name, df_taxi, zones_table_name, df_zones):
            # print("Creating the engine...")
            # need to convert a DDL statement into something Postgres will understand
            #   - via create_engine([database_type]://[user]:[password]@[hostname]:[port]/[database], con=[engine])
            engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}')    
            
            print('Loading in time zone data...')
            start = time.time()
            df_zones.to_sql(name=zones_table_name, con=engine, if_exists='replace')
            end = time.time()
            print('Time to insert zone data: %.3f seconds.' % (end - start))

            # get the header/column names
            header = df_taxi.head(n=0)
            # print(header)

            # add column headers to yellow_taxi_data table in the database connection, replace table if it exists
            header.to_sql(name=taxi_table_name, con=engine, if_exists='replace')

            print('Loading in taxi data...')
            # add first chunk of data
            start = time.time()
            df_taxi.to_sql(name=taxi_table_name, con=engine, if_exists='append')
            end = time.time()
            print('Time to insert taxi data: %.3f seconds.' % (end - start))
    ```
- We can now add in more things from Prefect, like **parameterization**
    - We can parameterize the flow to take a table name so that we could change the table name loaded each time the flow was run
        ```bash
        def main_flow(taxi_table_name: str, zones_table_name: str):
            user = "root"
            password = "root"
            host = "localhost"
            port = "5432"
            database = "ny_taxi"
            # taxi_table_name = taxi_table_name
            taxi_url = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz"
            # zones_table_name = zone_table_name
            zones_url = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv"

            raw_data_taxi, raw_data_zones = download_data(taxi_url, zones_url)
            transformed_data_taxi, transformed_data_zones = transform_data(raw_data_taxi), raw_data_zones
            load_data(user, password, host, port, database, taxi_table_name, 
                    transformed_data_taxi, zones_table_name, transformed_data_zones)
        ```
- We could even add a **subflow** (There’s a lot more you can do but here are just a few examples)
    ```bash
    @flow(name="Subflow", log_prints=True)
    def log_subflow(table_name: str):
        print(f"Logging Subflow for: {table_name}")
    ```
- Next, we can spin up the UI
    - First, in the *Anaconda command prompt* we've been using, run `prefect config set PREFECT_API_URL="http://127.0.0.1:4200/api"`
    - Then, run `prefect orion start`
    - In a browser, open up `http://localhost:4200/` to see the Orion UI and see all the flows we have ran in a nice dashboard
    - A quick navigation lets us dive into the logs of a flow run
    - Navigate around and you’ll notice on the left-hand side we have Deployments, Work Queues, Blocks, Notifications, and TaskRun Concurrency
        - You can set a multitude of different notifications for flows
            - Notifications are important so that we know when something has failed or if is wrong with our system
            - Instead of having to monitor our dashboard(s) frequently, we can get a notification when something goes wrong and needs to be investigated
        - Task Run concurrency can be configured on tasks by adding a tag to the task and then setting a limit through a CLI command
        - **Blocks** are a primitive within Prefect that enables the storage of configuration(s) and provides an interface with interacting with external systems
            - There are several different types of blocks you can build, and you can even create your own
            - **Block names are immutable** so they can be *reused* across multiple flows
                - So you can update credentials in the block without updating multiple sources of code
            - Blocks can also build upon blocks (like the Postgres connector that we will later build), or be installed as part of Intergration collection which is prebuilt tasks and blocks that are pip installable
                - For example, a lot of users use the SqlAlchemy
- Let’s now take our Postgres configuration and store that in a Block
    - Prefect has multiple different types of collections
    - Since SQLAlechmy was in our `requirements.txt`, if you don't see "SQLAlchemy Connector" as an available block, do `pip install sqlalchemy`
    - We are going to utilize this block to modify our flow to avoid hard-coding our user, password, port, and host
    - First, import the connector with `from prefect_sqlalchemy import SqlAlchemyConnector`
    - Then, we create the block in the UI
        - Give it a name "postgres-connector"
        - Then choose "SyncDriver" --> "postgresql+psycopg2"
        - Then add in our user, password, port, and host in the specified fields
    - Go to "Blocks" in the UI on the left, and see the code needed to use it
    - Then, we edit the `load_data()` function to utilize it
        ```bash
        def load_data(taxi_table_name, df_taxi, zones_table_name, df_zones):
            # print("Creating the engine...")
            # need to convert a DDL statement into something Postgres will understand
            #   - via create_engine([database_type]://[user]:[password]@[hostname]:[port]/[database], con=[engine])
            # engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}')
            connection_block = SqlAlchemyConnector.load("postgres-connector")
            with connection_block.get_connection(begin=False) as engine:  
                print('Loading in time zone data...')
                start = time.time()
                df_zones.to_sql(name=zones_table_name, con=engine, if_exists='replace')
                end = time.time()
                print('Time to insert zone data: %.3f seconds.' % (end - start))
                ...
        ```
    - Now run the load script again in a *new Anaconda command prompt* and you should see the flows in the Orion UI

## Prefect and GCP
- Now to bring some ETL into GCP
- Open a Git bash terminal to run the Prefect Orion server, and an Anaconda prompt in the `zoom` conda environment
- Run `prefect orion start` in the Anaconda prompt and go to `http://localhost:4200/` to see the Orion UI and our previously-ran flows
- In a new `etl_web_to_gcs.py` file, we will define a new main **flow function** that will call a bunch of **task functions**
- It will download the yellow taxi data, do some cleaning, and save it to a **parquet** file in our GCS data lake
    - **Parquet** = a lightweight way to save data frames in a *column-oriented format* (each column (field) of a record is stored with others of its kind)
        - Uses efficient data compression and encoding schemes for fast data storing and retrieval
        - Parquet with `gzip` compression (for storage) is slightly faster to export than just CSV (if the CSV needs to be zipped, then parquet is much faster), importing is about 2X times faster than CSV, and compression is ~22% of the original file size, about the same as zipped CSV files
- After finishing up `etl_web_to_gcs.py` in the `de_zoomcamp/week2/gcp` directory, create a new GCS bucket via "Cloud Storage" --> "Buckets" in our GCP project
- Name the bucket `prefect-[your project id]` and leave all other options as default, and create it
- Go to the Orion webserver UI and go to "Blocks" (Should see that SQLAlchemy `postgres-connector` from earlier)
    - Again, a **block** is a primitive within Prefect that enables the storage of configuration(s) in order to reuse them and provides an interface with interacting with external systems
- We will register a GCS block from the `prefect_gcp` Python module
    - To do so, in the Anaconda command prompt with the `zoom` environment activated, run `prefect block register -m prefect_gcp`
        - `-m` = module
    - Should see `Successfully registered 6 blocks` as a return statement with a table of said blocks, and we can see them at `http://127.0.0.1:4200/blocks/catalog`
    - In the cataloguem, add a GCS Bucket block, name it `zoom-gcs`, and enter your GCS Bucket name in the specified field
    - Note the option to create GCP credentials, which is a great way to store configurations and collaborate with others if using Prefect Cloud or hosting an Orion server so that others can use them
    - You *could* make a Bucket accessible to anyone, **but in reality, that's not a good idea**
    - Click the "+" next to "GCP credentials (optional)" and we will create a service account credential
        - Add in the block name `zoom-gcp-creds`
        - Then, we have to give it some service account file, or the data/info within some service account file directly
        - Back in GCS, go to "IAM" --> "Service Account"
        - Start to create a new one, name it `zoom-de-service-acct`
        - Give it the "BigQuery Admin" and "Storage Admin" roles
        - Then hit "Done"
        - After making this service account, we need to give it some **keys**
        - So, go to "Actions" to the far right of the account, and click "Manage keys"
        - Click "Add key" --> "Create new key", and select JSON
        - Save the resulting file ***locally***, and either upload it to the Block, or add in its contents
        - Click "create" to create the GCP credentials for the block
- Back in the GCS Block creation screen, get `zoom-gcp-creds` from the drop-down, then click "Create"
- We now see code that we can copy into `python etl_web_to_gcs.py` in order to use our new block
    - We edit this to `gcs_block = GcsBucket.load(bucket='zoom_gcs')`
- Once done writing it, run the flow via `python etl_web_to_gcs.py`
- Should see the completed flow in the terminal and in Orion, as well as the new directory containing the data in our GCS Bucket
- Next, we will take this data from this GCS Bucket and move it into a BigQuery data warehouse (or data lake)
- Once almost done writing `python etl_gcs_to_bq.py`, go to the GCP console, and go to "BigQuery" on the left
    - Click "Add" on the top left and choose "Google Cloud Storage"
    - To the right of "Select file from GCS bucket or use a URI pattern", click "Browse"
    - Click the arrow to the right of your bucket to see the parquet file, and select said file
    - Make sure "File format" is "parquet"
    - Then, under "Destination", create a new dataset called `de_zoomcamp`, and name the table `rides`, then click "Create table" at the bottom
    - Once it's done, you should see the project ID on the left in the Explorer, which we can expand to see our dataset, which we can expand to see our table
    - Double-click on the table to see the Schema
    - Then, from "Query" at the top, open a new tab, and drop the data in the table via ```TRUNCATE TABLE `[project ID].de_zoomcamp.rides` ```
    - Enter in the required arguments to `df.to_gbq()`
- Run `python etl_gcs_to_bq.py`
- Once the Prefect flow completes, check that we have data in a BigQuery Query tab/window via ```SELECT * FROM `[project ID].de_zoomcamp.rides` ``` or ```SELECT COUNT(*) FROM `[project ID].de_zoomcamp.rides` ```

## Parametrizing Flow & Deployments
- Next, we add Parameterization to our flows and create deployments by expanding upon `etl_web_to_gsc.py`
- This is building upon the existing flow and blocks that we have configured prior
- We are allowing our flows to take in parameters, so that when we schedule these flows, values aren't hard-coded (`color`, `month`, and `year` are passed at runtime)
- This allows multiple **flow runs** (instances of a flow) with different parameters
- We will also utilize **sub-flows**
     - Instead of runnning this for one month at a time, we will make a **parent flow** that will pass parameters to the ETL flow and we will set some defaults
     - This way, we're able to loop over a list of months and run the ETL pipeline for each dataset
        - i.e., Triggering this flow 3 times for 3 different months to get 3 instances of our single ETL flow all from one parent flow
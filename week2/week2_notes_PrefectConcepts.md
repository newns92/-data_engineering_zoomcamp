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
- So far, we've only been triggering flow runs via a terminal window
- Next, we want to utilize a **deployment** inside Prefect
    - https://docs.prefect.io/latest/concepts/deployments/
    - A **deployment** in Prefect = a server-side concept/component that *encapsulates* a flow, allowing it to be **scheduled and triggered via the API**
    - Using a deployment, we can have our flow code and a **deployment definition** which we send over to the Prefect API    
        - We can think of it as the container of metadata needed for the flow to be scheduled
            - This might be what type of infrastructure the flow will run on (Kubernetes, Docker, etc.), or where the flow code is stored (locally, GitHub, Docker, an S3 bucket), maybe it’s scheduled or has certain parameters, etc.
    - A single flow can have *multiple* deployments    
    - There are 2 ways to create a deployment 
        - 1. Using a CLI command (https://docs.prefect.io/latest/concepts/deployments/#create-a-deployment-on-the-cli) 
        - 2. With Python (https://docs.prefect.io/latest/concepts/deployments/#create-a-deployment-from-a-python-object)
- First, we will create a deployment via the CLI
    - In the Anaconda terminal, run `prefect deployment build ./parameterized_flow.py:etl_parent_flow -n "Parameterized ETL"`
        - The format is `prefect deployment build [file name]:[parent flow name/entrypoint to the flow] -n "Parameterized ETL"`
    - See that this creates a new `.prefectignore` file and a new YAML file with all of our details
        - *This* is the metadata 
        - We can adjust parameters here *or* in the UI after we **apply**
        - But let’s just do it here in the CLI
    - Edit the YAML file with `parameters: {"color": "yellow", "months" :[1, 2, 3], "year": 2021}`
    - Then, apply the deployment in the Anaconda terminal via `prefect deployment apply etl_parent_flow-deployment.yaml`
        - This tells the CLI to send all the metadata to the Prefect API to let it know we're scheduling/orchestrating this specific flow and how to orchestrate it
    - Once that finishes successfully, we should see the deployment at `http://127.0.0.1:4200/deployments`, as well as seeing a message saying that if we want to execute **flow runs** from this deployment, then we need to start an **agent** that pulls work from the 'default' work queue via `prefect agent start -q 'default'`
    - Back in the UI, we see that the deployment is "on" on the far right, as well as a hamburger menu (three dots) that let us trigger a flow run
    - Entering the flow by clicking on "Parameterized ETL" we could add a description if it wasn't specified in the YAML already (which it was (via the Python docstring???))
        - If we edit the description, we can give it a **work queue** or a **tag**, add a schedule, or change the default parameters
    - After exiting the description edit window, we can see that we can access the Runs of this deployment, as well as the parameters
    - On the top right, we see "Run"
        - "Quick Run" is just an instance of the default flow
        - "Custom run" is where we can customize the parameters for each individual run
    - Trigger a Quick Run, and notice on the bottom of the screen that we can click "View run"
    - We note that this is in a "scheduled" state (at the top of the screen in yellow)
    - The reason it is in this state is that Prefect knows that it is ready to run, *but we have no **agent** picking up this run!!*
        - i.e., We are now using the API to trigger and schedule flow runs with this deployment instead of manually, and we need to have an **agent** living in our execution environment (local)
    - Go to "Work Queues" on the far left
        - **Work queues** and **agents** are concepts in Prefect where an **agent** is a very lightweight Python process living in your execution environment (which right now, is our local machine)
        - That agent is pulling from a **work queue**, of which we can have many, and we can pause them as well
        - A deployment specifies where we want a flow to run by sending it to the work queue
            - Going back to "Deployments" on the far left, we can click on "Parameterized ETL" and see which work queue it is in on the far right
        - These are great especially if we want to run some flows locally, some on certain servers, or we have a cloud deployment as well (so we'd set up an agent on that cloud deployment, say in Kubernetes)
            - i.e., We can dictate what work goes where
    - Go back "Work Queues" on the left if need be, and enter the "default" work queue
        - Should see that this deployment/our upcoming run is "late"
        - Should see "Work queue is ready to go!" at the top along with some code to start an agent: `prefect agent start  --work-queue "default"`
        - Enter this code into the Anaconda terminal to start the agent
        - Notice this agent starts running the flow immediately, triggering it via a deployment with an agent
        - Should see the parent flow and all (3) sub-flows in the "Flow runs" menu in the Orion UI
    - Whether this would succeed or fail, we should set up some **notification** via the "Notifications" tab on the far-left
        - Now that we can trigger flow runs through deployments (setting them on a schedule and use an agent to orchestrate where in the execution environment they're going to run) instead of doing it manually, we want to set up notifications
        - In the Orion server UI, we want to create a new notification
            - These are based on the **states**
                - "Crash" indicates something is wrong with your infrastructure, not the flow itself
            - Choose the "failed" state
                - Could specify this for certain **tags** that we could've set for the flow/deployment
                - We can choose different **webhooks** to be notified by
        - Can also set notifications outside of the Orion UI, such as hard coding it via blocks or **collections** or something like that
        - Once a notification is set, we can turn them on/off
- Next, we'll do schedules and Docker storage with infrastructure

## Schedules & Docker Storage with Infrastructure
- Now, we will schedule flows and run them in Docker containers
- We have out Parameterized ETL deployment, and if we click on it in the Orion UI, we can see a "Schedule" option on the far right
    - Click "Add" to see the 3 types of schedules (intervals, Cron jobs, or Recurring Rule (or RRule))
        - RRule is a bit complicated to run in this UI
    - We could say, make it run every 5 minutes from the start date, and that will run so long as there is an agent to pick it up
- We can build a deployment for the `etl_parent_flow` flow named "etl2" with a specified schedule type (like `--cron`)from the (Anaconda `zoom` environment) CLI by, in the directory where `parameterized_flow.py` is located, running `prefect deployment build ./parameterized_flow.py:etl_parent_flow -n etl2 --cron "0 0 * * *" -a`, where `-a` is to apply the schedule
    - This cron text `"0 0 * * *" ` specifies to run every day at midnight
    - ***This creates a new `etl_parent_flow-deployment.yaml` file***
- This should successfully complete (green text in the CLI), and you should see it under "Deployments" in the Orion UI
- Toggle off/pause both of the current deployments that we have
- In a CLI, you can see how to build a deployment via `prefect deployment build --help`
- We can also set a schedule via the CLI *after* we've built the deployment with `--set-schedule` arguement
- So, schedules are easy to setup via the Orion UI or the CLI, and as long as there's an agent to pick them up and the Orion server or we're connected to Prefect Cloud (always running) , deployements will run as scheduled
- Now to run the flows in Docker containers
    - We've been running flows locally, but to have things running in a more production-like-setting way and to let other people have access to our flow code, we *could* put it up on some version control site like GitHub or BitBucket, or in S3 or GCS or Azure.
    - But we will store it in a **Docker image**, put it on DockerHub, and then when we run a Docker container, the code will be right there (we're baking it right into the image)
    - There's various ways to run Docker containers, but it's nice to bake in the code that we want *along* with some other things (like what pip packages to install, for example) into the image
    - First, make a `Dockerfile` in `week2/docker`, and once done, in the `week2/docker` dir, build the image via `docker image build -t [Dockerhub username]/prefect:zoom .`, where `-t` is how we tag the image, and we put the image in our account on Dockerhub tagged as `prefect:zoom`, and the `.` lets Docker know to use the local `Dockerfile`
    - Once we've successfully built the image, we need to push it to Dockerhub (*make sure you're logged in*)
    - Do this via `docker image push [Dockerhub username]/prefect:zoom`, and once it completes successfully, you should see the image at `https://hub.docker.com/r/[username]/prefect`
    - Next, we need to make a Docker Prefect block to use when we specify our deployment
    - In the Orion UI, go to "Blocks" and add a "Docker Container" block, name it "zoom"
        - We *could* put in some environment variables like pip packages, but it's quicker and easier to bake that into the image in the Dockerfile
    - Under "Image (Optional)", add in your Docker image `[Dockerhub username]/prefect:zoom`, and set "ImagePullPolicy" to "ALWAYS" so that we're always pulling the latest image
    - Set "Auto Remove (Optional)" to "True" to help keep things tidy (removes the container on completion), and finally click "Create"
    - See some code that we will use in our deployment:
        ```bash
        from prefect.infrastructure.docker import DockerContainer

        docker_container_block = DockerContainer.load("zoom")
        ```
    - *Can use `make_docker_block.py` to make the Docker Prefect block as well*
    - In the `week2/docker` dir, run `python docker_deploy.py`, and once it's done, you should see `etl-parent-flow/docker-flow` in your Deployments on the Orion UI
- Back to Prefect...
    - Running `prefect profile ls`, we'll see the Prefect profile we're using, which right now should be `*default`, which was installed with Prefect
    - Now, we want to make sure we now, instead of using the local, ephermeral API, that we use a specific API endpoint at a specific URL
    - We do this via `prefect config set PREFECT_API_URL="http://127.0.0.1:4200/api"` to allow the Docker container to interact with the Orion server
        - Could set other API URL's here, like if using Prefect Cloud
    - Start up an agent via `prefect agent start -q default` to look for work in the default work queue
    - Once that agent is running, we can run our flow in a separate Anaconda `zoom` environment (or in the Orion UI)
    - In the CLI, run `prefect deployment run etl-parent-flow/docker-flow -p "months=[1, 2]"`
        - With `-p`, we override the default parameters to run this flow for 
    - This will *not* run in our local machine/process in a subprocess, but instead will run in a Docker container
        - Should see this in the agent CLI logs and in the Orion UI
            - *Might have to hit some key in the agent CLI to get it running (?)*
        - In the Orion UI, go to Deployments and click on "docker-flow", and go to the "Runs" tab
        - Click on the current run for the deployment that we just started
        - Can watch the logs in real-time, as well as see the subflow runs and the parameters (which we changed)
            - Can also view the subflows and their specific logs, task runs, subflows, and parameters under "Flow Runs" in the Orion UI
        - Can then check the GCS Bucket that we've created earlier, and we should see the `data` dir, the `yellow` subdir, and the *two* parquet files
    - 

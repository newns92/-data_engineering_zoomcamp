# Introduction to Prefect Concepts

## Prefect
- **Prefect** = a modern open source dataflow automation platform that allows one to add observability and orchestration by utilizing Python to write code as **workflows** in order to build, run, and monitor pipelines at scale.

## Creating the environment
- Create a conda environment: `conda create -n zoom python=3.9`
- *In an Anaconda command window*, activate the environment: `conda activate zoom`
- Install the requirements found in `requirements.txt` via `pip install -r requirements.txt`
- Check `prefect version`
- Spin up the Postgres database via `docker-compose up -d` in the `week1/` directory
- Notice that the tables should have been loaded

## Prefect Flow and Scheduler
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
        - 

## Cloud setup
- First, upload the data to a GCS bucket via the `upload_all_data.py` file in the `week4/` directory
- Then, in BigQuery, create the external tables via:
    ```bash
        CREATE OR REPLACE EXTERNAL TABLE `de-zoomcamp-384821.ny_trips.external_yellow_trip_data`
        OPTIONS (
        format = 'PARQUET',
        uris = ['gs://de-zoomcamp-384821-taxi-data/data/yellow/yellow_tripdata_2019-*.parquet', 'gs://de-zoomcamp-384821-taxi-data/data/yellow/yellow_tripdata_2020-*.parquet']
        );

        CREATE OR REPLACE EXTERNAL TABLE `de-zoomcamp-384821.ny_trips.external_green_trip_data`
        OPTIONS (
        format = 'PARQUET',
        uris = ['gs://de-zoomcamp-384821-taxi-data/data/green/green_tripdata_2019-*.parquet', 'gs://de-zoomcamp-384821-taxi-data/data/green/green_tripdata_20209-*.parquet']
        );

        CREATE OR REPLACE EXTERNAL TABLE `de-zoomcamp-384821.ny_trips.external_fhv_trip_data`
        OPTIONS (
        format = 'PARQUET',
        uris = ['gs://de-zoomcamp-384821-taxi-data/data/fhv/fhv_tripdata_2019-*.parquet']
        );        
    ```
- Then, in BigQuery, create *non*-external tables via
    ```bash
        CREATE OR REPLACE TABLE `de-zoomcamp-384821.ny_trips.yellow_trip_data`
        AS
        SELECT * FROM `de-zoomcamp-384821.ny_trips.external_yellow_trip_data`;

        CREATE OR REPLACE TABLE `de-zoomcamp-384821.ny_trips.green_trip_data`
        AS
        SELECT * FROM `de-zoomcamp-384821.ny_trips.external_green_trip_data`;

        CREATE OR REPLACE TABLE `de-zoomcamp-384821.ny_trips.fhv_trip_data`
        AS
        SELECT * FROM `de-zoomcamp-384821.ny_trips.external_fhv_trip_data`;
    ```
- Then, check the row counts via
    ```bash
        SELECT COUNT(*) FROM `de-zoomcamp-384821.ny_trips.fhv_trip_data`;
        --- 43,244,696

        SELECT COUNT(*) FROM `de-zoomcamp-384821.ny_trips.yellow_trip_data`;
        --- 109,047,518

        SELECT COUNT(*) FROM `de-zoomcamp-384821.ny_trips.green_trip_data`;
        --- 7,778,101
    ```
- Then, create a free dbt Cloud account via https://www.getdbt.com/signup/
- Then, follow the instructions at https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/week_4_analytics_engineering/dbt_cloud_setup.md and https://www.youtube.com/watch?v=uF76d5EmdtU&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=31docker 
    - **Create a BigQuery service account**
        - First, create a client ID and secret key for authentication with BigQuery
            - This client ID and secret key will be stored in dbt Cloud to manage the OAuth connection between dbt Cloud users and BigQuery
        - Do this via by creating a BigQuery service account via the BigQuery credential wizard (https://console.cloud.google.com/apis/credentials/wizard) to create a service account in the taxi project
            - Select the BigQuery API as the API to use, then "application data", then "No, I'm not using them" for the last option
            - Name the service acccount `dbt-service-account`
            - Can either grant the specific roles the account will need (BigQuery Data Editor, Big Query Job User, BigQuery User) or simply use BigQuery Admin, as you'll be the sole user of both accounts and data
            - Ignore the last section, and click "Done"
        - Now that the service account has been created we need to add and download a JSON key
            - Go to the "Keys" section, and select "Add key", then "Create new key" 
            - Select key type "JSON", click "Create", and recieve a downloaded JSON file
    - **Create a dbt cloud project**
        - Create a dbt cloud account from their website (it's free for solo developers)
        - Once you have logged in into dbt cloud you will be prompt to create a new project
        - Name your project "Taxi Data" and under "Advanced Settings", set the directory to where we want to work with dbt (`week4_analytics_engineering/dbt_cloud`)
        - Choose BigQuery as the data warehouse
        - Upload the key JSON file you just downloaded under the "Upload from file" section for "Settings"
            - This will fill out most fields related to the production credentials
        - Scroll down to the end of the page and set up your development credentials
            - Enter your personal development credentials here (*not* deployment credentials!). 
            - dbt will use these credentials to connect to the database on your behalf
            - When ready to deploy a dbt project to production, you'll be able to supply your production credentials separately
            - The dataset you'll see under "Development Credentials" is the one you'll use to run and build models during development
            - Since BigQuery's default location may not match the one you used for your source data, it's recommended to create this schema manually to avoid multiregion errors
            - Name the dataset "ny_trips_dev", and set the target to "ny_trips"
        - Click "Test connection" to make sure we can connect
        - For "Setup a repository", select "Git Clone"
            - Add the SSH for the GitHub repo you are using and click "Import"
            - You will get a **deploy key**
            - Go to the GitHub repo and go to the "Settings" tab
            - Under "Security", you'll see the menu "Deploy keys" on the left
            - Click on "Add deploy key" and paste in the deploy key provided by dbt Cloud, while **making sure to check on "write access"**
            - *You could simplify the process of adding and creating repositories by linking your GitHub account* (https://docs.getdbt.com/docs/cloud/git/connect-github)
    - **Review your project settings**
        - Checkout the `dbt` branch in the project within the dbt Cloud IDE
        - Click "Initialize dbt project"
        - Commit the changes
        - Open a PR
- Once you have initialized the dbt project in the cloud, in `dbt_project.yml`, change the project name to `taxi_data`, but keep the profile `default` and leave the defaults for where our different files are located (under the `# These configurations specify where dbt...` section/comment)
    - The `profile` will define/configure which data warehouse dbt will use to create the project
    - Again, we could have one dbt project, and by changing the profile, we could change where we run the project (from Postgres to BigQuery or vice versa, for example)    
- Then, under `models:` near the bottom of `dbt_project.yml`, change it's value from `my_new_project` to `taxi_data`
- Then, since we're not using it yet, delete the `example: +materiliazed: view` part of the YAML file
- Can also note that in the `models/` directory, we can see some sample models with basic DAGs already set up
    - But we don't worry about this, as we will create our own models

## Creating the model
- Create a `staging/` subdirectory under the `models` directory
    - This is where we take in the raw data and apply some transforms if needed
- Create a `core/` subdirectory under the `models` directory
    - This is where we'll create models to expose to a BI tool or to stakeholders
- Under `staging/`
    - Create a new file: `stg_green_trip_data.sql`
    ```bash
        -- create views so we don't have the need to refresh constantly but still have the latest data loaded
        {{ config(materialized='view') }}

        {# SELECT * FROM {{ source([source name from schema.yml], [table name from schema.yml]) }} #}
        select * from {{ source('staging', 'green_trip_data') }}
        limit 100
    ```
    - Create a `schema.yml` file
    ```bash
        version: 2

        sources:
        - name: staging
            database: de-zoomcamp-384821  # i.e., the dataset (Project ID) in BigQuery
            schema: ny_trips  # the dataset itself

            tables:
            - name: green_trip_data
            - name: yellow_trip_data    
    ```
- Run `dbt run -m stg_green_trip_data` in the terminal at the bottom of the dbt Cloud IDE
- Then, change the `SELECT` statement to run with the new column definitions to make all column names consistent
- Then, can run `dbt run --select stg_green_trip_data`, which is equivalent to `dbt run -m stg_green_trip_data`
- Should see the new view under `ny_trips_dev` in BigQuery (since *that's what we named the dataset to be when we defined the project*)
- Can also see compiled code under `target/compiled`


## Macros
- These are similar to functions and are written in Jinja and SQL
- dbt has many build in macros (`config()`, `source()`), and we can define our own
- They return code, and are in the style `{% macro [macro name]([parameter(s)]) -%}   [some code]   {%- end macro %}`
- Helpful if we want to maintain the same type of transformation in several different models
- We create the `get_payment_type_description` macro under the `macros` subdirectory of the project in the `get_payment_type_description.sql` file
- We then use it in our `stg_green_trip_data.sql` model file and run it again via `dbt run --select stg_green_trip_data`
- Will then see the updated compiled code in `target/compiled` and the updated staging table in BigQuery's `ny_trips_dev`


## Packages
- Imported in the `packages.yml` file, *which you create* in the main dir of the project, and imported via `dbt deps`
- Can call them similar to library functions: `{{ [dbt package].[macro name]([parameter(s)]) }}`
- We are importing `dbt_utils` from dbt labs
- Create the `packages.yml` file and add in:
    ```bash
        packages:
        - package: dbt-labs/dbt_utils
            version: 0.8.0
    ```
- Then run `dbt deps` in the terminal at the bottom of the Cloud IDE
- Can view installed packages in the `dbt_packages/` subdirectory of the project, and see its own `macros/` subdirectory to see all of its macros
- We then create a **surrogate key** via `{{ dbt_utils.surrogate_key(['vendorid', 'lpep_pickup_datetime']) }} as tripid,` in our staging table model
- Run the model again via `dbt run --select stg_green_trip_data`, and again see the updated compiled code in `target/compiled` and the updated staging table in BigQuery's `ny_trips_dev`


## Variables
- Same as any other programming language
- Useful for defining values that should be used across the project
- With a macro, dbt allows us to provide data via variables to models for translation during compilation
- To use a variables, use the `{{ var('...')}}` function/macro
- Can do this in the CLI `via:
    ```bash
        -- dbt build -m [model.sql] --var 'is_test_run: false'
        {% if var('is_test_run', default=true) %}

            limit 100
            
        {% endif %}
    ```
- Add the above to the end of the `stg_green_trip_data.sql` model
- We can run our model and change the value of `is_test_run` using the command `dbt run --select stg_green_trip_data.sql --var 'is_test_run: false'` and you should NOT see `limit 100` in the compiled code
- Just running `dbt run --select stg_green_trip_data` should give the default value of `true` and you should see `limit 100` in the compiled code


## Yellow Taxi
- Create the `stg_yellow_trip_data.sql` model with a few changes from the `stg_green_trip_data.sql` model
- Then run *both* models it via `dbt run --var 'is_test_run: false'`
- Check for the new compiled code and the views in BigQuery


## Seeds
- These are CSV files that we can have in our repo and then run and use as tables via a **Ref macro**
- Meant to be used for smaller files that contain data that won't change often
- Cannot be loaded in the Cloud UI
- If done locally, can just copy the CSV to the `seeds/` subdirectory of the project
- In the cloud, you can add the file to the GitHub repo and then pull it into the dbt Cloud UI
    - Or just create the CSV in the Cloud UI and paste in the exact contents
- Once the CSV is there, run `dbt seed`, which will create the table in the data warehouse and will define for each of the fields, the data type that it corresponds to
- Once you run `dbt seed`, you should see the table in BigQuery
- However, we can define the data types ourselves in the `dbt_project.yml` file
- Here's an example of explicilty defining one column's data type, leaving the rest as defaults:
    ```bash
        seeds:
            taxi_data:
                taxi_zone_lookup:
                    +column_types:
                        locationid: numeric
    ```
- Run `dbt seed` again, you should see the updated table in BigQuery
- Now let's say we want to change some value in our data, like changing "EWR" to "NEWR"
- `dbt seed` will then *append* to things we've already created
- So, instead run `dbt seed --full-refresh` to drop and recreate the table
- Now, we can create a model based on this seed
    - Under `models/core/`, create a file `dim_zones.sql`
    - Here, we will first define the config as a materialized *table* rather than a view like we have been doing thus far in our models
        - Ideally we want everything in `models/core` to be a table, since this is what's exposed (to BI tools and/or to stakeholders)
    - Add the SQL to create the dim table
    - Before runnning this model, create a new one called `fact_trips.sql`
        - In here, we'll take both the staging yellow and staging green data and UNION them
    - Once `fact_trips.sql` is done, we can run `dbt run` which will run all of our models, *but not the seed*
        - To run the seed as well, run `dbt build` to build everything that we have, along with running some tests
    - Say we just want to run `fact_trips.sql`, we'd run `dbt build --select fact_trips.sql`
        - But to run everything that `fact_trips.sql` depends on first, we can run `dbt build --select +fact_trips.sql`


## Testing
- Create the `dm_monthly_zone_revenue.sql` file in `models/core`
- In the `staging/schema.yml` file, add the model descriptions, along with their column descriptions and some defined tests on each
    - Those tests with `severity: [severity]` will ask if dbt should keep running if it fails or not, or should it stop entirely
        - `severity: warn` means everything will run but it will give warnings at the end
        - `severity: never` means it will stop immediately
- Add the necessary section to `dbt_project.yml`
    ```bash
        vars:
            payment_type_values: [1, 2, 3, 4, 5, 6]
    ```
- Finally, run `dbt test` (which would run on all deployed models)
    - can run on a specific model via `dbt test --select [model.sql]`
    - can run on a specific model and its children via `dbt test --select [model.sql]+`
    - can run on a specific model and its ancestors via `dbt test --select +[model.sql]`
    - Also, `dbt build` would run *everything* we have in our project (seeds, test, and models)
- Might see that `tripid` is not unique as a warning after running `dbt test`, so add some de-duplication logic to both staging tables, then run `dbt build`
- Finally, add the `schema.yml` for the `models/core/` models
- Could even document seeds or macros if you wanted to


## Deployment
- At the top of the Cloud IDE, go to "Deploy" -> "Environments"
    - We should see a DEV environment that was created from the initial dbt Cloud setup
    - We then create a PROD environment named "Production" with a type of "Deployment" with the latest dbt version (1.4 to match the DEV environment as of 05/07/2023)
    - We then name the dataset we want to connect to: "ny_trips_prod"
- Then go to "Deploy" -> "Jobs"
    - https://docs.getdbt.com/docs/quickstarts/overview#create-a-new-job
    - https://discourse.getdbt.com/t/best-practices-for-cicd-deployment/618
    - Create a new job: "dbt build", make sure it's in the "Production" environment, inherit the dbt version from the environment, and leave the target as "default" to mean our target is the PROD database we defined when creating the environment
    - Check off to create docs, and we haven't defined a source freshness yet, so it doesn't make sense to check that off just yet
    - For commands to run, put:
        - `dbt seed`
        - `dbt run`
        - `dbt test`
    - Then, to schedule, we could use a CRON job, or every day, or any specific day and hour. We will do every day, every 6 hours
    - ~~Under the "webhooks" tab is where we can make this job run on a PR~~
    - Save the job, and then run it
    - Once it successfully completes, you should see all the tables in BigQuery in the PROD dataset
    - In the dbt Cloud IDE, you can click on the completed job to see the steps run under "Run Timing"
        - First, we see it cloned the repo for the main branch, then created the connection to BigQuery
        - It then ran `dbt deps` to make sure it always has the latest packages that we defined, and then it ran the dbt CLI commands we specified
        - We can see console and debug logs, and can download both
    - Under "Model Timing", we can see model timing, and under "Artifacts", we can see the compiled code (and the documentation as `manifest.json`)
    - There is also a "View documentation" button the top of the screen that takes you to a webpage with your docs: definitions, dependencies, test, macros, references, code, and compiled code
        - Should see that the compiled code for the `core/` models is connecting to `ny_trips_prod`
        - Can also access see the lineage graph on the bottom-right
            - Which you can full-screen to get a full DAG/lineage graph
            - Here, you can also play around with different `--select` arguments to see how the lineage graph changes
- We can then go to "Account Settings" and open the project
    - We can then click "Edit" and under "Artifacts", add/link our documentation from the `dbt taxi build` job
    - Refresh the dbt Cloud IDE, and then the "Documentation" tab at the top of the IDE should take you to this documentation


## BEFORE VISUALIZATION
- *Cloud*
    - Add *ALL* data via `dbt build --var 'is_test_run: false'` in the dbt Cloud for DEV
    - In the Job, edit `dbt run` to be `dbt run  --var 'is_test_run: false'` for PROD
- *Local*
    - Add *ALL* data via `dbt build --vars "is_test_run: false" --profiles-dir=../` in the CLI for DEV
    - Add *ALL* data via `dbt build -t prod --vars "is_test_run: false" --profiles-dir=../` in the CLI for PROD


## Visualization
- **Google Looker**
    - Go to https://lookerstudio.google.com/u/0/navigation/reporting
    - "Create" a "Data Source", choose BigQuery
    - Next, we'll be able to see our projects, so choose the correct one and then choose the PROD dataset, and select the `fact_trips` table, and click "Connect"
    - We now see all of our columns, with the option to do some default aggregations and write some descriptions, if desired
        - *Make sure just `passenger_count` has a sum on it*
        - Under "Metrics", we see the default of record count, which is useful to see how many trips we're looking at
        - We also could create our own fields here, but we will do that later
        - We can also define data freshness at the top of the webpage, as well as change the name of the table from `fact_trips` in the upper-left (which we should do if presenting to stakeholders who are not aware of dimensional modeling terms)
    - Click "Create report"
        - Remove the default table Looker places in the report
        - Go to "Add a chart", and select a "Sparkline" chart under "Time series", and see that Looker automatically populates it with a dimension (`pickup_datetime`) and metric (`Record count`)
        - Add a **breakdown dimension** of `service_type` to see the chart broken out by "Yellow" and "Green"
        - Change the chart to a normal "Time series" chart
        - If any outliers popped up in your data (years beyond what the data contains, for example), Looker has some **controls** like "Date range" controls
            - So, add the control and set the date range to 1/1/2019 to 12/31/2020
        - Can also add **filters** under the "Style" tab on the right
            - Or play around with different settings like grid type, background colors, borders, etc.
        - Can add text boxes to be chart titles
        - Let's now add a "Scorecard with compact numbers" chart, and remove the dimension that's automatically added to see the total number of records (in the current date range)
        - Next, add a pie chart to see service type distribution (Should happen automatically), and remove the dimension (also removes the filter since there's nothing to filter on)
        - We can note the dominance of yellow taxis (pie chart) as well as the huge drop in rides in Mar. 2020 due to COVID (line chart)
        - Add a "Table with heatmap", remove the date range dimension, and change the dimension to `pickup_zone` for trips per pickup zone
        - Then, for trips per month, add a "Column chart", then change the dimension to `pickup_datetime` and remove the breakdown dimension
            - We will now add (create) a new field to allow us to filter by month
            - Call it `pickup_month` and add the formula `MONTH(pickup_datetime)`
            - Then save it, click "Done", then add it as the dimension
            - But, we know there is a big discrepency between 2019 and 2020, so we want to drill down by year
            - Create `pickup_year` and add the formula `YEAR(pickup_datetime)`, and add it as the breakdown dimenstion
            - Make sure the bar chart is sorted by `pickup_month` and not `Record Count`, and remove the second sort
            - Then, under "Style", make sure there are 12 bars, one per month
        - Now, *change this to a stacked column chart*
        - Then, add a new control: a drop-down list, and make the dimension `service_type`
        - Finally, title the report "Taxi Trips Analysis: 2019-2020"
    - In the upper-right, can click "View" to preview it in an interactive mode
    - Can then either go back into "Edit" mode, or share the dashboard/report by inviting people to it, sharing a link, downloading the dashboard/report as a PDF, or scheduling an email with it (like sending it every Monday with the last week's data)
        - https://lookerstudio.google.com/s/lWmNXPZMwb4
- **Metabase**
    - When using a local environment like Postgres, we can't use Looker Studio
    - Metabase also has a cloud solution, but they also have an open-source solution that is free to use and install locally
    - Go to https://www.metabase.com/start/oss/
        - Get the Dockerfile from DockerHub via `docker pull metabase/metabase:latest` in the `dbt_local/` directory
        - Then run `docker run -d -p 3000:3000 --net=pg-network --name metabase metabase/metabase` *while the Postgres instance is running/available*, since that's what we're connecting to (*we specify the network*)
        - OR you can use the `.jar` file locally in order to run Metabase
    - Once you run `docker run`, check that it's running with `docker ps`
    - Once you have everything running, open `localhost:3000` in a browser
    - Set everything up by choosing a language, creating a profile, then creating the database connection to `localhost` with the Display name "Taxi Postgres", port `5432`, database name `ny_taxi`, username and password `root`, and "All" schemas.
    - At first, it will ask for some things for the initial settings, such as user and the connection to the database, and which database to use exactly
    - You should then be able to see your schemas (`public`, `staging`, `prod`) and each table within the schema
    - Once you select a table, Metabase tiles will be generate some **tiles** and filters about the table automatically
    - We will also see distributions of each of our columns
    - Can click "" at the bottom of the screen to see some time series and some other distributions
    - This is helpful to do EDA, especially if the data is new to us
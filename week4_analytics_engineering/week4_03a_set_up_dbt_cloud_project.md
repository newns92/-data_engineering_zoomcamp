# Starting a dbt Project in the Cloud

## Creating a dbt Project
- dbt provides a starter project with all basic files and folders at https://github.com/dbt-labs/dbt-starter-project
- A dbt **project** includes the following files:
    - `dbt_project.yml`: a file used to *configure* the dbt project
        - Defines things like the project name, different connections, where to store files, and other global configurations
            - So, we can set the project name to something like `ny_taxi_data` and profile name also to `ny_taxi_data`
        - We could have a dbt project, and by changing the *profile*, we could change *where* we run the project (from Postgres to BigQuery or vice versa, for example)
    - **Models**
        - Includes staging, core, and a datas marts models
        - Every model will be a view or a table, *unless indicated otherwise*
    - **Snapshots**:  are a way to capture the state of your mutable tables so you can refer to it later.
    - **Macros** that contain blocks of code that you can reuse multiple times
    - **Seeds**: CSV files with static data that you can load into your data platform with dbt
    - **Test**: SQL queries that you can write to test the models and resources in a dbt project
    - CSV files in the `data/` folder, which will be our **Sources**
    - For more information, see: https://docs.getdbt.com/docs/build/projects

- There are 2 ways to use dbt:
    1. With the CLI
        - After having installed dbt Core locally and setting up the `profiles.yml` files, in a terminal, run `dbt init` *within the path that we want to start the project in order to clone the starter project*
    2. With dbt Cloud
        - After having set up dbt Cloud credentials (consisting of a GitHub repo and a data warehouse), start the project from the web-based IDE


## Setting up a dbt Project in the Cloud
- Official documentation can be found at https://docs.getdbt.com/guides
- First, create a BigQuery service account specifically for dbt
    - In order to connect to dbt Cloud, we need a service account JSON file generated from BigQuery
        - Open the BigQuery credential wizard to create a service account in your NY taxi project: https://console.cloud.google.com/apis/credentials/wizard
            - Select the "BigQuery API" from the "APIs" drop-down
            - Select "Application data" as the type of data you will be accessing
            - Choose to create a *new* service account when prompted about using an existing one
            - Name it `dbt-service-account` and give it a description like "Service account for dbt Cloud"
            - For *roles*, you can either grant the specific roles the account will need or simply use "BigQuery Admin", as you'll be the sole user of both accounts and data
                - For specific roles, select "BigQuery Data Editor", "BigQuery Job User", and "BigQuery User"
                    - *\***NOTE**: If you decide to use specific roles instead of "BigQuery Admin", you may also need to add the "BigQuery Data Viewer" role to avoid encountering any denied access errors*
        - Skip the 3rd step and click "Done"
        - Now that the service account has been created, we need to create and download a JSON key
            - Click on the service account to open up its UI (or "Edit" on the far right of the page)
            - Go to the "Keys" tab at the top section, and select "Add key" and then "Create new key"
            - Select a key type of JSON, click "Create", and immediately see it being downloaded locally
- Next, open a free Developer dbt Cloud account at https://www.getdbt.com/signup/
- Once you have logged in into dbt Cloud, you will be prompted to create a new project
    - To do so, you need access to your (BigQuery) data warehouse and admin access to the GitHub repo where you will have the dbt project
    - Click "Create New Project", and name it `ny_taxi_data`
        - Then, cascade down "Advanced Settings" and input the project subdirectory in your GitHub repo (say, `week4_analytics_engineering/dbt_cloud`, for example)
            - *\***NOTE**: You have to add a "Project subdirectory" in the project settings if your dbt project code will be hosted in a subdirectory of your GitHub repo*
        - For Connection, click the "Select" drop-down, and select "+ Add a new connection" to open up the connection details page
            - Choose BigQuery as your warehouse connection
            - Give the connection a name like `BigQuery-dbt-zoomcamp2025`
            - Then, upload the JSON key from earlier under the "Upload a Service Account JSON file" option
            - This will fill out most of the fields related to the production credentials
            - Then click "Save" in the top right of the page
        - Afterwards, back in the project creation tab/screen, see your *development credentials* as the next section
            - *The "Dataset" you'll see under the development credentials is the one you'll use to run and build your models during development*
            - Give it a name if you prefer, such as `dbt_ny_taxi_zoomcamp2025`
                - *\***NOTE**: Since BigQuery's default location may not match the one you used for your source data, it's recommended to create this schema manually to avoid multiregion errors*
            - Then click "Test connection", and if passed, click "Save"
        - Then, in the "Setup a repository" section, select "git clone" as the option, and paste in the SSH key from your GitHub repo for the course
            - Then click "Import"
            - You will then be provided with a **deploy key**
            - In a browser, head to your course GitHub repo, and go to "Settings" 
            - Under "Security" on the right-hand side, click see "Deploy keys"
            - Then, click on "Add key", name it something like `dbt-zoom25-deploy`, and paste in the deploy key provided by dbt Cloud and *make sure to check off the "write access" box*
            - Finally, click "Add key" to save it
        - Back in on the dbt Cloud page, click "Next" to create the project    
    - **WARNING: User API Keys are being deprecated in dbt Cloud**
        - They highly recommend that API keys be replaced with the more secure account-scoped **Personal Access Tokens (PATs)** for improved account security
        - See documentation for help and please contact support if any issues arise: https://docs.getdbt.com/docs/dbt-cloud-apis/user-tokens
    - Once the project is opened in the IDE, initialize the project
    - Then, "commit and sync" the changes to the `master` branch
    - Then, create a new branch `dbt` in git or in the dbt Cloud IDE for dbt development, and dbt Cloud will automatically switch to this new branch
    - In the dbt Cloud IDE, open up `dbt_project.yml`
        - Rename the project to something like `ny_taxi_data`
        - Keep the profile as `default` and leave the defaults for where our different files are located (under the `# These configurations specify where dbt...` section/comment)
        - Also update the `models` part of the code like so:
            ```YML
                models:
                    ny_taxi_data:
                        # # Applies to all files under models/example/
                        # example:
                        #   +materialized: table
            ```
            - Since we're not using this code *just yet*, we can comment it out
        - We can also note that in the `models/` directory, we can see some sample models with basic DAGs already set up
            - But don't worry about this, as we will create our own models later
        - Finally, save the file and commit to GitHub via the dbt Cloud IDE
        - Then, create a Pull Request and **merge** the changes to the `master` branch on GitHub

# Starting a dbt Project in the Cloud

## Creating a dbt Project
- dbt provides a starter project with all basic files and folders at https://github.com/dbt-labs/dbt-starter-project
- A dbt **project** includes the following files:
    - `dbt_project.yml`: a file used to *configure* the dbt project
        - Defines things like the project name, different connections, where to store files, and other global configurations
            - So, we can set the project name to something like `taxi_data` and profile name `taxi_data`
        - We could have a dbt project, and by changing the *profile*, we could change *where* we run the project (from Postgres to BigQuery or vice versa, for example)
    - **Models**
        - Includes staging, core, and a datamarts models
        - Every model will be a view or a table, *unless indicated otherwise*
    - **Snapshots**, which are a way to capture the state of your mutable tables so you can refer to it later.
    - **Macros** that contain blocks of code that you can reuse multiple times
    - **Seeds**, which are CSV files with static data that you can load into your data platform with dbt
    - **Test**, which are SQL queries that you can write to test the models and resources in a dbt project
    - CSV files in the `data/` folder, which will be our **Sources**
    - For more information, see: https://docs.getdbt.com/docs/build/projects

- There are 2 ways to use dbt:
    1. With the CLI
        - After having installed dbt locally and setup the `profiles.yml` files, in a terminal, run `dbt init` *within the path that we want to start the project in order to clone the starter project*
    2. With dbt Cloud
        - After having set up dbt Cloud credentials (consisting of a GitHub repo and a data warehouse), start the project from the web-based IDE


## Setting up a dbt Project in the Cloud
- Official documentation can be found at https://docs.getdbt.com/guides
- First, create a BigQuery service account specifcally for dbt
    - In order to connect to dbt Cloud, we need a service account JSON file generated from BigQuery
        - Open the BigQuery credential wizard to create a service account in your taxi project: https://console.cloud.google.com/apis/credentials/wizard
            - Select the "BigQuery API" from the "APIs" drop-down
            - Select "Application data" as the type of data you will be accessing
            - Choose to create a *new* service account when prompted about using an existing one
            - Name it `dbt-service-account` and give it a description like "Service account for dbt Cloud"
            - For *roles*, you can either grant the specific roles the account will need or simply use "BigQuery Admin", as you'll be the sole user of both accounts and data
            - For specific roles, select "BigQuery Data Editor", "BigQuery Job User", and "BigQuery User"
                - Note: If you decide to use specific roles instead of "BigQuery Admin", you may also need to add the "BigQuery Data Viewer" role to avoid encountering any denied access errors
        - Now that the service account has been created, we need to add and download a JSON key
            - Click on the service account to open up its UI
            - Go to the "Keys" tab at the top section, and select "Create new key"
            - Select a key type of JSON, click "Create", and immediately see it being downloaded locally
- Next, open a free Developer dbt Cloud account at https://www.getdbt.com/signup/
- Once you have logged in into dbt Cloud, you will be prompted to create a new project
    - To do so, you need access to your (BigQuery) data warehouse and admin access to the GitHub repo where you will have the dbt project
    - Click "Create New Project", and name it `ny_taxi_data`
        - Choose BigQuery as your connection
        - Then, upload the JSON key from earlier unde the "Upload from file" option
            - This will fill out most of the fields related to the production credentials
            - Afterwards, to see your *development credentials*, scroll to the bottom of this webpage
                - *The dataset you'll see under the development credentials is the one you'll use to run and build your models during development*
                - Since BigQuery's default location may not match the one you used for your source data, it's recommended to create this schema manually to avoid multiregion errors
        - Then click "Test connection", and if passed, click "Next"
        - Then, select "git clone" as the option, and paste in the SSH key from your GitHub repo for the course

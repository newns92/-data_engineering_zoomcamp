# dbt

## What is dbt?
- **dbt** stands for "data build tool"
- The offer free courses: https://learn.getdbt.com/catalog
- It is **a transformation tool that allows anyone that knows SQL (and maybe some Python) to deploy analytics code following *software engineering (SWE) best practices* (like *modularity*, *version control*, *Don't Repeat Yourself (DRY) principles*, *portability*, *CI/CD*, and *documentation*)**
- After doing the extracting and the loading of data into a data warehouse (ELT), we need to **transform** all this raw data to later expose and present it to stakeholders, and to be able to perform analysis on it
    - Our data will likely come from various disparate sources, like both backend and frontend systems, 3rd-party data, apps, etc.
- dbt will help us transform the data *inside* the data warehouse, as well as introduce good SWE practices by defining a **development workflow**: **develop** the models, **test** and **document** them, and then go through the **deployment** phase (i.e., version control and CI/CD)
- We do this by adding a **modeling layer** to our workflow, where we *transform* raw data into a **derived dbt model** that's persisted *back into* the data warehouse
    - i.e., dbt will be sitting *on top* of the data warehouse to help us transform the data, so that it can be exposed and presented to stakeholders, BI tools, machine learning (ML) workflows, or other applications
- Again, a nice thing about dbt is that it introduces good SWE practices into an analytics workflow
    - It introduces the different layers of a typical SWE workflow (Development, testing, and production environments)
    - Different developers will have their own sandbox/development environment for specific projects


## How Does dbt Work?
- Each dbt **model** is:
    1. A `*.sql` file
    2. A `SELECT` statement with *no* Data Definition Language (i.e., DDL, which defines the structure/schema of the database) *nor* Data Manipulation Language (i.e., DML, which helps deal with managing and manipulating data in the database)
    3. A file that dbt will compile and run against our data warehouse (via a `dbt run` command)
        - It will compile the DDL/DML file and push that compute to our data warehouse in order to see our new table/view(s)
        - dbt abstracts complexity away for the developer to focus on the SQL
- Again, we turn data warehouse *tables* into *models*, by transforming raw data from data warehouse tables into **derived dbt models**, which then *persist* back to the data warehouse


## How to Use dtb?
- You can use dbt in 2 main ways:
    1. **dbt Core**: Open-source and free-to-use project that allows data transformation
        - This is the essence of dbt, which builds and runs a **dbt project** (SQL and YML files)
        - It includes SQL compilation logic, **macros** (i.e., functions), and database adapters
        - It includes a CLI to run dbt commands *locally*
    2. **dbt Cloud**: SaaS application to develop and manage dbt projects in a similar manner to dbt Core
        - This is a web-based IDE to develop, run, and test a dbt project
        - It is free for individuals (one developer seat per account)
        - It has :
            - **Managed environments**
            - Job(s) **orchestration**
            - **Logging** and **alerting**
            - Integrated/hosted **documentation**
            - Admin and metadata API's
            - A **semantic layer**
                - A metadata and abstraction layer built on the source data (e.g. data warehouse, data lake, or data mart)
                - A business representation of data that offers a unified and consolidated view of data across an organization
                - With a semantic layer, different data definitions from different data sources can be quickly mapped for a unified, consistent, and single view of data for analytics and other business purposes. 
                    - https://www.atscale.com/glossary/semantic-layer/


## How Will We Use dbt?   
- To use dbt in **BigQuery**:
    - You do development using the dbt Cloud IDE
    - There is *no* local installation of dbt Core
- To use dbt in a local database like **Postgres**:
    - You do development using a local IDE of your choice
    - You use a local installation of *dbt core*, connecting to a *local* database (like Postgres)
        - Note that you *cannot* connect a *local* database to dbt *Cloud*
    - You will be running dbt models through a CLI
- In the end, we'll have the taxi trip data loaded into our database/GCS Bucket (along with a CSV file for the taxi zones) as *raw* data
- We will then transform this raw data into *transformed* data via dbt within our BigQuery (or Postgres) data warehouse
- In the end, we'll be able to expose this transformed data to a dashboard tool

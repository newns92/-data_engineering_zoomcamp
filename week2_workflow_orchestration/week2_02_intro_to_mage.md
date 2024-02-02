# Intro to Mage
- In this section, we'll introduce the Mage platform
- We'll cover what makes Mage different from other orchestrators, the fundamental concepts behind Mage, and how to get started
- To cap it off, we'll spin Mage up via Docker and run a simple pipeline

## What is Mage?
- Mage was built with the developer experience in mind (flow states, feedback loops, cognitive loads, etc.) 
- It was developed in order to minimize cognitive load and to improve the ability to iterate quickly on pipelines and build data workflows with software engineering best practices in mind
- **Mage** is an open-source pipeline tool for orchestrating, transforming, and *integrating* data
    - By "integrating", we mean using a solution like Airbyte or Fivetran to take data from one source to another
- Main Mage concepts:
    - **Projects**
        - Forms the basis for all the work you can do in (can think of it like a GitHub repo)
        - Your homebase/overall unit of an environment
        - Contains the code for all of pipelines, blocks, and other assets
        - Can have multiple projects within a single instance
    - **Pipelines**
        - Workflows that execute some data operation (maybe extracting, transforming, and loading data from an API)
        - Also called DAGs or data workflows
        - Each project can have as many pipelines as needed
        - In Mage, pipelines can contain Blocks (written in SQL, Python, or R) and charts
        - Each pipeline is represented by a YAML file in the “pipelines” folder of a project
    - **Blocks**
        - These comprise pipelines
        - They are the resuable, atomic units that make up a Mage transformation and perform a variety of actions, from simple data transformations to complex ML models
        - They are files that can be executed independently or within a pipeline
        - Can be written in arbitrary Python, SQL, or R
        - Together, they create DAGs, which are called "pipelines" in Mage
        - Can do whatever you want, but are usually used to extract/export, transform, and load data
        - *A block won’t start running in a pipeline until all its upstream dependencies are met*
        - Changing one block will change it everywhere it’s used, but don’t worry, it’s easy to detach blocks to separate instances if necessary
        - Blocks can be used to perform a variety of actions, from simple data transformations to complex ML models
    - Load
    - Transform
    - Export
- Mage has some unique out-of-the-box functionality, including:
    - Sensors = blocks that can trigger on some event
    - Conditionals = blocks with branching or if/else logic
    - Dynamics = blocks can create dynamic children
    - Webhooks = blocks for additional functionality
- Mage also has:
    - Data integration
    - Unified pipelines (or the concept of passing objects between data pipelines)
    - Multi-user environments
    - Templating
    - And more
- Mage has a unique UI for editing, building, developing, and sharing pipelines
- Mage accelerates pipeline development via:
    - Hybrid environment
        - Can use their GUI for interactive development (or don’t, and just use an editor like VSCode and just sync to the Mage UI)
        - Use **blocks** as testable, reusable pieces of code, ideal for software engineering best practices
    - Improved Developer Experience (DevEx)
        - Code *and* test *in parallel*
        - Reduce your dependencies, switch tools less, and to be efficient
- Mage has a lot of software engineering best practices built-in:
    - In-line testing and in-line debugging in a familiar, notebook-style format
    - Fully-featured observability
        - Integration allows transformation in *one place*: dbt models, streaming, batch, & more are all integrated
    - DRY (Don't Repeat Yourself) principles
        - No more messy, spaghetti code-style DAGs with duplicate functions and weird imports, such as in Airflow
- The whole point of this improved developer experience and tooling is to **reduce time spent in *undifferentiated* work**
    - Differentiated work produces *tangible* outcomes
    - Undifferentiated work includes setups, configurations, etc.


## Configuring Mage
- See the instructions at https://github.com/mage-ai/mage-zoomcamp
- We are basically cloning this repo, making sure we ignore `.env` files to avoid committing secrets to GitHub, and then running `docker compose build` (*Make sure the Docker daemon (i.e., Docker Desktop) is running*) to build an **image** for our project
    - To pull the most recent Mage image (say if you see "update" in the Mage UI), run `docker pull mageai/mageai:latest` to pull the latest image from the Mage repo
- We start the container based on this image via `docker compose up` to kick off the services in `docker-compose.yml` and start running them locally
- Then, we nagivate to http://localhost:6789 in a browser, we're ready to get started with this part of the course


## A Simple Pipeline
- In the Mage UI, navigate to "Pipelines" on the left-hand side
- Notice there is an example pipeline in our `magic-zoomcamp` project (see the top-left of the UI for the project name)
- Open this pipeline and see that we are doing a simple read of some data from an API, filling in some missing values, then exporting to a local **dataframe**
- Navigate to the "Edit pipeline" menu on the left-hand side to see all the projects in the file
- Notice the `load_titanic.py` file (*our first Mage **block**) under the `data_loaders` directory in the project file tree
    - Here, we're reading data from an API into a CSV and then check that the dataframe is not `None`
    - Can run the file in the top-right of the UI, and notice we end up with 891 rows and 12 columns
- The next block is a transformation step in the `transformers` directory called `fill_in_missing_values.py`
    - Run this as well
- Notice on the right-hand side of the UI, in the diagram, that these blocks are connected by a line/pipe
    - This indicates that the output dataframe from the load block is the input dataframe to the transform block
- Our final `export_titanic_clean.py` block in the `data_exporters` directory exports the output dataframe from the transform block into a CSV file
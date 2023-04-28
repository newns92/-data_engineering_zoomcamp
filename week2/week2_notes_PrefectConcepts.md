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
- A **flow** is the most basic Prefect **object** that is a **container** for workflow logic and allows you to interact with and understand the state of the workflow
    - Flows are like functions: they take inputs, perform work, and return an output
- We can start by using the `@flow` decorator to a `main_flow` function


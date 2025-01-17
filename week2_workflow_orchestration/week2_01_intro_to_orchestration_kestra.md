# Intro to Orchestration


## What is Orchestration (2024 Zoomcamp)?
- A lot of data engineering is ETL/ELT between various sources and destinations
- **Orchestration** is a process of *dependency management*, facilitated through *automation*
    - Automation is key here
    - As engineers, the idea is to *minimize manual labor* by automating as many processes as possible
- The **data orchestrator** manages *scheduling*, *triggering*, *monitoring*, and even *resource allocation*
- Every **workflow** requires *sequential* steps, in a particular order, since downstream processes will depend on upstream processes
- We will refer to "steps" as **tasks** (or "blocks" in Mage) and to workflows as **pipelines** or **DAGs  (Directed Acyclic Graphs)**
- Orchestration is one of the **undercurrents** of the **Data Engineering Lifecycle** from the *Fundamentals of Data Engineering* book (https://www.oreilly.com/library/view/fundamentals-of-data/9781098108298/)
    - By "undercurrent", we mean that it happens throughout the *entire* lifecycle, and it is key to building data engineering pipelines
- So, it's important to have a good orchestrator that fits your specific use case(s) well (there is no "perfect" solution for all use cases)
- So, *what does a good solution look like?*
    - A good orchestrator handles:
        - Workflow management
            - Define schedules, manage workflows efficiently, ensure tasks are executed in the right order, manages dependencies, etc.
        - Automation
            - Important since we're trying to automate as much as possible
        - Error handling
            - Things *will* break, so orchestrators need built-in solutions for: handling errors, conditional logic, branching, and retrying failed tasks
        - Recovery
            - Again, things *will* break, so we need an efficient way to **backfill** or recover any lost/missing data
        - Monitoring and alerting
            - Notifications should be able to be sent if something fails or is being retried in a pipeline
        - Resource optimization
            - Ideally, an orchestrator is optimizing the best route for where jobs are executed
        - Observability
            - A very important part of data engineering is having visibility into *every* part of a data pipeline
        - Debugging
            - This is a part of observability, and this should be easily done via the orchestrator
        - Compliance/Auditing
            - Because the orchestrator should have observability and debugging functionalities (and because it's an undercurrent), it should help with compliance and auditing 
    - Also, a good orchestrator *prioritizes* **the developer experience**:
        - Flow state
            - Don't want to be switching between a lot of different services/tools
        - Feedback loops
            - Want to be able to iterate quickly, fail fast, build good products and get tangible feedback quickly
        - Cognitive load
            - How much do you need to know to do your job? Was the day of work effortless or headache-inducing?
- So, a good orchestrator handles all the data engineering tasks mentioned above but also facilitates rapid and almost seamless development of efficient pipelines
- FROM 2025 ZOOMCAMP:
    - So, we have a bunch of code scripts (like in Python) that perform various tasks
    - But running them independently is only a small set of our overall job
    - Getting them all to work together and making sure they can access and rely on each other, as well as understanding what is going on with all the complexity, is the challenging aspect


## Kestra
- **Kestra** is an open-source, event-driven orchestration platform that simplifies building both scheduled and event-driven workflows
- By adopting Infrastructure as Code (IaC) practices for data and process orchestration, Kestra enables you to build reliable workflows with just a few lines of YML
- It is an all-in-one automation and orchestration platform that allows us to do ETL, batch data pipelines, schedule piplines to run on a routine or event-based schedule, etc.
- Kestra gives us flexibility on how we control and run workflows (no code, low-code, or full code) in a varity of coding languages (Python, R, JavaScript, C, Rust, etc.) depending on what is best for your project
- Kestra also allows us to monitor everything in our pipeline and give us insight as to what is going on in them
- It has 600+ plug-ins of a variety of tools (Databricks, Snowflake, cloud platforms, dbt, etc.)


## What Will We Cover?
- A more in-depth introductin to Kestra
- ETL pipelines into both Postgres and GCP (both in GCS and BigQuery)
- Parameterizing execution
    - To make workflows dynamic by passing in parameters *at execution* to allow different things to happen without having to create different workflows
    - This gives us flexibility in choosing how our workflows should run without having to manually code it all in
- Scheduling and backfills
- Installing Kestra on the GCP and syncing Kestra Flows with git


## Demo
- The workflow will have an `id` (unique to Kestra) and a `namespace` (sort of like a folder where we store our workflows) that we use to organize the workflow
- We also have `inputs`, which are values we pass in at the start of a workflow execution to define what happens
- Afterwards, we have `tasks`, each which has an `id` and `type`, and possible `script`'s and/or `sql` blocks
- When running a workflow, we can visualize which task runs when, and at what point the workflow is at, as well as access logs of what is going on
- The "Outputs" tab will then show some of the data generated by our tasks

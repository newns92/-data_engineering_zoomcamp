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
    - Projects
        - Forms the basis for all the work you can do in (can think of it like a GitHub repo)
        - Your homebase/overall unit of an environment
        - Contains the code for all of pipelines, blocks, and other assets
        - Can have multiple projects within a single instance
    - Pipelines
        - Workflows that execute some data operation (maybe extracting, transforming, and loading data from an API)
        - Also called DAGs or data workflows
        - Each project can have as many pipelines as needed
        - In Mage, pipelines can contain Blocks (written in SQL, Python, or R) and charts
        - Each pipeline is represented by a YAML file in the “pipelines” folder of a project
    - Blocks
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
- 


## A Simple Pipeline
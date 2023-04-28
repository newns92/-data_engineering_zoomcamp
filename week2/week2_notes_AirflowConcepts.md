# Airflow Concepts - Architecture Overview

## Airflow installation
- Generally consists of the following components:
    - **Webserver** - a GUI to inspect, trigger, and debug the behaviour of DAGs and tasks available at http://localhost:8080
    - **Scheduler** - Responsible for scheduling jobs
        - Handles both triggering and scheduled workflows
        - Submits Tasks to the Executor to run
        - Monitors all Tasks and DAGs
        - Then triggers the Task instances once their dependencies are complete
    - **Executor** - which handles running Tasks
        -  In the default Airflow installation, this runs everything inside the Scheduler, but most production-suitable executors actually push task execution out to Workers
    - **Worker** - Component that executes the Tasks given by the Scheduler
    - **Metadata database** (Postgres) - Backend to the Airflow environment
        - Used by the Scheduler, Executor and Webserver to store state
    - Other components (seen in `docker-compose` services):
        - `redis` - Message broker that forwards messages from Scheduler to Worker.
        - `flower`: The flower app for monitoring the environment available at http://localhost:5555
        - `airflow-init`: initialization service (customized as per this design)
- All these services allow you to run Airflow with `CeleryExecutor` 
- Most Executors generally also introduce other components to let them talk to their Workers (like a **task queue**),but you can still *think of the Executor and its Workers as a single logical component in Airflow overall*, handling the actual Task execution
- Airflow itself = agnostic to what is running = will happily orchestrate and run anything, either with high-level support from one of various provider, or directly as a command using the shell or Python Operators

## Workloads
- **DAG** = Directed Acyclic Graph that specifies the **dependencies** between a set of **Tasks** with explicit execution order, and has a beginning as well as an end
    - DAG Structure = **DAG Definition**, **Tasks** (eg. **Operators**), Task **Dependencies** (control flow: `>>` or `<<`)
    - **DAG Run**: individual execution/run of a DAG scheduled or triggered
- A **DAG** runs through a series of **Tasks**
- A **Task:** = a defined unit of work (aka **Operators** in Airflow)
    - The Tasks themselves describe what to do (be it fetching data, running analysis, triggering other systems, etc.)
    - There are 3 common types of Tasks seen:
        - *Operators* = predefined tasks you can string together quickly to build most parts of DAGs
        - *Sensors* = a special subclass of Operators which are entirely about waiting for an external event to happen
        - A *TaskFlow*-decorated `@task` = a custom Python function packaged up as a Task
    - Internally, these are all actually subclasses of Airflow's `BaseOperator`, and the concepts of Task and Operator are somewhat interchangeable, but it's useful to think of them as separate concepts
    - Essentially, Operators and Sensors are templates, and when you call one in a DAG file, you're making a Task
    - **Task Instance** = an individual run of a single Task
        - These also have an indicative state, which could be “running”, “success”, “failed”, “skipped”, “up for retry”, etc. 
        - Ideally, a Task should flow from `none` > `scheduled` > `queued` > `running` > `success`

## Control Flow
- **DAGs** are designed to be run many times, and *multiple runs of them can happen in parallel*
- DAGs are *parameterized*, always including an interval they are "running for" (the **data interval**), but with other optional parameters as well.
- **Tasks** have **dependencies** declared on each other, seen in a DAG either using the `>>` and `<<` operators:
    ```bash
    first_task >> [second_task, third_task]
    fourth_task << third_task
    ```
    - Or, with the `set_upstream` and `set_downstream` methods:
    ```bash
    first_task.set_downstream([second_task, third_task])
    fourth_task.set_upstream(third_task)
    ```
    - These dependencies are what make up the "edges" of the graph, and how Airflow works out which order to run your tasks in
    - By default, a task will wait for all upstream tasks to succeed before it runs, but this can be customized using features like **Branching**, **LatestOnly**, and **Trigger Rules**.

- To pass data between tasks you have 3  options:
    - **XComs ("Cross-communications")** = a system where you can have Tasks push and pull small bits of metadata
    - Uploading and downloading large files from a storage service (either one you run, or part of a public cloud)
    - TaskFlow API automatically passes data between tasks via implicit **XComs**

- Airflow sends out Tasks to run on Workers as space becomes available, so there's *no guarantee all the tasks in a DAG will run on the same worker or the same machine*

- As you build out DAGs, they are likely to get very complex, so Airflow provides several mechanisms for making this more sustainable 
    - **SubDAGs** let you make "reusable" DAGs you can embed into other ones
    - **TaskGroups** let you visually group tasks in the UI.

- There are also features for letting you easily pre-configure access to a central resource, like a **datastore**, in the form of **Connections & Hooks**, and for limiting concurrency, via **Pools**.

## UI
- Airflow comes with a user interface that lets you see what DAGs and their tasks are doing, trigger runs of DAGs, view logs, and do some limited debugging + resolution of problems with DAGs
- It's generally the best way to see the status of your Airflow installation as a whole, as well as diving into individual DAGs to see their layout, the status of each task, and the logs from each task


## Project Structure:
- `./dags` - DAG_FOLDER for DAG files (use `./dags_local` for the local ingestion DAG)
- `./logs` - contains logs from Task execution and Scheduler
- `./plugins` - for custom plugins


## 
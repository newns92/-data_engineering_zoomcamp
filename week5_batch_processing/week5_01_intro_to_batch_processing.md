# Batch Processing


## Intro to Batch Processing
- There are 2 main ways of processing data: **Batch** and **Streaming (online)**
    - 1\) **Batch** jobs are routines that are run on regular intervals, the most common typically being daily or hourly jobs, that, say, take data from a database, process it, and put it into another database
        - Batch jobs process data *after* the reference time period is over (e.g., after a day ends, a batch job processes all data that was gathered in that day)
            - i.e., Processing and analysis happens on a set of data that has already been stored over a period of time
            - It involves processing chunks of data at regular intervals
        - Different tech can be used for batch jobs, such as Python scripts, SQL (like via dbt), Spark, Flink
        - Batch jobs are **easy to manage, re-try** (which also helps for fault tolerance) and **scale**
        - Examples of batch jobs could be payroll and billing systems that have to be processed weekly or monthly
        - The **main disadvantage** of batch jobs is that we won't have the *most* recent data available, since we need to wait for an interval to end and our batch workflows to run before being able to do anything with our data
    - 2\) **Streaming** jobs are "on the fly" **events**
        - i.e., Data processing is "on the fly"
        - Events happen as the data flows through a system, which results in analysis and reporting of events *as it happens*
        - Examples are streaming jobs are fraud detection, intrusion detection, or a taxi has a device that sends an **event** to a **data stream**, which itself has a **processor** that processes data and puts it into another data stream


## Batch Jobs
- Again, a batch job is a **job** (AKA a unit of work) that will process data in, of course, batches
- Examples of batch intervals include weekly, daily, hourly, 3 times per hour, every 5 minutes, etc.
- These jobs could be Python scripts (**chunking**) on a monthly basis (ran *anywhere*, such as on Kubernetes (K8's), AWS Batch, etc.), SQL to define transformations (dbt), Spark jobs, Flink jobs, etc.
- Jobs can be **orchestrated** via Airflow, Prefect, Mage, Dagster, etc.
    - For an example workflow: 
        - You have data as CSV's in a data lake
        - Then you have a Python script (job) to grab these files, possibly transform them, and put them into a data warehouse
        - Then you have a SQL job (dbt) to do some data preperation
        - Then you run Spark on it
        - Then perhaps you end up with another Python script to expose the data
        - *Each of the above steps are batch jobs, using different tech, all hopefully orchestrated by an orchestration tool*
- *Batch Advantages*:
    - Batch is **easy to manage**
        - There are multiple tools to manage and parameterize jobs (such as the tech mentioned just prior)
    - They are **re-executable**
        - Jobs can be easily re-tried if they fail
    - They are **scalable**
        - Scripts can be executed in larger and/or more capable machines, Spark can be run in bigger clusters, etc.
- *Batch Disadvantages*:
    - There is a **delay**
        - Each task of the workflow mentioned in the example above may take a few minutes
        - Assuming the whole workflow takes 20 minutes, we'd need to wait those 20 minutes until the data is ready for work
            - In many cases, this is just fine, and the task does not require streaming
- *The advantages of batch jobs often compensate for its shortcomings*, and as a result **most companies that deal with data tend to work with batch jobs most of the time (*for now)***

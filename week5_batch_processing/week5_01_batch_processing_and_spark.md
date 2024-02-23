# Batch Processing


## Intro to Batch Processing
- There are 2 ways of processing data: **Batch** and **Streaming (online)**
    - Batch **jobs** are routines that are run on regular intervals, the most common being daily or hourly jobs
        - Batch jobs process data *after* the reference time period is over (e.g., after a day ends, a batch job processes all data that was gathered in that day)
            - i.e., Processing and analysis happens on a set of data that has already been stored over a period of time
            - It involves processing chunks of data at regular intervals
        - Batch jobs are **easy to manage, re-try** (which also helps for fault tolerance) and **scale**
        - Examples of batch jobs could be payroll and billing systems that have to be processed weekly or monthly
        - The **main disadvantage** of batch jobs is that we won't have the *most* recent data available, since we need to wait for an interval to end and our batch workflows to run before being able to do anything with our data
    - **Streaming** jobs are "on the fly" **events**
        - i.e., Data processing is "on the fly"
        - Events happen as the data flows through a system, which results in analysis and reporting of events *as it happens*
        - Examples are streaming jobs are fraud detection or intrusion detection


## Batch Jobs
- Again, a batch job is a **job** (AKA a unit of work) that will process data in, of course, batches
- Examples of batch intervals include weekly, daily, hourly, 3 times per hour, every 5 minutes, etc.
- These jobs could be Python scripts (**chunking**) on a monthly basis (ran *anywhere*, such as on Kubernetes, AWS Batch, etc.), SQL to define transformations (dbt), Spark jobs, Flink jobs, etc.
- Jobs can be **orchestrated** via Airflow, Prefect, Mage, Dagster, etc.
    - For an example workflow: 
        - You have data as CSV's in a data lake
        - Then you have a Python script (job) to grab these files, possibly transform them, and put them into a data warehouse
        - Then you have a SQL job (dbt) to do some data preperation
        - Then you run Spark on it
        - Then you end up with another Python script to expose the data perhaps
        - *Each of the above steps are batch jobs, using different tech, all orchestrated by an orchestration tool*
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
- *The advantages of batch jobs often compensate for its shortcomings*, and as a result **most companies that deal with data tend to work with batch jobs most of the time, *for NOW***


## Intro to Spark
- **Apache Spark** is a unified, multi-language (Java, Scala (the native way), Python, R, etc.) analytics **engine** (i.e., the processing happens *in* Spark) for large-scale data processing, or for executing data engineering, data science, and ML on single-node machines/clusters
- See more at https://spark.apache.org/docs/latest/index.html
- Spark can pull data from data warehouses/lakes/databases to its **executors**, do something to the data, and then output it to a data warehouse/lake/database
- Spark is a **distributed** data processing engine, with its components working collaboratively on potentially a cluster of machines, each cluster having 10's or 100's or 1000's of machines
- Spark is normally used for *batch* processing (although it *can* also be used for streaming)
- At a high level in the Spark architecture, a Spark **application** consists of a **driver program** responsible for orchestrating parallel operations on the Spark **cluster** 
    - The driver accesses the distributed components in the cluster (the Spark **executors** and **cluster manager**) through a **SparkSession**
- Spark provides high-level API's in Java, Scala, Python (PySpark) and R, and an optimized engine that supports general execution graphs
    - It also supports a rich set of higher-level tools including:
        - **Spark SQL** for SQL and structured data processing
        - **pandas** API on Spark for Python pandas workloads
        - **MLlib** for machine learning
        - **GraphX** for graph processing
        - **Structured Streaming** for incremental computation and stream processing
- When to use Spark:
    - When data is in a data lake (like in S3 or GCS with a bunch of CSV's or parquet files, etc.)
        - Spark pulls this data, does some processing, and puts it back into the data lake (or into another destination)
    - We can use it in the same places we'd typically use SQL (which isn't always easy to use with data lakes, but *could* be done with Hive, Presto, Athena, etc.)
        - **If you *can* express your jobs as SQL queries, it's best to go with it** (i.e., go with Athena/Presto, or use external tables in BigQuery, etc.)
        - But for other things, like ML, Spark may be the way to go
    - The Spark engine is recommended:
        - 1\) For **dealing *directly* with files**
        - 2\) In situations where we need **more flexibility than SQL offers**, such as:
            - If we want to split our code into different modules, write unit tests, or just have some functionality that may not be possible to write using SQL (e.g., ML-related routines, such as training and/or using a model)
    - A typical workflow may combine both tools, Spark *and* SQL
        - Example of a workflow involving ML may be:
            - Raw data is placed into a data lake
            - We then xecute transformations on the data, like aggregatinos and JOIN's via SQL Athena (This is most of the pre-processing)
            - Then, we need some more *complex* logic/computation that we cannot express via SQL, so we use Spark
            - We train an ML model in Python (or apply it in Spark)
            - Then, data is put *back* into the data lake (or some other destination)

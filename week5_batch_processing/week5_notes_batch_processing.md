# Batch Processing

## Intro to Batch Processing
- 2 ways of processing data: Batch vs. Streaming (online)
- Batch **jobs** = routines that are run in regular intervals
    - The most common types of batch jobs are either daily or hourly jobs
    - Batch jobs process data *after* the reference time period is over (e.g., after a day ends, a batch job processes all data that was gathered in that day)
        - i.e., Processing and analysis happens on a set of data that have already been stored over a period of time.
        - Processing chunks of data at regular intervals
    - **Batch** jobs are **easy to manage, re-try** (also helps for fault tolerance) and **scale**        
    - Ex: Payroll and billing systems that have to be processed weekly or monthly
    - **Main disadvantage** = won't have the most recent data available, since we need to wait for an interval to end and our batch workflows to run before being able to do anything with such data
- **Streaming** jobs
    - "On the fly" **events**/data processing is "on the fly"
    - Happens as the data flows through a system which results in analysis and reporting of events *as it happens*
    - Ex: Fraud detection or intrusion detection

## Batch Jobs
- A batch job = a **job** (a unit of work) that will process data in batches
- Examples of intervals: weekly, daily, hourly, 3 times per hour, every 5 minutes, etc.
- Could be Python scripts (chunking) on a monthly basis (run *anywhere*, such as Kubernetes, AWS Batch, etc.), SQL to define transformations (dbt), Spark, Flink, etc.
- Can be **orchestrated** via Airflow, Prefect, etc.
    - Have data as CSV's in a data lake
    - Then have a Python job to grab these files, possibly transforms them, and puts them into a data warehouse
    - Then have a SQL job (dbt) to do some data prep
    - Then have Spark running
    - Then ending up with another Python script
    - *Each of the above steps are batch jobs, using different techs, all orchestrated by an orchestration tool*
- *Advantages*:
    - Easy to manage = There are multiple tools to manage and parameterize them (the technologies mentioned prior)
    - Re-executable = Jobs can be easily re-tried if they fail
    - Scalable = Scripts can be executed in larger or more capable machines, Spark can be run in bigger clusters, etc.
- *Disadvantages*:
    - Delay = Each task of the workflow in the previous section may take a few minutes
        - Assuming the whole workflow takes 20 minutes, we'd need to wait those 20 minutes until the data is ready for work
- *Advantages of batch jobs often compensate for its shortcomings*, and as a result **most companies that deal with data tend to work with batch jobs most of the time, *for now***

## Intro to Spark
- **Apache Spark** = a unified, multi-language (Java, Scala (the native way), Python, R, etc.) analytics **engine** (i.e., the processing happens *in* Spark) for large-scale data processing, or for executing data engineering, data science, and ML on single-node machines/clusters
- https://spark.apache.org/docs/latest/index.html
- Spark can pull data from data warehouses/lakes/databases to its **executors**, does something to the data, and then outputs it to a data warehouse/lake/database
- Spark = a *distributed* data processing engine with its components working collaboratively on potentially a cluster of machines, each cluster having 10s or 100s or 1000s of machines
- Normally used for batch processing (although it can also be used for streaming)
- At a high level in the Spark architecture, a **Spark application** consists of a **Driver program** responsible for orchestrating parallel operations on the **Spark cluster** 
    - The driver accesses the distributed components in the cluster (the **Spark executors** and **cluster manager**) through a **SparkSession**
- Spark provides high-level APIs in Java, Scala, Python (PySpark) and R, and an optimized engine that supports general execution graphs
    - It also supports a rich set of higher-level tools including:
        - **Spark SQL** for SQL and structured data processing
        - **pandas** API on Spark for pandas workloads
        - **MLlib** for machine learning
        - **GraphX** for graph processing
        - **Structured Streaming** for incremental computation and stream processing.
- When to use it:
    - When data is in a data lake (like in S3 or GCS with a bunch of CSVs or parquet files, etc.)
    - Spark pulls this data, does some processing, and puts it back into the data lake (or into another destination)
    - Can use it in the same places we'd typically use SQL (which isn't always easy to use with data lakes, but *could* be done with Hive, Presto, Athena, etc.)
        - **If you *can* express your jobs as SQL queries, it's best to go with it** (i.e., go with Athena/Presto, or use external tables in BigQuery, etc.)
    - The Spark engine is recommended 
        - 1\) For **dealing *directly* with files**
        - 2\) In situations where we need **more flexibility than SQL offers**, such as:
            - If we want to split our code into different modules, write unit tests, or just have some functionality that may not be possible to write using SQL (e.g., ML-related routines, such as training and/or using a model)
    - A typical workflow may combine both tools, Spark *and* SQL
        - Example of a workflow involving ML may be:
            - Raw data is placed into a data lake
            - Execute transformations on the data, like aggregatinos and JOINs via SQL Athena (most of the pre-processing)
            - Need some more complex logic/computation, so we use Spark
            - Train the ML model in Python or apply it in Spark
            - Data is put back into the data lake or some other destination

## Installing Spark on Windows
- Via Git Bash MINGW terminal
- Installing Java
    - Spark needs Java 11: https://www.oracle.com/de/java/technologies/javase/jdk11-archive-downloads.html
    - Select “Windows x64 Compressed Archive” (may have to create an Oracle account)
    - Configure it and add it to `PATH` via `export JAVA_HOME="C:\jdk"` then `export PATH="${JAVA_HOME}/bin:${PATH}"`
    - Check that Java works correctly via `java --version`
- Installing **Hadoop**
    - Need to have Hadoop binaries from Hadoop 3.2 which we'll get from: https://github.com/cdarlint/winutils/tree/master/hadoop-3.2.0
    - Create a folder (`C:\hadoop`) and `cd` to that directory
    - To get the files, run `HADOOP_VERSION="3.2.0"`, then `PREFIX="https://raw.githubusercontent.com/cdarlint/winutils/master/hadoop-${HADOOP_VERSION}/bin/"`, then `FILES="hadoop.dll hadoop.exp hadoop.lib hadoop.pdb libwinutils.lib winutils.exe winutils.pdb"`
    - Then, run :
        ```bash
            for FILE in ${FILES}; do
                wget "${PREFIX}/${FILE}"
            done
        ```
    - Add it to `PATH` via `export HADOOP_HOME="C:\hadoop"` then `export PATH="${HADOOP_HOME}/bin:${PATH}"`
- Installing Spark
    - Download Spark version 3.3.2 via `wget https://dlcdn.apache.org/spark/spark-3.3.2/spark-3.3.2-bin-hadoop3.tgz`
    - Unpack it in some location `C:\spark` via `tar xzfv spark-3.3.2-bin-hadoop3.tgz`
    - Add it to `PATH` via `export SPARK_HOME="C:\spark` then `export PATH="${SPARK_HOME}/bin:${PATH}"`
- Testing
    - ***In an Anaconda command prompt***, `cd` to `C:\spark\bin`
    - Run spark-shell via `spark-shell.cmd`
        - At this point, you may get a message from Windows Firewall, just allow it
        - There could be some warnings, like this:
        ```bash
            WARNING: An illegal reflective access operation has occurred
            WARNING: Illegal reflective access by org.apache.spark.unsafe.Platform (file:/C:/spark/jars/spark-unsafe_2.12-3.3.2.jar) to constructor java.nio.DirectByteBuffer(long,int)
            WARNING: Please consider reporting this to the maintainers of org.apache.spark.unsafe.Platform
            WARNING: Use --illegal-access=warn to enable warnings of further illegal reflective access operations
            WARNING: All illegal access operations will be denied in a future release
        ```
    - Now run:
    ```bash
    val data = 1 to 10000
    val distData = sc.parallelize(data)
    distData.filter(_ < 10).collect()
    ```
- Installing PySpark
    - Assuming we already have Python, to run PySpark, we first need to add it to `PYTHONPATH`
    - Do so via `export PYTHONPATH="C:\ProgramData\Miniconda3\python.exe"`, then `export PYTHONPATH="%SPARK_HOME%\python\:$PYTHONPATH"`, then `export PYTHONPATH="%SPARK_HOME%\python\lib\py4j-0.10.9.5-src.zip:$PYTHONPATH"`
        - Or **do this manually on Windows**
        - **Make sure that the version under `$%SPARK_HOME%\python\lib\` matches the filename of `py4j` or you will encounter `ModuleNotFoundError: No module named 'py4j'` while executing `import pyspark`**
    - Now you can run Jupyter or IPython to test if things work
    - Go back to `week5/` via `cd`, and download the zone lookup data via `wget https://s3.amazonaws.com/nyc-tlc/misc/taxi+_zone_lookup.csv` and also get the January FHV data from https://github.com/DataTalksClub/nyc-tlc-data/releases/tag/fhvhv
    - In a `zoom` conda environment, create a new notebook after running `jupyter notebook`
    - Run:
        ```bash
            import pyspark
            from pyspark.sql import SparkSession

            spark = SparkSession.builder \
                .master("local[*]") \
                .appName('test') \
                .getOrCreate()

            df = spark.read \
                .option("header", "true") \
                .csv('taxi+_zone_lookup.csv')

            df.show()
        ```
        - In the above code:
            - `SparkSession` is the class of the object that we instantiate
                - This class is the entry point into all functionality in Spark 
                - A `SparkSession` can be used create DataFrames, register DataFrames as tables, execute SQL over tables, cache tables, and read parquet files
            - `builder` is the builder method
                - It's a class attribute that is an instance of `pyspark.sql.session.SparkSession.Builder` that is used to construct SparkSession instances
            - `master()` sets the Spark master URL to connect to
                - The `local[*]` string means Spark will run on a local cluster (local machine)
                    - `[*]` means Spark will run with as many CPU cores as possible
                        - i.e., tells Spark to use all available cores (e.g., if we wanted to use only 2 cores, we would write `local[2]`)
            - `appName()` defines the name of our application/session, which will show in the Spark UI at http://localhost:4040/
            - `getOrCreate()` will create the session or recover the object if it was previously created
                - i.e., returns an existing `SparkSession`, if available, or creates a new one
        - Can also test that writing works via `df.write.parquet('zones')`
- To see conda environments in Juptyter notebooks:
    - Run `conda install nb_conda_kernels` in your base environment
    - In the `zoom` environment, run `conda install ipykernel`
    - Restart Jupyter Notebooks
    - Should see the conda environments as options under the "Kernel" tab

## Spark UI:
- Available at http://localhost:4040/
- Every **SparkContext** launches a web UI, by default on port `4040`, and it displays useful information about the application including:
    - A list of scheduler stages and tasks
    - A summary of RDD sizes and memory usage
    - Environmental information
    - Information about the running executors
- If multiple SparkContexts are running on the same host, they will bind to successive ports beginning with `4040` (`4041`, `4042`, etc)
- More info: https://spark.apache.org/docs/2.2.3/monitoring.html
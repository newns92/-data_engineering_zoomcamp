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


## Installing Spark on Windows
- Do this via the Git Bash `MINGW` terminal
- Installing **Java**:
    - Spark needs Java 11: https://www.oracle.com/de/java/technologies/javase/jdk11-archive-downloads.html
    - Select “Windows x64 Compressed Archive” (you may have to create an Oracle account)
    - Configure it and add it to `PATH` via `export JAVA_HOME="C:\jdk"` then `export PATH="${JAVA_HOME}/bin:${PATH}"`
    - Check that Java works correctly via `java --version`
- Installing **Hadoop**
    - We need to have the Hadoop binaries from Hadoop 3.2, which we'll get from: https://github.com/cdarlint/winutils/tree/master/hadoop-3.2.0
    - Create a directory (`C:\hadoop\`) and `cd` into that directory
    - To get the files, run `HADOOP_VERSION="3.2.0"`, then `PREFIX="https://raw.githubusercontent.com/cdarlint/winutils/master/hadoop-${HADOOP_VERSION}/bin/"`, then `FILES="hadoop.dll hadoop.exp hadoop.lib hadoop.pdb libwinutils.lib winutils.exe winutils.pdb"`
    - Then, run :
        ```bash
            for FILE in ${FILES}; do
                wget "${PREFIX}/${FILE}"
            done
        ```
    - Add it to `PATH` via `export HADOOP_HOME="C:\hadoop"` then `export PATH="${HADOOP_HOME}/bin:${PATH}"`
- Installing **Spark**
    - Download Spark version 3.3.2 via `wget https://dlcdn.apache.org/spark/spark-3.3.2/spark-3.3.2-bin-hadoop3.tgz`
    - Unpack it in some location such as `C:\spark` via `tar xzfv spark-3.3.2-bin-hadoop3.tgz`
    - Add it to `PATH` via `export SPARK_HOME="C:\spark`, then `export PATH="${SPARK_HOME}/bin:${PATH}"`
- Testing
    - ***In an Anaconda command prompt in the `zoom` environment***, `cd` to `C:\spark\bin`
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
    - You should see a result like `res0: Array[Int] = Array(1, 2, 3, 4, 5, 6, 7, 8, 9)`
- Installing **PySpark**
    - Assuming we already have Python, to run PySpark, we first need to add it to the `PYTHONPATH`
    - Do so via `export PYTHONPATH="C:\ProgramData\Miniconda3\python.exe"`, then `export PYTHONPATH="%SPARK_HOME%\python\:$PYTHONPATH"`, then `export PYTHONPATH="%SPARK_HOME%\python\lib\py4j-0.10.9.5-src.zip:$PYTHONPATH"`
        - Or **do this manually on Windows**
        - **Make sure that the version under `$%SPARK_HOME%\python\lib\` matches the filename of `py4j` or you will encounter `ModuleNotFoundError: No module named 'py4j'` while executing `import pyspark`**
    - Now you can run Jupyter or IPython to test if things work
    - Go back to `week5/` via `cd`, and download the zone lookup data via `wget https://s3.amazonaws.com/nyc-tlc/misc/taxi+_zone_lookup.csv` and also get the January 2019 FHV data from https://github.com/DataTalksClub/nyc-tlc-data/releases/tag/fhvhv
    - In a `zoom` conda environment, create a new notebook after running `jupyter notebook` in this `week5/` directory
    - Run:
        ```Python
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
            - `SparkSession` is the **class** of the object that we instantiate
                - This class is the entry point into all functionality in Spark 
                - A `SparkSession` can be used create DataFrames, register DataFrames as tables, execute SQL over tables, cache tables, and read Parquet files
            - `builder` is the builder **method**
                - It's a class **attribute** that is an **instance** of `pyspark.sql.session.SparkSession.Builder` that is used to **construct** SparkSession instances
            - `master()` sets the Spark master URL to connect to
                - The `local[*]` string means Spark will run on a local cluster (local machine)
                    - `[*]` means Spark will run with as many CPU cores as possible
                        - i.e., This tells Spark to use all available cores (e.g., if we wanted to use only 2 cores, we would write `local[2]`)
            - `appName()` defines the name of our application/session, which will show in the Spark UI at http://localhost:4040/
            - `getOrCreate()` will create the session or recover the object if it was previously created
                - i.e., It returns an existing `SparkSession`, if available, or creates a new one
        - We can also test that writing works via `df.write.parquet('zones')`
- NOTE: *To see the various conda environments on your local machine within a Juptyter notebook*:
    - Run `conda install nb_conda_kernels` in your base environment
    - In the `zoom` environment, run `conda install ipykernel`
    - Restart Jupyter Notebooks
    - Should see the conda environments as options under the "Kernel" tab


## Spark UI:
- This is available at http://localhost:4040/ after creating a SparkSession (in the Jupyter notebook above)
- Every **SparkContext** launches a web UI (by default on port `4040`) which displays useful information about the application including:
    - A list of scheduler stages and tasks
    - A summary of RDD sizes and memory usage
    - Environmental information
    - Information about the running executors
- If multiple SparkContexts are running on the same host, they will bind to successive ports beginning with `4040` (then to `4041`, `4042`, etc)
- More info can be found at: https://spark.apache.org/docs/2.2.3/monitoring.html


## Get the data
- Run `./download_data.sh` to download 2020 and 2021 yellow and green taxi data
- Run `python create_taxi_schema.py` ***in a `zoom` Conda environment terminal***
- ***IN THE VM***
    - Copy over the `download_data.sh` file to the VM via a VSCode Remote Window into the `pyspark_testing/` dir
    - `cd` into that dir, then run `chmod +x download_data.sh`
    - Run it
    - Run `pip install pandas` if need be
    - Copy over `create_taxi_schema.py` and run `python create_taxi_schema.py`
    - Can view this stuff in a terminal via `tree data/parquet`            
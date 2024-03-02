# Spark Internals

## Anatomy of a Spark Cluster
- We can have a cluster in our local environment, and it will contain **executors**, which execute **Spark jobs**
- When we set our Spark **context**, we specify the **master**, and for a local cluster, we set `local[*]` to use as many CPU cores as possible locally
    ```Python
        spark = SparkSession.builder \
                    .master("local[*]")
    ```
    - `master()` sets the Spark master URL to connect to
        - The `local[*]` string means Spark will run on a local cluster (local machine)
            - `[*]` means Spark will run with as many CPU cores as possible

### Spark Execution modes
- It's possible to run a Spark application using **cluster mode**, **local mode (pseudo-cluster)** or with an **interactive shell** (`pyspark` or `spark-shell`)
- **Local Mode**
    - So far, we've just used a local cluster to run Spark code, but Spark clusters often contain *multiple* CPU's that act as executors
    - Usually, we write a script or package written in Java/Python/Scala on a local machine (or via Airflow) along with a Spark cluster
    - Within our cluster, we have a manager/coordinator called a **Spark master**, which behaves similarly to an **entry point** to a Kubernetes cluster
        - The master usually has a web UI on port `4040` to see what's being executed on a cluster
        - We use a special command `spark-submit` to send code to the master (i.e., a URL)
    - Again, within the cluster, we have **executors** (the CPU's that are actually doing computations/running jobs coordinated/orchestrated by the master)
        - A **driver** (an Airflow DAG, a CPU running a local script, etc.) who wants to run a Spark job sends the job to the master, who in turn distributes the work among the executors in the cluster
        - *Since the master should always be running*, if an executor fails/goes down, the master will know this, and re-assign the task that should've went to that executor to another executor that is up and running
        - Executors will pull and process data (Say, many Parquet files contained in S3 or GCS that contain partitions of a DataFrame each being pulled to an executor), and then store it somewhere
            - In prior years, this was done with Hadoop (HDFS)
                - The idea with HDFS was data from a data lake is stored *on* the executors *with redudancies* (i.e., some partitions were stored on multiple different executors) in case a node fails
                - Then, instead of bringing in/downloading data onto a machine, *you download code to a machine that already has the data* (i.e., **data locality**)
                - Data locality made sense, since the partition files were large (say, 100MB), while the code to run was relatively small (say, 10MB)
            - **Nowadays, thanks to cloud providers, the Spark clusters and the cloud storage services live in the same data center**
                - Now, downloading data for an executor is fast (Note: It's a little slower than reading from disk, but not significantly slower)
                - Executors now don't keep data on their machines, but can just pull it from data storage and save results to a data lake
                - This all reduces overhead that came from Hadoop/HDFS
- **Cluster Mode**
    - Spark applications are run as *independent* sets of processes, coordinated by a **SparkContext** object in your main program (called the **driver program**)
    - The **context** connects to the **cluster manager** which allocates resources
    - Each **worker** in the cluster is managed by an **executor**
    - The executor manages computation *as well as* storage and caching on each machine
    - The application code is sent from the driver to the executors, and the executors specify the context and the various tasks to be run
    - The driver program must listen for and accept incoming connections from its executors throughout its lifetime

- **Clusters and partitions**
    - To distribute work across a cluster and reduce memory requirements of each node, Spark splits data into smaller parts called **partitions**
    - Each of these is then sent to an executor to be processed
    - **Only *one* partition is computed per executor thread at a time**, therefore the size and quantity of partitions passed to an executor is directly proportional to the time it takes to complete
    - See more at https://blog.scottlogic.com/2018/03/22/apache-spark-performance.html

- **More terms**
    - See more at https://spark.apache.org/docs/3.3.2/cluster-overview.html
    - **Application**: A user program built on Spark that consists of a driver program and executors on the cluster
    - **Application jar**: A `jar` containing a user's Spark application
        - In some casesm, users will want to create an "uber `jar`" containing their application *along with its dependencies*
        - The user's `jar` should *never* include Hadoop or Spark libraries, however, as these will be added at runtime
    - **Driver program**: The process running the `main()` function of the application and creating the **SparkContext**
    - **Cluster manager**: External service for acquiring resources on the cluster (e.g., standalone manager, Mesos, YARN, Kubernetes)
    - **Deploy mode**: Distinguishes where the driver process runs
        - In "cluster" mode, the framework launches the driver inside of the cluster
        - In "client" mode, the submitter launches the driver outside of the cluster
    - **Worker node**: Any node that can run application code in the cluster
    - **Executor**: A process launched for an application on a worker node that runs tasks and keeps data in memory or disk storage across them
        - *Each application has its own executors*
    - **Task**: A unit of work that will be sent to *one* executor
    - **Job**: A parallel computation consisting of multiple tasks that gets spawned in response to a Spark **action** (e.g. save, collect)
        - You'll see this term used in the driver's logs
    - **Stage**: Each job gets divided into smaller sets of tasks called stages that depend on each other (similar to the map and reduce stages in MapReduce)
        - You'll see this term used in the driver's logs


## GROUP BY in Spark
- Spark works with *multiple* partitions and clusters in order to combine files
- Each executor does filtering and then an *initial* GROUP BY to get **subresults**
    - We say "initial" GROUP BY's since each executor can only process one partition at a time, so each "intial" GROUP BY is done *within a partition*
- These executors will output those subresults GROUP-ed BY *just for that partition*
- As a result, for each partition, we have a bunch of *temp files* (our *subresults*), that we must combine
- Subresults are **(re)-shuffled** (i.e., Spark moves records between partitions in order to group records with the same key in the same partition)
- Then, there is an **external merge sort** (i.e., an algorithm for sorting the data in a distributed manner) that is performed
    - https://www.sparkcodehub.com/spark-what-is-a-sort-merge-join-in-spark-sql
- After re-shuffling, Spark does *another* GROUP BY to group all records with the same key and then reduces the groups to *single* records
- **Shuffling** is a mechanism Spark uses to move/redistribute data across different executors/partitions, and even across machines
    - It moves data from smaller partitions into larger partitions, and that's where the external merge sort is applied
    - Within these larger partitions, we can do *another* GROUP BY
    - Shuffle is an *expensive* operation, as it involves moving data across the nodes in a cluster, which involves network and disk I/O
    - **It is always a good idea to reduce the amount of data that needs to be shuffled**
    - *Tips to reduce shuffle*:
        - Tune the `spark.sql.shuffle.partitions`
            - A formula recommendation for `spark.sql.shuffle.partitions`:
                - For large datasets, aim for anywhere from 100MB to < 200MB task target size for a partition (use target size of 100MB, for example)
                - A `spark.sql.shuffle.partitions` quotient could be: `((shuffle stage input size/target size)/total cores) * total cores`
        - Partition the input dataset appropriately so each task size is not too big
        - Use the Spark UI to study the plan to look for opportunities to reduce the shuffle as much as possible
- See "Explore best practices" for Spark performance optimization for more information:
    - https://developer.ibm.com/blogs/spark-performance-optimization-guidelines/


## JOINs in Spark
- Spark can join 2 tables quite easily, and syntax is easy to understand via `.join()`
- For the JOINs, suppose we have 2 partitions per dataset (i.e., 2 partitions for yellow and 2 partitions for green), where `Y1`, `Y2`, `Y3` and `G1`, `G2`, `G3` are the records of each dataset 
    - Each record is composed of multiple columns: `hour`, `zone`, `amount` and `number_of_trips`
    - Records will be joined by a **composite key** [`hour`, `zone`]
    - In the next step, Spark once again does re-shuffling with External Merge Sort
    - Suppose we have 3 output partitions: every record with composite key 1 will go to the 1st partition, every record with composite key 2 will go to the 2nd, every record with composite key 3 to the 3rd, and every record with composite key 4 would go to the *1st* partition
        - As a reminder, *re-shuffling is performed to ensure records with the same keys end up in the same partitions*
    - Lastly, Spark performs a REDUCE step similar to the one in GROUP BY, where *multiple records are reduced into one*
- Spark **broadcast joins** are perfect for joining a *large* DataFrame with a *small* DataFrame.
    - Spark can "broadcast" a small DataFrame by sending *all* the data in that small DataFrame to *all* nodes in the cluster
    - After the small DataFrame is broadcasted, Spark can perform a join *without shuffling any of the data in the large DataFrame*
        - Example: Joining our joined green and yellow results DataFrame with a small zones lookup CSV/table

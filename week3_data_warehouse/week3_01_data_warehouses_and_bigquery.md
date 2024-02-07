# Data Warehouses and Google BigQuery

## Data Warehouses

### OLTP vs. OLAP
- ***Online Transactional Processing (OLTP) systems*** are typically used in **backend services**, where sequences of SQL statements are grouped together in the form of **transactions**
    - Transactions are **rolled back** if *any* of their statements fail
    - OLTP systems deal with **fast but small** updates and store data in database designs that are **normalized**, both for efficiency reasons and to **reduce data redundancy and increase productivity of *end users***
    - The purpose of an OLTP system is to control and run essential business operations **in real-time**
    - Data updates are typically short and fast and initiated by a user
    - In terms of space requirements, they are generally small, *if* historical data is archived
    - For backup and recovery, **regular backups** are required in order to ensure business continuity and to meet legal and governance requirements
    - They contain **day-to-day business *transactions***
    - Examples of users of such systems are customer-facing personnel, clerks, and online shoppers
- ***Online Analytical Processing (OLAP) systems*** are composed of ***de*-normalized** databases, which simplify **analytics queries**, are mainly used for **data mining**, generally contain **data from *many* sources** (e.g., different *OLTP* systems), and implement **Star or Snowflake schemas** that are **optimized for analytical tasks**
    - The purpose of an OLAP system is to **plan, solve problems, support decisions, and discover hidden insights** using a *lot* of data
    - For data updates, data is typically **refreshed *periodically*** with **scheduled, long-running *batch* jobs**
    - In terms of space requirements, they are generally large due to the aggregating of large datasets
    - For backup and recovery, **lost data can be reloaded from OLTP database** in lieu of regular backups
    - OLAP systems usually increase the productivity of business managers, data analysts and data scientists, and executives
    - The data view is a **multi-dimensional** view of *enterprise* data
    - Examples of users of such systems are knowledge workers (such as business managers as mentioned above), data analysts and data scientists, and executives

## What is a Data Warehouse?
- A ***data warehouse (DW)*** is an *OLAP* solution used for **reporting and data analysis**
- It generally consists of **raw data, metadata, and summary data**, all **from various sources** (flat files, different operational systems, OLTP databases, etc.) connected to a **staging** area before being loaded into the data warehouse
- They can connect to and be output as **data marts** (such as marts for purchasing, sales, and inventory) for consumption by different end users (for analysis, reporting, mining, etc.)
    - Some users, like data scientists, may look *directly* at raw data in the data warehouse


## Google BigQuery

### Intro to BigQuery
- Google BigQuery is a **serverless** data warehouse
    - In other words, there are no servers to manage nor any database software to install
    - Generally when a company starts on a journey of data warehousing/analytics, a large amount of time is spent creating a data warehouse (not to mention maintaining it)
    - BigQuery can help alleviate this overhead
- BigQuery provides **software *as well as* infrastructure** including features such as **scalability** (from GB up to PB) and **high-availability**
    - You don't need to create and maintain your own data warehouse
- It has a varity of **built in-features**, such as ML, geospatial analysis, BI, etc.
- BigQuery **maximizes *flexibility* by *separating* the compute engine (which analyzes your data) from your storage**
    - Generally, with one big server having storage and compute together (or **tightly-coupled**), once your data size increases, your machine size *must* grow with it
- BigQuery has **on-demand pricing** (For example: 1 TB of data processed costs $5)
    - BigQuery also has *flat-rate pricing*
        - This ased on number of pre-requested slots (100 slots gives $2,000/month, which equals 400 TB of data processed via on-demand pricing)
        - *It doesn't really make sense to use this unless processing a LOT of data (say, above 200 TB of data)*
        - You must also think about queries competing with one another
            - For example, if you have 50 queries running and all 100 of your slots are full, a 51st query will have to wait
                - However, in on-demand BigQuery, this would not be the case, as it can provide you with additional slots as per the query's needs
- BigQuery generally **caches** data (which you *can* disable in "Query settings" in the BigQuery SQL UI to achieve consistent results)
- You can easily view the **schema** of datasets in BigQuery, as well as other details and a quick preview of a dataset
- BigQuery provides a lot of **open source public data** (like a NYC Citibike stations dataset `citibike_stations`) that you can search for within BigQuery
    - i.e., You can query the `station_id` and `name` fields from the `citibike_stations` table via ```SELECT station_id, name FROM `bigquery-public-data.new_york_citibike.citibike_stations` LIMIT 100;```
    - Results of such queries can be saved or explored via Data Studio
- As a practical example, we will create an **external table** (https://cloud.google.com/bigquery/docs/external-data-sources):
     - **External tables** are similar to standard BigQuery tables, in that these tables store their metadata and schema in BigQuery storage 
        - However, their **data resides in an *external* source**
        - Even so, you **can directly query it** from within BigQuery
        - "External tables are contained *inside a dataset*, and you manage them in the same way that you manage a standard BigQuery table"
     - We will create the external table from one of our yellow taxi datasets as an **external source**
        - BigQuery allows us to make tables based off of GCS Buckets via **gsutil Uniform Resource Identifiers (URI's)**
            - These URI's are in the format `gs://<bucket-name>/<file-name>`
        - To start off, make sure there is some data in your GCS bucket that you will be using
            - Do this via drag-and-drop of Parquet files or via **Mage**
                - ***May run into an issue of various fields being FLOATs and INTs, due to a `nan` value and have to fix***
        - Once the data is there, make sure you have a `ny_taxi` dataset under your project ID in BigQuery, and *NO* `external_nyc_yellow_taxi_data` table (***If it's there, drop it***)
        - Then, using the **gsutil URI's** of the data files, run
            ```SQL
                -- Creating external table referring to GCS path (gutil URI)
                CREATE OR REPLACE EXTERNAL TABLE `<project-id>.ny_taxi.external_nyc_yellow_taxi_data`
                    OPTIONS (
                        format = 'PARQUET',
                        uris = ['gs://<bucket-name>/data/yellow/yellow_tripdata_2019-*.parquet', 'gs://<bucket-name>/data/yellow/yellow_tripdata_2020-*.parquet']
                    );
            ```    
        - Then run:
            ```SQL
            SELECT * FROM `<project-id>.ny_taxi.external_nyc_yellow_taxi_data` limit 10;
            ```
    - When loading in the data BigQuery *knows* what data type a field is and *makes* it that data type, as well as convert and figure out if the field is NULL-able or not
        - In this way, **we don't always have to define our schema (*but we could do that if we really wanted to*)**
    - Go to the "Details" tab of the table once you have it open, and notice "Table Size" and "Long-term storage size" are both 0 Bytes, and "Number of Rows" is blank
        - Unfortunately, with *external* tables, BigQuery is unable to not able to determine the number of rows or the table size cost, since the data itself is not *inside* BigQuery, but is instead in external data storage (such as a GCS Bucket)

### Partitioning in BigQuery
- Generally, when we create a dataset, we have one or more certain columns that many queries are based off of and that can be used as some type of *"filter"*
- In such cases, we can **partition** a table based on such columns to improve BigQuery's performance
    - https://cloud.google.com/bigquery/docs/partitioned-tables
    - Example: A dataset containing StackOverflow questions partitioned by a `creation_date` field
- **Partitioning** is a powerful feature of BigQuery
    - Suppose we want to query the StackOverflow questions created on a specific date
    - **Partitionining improves processing**, because *BigQuery will not read or process any data from other dates*, which improves efficiency and reduces querying costs by processing less data
- To view the performance improvements, create a *non*-partitioned table from the external table via
    ```SQL
        -- Create a non-partitioned table from external table
        CREATE OR REPLACE TABLE `<project-id>.ny_taxi.yellow_taxi_data_non_partitioned`
        AS
        SELECT * FROM `<project-id>.ny_taxi.external_yellow_tripdata`;
    ```
- Next, create a *partitioned* table from the *same* external table via
    ```SQL
        -- Create a partitioned table from external table
        CREATE OR REPLACE TABLE `<project-id>.ny_taxi.yellow_taxi_data_partitioned`
        PARTITION BY
            DATE(tpep_pickup_datetime) AS
        SELECT * FROM `<project-id>.ny_taxi.external_yellow_tripdata`;
    ```
- We can see the partitioning details in the "Details" tab of the partitioned table
- Then, to see the difference in processing, run the same query on both tables:
    - First:
        ```SQL
            -- Impact of partition
            -- Scanning 583MB of data for the 1st 3 months of Yellow 2019 data
            SELECT DISTINCT(VendorID)
            FROM <project-id>.ny_taxi.yellow_tripdata_non_partitioned
            WHERE DATE(tpep_pickup_datetime) BETWEEN '2019-01-01' AND '2019-03-31';
        ```
    - And then:
        ```SQL
            -- Scanning ~106 MB of DATA
            SELECT DISTINCT(VendorID)
            FROM <project-id>.ny_taxi.yellow_taxi_data_partitioned
            WHERE DATE(tpep_pickup_datetime) BETWEEN '2019-01-01' AND '2019-03-31';
        ```
- You will see 583 MB Bytes processed, 583 MB Bytes billed for the NON-partitioned table, and 344 MB Bytes processed, 344 MB Bytes billed for the partitioned table (*for the first 3 months of 2019*)
    - *If you highlight the query in the editor, in the top right BigQuery will tell you this info before you run it*
- We can even look *directly into* the partitons to see how many rows are in each partition via
    ```SQL
        -- Look into the partitons
        SELECT table_name, partition_id, total_rows
        FROM `ny_taxi.INFORMATION_SCHEMA.PARTITIONS`
        WHERE table_name = 'yellow_taxi_data_partitioned'
        ORDER BY total_rows DESC;
    ```
    - This is helpful in determining if we have a *bias* in our partition
        - i.e., If we have some partitions getting more rows/data relative to others
- In BigQuery, we can partition data by:
    - A time-unit column: daily (default), hourly (if you have a *huge* amount of data coming in), monthly, or yearly options (if you have a smaller amount of data coming in)
    - Ingestion time (`_PARTITIONTIME`): daily (default), hourly (if you have a *huge* amount of data coming in), monthly, or yearly options (if you have a smaller amount of data coming in)
    - An integer range
- **When partitioning data, to achieve its *full* potential, we'd prefer *evenly-distributed* partitions**
- In addition, we **must take into account the number of partitions that we will need**, since **BigQuery limits the number of partitions to 4000**
    - Might want to have an **expire partitioning strategy**
        - https://cloud.google.com/bigquery/docs/managing-partitioned-tables#partition-expiration
- But, partitioning **typically doesn't show much improvement for tables with < 1 GB of data**, since it incurs metadata reads and metadata maintenance
- Again, more info can be found at: https://cloud.google.com/bigquery/docs/partitioned-tables 


### Clustering in BigQuery
- We can also **cluster** tables based on some field
    - In the StackOverflow example, *after* partitioning questions by date, we may want to additionally cluster them by `tag` *within each partition*
- **Clustering also helps us to reduce costs and improve query performance**
- *The field that we choose for clustering depends on how the data will be queried*
- For our taxi data, do:
    ```SQL
        -- Creating a partition and cluster table
        CREATE OR REPLACE TABLE <project-id>.ny_taxi.yellow_taxi_data_partitioned_clustered
        PARTITION BY DATE(tpep_pickup_datetime)
        CLUSTER BY VendorID
        AS
        SELECT * FROM <project-id>.ny_taxi.external_yellow_tripdata;
    ```
    - In this example, we're assuming we typically filter on date *and* `VendorID`
- We can see the partitioning *and* clustering details in the "Details" tab of the table    
- - You will see 584 MB Bytes processed billed for the partitioned table, and 449 MB Bytes processed for the partitioned *and* clustered table after running the following:
    - Just partitioned:
        ```SQL
            SELECT COUNT(*) as trips
            FROM <project-id>.ny_taxi.yellow_taxi_data_partitioned
            WHERE 
            DATE(tpep_pickup_datetime) BETWEEN '2019-01-01' AND '2020-03-31'
            AND VendorID=1;
        ```
    - Partitioned and clustered:
        ```SQL
            SELECT COUNT(*) as trips
            FROM <project-id>.ny_taxi.yellow_taxi_data_partitioned_clustered
            WHERE 
            DATE(tpep_pickup_datetime) BETWEEN '2019-01-01' AND '2020-03-31'
            AND VendorID=1;        
        ```
- When clustering in BigQuery, columns we specify are used to **colocate** related data 
- **A maximum of 4 clustering columns can be used**, and **the *order* the columns are specified is important as it determines the *sort order* of the data**
    - Clustering columns *must* be **top-level, non-repeated columns**
        - Such as `DATE`, `BOOL`, `GEOGRAPHY`, `INT64`, `NUMERIC`, `BIGNUMERIC`, `STRING`, `TIMESTAMP`, `DATETIME` types
- Clustering **improves both filtering and aggregation queries**
- *But*, clustering **typically doesn't show much improvement for tables with < 1 GB of data**, since it incurs metadata reads and metadata maintenance
- **Automatic reclustering:**
    - https://cloud.google.com/bigquery/docs/clustered-tables#automatic_reclustering
    - As data is added to a clustered table:
        - The newly inserted data can be written to **blocks** which contain key ranges that overlap with the key ranges in *previously* written blocks
        - These overlapping keys *weaken* the sort property of the table and hinder/increase query times
    - *To maintain the performance characteristics of a clustered table*:
        - BigQuery performs automatic ***re*-clustering** in the background to restore the sort property of the table
        - For partitioned tables, clustering is maintained for data within the scope of each partition
        - This is also good because **it doesn't cost the end user anything**
- Again, more info can be found at: https://cloud.google.com/bigquery/docs/clustered-tables


### Partitioning vs Clustering
- In *partitioning*, the *cost is **known** upfront*, while the **cost benefit is unknown for clustering**
    - If it's *really* important for us to maintain our queries below some cost, then *clustering* becomes important
        - In BigQuery, you can specify that a query not run if it exceeds some cost
        - This would not be possible if *just* clustering a table
            - You'd need partitioniong to know the upfront costs
- Use partitioning when you need partition-level management (creating new or deleting or moving partitions, etc.), but **use clustering when you need more granularity than what partitioning alone allows**
- Use **partitioning if you want to filter or aggregate on a *single column***, and use ***clustering* when your queries commonly use filters or aggregations against *multiple* particular columns**
- Also, **use clustering when the *cardinality* of the number of values in a column or group of columns is large**
    - This becomes a hindrance in partitioning due to the 4000 partition limit in BigQuery
- ***Use clustering over partitioning when:***
    - Partitioning results in a small amount of data per partition (approximately < 1 GB)
        - So if partitions are really small or columns have a lot of granularity, use clustering instead
    - Partitioning results in a large number of partitions, beyond the limits on partitioned tables (4000 partitions)
    - Partitioning results in your mutation operations modifying the majority of partitions in the table frequently (for example, every few minutes)

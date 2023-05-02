# Data Warehouses and Google BigQuery

## Data Warehouses

### OLAP vs OLTP
- ***OLTP***: typically used in **backend services**, where sequences of SQL statements are grouped together in the form of **transactions**, which are **rolled back** if any of their statements fails. These systems deal with **fast and small updates**, store data in **normalized** databases that **reduce data redundancy and increase productivity** of end user
    - Purpose = control and run essential business operations **in real-time**
    - Data updates = short, fast updates by a user
    - Database design = **Normalized** for efficiency
    - Space requirements = Generally small if historical data is archived
    - Backup and recovery = **Regular backups** required to ensure business continuity and meet legal and governance requirements
    - Productivity = Increases end user productivity
    - Data view = **Day-to-day** *business transactions*
    - User examples = Customer-facing personnel, clerks, online shoppers
- ***OLAP***: composed by **denormalized** databases, which simplify **analytics queries**, and are mainly used for **data mining**, and they generally contain **data from many sources** (e.g., different OLTP systems) and implement **star or snowflake schemas** that are optimized for analytical tasks
    - Purpose = Plan, solve problems, support decisions, discover hidden insights using a *lot* of data
    - Data updates = data **refreshed periodically** with scheduled, long-running **batch jobs**
    - Database design = **De-normalized** for analysis
    - Space requirements = Generally large due to aggregating large datasets
    - Backup and recovery = Lost data can be reloaded from OLTP database in lieu of regular backups
    - Productivity = Increases business manager, data analyst and data scientist, and executive productivity
    - Data view = **Multi-dimensional** view of *enterprise data*
    - User examples = Knowledge workers such as business managers, data analysts and data scientists, and executives


### What is a Data Warehouse
- An OLAP solution used for reporting and data analysis
- Generally consists of raw data, metadata, and summary data, all from various sources (flat files, different operational systems, OLTP databases, etc.) connected by a **staging** area
- Can connect to/be output as **data marts** for consumption by end users (analysis, reporting, mining, etc.)
    - Some users, like data scientists, may look directly at raw data in the warehouse


## BigQuery

### Intro to BigQuery
- A **serverless** data warehouse
    - No servers to manage or database software to install
- Software as well as infrastructure including: **scalability** and **high-availability**
    - Don't need to create and maintain your own data warehouse
- Built in-features (such as ML, geospatial analysis, BI, etc.)
- BigQuery **maximizes flexibility by separating the compute engine that analyzes your data from your storage**
    - Generally, with one big server with storage and compute together, once your data size increases, your machine *must* grow with it    
- Has **on-demand pricing** (1 TB of processing is $5)
- Also has flat-rate pricing
    - Based on number of pre requested slots (100 slots -> $2,000/month = 400 TB data processed on-demand pricing)
    - *Doesn't really make sense to use this unless processing a lot of data*
- Generally **caches** data (which you can disable to achieve consistent results)
- Provides a lot of open source public data (like a NYC Citibike stations dataset) that you can search for withing BigQuery
    - i.e., Can query `station_id` and `name` fields from the `citibike_stations table` via ```SELECT station_id, name FROM `bigquery-public-data.new_york_citibike.citibike_stations` LIMIT 1000;```
- As a practical example, we will create an external table (https://cloud.google.com/bigquery/docs/external-data-sources):
     - *"**External tables** are similar to standard BigQuery tables, in that these tables store their metadata and schema in BigQuery storage. However, their **data resides in an external source**"
     - *"External tables are contained inside a dataset, and you manage them in the same way that you manage a standard BigQuery table."*
     - We will create the external table from one of our yellow taxi datasets as an **external source**
     - BigQuery allows us to make tables based off of GCS Buckets via **gsutil URI's**
     - Make sure there is some 2019 data in your GCS bucket
        - If not, run ***THE UPDATED `parameterized_flow.py`*** flow in the `week3_data_warehouse/` directory while in the `zoom` conda environment via `python parameterized_flow.py`
            - ***Ran into an issue of various fields being FLOATs and INTs, due to a `nan` value, had to fix***
    - Once the data is there, make sure you have a `ny_trips` dataset in BigQuery, and *NO* `external_yellow_trip_data` table (**If it's there, drop it***)
    - Then, using the **gsutil URI's** of the data files, run
        ```bash
            CREATE OR REPLACE EXTERNAL TABLE `de-zoomcamp-384821.ny_trips.external_yellow_trip_data`
                OPTIONS (
                format = 'PARQUET',
                uris = [r'gs://prefect-de-zoomcamp-384821/data\yellow\yellow_tripdata_2019-*.parquet', r'gs://prefect-de-zoomcamp-384821/data\yellow\yellow_tripdata_2020-*.parquet']
                );
        ```
    - OR run 
        ```bash
            CREATE OR REPLACE EXTERNAL TABLE `de-zoomcamp-384821.ny_trips.external_yellow_trip_data`
                OPTIONS (
                format = 'PARQUET',
                uris = ['gs://prefect-de-zoomcamp-384821/data/yellow/yellow_tripdata_2019-*.parquet', 'gs://prefect-de-zoomcamp-384821/data/yellow/yellow_tripdata_2020-*.parquet']
                );
        ```    
    - Then run ```SELECT * FROM `de-zoomcamp-384821.ny_trips.external_yellow_trip_data` limit 10;```
    - When loading in the data BigQuery *knows* what data type a field is and makes it that data type, as well as convert and figure out if the field is nullable or not
        - In this way, we don't always have to define our schema (*but we could do that if we really wanted to*)
    - Go to the "Details" tab of the table once you have it open, and notice "Table Size" and "Long-term storage size" are both 0 Bytes, and "Number of Rows" is blank
    - Unfortunately, with external tables, BigQuery is unable to not able to determine the number of rows or the table size cost, since the data itself is not *inside* BigQuery, but is instead in external data storage, like a GCS Bucket


### Partitioning in BigQuery
- Generally, when we create a dataset, we have one or more certain columns that can be used as some type of *"filter"*
- In such cases, we can **partition** a table based on such columns to improve BigQuery's performance
    - Example: A dataset containing StackOverflow questions partitioned by the `creation_date field`
- Partitioning is a powerful feature of BigQuery
    - Suppose we want to query the StackOverflow questions created on a specific date
    - **Partitionining improves processing**, because *BigQuery will not read or process any data from other dates*, which improves efficiency and reduces querying costs by processing less data
- To view the performance improvements, create a *non*-partitioned table from the external table via
    ```bash
        CREATE OR REPLACE TABLE `de-zoomcamp-384821.ny_trips.yellow_trip_data_non_partitioned`
        AS
        SELECT * FROM `de-zoomcamp-384821.ny_trips.external_yellow_trip_data`;
    ```
- Next, create a partitioned table from the same external table via
    ```bash
        CREATE OR REPLACE TABLE `de-zoomcamp-384821.ny_trips.yellow_trip_data_non_partitioned`
        PARTITION BY
            DATE(tpep_pickup_datetime) AS
        SELECT * FROM `de-zoomcamp-384821.ny_trips.external_yellow_trip_data`;
    ```
- We can see the partitioning details in the "Details" tab of the table
- Then, to see the difference in processing, run the same query on both tables
    ```bash
        SELECT DISTINCT(VendorID)
        FROM de-zoomcamp-384821.ny_trips.yellow_trip_data_non_partitioned
        WHERE DATE(tpep_pickup_datetime) BETWEEN '2019-01-01' AND '2019-03-31';
    ```
    - And 
        ```bash
            SELECT DISTINCT(VendorID)
            FROM de-zoomcamp-384821.ny_trips.yellow_trip_data_partitioned
            WHERE DATE(tpep_pickup_datetime) BETWEEN '2019-01-01' AND '2019-03-31';
        ```
- You will see 583.36 MB Bytes processed, 583 MB Bytes billed for the NON-partitioned table, and 343.61 MB Bytes processed, 344 MB Bytes billed for the partitioned table
    - *If you highlight the query in the editor, in the top right BigQuery will tell you this info before you run it*
- We can look directly into the partitons to see how many rows are in each partition via
    ```bash
        SELECT table_name, partition_id, total_rows
        FROM `ny_trips.INFORMATION_SCHEMA.PARTITIONS`
        WHERE table_name = 'yellow_trip_data_partitioned'
        ORDER BY total_rows DESC;
    ```
    - This is helpful in determining if we have a bias in our partition
        - i.e., if we have some partitions getting more rows/data relative to others
- In BigQuery, we can partition data by:
    - A time-unit column: daily (default), hourly (if you have a *huge* amount of data coming in), monthly, or yearly options (if you have a smaller amount of data coming in)
    - Ingestion time (`_PARTITIONTIME`): daily (default), hourly (if you have a *huge* amount of data coming in), monthly, or yearly options (if you have a smaller amount of data coming in)
    - An integer range
- **When partitioning data, to achieve its full potential, we'd prefer *evenly-distributed* partitions**
- In addition, we **must take into account the number of partitions that we will need**, since **BigQuery limits the number of partitions to 4000*
    - Might want to have an **expire partitioning strategy**
- But, partitioning **typically doesn't show much improvement for tables with < 1 GB of data**, since it incurs metadata reads and metadata maintenance
- https://cloud.google.com/bigquery/docs/partitioned-tables 


### Clustering in BigQuery
- We can also **cluster** tables based on some field
    - In the StackOverflow example, after partitioning questions by date, we may want to cluster them by `tag` *within each partition*
- Clustering also helps us to reduce costs and improve query performance
- The field that we choose for clustering depends on how the data will be queried
- For our taxi data, do:
    ```bash
        CREATE OR REPLACE TABLE de-zoomcamp-384821.ny_trips.yellow_tripdata_partitoned_clustered
        PARTITION BY DATE(tpep_pickup_datetime)
        CLUSTER BY VendorID AS
        SELECT * FROM de-zoomcamp-384821.ny_trips.external_yellow_trip_data;
    ```
- We can see the partitioning *and* clustering details in the "Details" tab of the table    
- - You will see 583.36 MB Bytes processed billed for the partitioned table, and 448.91 MB Bytes processed for the partitioned *and* clustered table
    - 1:
        ```bash
            SELECT COUNT(*) as trips
            FROM de-zoomcamp-384821.ny_trips.yellow_trip_data_partitioned
            WHERE 
            DATE(tpep_pickup_datetime) BETWEEN '2019-01-01' AND '2020-03-31'
            AND VendorID=1;
        ```
    - 2:
        ```bash
            SELECT COUNT(*) as trips
            FROM de-zoomcamp-384821.ny_trips.yellow_tripdata_partitoned_clustered
            WHERE 
            DATE(tpep_pickup_datetime) BETWEEN '2019-01-01' AND '2020-03-31'
            AND VendorID=1;        
        ```
- When clustering in BigQuery, columns we specify are used to **colocate** related data 
- **A maximum of 4 clustering columns can be used**, and **the order the columns are specified is important as it determines the sort order of the data**
    - Clustering columns *must* be **top-level, non-repeated columns**
        - Such as `DATE`, `BOOL`, `GEOGRAPHY`, `INT64`, `NUMERIC`, `BIGNUMERIC`, `STRING`, `TIMESTAMP`, `DATETIME`
- Clustering **improves both filtering and aggregation queries**
- But, clustering **typically doesn't show much improvement for tables with < 1 GB of data**, since it incurs metadata reads and metadata maintenance
- **Automatic reclustering**
    - As data is added to a clustered table:
        - The newly inserted data can be written to **blocks** which contain key ranges that overlap with the key ranges in *previously* written blocks
        - These overlapping keys *weaken* the sort property of the table and hinder/increase query times
    - *To maintain the performance characteristics of a clustered table*:
        - BigQuery performs automatic **re-clustering** in the background to restore the sort property of the table
        - For partitioned tables, clustering is maintained for data within the scope of each partition.
- https://cloud.google.com/bigquery/docs/clustered-tables

### Partitioning vs Clustering
- In partitioning, the cost is known upfront, while the *cost benefit is unknown for clustering*
    - If it's really important for us to maintain our queries below some cost, then clustering becomes important
    - This would not be possible if *just* clustering a table
- Use partitioning when you need partition-level management (creating new or deleting or moving partitions, etc.), but use clustering when you need more granularity than what partitioning alone allows
- Use *partitioning* if you want to filter or aggregate on a *single column*, and use *clustering* when your queries commonly use filters or aggregations against *multiple* particular columns
- Also, use clustering when the **cardinality** of the number of values in a column or group of columns is large
    - This becomes a hindrance in partitioning due to the 4000 partition limit in BigQuery
- **Use clustering over partitioning when:**
    - Partitioning results in a small amount of data per partition (approximately < 1 GB)
        - So if partitions are really small or columns have a lot of granularity, use clustering instead
    - Partitioning results in a large number of partitions beyond the limits on partitioned tables (4000 partitions)
    - Partitioning results in your mutation operations modifying the majority of partitions in the table frequently (for example, every few minutes)


### BigQuery Best Practices
- **Cost reduction**:
    - Avoid using `SELECT *` = It is much better to specify a particular subset of columns to reduce the amount of scanned data, since **BigQuery stores data in a columnar-type storage**
    - *Price* queries before running them
    - Use clustered or partitioned tables to optimize the number of scanned records
    - Use **streaming inserts** with caution, because they could drastically increase the costs
    - Materialize query results in *different stages* (like materialize CTE's before using them later in multiple locations)
- **Query performance**:
    - *Always filter data using partitioned or clustered columns*
    - Use **denormalized data** that facilitate *analytical* queries
        - Use **nested** or **repeated columns** in case you have a complicated structure to help denormalize
    - Excess usage of external storage might incur in more costs, use them appropriately
    - Reduce data before performing a `JOIN` operation
    - Optimize `JOIN` patterns
    - Don't treat `WITH` clauses as *prepared* statements
    - `ORDER` statements must be *last* part of the query to optimize performance
    - In queries, as a best practice, **place the table with the largest number of rows first, followed by the table with the fewest rows, and then place the remaining tables by decreasing sizes**
        - The first table will be distributed equally, and the next table will be **broadcasted** to all nodes
    - Avoid **oversharding** tables
        - **Table sharding** = the practice of storing data in multiple tables, using a naming prefix such as [PREFIX]_YYYYMMDD
            - Partitioning is recommended over table sharding, because partitioned tables perform better
            With sharded tables, BigQuery must maintain a copy of the schema and metadata for *each* table
            - BigQuery might also need to verify permissions for each queried table
            - This practice also adds to query overhead and affects query performance
            - https://cloud.google.com/bigquery/docs/partitioned-tables
    - Avoid JavaScript user-defined functions
    - Use appropriate aggregation functions (HyperLogLog++)


### BigQuery Internals
- Generally don't have to know this stuff, so long as you know best practices of BigQuery
- 
- **Colossus**: Google's distributed file storage that stores data in a *columnar* format
    - Colossus is *separated from computation*, and thus, it is generally cheap with significantly less cost
- **Jupiter**: Since compute and storage are in *different* hardware, Google needs a very fast network for communication to avoid long query times
    - Jupiter = the network that is implemented inside BigQuery's datacenter and has ~1 TB bandwidth/network speed
- **Dremel**: The query execution engine
    - Dremel generally divides each query into a tree structure, whose parts are executed in parallel across several **nodes** (each node can execute an individual subset of the query)
- **Column-oriented storage**: Type of storage that is optimized for querying subsets of columns from tables (think parquet files vs. row-oriented storage like CSV's)
    - It is also efficient for performing filtering or aggregation functions over columns
    - When BigQuery recieves a query, it *understands* it and knows how to divide it into smaller sub-modules
    - Then **mixers** recieve the modified query, and these further divide them into smaller sub-queries and send them to nodes
    - The **leaf nodes** are who actually talks to Colossus, fetches the data, performs operations on it, and returns it back the mixers, who then return everything to the root server(s) where everything is aggregated and returned
    - *This distribution of workers in here is why BigQuery is so fast*
- References:
    - https://cloud.google.com/bigquery/docs/how-to
    - https://research.google/pubs/pub36632/
    - https://panoply.io/data-warehouse-guide/bigquery-architecture/
    - http://www.goldsborough.me/distributed-systems/2019/05/18/21-09-00-a_look_at_dremel/


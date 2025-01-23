# Data Warehouses and Google BigQuery

## Data Warehouses

### OLTP vs. OLAP
- ***Online Transactional Processing (OLTP) systems*** are typically used in **backend services**, where sequences of SQL statements are grouped together in the form of **transactions**
    - Transactions are **rolled back** if *any* of their statements fail
    - OLTP systems deal with **fast but small** updates and store data in database designs that are **normalized**, both for efficiency reasons and to **reduce data redundancy and increase productivity of *end users***
    - The purpose of an OLTP system is to control and run essential business operations **in real-time**
    - Data updates are typically short and fast, and initiated by a user
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
- For more, see:
    - https://www.theseattledataguy.com/oltp-vs-olap-what-is-the-difference/
    - https://aws.amazon.com/compare/the-difference-between-olap-and-oltp/
    - https://www.snowflake.com/guides/olap-vs-oltp/
    - https://www.ibm.com/think/topics/olap-vs-oltp

## What is a Data Warehouse?
- A ***data warehouse (DW)*** is an *OLAP* (large amounts of data, usually denormalized, from various sources, etc.) solution used for **reporting and data analysis**
- It generally consists of **raw data, metadata, and summary data**, all **from various sources** (flat files, different operational systems, OLTP databases, etc.) that are connected to a **staging** area before being loaded into the data warehouse
- They can connect to and be output as **data marts** (such as marts for purchasing, sales, and inventory, etc.) for consumption by different end users (for analysis, reporting, mining, etc.)
    - Some users, like data scientists, may look *directly* at raw data in the data warehouse, while analysts mostly look at marts


## Google BigQuery

### Intro to BigQuery
- Google BigQuery is a **serverless** data warehouse
    - In other words, there are no servers to manage nor any database software to install
    - Generally when a company starts on a journey of data warehousing/analytics, a large amount of time is spent creating a data warehouse (not to mention maintaining it)
    - BigQuery can help alleviate this overhead
- BigQuery provides **software *as well as* infrastructure** including features such as **scalability** (start from GB and scale up to PB in size) and **high-availability**
    - You don't need to create and maintain your *own* data warehouse
- It has a varity of **built in-features**, such as machine learning (ML), geospatial analysis, business intelligence (BI), etc.
- BigQuery **maximizes *flexibility* by *separating* the compute engine (which analyzes your data) from your storage**
    - Generally, with one big server having storage and compute together (or **tightly-coupled**), once your data size increases, your machine size *must* grow with it
- BigQuery has **on-demand pricing** (For example: 1 TB of data processed costs $5, as of 2022)
    - BigQuery also has *flat-rate pricing*
        - This is based on number of pre-requested slots (For example: 100 slots gives $2,000 per month, which equals 400 TB of data processed via on-demand pricing)
        - *It doesn't really make sense to use this unless you are processing a LOT of data (say, above 200 TB of data)*
        - You must also think about queries competing with one another
            - For example, if you have 50 queries running and all 100 of your slots are full, a 51st query will have to wait
                - However, in on-demand BigQuery, this would not be the case, as it can provide you with additional slots as per the query's needs
- BigQuery generally **caches** data (which you *can* disable in "Query settings" in the BigQuery SQL UI to achieve consistent results)
- You can easily view the **schema** of datasets in BigQuery, as well as other details and a quick preview of a dataset
- BigQuery provides a lot of **open source public data** (like a NYC Citibike stations dataset `citibike_stations`) that you can search for within BigQuery
    - i.e., You can query the `station_id` and `name` fields from the `citibike_stations` table via ```SELECT station_id, name FROM `bigquery-public-data.new_york_citibike.citibike_stations` LIMIT 100;```
    - Results of such queries can be saved or explored via Data Studio


## BigQuery Example: External Tables
- As a practical example, we will create an **external table** (https://cloud.google.com/bigquery/docs/external-data-sources):
     - **External tables** are similar to standard BigQuery tables, in that these tables store their *metadata and schema* in BigQuery storage 
        - However, their ***data* resides in an *external* source**, such as Google Cloud Storage (GCS)
        - Even so, you **can directly query it** from within BigQuery
        - "External tables are contained *inside a dataset*, and you manage them in the same way that you manage a standard BigQuery table"
     - We will create the external table from one of our yellow taxi datasets as an **external source**
        - BigQuery allows us to make tables based off of GCS Buckets via **gsutil Uniform Resource Identifiers (URI's)**
            - These URI's are in the format `gs://<bucket-name>/<file-name>`
        - To start off, make sure there is some data in your GCS bucket that you will be using (green, yellow, and possibly FHV datasets)
            - Do this via drag-and-drop of Parquet files or via an orchestration tool or Python script utilizing CSV's
                - ***May run into an issue of various fields being FLOATs and INTs, due to a `nan` value and have to fix***
                - ***See `upload_all_data_gcs_parquet.py` in GitHub repo for details***
        - Once the data is there (`python upload_all_data_gcs_parquet.py`), make sure you have a `ny_taxi` dataset under your project ID in BigQuery, and *NO* `external_nyc_yellow_taxi_data` table (***If it's there, drop it***)
        - Then, using the **gsutil URI's** of the data files, run
            ```SQL
                -- Creating external table referring to GCS path (gutil URI)
                CREATE OR REPLACE EXTERNAL TABLE `<project-id>.de_zoomcamp.external_nyc_yellow_taxi_data`
                    OPTIONS (
                        format = 'PARQUET',
                        uris = ['gs://<bucket-name>/data/yellow/yellow_tripdata_2019-*.parquet',
                            'gs://<bucket-name>/data/yellow/yellow_tripdata_2020-*.parquet']
                    );
            ```    
        - Then run:
            ```SQL
            SELECT * FROM `<project-id>.de_zoomcamp.external_nyc_yellow_taxi_data` limit 10;
            ```
    - When loading in the data, BigQuery *knows* what data type a field is in the source and *makes* it that data type in the destination, as well as converting and figuring out if the field is `NULL`-able or not
        - In this way, **we don't always have to define our schema (*but we could do that if we really wanted to*)**
    - Go to the "Details" tab of the table once you have it open, and notice "Table Size" and "Long-term storage size" are both 0 Bytes, and "Number of Rows" is blank
        - Unfortunately, with *external* tables, BigQuery is unable to not able to determine the number of rows or the table size cost, since the data itself is not *inside* BigQuery, but is instead in external data storage (such as a GCS Bucket)

### Partitioning in BigQuery
- Generally, when we create a dataset, we have one or more certain columns that many queries are based off of and that can be used as some type of *"filter"*
- In such cases, we can **partition** a table based on such columns to improve BigQuery's performance
    - https://cloud.google.com/bigquery/docs/partitioned-tables
    - Example: A dataset containing StackOverflow questions partitioned by a `creation_date` field, since we often filter on dates
- **Partitioning** is a powerful feature of BigQuery
    - Suppose we want to query the StackOverflow questions created on a specific date
    - **Partitionining improves processing**, because *BigQuery will not read or process any data from other dates*, which improves efficiency and reduces querying costs by processing less data
- To view the performance improvements, create a *non*-partitioned table from the external table via
    ```SQL
        -- Create a non-partitioned table from external table
        CREATE OR REPLACE TABLE `<project-id>.de_zoomcamp.yellow_taxi_data_non_partitioned`
        AS
        SELECT * FROM `<project-id>.de_zoomcamp.external_nyc_yellow_taxi_data`
        ;
    ```
- Next, create a *partitioned* table from the *same* external table via
    ```SQL
        -- Create a partitioned table from external table
        CREATE OR REPLACE TABLE `<project-id>.de_zoomcamp.yellow_taxi_data_partitioned`
        PARTITION BY DATE(tpep_pickup_datetime) 
        AS
        SELECT * FROM `<project-id>.de_zoomcamp.external_nyc_yellow_taxi_data`
        ;
    ```
- We can see the partitioning details in the "Details" tab of the partitioned table
    - For example, it notes that the partitioned table is partitioned by *day*, from the `tpep_pickup_datetime` field
- Then, to see the difference/advantage in processing, highlight both queries and note the processing size on the top right of the query UI:
    - First:
        ```SQL
            -- See impact of partition in scanned data size
            SELECT DISTINCT(vendor_id)
            FROM `<project-id>.de_zoomcamp.yellow_taxi_data_non_partitioned`
            WHERE DATE(tpep_pickup_datetime) BETWEEN '2019-06-01' AND '2019-06-30'
            ;
            -- Scanning 1.62GB of data for Yellow June 2019 data

        ```
    - And then:
        ```SQL
            SELECT DISTINCT(vendor_id)
            FROM `<project-id>.de_zoomcamp.yellow_taxi_data_partitioned`
            WHERE DATE(tpep_pickup_datetime) BETWEEN '2019-06-01' AND '2019-06-30'
            ;
            -- Scanning 343.61MB of data for Yellow June 2019 data
        ```
- You will see 344 MB processed for the NON-partitioned table, and 1.62 GB (162 MB) processed for the partitioned table
    - *Again, if you highlight the query in the editor, in the top right corner of the query UI in BigQuery will tell you this info **before** you run it*
- We can even look *directly into* the partitons to see how many rows are in each partition via:
    ```SQL
        -- Look into the partitons
        SELECT table_name, partition_id, total_rows
        FROM `de_zoomcamp.INFORMATION_SCHEMA.PARTITIONS`
        WHERE table_name = 'yellow_taxi_data_partitioned'
        ORDER BY total_rows DESC
        ;
    ```
    - This is helpful in determining if we have a *bias* in our partition
        - i.e., If we have some partitions getting more rows/data relative to others
- In BigQuery, we can partition data by:
    - A time-unit column: daily (default), hourly (if you have a *huge* amount of data coming in), monthly, or yearly options (if you have a smaller amount of data coming in)
    - Ingestion time (`_PARTITIONTIME`): daily (default), hourly (if you have a *huge* amount of data coming in), monthly, or yearly options (if you have a smaller amount of data coming in)
    - An integer range
- **When partitioning data, to achieve its *full* potential, we'd prefer *evenly-distributed* partitions**
- In addition, we **must take into account the number of partitions that we will need**, since **BigQuery limits the number of partitions to 4,000**
    - Might want to have an **expire partitioning strategy**
        - https://cloud.google.com/bigquery/docs/managing-partitioned-tables#partition-expiration
- **NOTE:** Partitioning **typically doesn't show much improvement for tables with < 1 GB of data**, since it incurs metadata reads and metadata maintenance
- Again, more info can be found at: https://cloud.google.com/bigquery/docs/partitioned-tables 


### Clustering in BigQuery
- We can also **cluster** tables based on some field
    - In the StackOverflow example, *after* partitioning questions by date, we may want to additionally cluster them by `tag` *within each partition*
- **Clustering also helps us to reduce costs and improve query performance**
- *The field that we choose for clustering depends on how the data will be queried*
- For our taxi data, do:
    ```SQL
        -- Creating a partition and cluster table
        CREATE OR REPLACE TABLE `<project-id>.de_zoomcamp.yellow_taxi_data_partitioned_clustered`
        PARTITION BY DATE(tpep_pickup_datetime)
        CLUSTER BY vendor_id
        AS
        SELECT * FROM `<project-id>.de_zoomcamp.external_nyc_yellow_taxi_data`
        ;
    ```
    - In this example, we're assuming that we typically filter on date *and* `vendor_id`
- We can see the partitioning *and* clustering details in the "Details" tab of the table overview UI  
- Note any potential difference in data scanned:
    - Just partitioned:
        ```SQL
            -- See impact of partition AND cluster in scanned data size
            SELECT COUNT(*) as trips
            FROM `<project-id>.de_zoomcamp.yellow_taxi_data_partitioned`
            WHERE 
                DATE(tpep_pickup_datetime) BETWEEN '2019-01-01' AND '2020-03-31'
                AND vendor_id = 1
            ;
            -- 1.49GB scanned
        ```
    - Partitioned and clustered:
        ```SQL
            SELECT COUNT(*) as trips
            FROM `<project-id>.de_zoomcamp.yellow_taxi_data_partitioned_clustered`
            WHERE 
                DATE(tpep_pickup_datetime) BETWEEN '2019-01-01' AND '2020-03-31'
                AND vendor_id = 1
            ;
            -- 1.49GB scanned
        ```
- When clustering in BigQuery, columns we specify are used to **colocate** related data 
- **A maximum of 4 clustering columns can be used**, and **the *order* the columns as specified is important as it determines the *sort order* of the data**
    - Clustering columns *must* be **top-level, non-repeated columns**
        - Such as `DATE`, `BOOL`, `GEOGRAPHY`, `INT64`, `NUMERIC`, `BIGNUMERIC`, `STRING`, `TIMESTAMP`, `DATETIME` types
- Clustering **improves both *filtering* and *aggregation* queries**
- **NOTE:** Clustering **typically doesn't show much improvement for tables with < 1 GB of data**, since it incurs metadata reads and metadata maintenance
- **Automatic reclustering:**
    - https://cloud.google.com/bigquery/docs/clustered-tables#automatic_reclustering
    - As data is added to a clustered table:
        - Generally, the newly inserted data can be written to **blocks** which contain key ranges that overlap with the key ranges in *previously*-written blocks
        - These overlapping keys *weaken* the sort property of the table and hinder/increase query times
    - *To maintain the performance characteristics of a clustered table*:
        - BigQuery performs automatic ***re*-clustering** in the background (i.e., you shouldn't notice) to restore the sort property of the table
        - For partitioned tables, clustering is maintained for data within the scope of each partition
        - This is also good because **it doesn't cost the end user anything**
- Again, more info can be found at: https://cloud.google.com/bigquery/docs/clustered-tables


### Partitioning vs Clustering
- In *partitioning*, the *cost is **known** upfront*, while the **cost benefit is unknown for *clustering***
    - If it's *really* important for us to maintain our queries below some cost, then *clustering* becomes important
        - In BigQuery, you can specify that a query not run if it exceeds some cost
        - This would not be possible if *just* clustering a table
            - You'd need partitioniong to know the *upfront* costs
- Use partitioning when you need **partition-level management** (creating new or deleting or moving partitions, etc.), but **use clustering when you need more granularity than what partitioning alone allows**
- Use **partitioning if you want to filter or aggregate on a *single* column**, and, generally, use ***clustering* when your queries commonly use filters or aggregations against *multiple* particular columns**
- Also, **use clustering when the *cardinality* of the number of values in a column or group of columns is large**
    - This becomes a hindrance in partitioning due to the 4000 partition limit in BigQuery
    - NOTE: High cardinality means columns with values that are very uncommon or unique (i.e., containing few or no duplicate values)
- ***Use clustering over partitioning when:***
    - Partitioning results in a small amount of data per partition (approximately < 1 GB)
        - In other words, if partitions are really small or if columns have a lot of granularity, use clustering instead
    - Partitioning results in a large number of partitions, beyond the limits on partitioned tables (4,000 partitions)
    - Partitioning results in your mutation operations modifying the majority of partitions in the table frequently (for example, every few minutes)


### BigQuery Best Practices
- Generally, most of our efforts will be based on **cost reduction** on improving **query performance**
    - **Cost reduction**:
        - **Avoid using `SELECT *`** 
            - It is much better to specify a *particular subset* of columns to **reduce the amount of *scanned* data**, since **BigQuery stores data in a *columnar-type* storage**
        - *Price* queries *before* running them
            - Seen in the top right-hand side of a query window when highlighting a query in the BigQuery query UI
        - Use **clustered** or **partitioned** tables to optimize the number of scanned records
        - Use **streaming inserts** *with caution*
            - They could drastically increase costs
        - **Materialize** query results in *different **stages***
            - Like materializing CTE's before using them later, in multiple locations
        - Also note that **BigQuery *caches* query results**
    - **Query performance**:
        - ***Always* filter data on a partitioned or clustered column(s)**
        - ***De*-normalize data** to facilitates *analytical* queries
        - Use **nested** or **repeated columns** (in case you have a complicated structure, in order to help de-normalize)
        - *Excess* usage of *external* storage might incur in more costs, so use them appropriately
        - Reduce data *before* performing a `JOIN` operation
        - Optimize `JOIN` patterns
        - *Don't* treat `WITH` clauses as *prepared* statements
        - `ORDER` statements must be *last* part of the query to optimize performance
            - See https://cloud.google.com/bigquery/docs/best-practices-performance-compute#optimize_the_order_by_clause
        - In queries, as a best practice, **place the table with the largest number of rows first, followed by the table with the fewest rows, and *then* place the remaining tables by decreasing sizes**
            - The first, largest table will be distributed equally, and the *next* table will be **broadcasted** to all nodes
            - See: https://cloud.google.com/bigquery/docs/best-practices-performance-compute#optimize_your_join_patterns
        - Avoid **oversharding** tables
            - **Table sharding** is the practice of storing data in multiple tables, using a naming prefix such as `[PREFIX]_YYYYMMDD`
                - **Partitioning is recommended over table sharding, because partitioned tables perform better**
                - With sharded tables, BigQuery must maintain a copy of the schema and metadata for *each* table
                - BigQuery might also need to verify permissions for each queried table
                - This practice also adds to query overhead and affects query performance
                - See https://cloud.google.com/bigquery/docs/partitioned-tables#dt_partition_shard
        - *Avoid* JavaScript user-defined functions (UDFs)
        - Use appropriate aggregation functions (such as `HyperLogLog++`)


### BigQuery Internals
- One doesn't generally don't have to know this information, so long as you know best practices of BigQuery
    - But knowing the internals of a cloud data warehouse such as BigQuery may help with building a data product in the future
- **Colossus**: Google's distributed file storage that stores data in a **columnar format**
    - BigQuery stores data in this *separate* storage file system
    - Colossus is **separated from computation*, and thus, it is *generally cheap with significantly less cost*
        - If your data size drastically increases, you're only paying for *storage* costs
        - **The most amount of cost incurred comes from reading or doing/running queries, which involves the *compute* engine**
        - This is why separating compute from storage is an advantage for BigQuery
- If network connection is bad, it would result in poor (high) query time, but BigQuery has a solution to this:
    - **Jupiter**: The network implemented inside BigQuery's data center with ~1 TB bandwidth/network speed
        - Since compute and storage are in *different/separate* hardware, Google needs a very fast network for communication to avoid long query times
- **Dremel**: The query execution engine for BigQuery
    - Dremel generally divides each query into a tree structure, whose parts are executed *in parallel* across several **nodes** (each node can execute an individual subset of the query)
- **Column-oriented storage**: A type of storage that is optimized for querying subsets of columns from tables (think *parquet* files vs. row-oriented storage like CSV's)
    - It is also efficient for performing filtering or aggregation functions *over columns*
    - When BigQuery recieves a query, it *understands* it and knows how to *divide it into smaller sub-modules*
    - Then **mixers** recieve the modified query, further divide sub-queries into *even smaller* sub-queries, and send them to leaf nodes
    - The **leaf nodes** are who actually talks to the Colossus database (storage), fetch the data, perform operations on it, and return it back the mixers, who in turn return everything to the root server(s) where everything is aggregated and returned
    - **This distribution of workers in here is why BigQuery is so fast**
- References:
    - https://cloud.google.com/bigquery/docs/how-to
    - https://research.google/pubs/pub36632/
    - https://panoply.io/data-warehouse-guide/bigquery-architecture/
    - http://www.goldsborough.me/distributed-systems/2019/05/18/21-09-00-a_look_at_dremel/

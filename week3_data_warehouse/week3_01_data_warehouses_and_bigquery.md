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

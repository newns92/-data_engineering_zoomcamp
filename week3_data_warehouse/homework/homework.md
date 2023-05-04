## Week 3 Homework
***Important Note:***
- You can load the data however you would like, but keep the files in .GZ Format. 
- If you are using orchestration such as Airflow or Prefect do not load the data into Big Query using the orchestrator.
- Stop with loading the files into a bucket.
- *NOTE:* You can use the CSV option for the GZ files when creating an External Table

- ***Ignore "Stop with loading the files into a bucket" (see Question 8)***
- ***Run `get_fhv_data.py` in a `zoom` Anaconda environment (to be safe)***
- ***Once all 12 data files are in a GCS Bucket, proceed to next step***

***SETUP:***
- Create an external table using the fhv 2019 data.
- Create a table in BQ using the fhv 2019 data (do not partition or cluster this table).
- Data can be found here: https://github.com/DataTalksClub/nyc-tlc-data/releases/tag/fhv

- ***Create an external table via BigQuery UI***
    ```bash
        CREATE OR REPLACE EXTERNAL TABLE `de-zoomcamp-384821.fhv.external_fhv_data`
        OPTIONS (
        format = 'PARQUET',
        uris = ['gs://de-zoomcamp-384821-taxi-data/fhv_data/fhv_tripdata_2019-*.parquet']
        )
        ;
    ```
- Create a table in BigQuery (NOT external)
    ```bash
        CREATE OR REPLACE TABLE `de-zoomcamp-384821.fhv.fhv_data`
        AS
        SELECT * FROM `de-zoomcamp-384821.fhv.external_fhv_data`
        ;
    ```

## Question 1:
What is the count for fhv vehicle records for year 2019?

- Run:
    ```bash
        SELECT COUNT(*) FROM `de-zoomcamp-384821.fhv.fhv_data`
    ```

- ~~65,623,481~~
- ***43,244,696***
- ~~22,978,333~~
- ~~13,942,414~~

## Question 2:
- Write a query to count the distinct number of `affiliated_base_number` for the entire dataset on both the tables.
- What is the estimated amount of data that will be read when this query is executed on the External Table and the Table?

- ***Look at:***
    ```bash
        SELECT COUNT(*) FROM `de-zoomcamp-384821.fhv.external_fhv_data`
    ```
- ***And:***
    ```bash
        SELECT COUNT(*) FROM `de-zoomcamp-384821.fhv.fhv_data`
    ```

- ~~25.2 MB for the External Table and 100.87MB for the BQ Table~~
- ~~225.82 MB for the External Table and 47.60MB for the BQ Table~~
- ~~0 MB for the External Table and 0MB for the BQ Table~~
- ***0 MB for the External Table and 317.94MB for the BQ Table***


## Question 3:
How many records have both a blank (null) PUlocationID and DOlocationID in the entire dataset?
- 717,748
- 1,215,687
- 5
- 20,332

## Question 4:
What is the best strategy to optimize the table if query always filter by pickup_datetime and order by affiliated_base_number?
- Cluster on pickup_datetime Cluster on affiliated_base_number
- Partition by pickup_datetime Cluster on affiliated_base_number
- Partition by pickup_datetime Partition by affiliated_base_number
- Partition by affiliated_base_number Cluster on pickup_datetime

## Question 5:
Implement the optimized solution you chose for question 4. Write a query to retrieve the distinct affiliated_base_number between pickup_datetime 2019/03/01 and 2019/03/31 (inclusive).</br> 
Use the BQ table you created earlier in your from clause and note the estimated bytes. Now change the table in the from clause to the partitioned table you created for question 4 and note the estimated bytes processed. What are these values? Choose the answer which most closely matches.
- 12.82 MB for non-partitioned table and 647.87 MB for the partitioned table
- 647.87 MB for non-partitioned table and 23.06 MB for the partitioned table
- 582.63 MB for non-partitioned table and 0 MB for the partitioned table
- 646.25 MB for non-partitioned table and 646.25 MB for the partitioned table


## Question 6: 
Where is the data stored in the External Table you created?

- Big Query
- GCP Bucket
- Container Registry
- Big Table


## Question 7:
It is best practice in Big Query to always cluster your data:
- True
- False


## (Not required) Question 8:
A better format to store these files may be parquet. Create a data pipeline to download the gzip files and convert them into parquet. Upload the files to your GCP Bucket and create an External and BQ Table. 


Note: Column types for all files used in an External Table must have the same datatype. While an External Table may be created and shown in the side panel in Big Query, this will need to be validated by running a count query on the External Table to check if any errors occur. 
 
## Submitting the solutions

* Form for submitting: https://forms.gle/rLdvQW2igsAT73HTA
* You can submit your homework multiple times. In this case, only the last submission will be used. 

Deadline: 13 February (Monday), 22:00 CET


## Solution

Solution: https://www.youtube.com/watch?v=j8r2OigKBWE

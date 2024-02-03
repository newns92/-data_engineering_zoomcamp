# ETL: From Google Cloud Storage to Google BigQuery
- Now that we've written data to a GCS Bucket, let's load it into BigQuery
- We'll walk through the process of using Mage to load our data from GCS to BigQuery
- This closely mirrors a very common data engineering workflow: taking data from an external source, loading it (or **staging** it) in a **data lake**, and then loading (while potentially doing some more processing on it) it into a **data warehouse**

## Writing an ETL Pipeline
- So, again, we will be taking the data that we wrote to a GCS Bucket, process it some more, and write it to BigQuery, an **OLAP database**
- In Mage, create a new batch pipeline, `gcs_to_bigquery`
- In "Edit pipeline", create a new GCS Python data loader block, `load_taxi_gcs`
    - We know the name of our GCS Bucket and the name of the (*unpartitioned* in this example) file, `nyc_taxi_data.parquet`
        - If desired, you could use PyArrow again to *read* from GCS
    - After defining those two things, you can run the block and you should see a preview of the file as a result in the Mage UI
- Next, we will create a generic Python transformer block, `transform_stage_data`
    - A common data engineering best practice is to **standardize column names**
    - Right now, the casing on the column names is not very consistent (some are all lowercase, some Camel-case, etc.), so we will standardize them
    - To do this in pandas, we can use `data.columns` to define the transformations we'd like to see
        - We will replace any spaces with `_` and then lower any capital letters
        - We can do this in our `transform()` function in the block via:
            ```Python
            # Standardize the column names
            data.columns = (data.columns
                            .str.replace(' ', '_')
                            .str.lower()
            )
            ```
- Next, create a SQL data exporter block, `write_taxi_to_bigquery`
    - Use the BigQuery connection and the `default` profile
    - We can then define the database, schema, and table in Mage
        - The database should just be a default (i.e., don't fill it in inside the Mage UI for the block)
        - Name the schema `ny_taxi` and the table `yellow_taxi_data`
    - A cool thing about Mage is we can **select directly from data frames**
    - Our transformer block returns a dataframe `df_1` that we can query in the exporter block with Jinja via `SELECT * FROM {{ df_1 }};`
    - This should SELECT all rows from our previous table (`df_1`) and export them to `<project-id>.ny_taxi.yellow_taxi_data` in BigQuery
    - Run this exporter block and make sure there are no errors
        - ***NOTE:*** *If you get an error due to your project ID having a **reserved word** in it, you can use a BigQuery Python data exporter block instead (see video for this part of the course)*
    - Once complete, go to BigQuery in the GPC console
    - In the project on the drop-down on the left, note that we should see the `ny_taxi` schema
    - Within this schema, we should see the `yellow_taxi_data` table with 1,244,687 rows
        - *NOTE:* If using the SQL exporter block, you may see a staging table (`dev_gcs_to_bigquery_transform_stage_data_v1`) in BigQuery as well


## Advanced Mage Concepts
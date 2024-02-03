# ETL: From API to Google Cloud Storage

## Configuring GCS
- First, we must create a GCS **bucket** if we don't already have one
    - Name it `mage-zoomcamp-[username]`
        - *These MUST be globally unique names*
    - We can keep all the default options before creating it
- Mage uses **service accounts** to connect to GCP, so we must create a new one
    - These are just a set of permissions we're granting and credentials for those permissions
    - Name the service account `mage-zoomcamp`
    - Give it an **owner** role
    - Under the list of all service accounts, open this new account, go to "Keys", and select "Create new key" from the "Add key" drop-down
    - Use a JSON key and receive the downloaded file
    - Copy this file into the Mage project directory (`mage-zoomcamp/`)
        - *Don't worry, this is in the `.gitignore` file, so these credentials will not be uploaded to GitHub*
- Now, notice that in the `docker-compose.yml` file in `mage-zoomcamp`, that we have a **volume** defined for the Mage instance (local files are going to `./home/src` in the Mage container)
    - So, our recently-copied JSON credentials file will be **mounted** to our Mage volume
    - We can then use these credentials to authenticate with GCP
- At http://localhost:6789/, go to the "Files" section of the project
    - Open `io_config.yaml` and note that there are 2 ways to authenticate with Google service accounts
        - 1) Paste the JSON payload into the file
        - 2) Use the JSON service account key *file path*
    - We will be using the 2nd option, which will just be `GOOGLE_SERVICE_ACC_KEY_FILEPATH: "/home/src/<name-of-key-file>.json"`
        - *Do this under the `default` profile in `io_config.yaml`*
    - Mage will now use this service account's credentials (in the file) to interact with GCP
- Go back to the `test_config` pipeline from earlier
    - In the `test_postgres` data loader block, change the connection to be `BigQuery`, and set the profile to be `default`
    - Then test `SELECT 1` in the SQL data loader block to see if we can connect to Google BigQuery
- To test GCS to make sure we can read *and* write files, go to the `example_pipeline` pipeline
    - Remember that this pipeline reads Titanic data from an API into a dataframe and then writes it to a file
    - The full pipline exports a CSV to the Mage project directory (`mage-zoomcamp/`)
    - We can then load this CSV to GCS just by dragging-and-dropping it from Windows Explorer (or VSCode or whatever you have) into the GCS Bucket console in GCP in a browser
    - Once that's been uploaded to GCS, go back to the `test_config` pipeline
    - Then, under "Edit pipeline", create a new GCS Python data loader block named `test_gcs`
    - Within the `load_from_google_cloud_storage` loader function in the resulting file, add you Bucket name and **object key** (AKA the file name, `titanic_clean.csv`) as follows:
        ```Python
        bucket_name = 'mage-zoomcamp-<username>'
        object_key = 'titanic_clean.csv'
        ```
    - Then run the block to make sure we can connect to GCS (you should see a preview of the CSV returned in Mage)

## Writing an ETL Pipeline
- So far, we've read data from an API and wrote that data to a Postgres database, which is an **structured OLTP (i.e., row-oriented) database**
- Now we're going to write to GCS, which is a file system located on the cloud
- Often in data engineering, we write to cloud storage because it's (sometimes) cheaper and can (sometimes) handle semi-structured and unstructered data better than a relational database
- From there, workflows typically involve staging data, doing additional cleaning, and then writing to destinations like an analytical source, a data lake solution, or a data lakehouse solution
    - Many data teams start with extracting data from a source and writing it to a data lake *before* loading it to a *structured* data source, like a (relational) database
- We're going to largely build upon what we've done so far with some notable changes in the end
- Start by creating a new batch pipeline in Mage and name it `api_to_gcs`
- Then, since **Mage blocks are modular**, we can *drag-and-drop the `load_api_data.py` data load block for the Yellow Taxi data into our current pipeline*
- Do this again for the `transform_taxi_data.py` data transformer block
- Then, attach these blocks on the right-hand side of the Mage UI in the dependency graph
- Finally, we must write the cleaned taxi data to GCS
    - Since we already configured GCP, this should be good to go
    - Start by creating a new GCS Python data exporter block named `taxi_to_gcs_parquet`
        - *Note that we're writing to a Parquet file*
    - Make sure this exporter block is attached to the transformer block in the dependency graph
    - Then, enter in your GCS Bucket name and object key (name it `nyx_taxi_data.parquet`) into the data exporter code where prompted
    - Mage will infer the Parquet file format here and then write directly to the `nyx_taxi_data.parquet` location (*not* in any folder or anything)
    - Run all the blocks to see if the pipeline is working
    - Once the pipeline is finished, check the Bucket in the GCS console to see that the Parquet file is indeed present
- Note: Often it is not the case in data engineering to write any possible large datasets to a *single* Parquet file
- We will go one step further and write to a **partitioned** Parquet file structure
    - This means we're breaking the dataset up by some row or characteristic
    - Partitioning by date is particularly useful in our case since it (hopefully) creates an even distribution of taxi rides, and because it's a natural way to query data which makes it easy to access, by extension
    - Partitioning large datasets is common because writing a, say, 2GB dataset to single file would be slow to read and write
        - But if we partition the dataset, there's a lot of advantages to querying the data as well as I/O operations
- So, in addition to our single Parquet file, we will do this slightly more advanced method
    - Add a generic Python data exporter block to the pipeline called `taxi_to_gcs_partitioned_parquet`
    - *Make sure this block is connected to the transformer block so that we're ingesting the cleaned taxi data to this block*
        - Mage can run our partitioned and unpartitioned blocks will run **in parallel**
    - We will then manually define our credentials and use the **PyArrow** library to partition the dataset
        - PyArrow is an open-source Python library that provides a fast, efficient way to process and analyse large datasets, especially those in Apache Arrow format
        - It is used for handling columnar and/or chunked data in memory, including reading and writing data from/to disk and interprocess communication
        - https://tradingstrategy.ai/glossary/pyarrow#:~:text=PyArrow%20is%20an%20open%2Dsource,to%20disk%20and%20interprocess%20communication.
    - PyArrow should be in the Docker image, so you can add `import pyarrow as pa` and `import pyarrow.parquet as pq` to the top of the `taxi_to_gcs_partitioned_parquet` block
    - Also add `import os` so that we can work with environment variables
    - In order to use the PyArrow library, we need to tell PyArrow where our credentials live
        - This is something Mage can do, which we set in that `io_config.yaml` file
        - *BUT we will do it manually*
    - So, for our logic for exporting data within the `export_data()` function, enter `os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/src/<key-file-name>.json'` to SET an environment variable to be the credentials file that we mounted
        - This tells PyArrow where our credentials are located
    - Then we must define the Bucket name via the line `bucket_name = 'mage-zoomcamp-[username]'`
    - Then we need a project ID via the line `project_id = '<your-GCP-project-id>'`
    - Then we need to *define* a table name via the line `table_name = 'nyc_taxi_data'`
    - From here, PyArrow will handle the partitioning
        - It's just easier to do it all here just *one time* in the exporter block than in code somewhere else
    - Next, we need to create the **root path** via the line `root_path = f'{bucket_name}/{table_name}'`
    - We mentioned that partitioning by date is a helpful pattern, so first we need to *create* the date column to partition on
        - *Right now, we only have a datetime column, `tpep_pickup_datetime`, which is defined as a datetime string*
    - So, in the `export_data()` function in the block, create this column *in a String format* via:
        ```Python
        # Define/Create the column to partition on
        data['tpep_pickup_date'] = data['tpep_pickup_datetime'].dt.date
        ```
    - Next, for PyArrow, we need to define a **PyArrow table** via:
        ```Python
        # Create the PyArrow table from our dataset
        pa_table = pa.Table.from_pandas(data)
        ```
    - Next, we will find our GCS object via:
        ```Python
        # Find/Define the GCS file system (.fs) object via our environment variable(s)
        gcs_fs = pa.fs.GcsFileSystem()
        ```
        - Where `.fs` stands for file system
        - This is saying "we need this file system object" and will authorize using our environment variable *automatically*
    - Finally, we need to write the dataset via a PyArrow Parquet method of:
        ```Python
        # Write the PyArrow table to the dataset with partitions
        pq.write_to_dataset(
            table = pa_table, # must be a PyArrow table
            root_path = root_path,
            partition_cols = ['tpep_pickup_date'], # must be a list
            filesystem = gcs_fs
        )
        ```
        - See https://arrow.apache.org/docs/python/generated/pyarrow.parquet.write_to_dataset.html
    - Run this block (and fix any potential errors if it doesn't finish)
    - Once finished (with no errors), check the GCS Bucket in the GCP console, and you should again see the single Parquet file, but now also see an entire *directory/folder*, `nyc_taxi_data`
        - Click the directory to open/enter it, and note that each date has its own sub-directory/sub-folder in the `nyc_taxi_data` directory
        - You can enter any one of these sub-directories and see that the data is in a Parquet file with a random String name, and in each of these Parquet files are the taxi rides for the specific sub-directory date
        - So, if running a query against this dataset that only wants rides from a single, specific date, then now we're only reading a single folder instead of the entire file, which is much more efficient from a query standpoint
    - PyArrow abstracts away all of the communicating with pandas and GCS and the **chunking** logic where, if we did this by ourselves, we'd have to manually iterate through the dataframe and do a bunch of I/O operations
- Next, we will learn how to write from GCS to an OLAP database (BigQuery)
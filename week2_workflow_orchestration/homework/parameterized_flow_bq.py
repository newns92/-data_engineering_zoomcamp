from pathlib import Path
import pandas as pd
from prefect import flow, task
# for caching
from prefect.tasks import task_input_hash
from datetime import timedelta
# https://prefecthq.github.io/prefect-gcp/
# below is how we access our data in our GCS data lake/bucket via a reusable **block**
from prefect_gcp.cloud_storage import GcsBucket
# below is the block we made with our service account permissions for our Bucket and BigQuery
from prefect_gcp import GcpCredentials


@task(log_prints=True, retries=3, cache_key_fn=task_input_hash, cache_expiration=timedelta(days=1))
def extract(color: str, year: int, month: int) -> Path:  # using typehints (: str), returning a Path
    '''Read taxi data from a GCS Bucket into file locally'''
    # Create the name of the path that's in the GCS Bucket
    gcs_path = f'data\{color}\{color}_tripdata_{year}-{month:02}.parquet'
    # print(f'GCS PATH: {gcs_path}')

    # Connect to the GCS Prefect block that we created
    gcs_block = GcsBucket.load('zoom-gcs')
    
    # Copy a directory from the configured GCS bucket path to a local directory
    # Default = copying entire contents of the block's bucket_folder to the current working directory
    gcs_block.get_directory(from_path=gcs_path, local_path='./')
    
    # get the dataframe from the parquet file at the GCS path
    df = pd.read_parquet(Path(gcs_path))

    return df


# @task(log_prints=True, retries=3)
# def transform(path: Path) -> pd.DataFrame: # typehints (: Path), returning Pandas dataframe
#     '''Removes trips with 0 passengers, which is invalid'''
#     # read the data in a DataFrame
#     df = pd.read_parquet(path)

#     # remove the trips with 0 passengers
#     print(f"Pre: Missing passenger count: {df.passenger_count.isna().sum()}")
#     df.passenger_count.fillna(0, inplace=True)
#     print(f"Post: Missing passenger count: {df.passenger_count.isna().sum()}")

#     return df


@task(log_prints=True, retries=3)
def write_bq(df: pd.DataFrame) -> None:
    '''Writes a Pandas DataFrame to BigQuery'''
    # Connect to our credentials block
    gcp_credentials_block = GcpCredentials.load('zoom-gcp-creds')
    
    # Pandas has a .to_bgq() function to write to BigQuery table
    df.to_gbq(
        destination_table='de_zoomcamp.rides', # Name of table to be written in form: dataset.tablename
        project_id='de-zoomcamp-384821', # Google Cloud project ID
        # Use Prefect helper method to serialize credentials by using service_account_file/service_account_info
        credentials=gcp_credentials_block.get_credentials_from_service_account(), # Credentials for accessing Google APIs
        chunksize=500_000, # Number of rows to be inserted in each chunk from the dataframe
        if_exists='append' # If table exists, insert data. Create if does not exist
    )

    return


# Make a sub-flow
@flow(log_prints=True, name='Homework BQ ETL Flow')
def etl_gcs_to_bq(color: str, year: int, month: int) -> int:  # at first takes no args, will change this in the future
    '''Main ETL function'''  # docstring
    # call Task functions to download (extract), clean (transform), and 
    #   load the data from GCS to a BigQuery table
    df = extract(color, year, month)
    # df = transform(df)
    write_bq(df)

    # get the count of rows to return in order to print to the logs
    row_count = len(df)

    return row_count

# Parent flow will some default values such that we can loop over our sub-flow, ETL Flow
@flow(log_prints=True)
def etl_parent_flow(color: str = "yellow", year: int = 2019, months: list[int] = [2, 3]):
    '''Take in a list of months and loop over the sub-flow for each month'''
    row_count = 0

    for month in months:
        month_rows = etl_gcs_to_bq(color, year, month)
        row_count += month_rows

    print(f'TOTAL NUMBER OF ROWS LOADED TO BIGQUERY: {row_count}')

if __name__ == '__main__'   :
    # parameters to pass int
    color = "green"
    months = [1]
    year = 2020

    # run the parent flow (loops over the ETL sub-flow)
    etl_parent_flow(color, year, months)
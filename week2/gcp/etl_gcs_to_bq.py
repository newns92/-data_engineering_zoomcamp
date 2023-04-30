from pathlib import Path
import pandas as pd
from prefect import flow, task
# below is how we access our data in our GCS data lake/bucket via a reusable **block**
from prefect_gcp.cloud_storage import GcsBucket
# below is the block we made with our service account permissions for our Bucket and BigQuery
from prefect_gcp import GcpCredentials
# for creating the data directory if it does not exist
import os, os.path


@task(log_prints=True, retries=3)
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
    
    # return the path to the data as a Path object
    return Path(gcs_path)


# @task(log_prints=True, retries=3)
# def transform(df: pd.DataFrame) -> pd.DataFrame: # typehints (: pd.DataFrame), returning Pandas dataframe
#     '''Fix datatype issues'''
#     # fix datetimes
#     df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
#     df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

#     # Print some stuff
#     print(df.head(2))
#     print(f"\nColumns:\n{df.dtypes}")
#     print(f"Number of rows: {len(df)}")

#     return df


# @task(log_prints=True, retries=3)
# def write_local(df: pd.DataFrame, color, file: str) -> Path:
#     '''Write DataFrame out locally as parquet file'''
#     # create the path of where to store the parquet file
#     path = Path(f'data/{color}/{file}.parquet')

#     # create the data directory if it does not exist
#     # https://stackoverflow.com/questions/23793987/write-a-file-to-a-directory-that-doesnt-exist
#     os.makedirs(os.path.dirname(path), exist_ok=True)
    
#     # convert the DataFrame to a zipped parquet file and save to specified location
#     df.to_parquet(path, compression='gzip')

#     return path


# @task(log_prints=True, retries=3)
# def write_gcs(path: Path) -> None:
#     '''Upload a local parquet file to GCS'''
#     # Connect to the GCS Prefect block that we created
#     gcs_block = GcsBucket.load('zoom-gcs')
    
#     # Use our block to upload the file
#     gcs_block.upload_from_path(from_path=path, to_path=path)
#     # from_path (required) = the path to the file to upload from
#     # to_path (optional) = The path to upload the file to
#     #   - If not provided, will use the file name of from_path
#     #   - This gets prefixed with the `bucket_folder`

#     return


# Make a flow
@flow(name='BigQuery ETL Flow')
def etl_gcs_to_bq() -> None:  # at first takes no args, will change this in the future
    # add docstring
    '''Main ETL function for GCS Bucket to BigQuery'''
    # Hard-code some things that will be parameterized in the future
    color = 'yellow'
    year = 2021
    month = 1

    # call Task functions to download (extract), clean (transform), and 
    #   load the data locally *and* to GCS as a parquet file
    path = extract(color, year, month)
    # df = transform(df) 
    # path = write_local(df, color, dataset_file)
    # write_gcs(path)
    

if __name__ == '__main__'   :
    etl_gcs_to_bq()
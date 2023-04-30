from pathlib import Path
import pandas as pd
from prefect import flow, task
# https://prefecthq.github.io/prefect-gcp/
# below is how we access our data in our GCS data lake/bucket via a reusable **block**
from prefect_gcp.cloud_storage import GcsBucket
# below is the block we made with our service account permissions for our Bucket and BigQuery
from prefect_gcp import GcpCredentials


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


@task(log_prints=True, retries=3)
def transform(path: Path) -> pd.DataFrame: # typehints (: Path), returning Pandas dataframe
    '''Removes trips with 0 passengers, which is invalid'''
    # read the data in a DataFrame
    df = pd.read_parquet(path)

    # remove the trips with 0 passengers
    print(f"Pre: Missing passenger count: {df.passenger_count.isna().sum()}")
    df.passenger_count.fillna(0, inplace=True)
    print(f"Post: Missing passenger count: {df.passenger_count.isna().sum()}")

    return df


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
    df = transform(path) 
    write_bq(df)
    

if __name__ == '__main__'   :
    etl_gcs_to_bq()
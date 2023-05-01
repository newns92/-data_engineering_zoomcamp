from pathlib import Path
import pandas as pd
from prefect import flow, task
# below is how we will get data into our GCS data lake/bucket via a reusable **block**
from prefect_gcp.cloud_storage import GcsBucket
# for creating the data directory if it does not exist
import os, os.path


@task(log_prints=True, retries=3)
def extract(url: str) -> pd.DataFrame:  # using typehints (: str), returning a Pandas dataframe
    '''Read taxi data from the web into a Pandas dataframe'''
    df = pd.read_csv(url)
    
    return df


@task(log_prints=True, retries=3)
def transform(df: pd.DataFrame, color: str) -> pd.DataFrame: # typehints (: pd.DataFrame), returning Pandas dataframe
    '''Fix datatype issues'''
    # fix datetimes
    if color == "yellow":
        df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
        df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
    else:
        df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
        df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)  

    # Print some stuff
    print(df.head(2))
    print(f"\nColumns:\n{df.dtypes}")
    print(f"Number of rows: {len(df)}")

    return df


@task(log_prints=True, retries=3)
def write_local(df: pd.DataFrame, color, file: str) -> Path:
    '''Write DataFrame out locally as parquet file'''
    # create the path of where to store the parquet file
    path = Path(f'data/{color}/{file}.parquet')

    # create the data directory if it does not exist
    # https://stackoverflow.com/questions/23793987/write-a-file-to-a-directory-that-doesnt-exist
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    # convert the DataFrame to a zipped parquet file and save to specified location
    df.to_parquet(path, compression='gzip')

    return path


@task(log_prints=True, retries=3)
def write_gcs(path: Path) -> None:
    '''Upload a local parquet file to GCS'''
    # Connect to the GCS Prefect block that we created
    gcs_block = GcsBucket.load('zoom-gcs')
    
    # Use our block to upload the file
    print("UPLOADING FILE")
    gcs_block.upload_from_path(from_path=path, to_path=path)
    # from_path (required) = the path to the file to upload from
    # to_path (optional) = The path to upload the file to
    #   - If not provided, will use the file name of from_path
    #   - This gets prefixed with the `bucket_folder`

    return


# Make a sub-flow
@flow(name='ETL Flow')
def etl_web_to_gcs(color: str, year: int, month: int) -> None:  # at first takes no args, will change this in the future
    '''Main ETL function'''  # docstring
    dataset_file = f'{color}_tripdata_{year}-{month:02}'
    dataset_url = f'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{color}/{dataset_file}.csv.gz'

    # call Task functions to download (extract), clean (transform), and 
    #   load the data locally *and* to GCS as a parquet file
    df = extract(dataset_url)
    df = transform(df, color) 
    path = write_local(df, color, dataset_file)
    write_gcs(path)
    

# Parent flow will some default values such that we can loop over our sub-flow, ETL Flow
@flow()
def etl_parent_flow(color: str = "green", year: int = 2020, months: list[int] = [1]):
    '''Take in a list of months and loop over the sub-flow for each month'''
    for month in months:
        etl_web_to_gcs(color, year, month)

if __name__ == '__main__'   :
    # parameters to pass int
    color = "green"
    months = [1]
    year = 2020

    # run the parent flow (loops over the ETL sub-flow)
    etl_parent_flow(color, year, months)
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
def transform(df: pd.DataFrame) -> pd.DataFrame: # typehints (: pd.DataFrame), returning Pandas dataframe
    '''Fix datatype issues'''
    # fix datetimes
    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

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
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    # convert the DataFrame to a zipped parquet file and save to specified location
    df.to_parquet(path, compression='gzip')

    return path


@task(log_prints=True, retries=3)
def write_gcs(path: Path) -> None:
    '''Upload a local parquet file to GCS'''
    # Create the GCS Prefect block
    gcs_block = GcsBucket.load('zoom_gcs')
    
    #
    gcs_block.upload_from_path(from_path=path, to_path=path)

    return


# Make a flow
@flow(name='ETL Flow')
def etl_web_to_gcs() -> None:  # at first takes no args, will change this in the future
    # add docstring
    '''Main ETL function'''
    # Hard-code some things *that will be parameterized in the future
    color = 'yellow'
    year = 2021
    month = 1
    dataset_file = f'{color}_tripdata_{year}-{month:02}'
    dataset_url = f'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{color}/{dataset_file}.csv.gz'

    # call Task functions to download (extract), clean (transform), and 
    #   load the data locally *and* to GCS as a parquet file
    df = extract(dataset_url)
    df = transform(df) 
    path = write_local(df, color, dataset_file)
    


if __name__ == '__main__'   :
    etl_web_to_gcs()
import os
import pandas as pd
from pathlib import Path
# from prefect_gcp.cloud_storage import GcsBucket
from google.cloud import storage
from config import gcloud_creds, bucket_name
import time
import shutil

'''
Script to download FHV from 2019 and load them to a GCS Bucket as parquer files
    - Run this in the `zoom` Conda environment
'''


def download_data():
    for month in range(1, 13):
        # Get the URL for the specific month
        file_name = f'fhv_tripdata_2019-{month:02d}.csv.gz'
        df_file_name = f'fhv_tripdata_2019-{month:02d}'
        url = f'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhv/fhv_tripdata_2019-{month:02d}.csv.gz'
        
        # download it into a DataFrame directly from the URL
        print(f'Downloading file {file_name}...')
        df = pd.read_csv(url)

        # create the path of where to store the parquet file
        # Use .as_posix() for easier GCS and BigQuery access
        # https://stackoverflow.com/questions/68369551/how-can-i-output-paths-with-forward-slashes-with-pathlib-on-windows
        path = Path(f'data/{df_file_name}.parquet').as_posix()
        # print(f'PATH: {path.as_posix()}')

        # create the data directory if it does not exist
        # https://stackoverflow.com/questions/23793987/write-a-file-to-a-directory-that-doesnt-exist
        os.makedirs(os.path.dirname(path), exist_ok=True)

        df.pickup_datetime = pd.to_datetime(df.pickup_datetime)
        df.dropOff_datetime = pd.to_datetime(df.dropOff_datetime)
        # print(f"Unique dispatching_base_num values: {df.dispatching_base_num.unique()}")    
        # print(f"Unique PUlocationID values: {df.PUlocationID.unique()}")
        # print(f"Unique DOlocationID values: {df.DOlocationID.unique()}")
        # print(f"Unique SR_Flag values: {df.SR_Flag.unique()}")
        df.PUlocationID = df.PUlocationID.fillna(0).astype('int')
        df.DOlocationID = df.DOlocationID.fillna(0).astype('int')
        df.SR_Flag = df.SR_Flag.fillna(0).astype('int')
        
        # convert the DataFrame to a zipped parquet file and save to specified location
        print(f'Converting fhv_tripdata_2019-{month:02d}.csv.gz to a parquet file')
        df.to_parquet(path, compression='gzip')


def upload_to_bucket(bucket_name, gcloud_creds):
    """
    Upload data to a bucket
    https://stackoverflow.com/questions/37003862/how-to-upload-a-file-to-google-cloud-storage-on-python-3
    https://stackoverflow.com/questions/43264664/creating-uploading-new-file-at-google-cloud-storage-bucket-using-python
    """
     
    # Create a client object
    # - Explicitly use service account credentials by specifying the private key file.
    storage_client = storage.Client.from_service_account_json(gcloud_creds)
    # print(list(storage_client.list_buckets()))

    # Provide the bucket object
    bucket = storage_client.get_bucket(bucket_name)
    
    # Loop through the month files and upload them to the bucket
    for month in range(1, 13):
        time.sleep(1)  # to prevent rate limiting

        # https://stackoverflow.com/questions/56896710/does-time-sleep-not-work-inside-a-for-loop-with-a-print-function-using-the
        print(f'Uploading ./data/fhv_tripdata_2019-{month:02d}.parquet', flush = True)
        
        # The blob method creates the new file, also an object
        blob = bucket.blob(f'fhv_data/fhv_tripdata_2019-{month:02d}.parquet')
        # print(blob.public_url)

        # Upload the file
        blob.upload_from_filename(Path(f'data/fhv_tripdata_2019-{month:02d}.parquet').as_posix())
    

def remove_files():
    # https://stackoverflow.com/questions/48892772/how-to-remove-a-directory-is-os-removedirs-and-os-rmdir-only-used-to-delete-emp
    shutil.rmtree('./data/')


if __name__ == '__main__':
    download_data()
    upload_to_bucket(bucket_name, gcloud_creds)
    remove_files()

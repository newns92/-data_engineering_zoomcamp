import io
import os
import requests
import pandas as pd
from google.cloud import storage
from config import gcloud_creds, bucket_name
from pathlib import Path
import shutil


"""
Pre-reqs: 
1. `pip install pandas pyarrow google-cloud-storage`
2. Set GOOGLE_APPLICATION_CREDENTIALS to your project/service-account key
3. Set GCP_GCS_BUCKET as your bucket or change default value of BUCKET
"""

# services = ['fhv','green','yellow']
init_url = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/'
# switch out the bucketname
storage_client = storage.Client.from_service_account_json(gcloud_creds)
# BUCKET = os.environ.get("GCP_GCS_BUCKET", "dtc-data-lake-bucketname")
gcs_bucket = storage_client.get_bucket(bucket_name)


def upload_to_gcs(bucket, object_name, local_file):
    """
    Ref: https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-python
    """
    # # WORKAROUND to prevent timeout for files > 6 MB on 800 kbps upload speed.
    # # (Ref: https://github.com/googleapis/python-storage/issues/74)
    # storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB
    # storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB

    # client = storage.Client()
    # bucket = client.bucket(bucket)
    blob = bucket.blob(object_name)
    blob.upload_from_filename(local_file)


def remove_files():
    # https://stackoverflow.com/questions/32834731/how-to-delete-a-file-by-extension-in-python
    dir_name = "./"
    local_data = os.listdir(dir_name)

    # remove the local CSV's
    for item in local_data:
        if item.endswith(".csv.gz"):
            os.remove(os.path.join(dir_name, item))

    # Remove the local parquet files
    # https://stackoverflow.com/questions/48892772/how-to-remove-a-directory-is-os-removedirs-and-os-rmdir-only-used-to-delete-emp
    shutil.rmtree('./data/')


def clean_data(df, service):
    '''Fix datatype issues'''

    if service == 'yellow':
        # fix datetimes
        df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
        df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

        # this fixes fields for files that have NAN values and thus aren't INTs
        # when they should be INTs
        # https://pandas.pydata.org/pandas-docs/stable/user_guide/integer_na.html#integer-na
        df.VendorID = pd.array(df.VendorID, dtype=pd.Int64Dtype())
        df.passenger_count = pd.array(df.passenger_count, dtype=pd.Int64Dtype())
        df.payment_type = pd.array(df.payment_type, dtype=pd.Int64Dtype())
        df.RatecodeID = pd.array(df.RatecodeID, dtype=pd.Int64Dtype())

    elif service == 'green':
        # fix datetimes
        df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
        df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)

        # this fixes fields for files that have NAN values and thus aren't INTs
        # when they should be INTs
        # https://pandas.pydata.org/pandas-docs/stable/user_guide/integer_na.html#integer-na
        df.VendorID = pd.array(df.VendorID, dtype=pd.Int64Dtype())
        df.passenger_count = pd.array(df.passenger_count, dtype=pd.Int64Dtype())
        df.payment_type = pd.array(df.payment_type, dtype=pd.Int64Dtype())
        df.trip_type = pd.array(df.trip_type, dtype=pd.Int64Dtype())
        df.RatecodeID = pd.array(df.RatecodeID, dtype=pd.Int64Dtype())

    # elif service == 'fhv':
    else:
        # Rename columns
        df.rename({'dropOff_datetime':'dropoff_datetime'}, axis='columns', inplace=True)
        df.rename({'PUlocationID':'PULocationID'}, axis='columns', inplace=True)
        df.rename({'DOlocationID':'DOLocationID'}, axis='columns', inplace=True)

        # fix datetimes
        df.pickup_datetime = pd.to_datetime(df.pickup_datetime)
        df.dropoff_datetime = pd.to_datetime(df.dropoff_datetime)

        # this fixes fields for files that have NAN values and thus aren't INTs
        # when they should be INTs
        # https://pandas.pydata.org/pandas-docs/stable/user_guide/integer_na.html#integer-na
        df.PULocationID = pd.array(df.PULocationID, dtype=pd.Int64Dtype())
        df.DOLocationID = pd.array(df.DOLocationID, dtype=pd.Int64Dtype())           

    return df


def web_to_gcs(year, service, gcs_bucket):

    # Loop through the months
    for i in range(12):
        
        # Set the month part of the file_name string
        month = '0'+str(i + 1)
        month = month[-2:]

        # create CSV file_name and path to write parquet file to
        file_name = f'{service}_tripdata_{year}-{month}.csv.gz'
        path = Path(f'data/{service}_tripdata_{year}-{month}.parquet').as_posix()

        # Make the directory to hold the parquet file if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)

        # Download CSV using requests via a Pandas DataFrame
        print(f'\nDownloading {file_name}...')
        request_url = f"{init_url}{service}/{file_name}"
        r = requests.get(request_url)
        open(file_name, 'wb').write(r.content)

        # Read it back into a parquet file
        print(f'Saving {file_name} to {path}...')
        df = pd.read_csv(file_name, compression='gzip')

        # clean the data and fix the data types
        df = clean_data(df, service)

        file_name = file_name.replace('.csv.gz', '.parquet')
        df.to_parquet(path, engine='pyarrow')

        # Upload parquet to GCS Bucket
        print(f'Uploading {path} to GCS...')
        upload_to_gcs(gcs_bucket, f'data/{service}/{file_name}', f'data/{file_name}')


if __name__ == '__main__':
    web_to_gcs('2019', 'green', gcs_bucket)
    web_to_gcs('2020', 'green', gcs_bucket)
    web_to_gcs('2019', 'yellow', gcs_bucket)
    web_to_gcs('2020', 'yellow', gcs_bucket)
    web_to_gcs('2019', 'fhv', gcs_bucket)
    remove_files()


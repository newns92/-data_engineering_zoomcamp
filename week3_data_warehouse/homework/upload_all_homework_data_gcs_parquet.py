# import io
import os
import requests
import pandas as pd
from google.cloud import storage
from config import gcloud_creds, bucket_name
from pathlib import Path
# import shutil

# For Parquet manipulation
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.compute as pc

'''
Pre-reqs: 
1. `pip install pandas pyarrow google-cloud-storage` if needed
2. Set GOOGLE_APPLICATION_CREDENTIALS to your project/service-account key
    - Or import from a `config.py` file
3. Set GCP_GCS_BUCKET as your bucket or change default value of BUCKET
    - Or import from a `config.py` file
'''


# services = ['fhv','green','yellow']
## Set the download directory URL from the course repo
# init_url = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/'
init_url = 'https://d37ci6vzurychx.cloudfront.net/trip-data/' # yellow_tripdata_2024-01.parquet'
## Switch out the GCP credentials and GCS bucketname that were imported from config.py
storage_client = storage.Client.from_service_account_json(gcloud_creds)
# BUCKET = os.environ.get('GCP_GCS_BUCKET', 'dtc-data-lake-bucketname')
gcs_bucket = storage_client.get_bucket(bucket_name)


def upload_to_gcs(bucket, object_name, local_file):
    '''
    Ref: https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-python
    '''
    # # WORKAROUND to prevent timeout for files > 6 MB on 800 kbps upload speed.
    # # (Ref: https://github.com/googleapis/python-storage/issues/74)
    # storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB
    # storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB

    # client = storage.Client()
    # bucket = client.bucket(bucket)
    blob = bucket.blob(object_name)  ## Basically the destination within the bucket
    blob.upload_from_filename(local_file)


def remove_files():
    print('Removing files...')
    # https://stackoverflow.com/questions/32834731/how-to-delete-a-file-by-extension-in-python
    dir_name = './data'
    local_data = os.listdir(dir_name)

    ## Remove the local compressed and uncompressed CSV's and any Parquet files
    for item in local_data:
        if item.endswith('.csv.gz'):
            os.remove(os.path.join(dir_name, item))
        elif item.endswith('.csv'):
            os.remove(os.path.join(dir_name, item))
        elif item.endswith('.parquet'):
            os.remove(os.path.join(dir_name, item))

    # # Remove all other the local files in the 'data' directory
    # # https://stackoverflow.com/questions/48892772/how-to-remove-a-directory-is-os-removedirs-and-os-rmdir-only-used-to-delete-emp
    # shutil.rmtree('./data/')


def clean_data(df, service):
    '''Fix datatype issues'''

    if service == 'yellow':           
        ## Rename columns to be better suited for a database/data warehouse table
        df.rename({'VendorID':'vendor_id',
                   'PULocationID':'pu_location_id',
                   'DOLocationID':'do_location_id',
                   'RatecodeID':'rate_code_id'
                },
            axis='columns', inplace=True
        )
        
        ## Fix datetimes
        df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
        df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

        ## This fixes fields for files that have NAN values and thus aren't INTs
        ##   when they should be INTs
        ## https://pandas.pydata.org/pandas-docs/stable/user_guide/integer_na.html#integer-na
        df.vendor_id = pd.array(df.vendor_id, dtype=pd.Int64Dtype())
        df.passenger_count = pd.array(df.passenger_count, dtype=pd.Int64Dtype())
        df.payment_type = pd.array(df.payment_type, dtype=pd.Int64Dtype())
        df.rate_code_id = pd.array(df.rate_code_id, dtype=pd.Int64Dtype())

    return df


def web_to_gcs(year, service, gcs_bucket):

    ## Loop through the months
    for i in range(1, 7):
    # for i in range(3):
        
        ## Set the month part of the file_name string
        if len(str(i)) == 1:
            # print(f'Single digit: {i}')
            month = '0' + str(i)
        else:
            # print(f'Double digit: {i}')
            month = i
        # print(month)

        ## Create Parquet file_name to download
        file_name = f'{service}_tripdata_{year}-{month}.parquet'
        
        ## Create the path to write the eventual parquet file to
        path = Path(f'./data/{service}_tripdata_{year}-{month}.parquet').as_posix()

        ## Make the directory to hold the parquet file if it doesn't already exist
        os.makedirs(os.path.dirname(path), exist_ok=True)

        ## Download the source CSV file using `requests` library
        print(f'\nDownloading {file_name}...')
        request_url = f'{init_url}{file_name}'
        r = requests.get(request_url)
        open(f'./data/{file_name}', 'wb').write(r.content)

        ## Read in the table to a table, then into a DataFrame
        table = pq.read_table(f'./data/{file_name}')
        df = table.to_pandas()

        ## Clean the data and fix the data types
        print(f'Cleaning {path}...')
        df = clean_data(df, service)

        ## Read DataFrame into a Parquet file using `pyarrow` engine
        df.to_parquet(f'./data/{file_name}', engine='pyarrow')
        
        ## Upload the resulting Parquet file to the GCS Bucket, whilst
        ##      creating a `data/` directory in GCS
        print(f'Uploading {path} to GCS...')
        upload_to_gcs(gcs_bucket, f'data/{service}/{file_name}', f'data/{file_name}')


if __name__ == '__main__':
    web_to_gcs('2024', 'yellow', gcs_bucket)
    remove_files()

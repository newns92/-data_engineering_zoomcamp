import io
import os
import requests
import json
import csv
import pandas as pd
from google.cloud import storage
from config import tmdb_api_key, tmdb_api_read_access_token  # gcloud_creds, bucket_name
from pathlib import Path
import shutil


"""
Pre-reqs: 
1. `pip install pandas pyarrow google-cloud-storage`
2. Set GOOGLE_APPLICATION_CREDENTIALS to your project/service-account key
3. Set GCP_GCS_BUCKET as your bucket or change default value of BUCKET
"""

# https://web.archive.org/web/20210112170836/https://towardsdatascience.com/this-tutorial-will-make-your-api-data-pull-so-much-easier-9ab4c35f9af
# Use requests package to query API and get back JSON
# api_key = tmdb_api_key
# movie_id = '464052'

# # switch out the bucket name
# storage_client = storage.Client.from_service_account_json(gcloud_creds)
# # BUCKET = os.environ.get("GCP_GCS_BUCKET", "dtc-data-lake-bucketname")
# gcs_bucket = storage_client.get_bucket(bucket_name)


# def get_movie_data(tmdb_api_key, movie_id):
#     query = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={tmdb_api_key}&language=en-US'
#     response = requests.get(query)
    
#     if response.status_code == 200:  # if API request was successful
#         array = response.json()
#         text = json.dumps(array)
#         # print(text)
#         return text
    
#     else:
#         return "API Error"


def get_popular_movies():
    dataset = []

    # https://developer.themoviedb.org/reference/movie-lists
    # Get 5 pages of data
    for page in range(1, 6):
        # print('Page:', page)

        url = f'https://api.themoviedb.org/3/movie/popular?language=en-US&page={page}'
        # headers = dictionary of HTTP headers to send to the specified url
        headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {tmdb_api_read_access_token}'
        }

        response = requests.get(url, headers=headers)
        # print(response)

        # Check that request went through (i.e., if API request was successful)
        if response.status_code == 200:
            # Get JSON object of the request result
            array = response.json()
            # Convert from Python to JSON
            text = json.dumps(array)
            # Convert from JSON back to Python
            dataset_page = json.loads(text)

            # Concatenate results lists
            for item in dataset_page['results']:
                dataset.append(item)
            # print(len(dataset))

        else:
            return "API Error"
        
    return dataset    


def write_movie_file(file_name, dataset):
    # csv_file = open(file_name, 'a')
    # csv_writer = csv.writer(csv_file)

    # Create empty dataframe with headers
    df = pd.DataFrame(columns=['title', 'original_language', 'popularity', 'release_date', 
                               'vote_average', 'vote_count'])

    # For each movie in the dataset, add its info to the dataframe
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#setting-with-enlargement
    for i in range(len(dataset)):
        # print(dataset[i]['title'])
        df.loc[i] = [dataset[i]['title'], dataset[i]['original_language'], 
                     dataset[i]['popularity'], dataset[i]['release_date'], 
                     dataset[i]['vote_average'], dataset[i]['vote_count']]
        
    # convert release_date to datetime
    df.release_date = pd.to_datetime(df.release_date)
    
    # print(df[:5])
    # print(df.dtypes)
    # print(df.describe())
    # print(df.isnull().sum())

    # Create the path of where to store the parquet file
    # - Use .as_posix() for easier GCS and BigQuery access
    # https://stackoverflow.com/questions/68369551/how-can-i-output-paths-with-forward-slashes-with-pathlib-on-windows
    path = Path(f'data/{file_name}.parquet').as_posix()
    # path_csv = Path(f'data/{file_name}.csv')  # .as_posix()
    # print(f'PATH: {path.as_posix()}')

    # Create the data directory if it does not exist
    # https://stackoverflow.com/questions/23793987/write-a-file-to-a-directory-that-doesnt-exist
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # Convert the DataFrame to a zipped parquet file and save to specified location
    print(f'Converting dataframe to a parquet file')
    df.to_parquet(path, compression='gzip')
    # df.to_csv(path_csv)


def write_movie_file_to_gcs(file_name, dataset, bucket):
    # csv_file = open(file_name, 'a')
    # csv_writer = csv.writer(csv_file)

    # Create empty dataframe with headers
    df = pd.DataFrame(columns=['title', 'original_language', 'popularity', 'release_date', 
                               'vote_average', 'vote_count'])

    # For each movie in the dataset, add its info to the dataframe
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#setting-with-enlargement
    for i in range(len(dataset)):
        # print(dataset[i]['title'])
        df.loc[i] = [dataset[i]['title'], dataset[i]['original_language'], 
                     dataset[i]['popularity'], dataset[i]['release_date'], 
                     dataset[i]['vote_average'], dataset[i]['vote_count']]
        
    # convert release_date to datetime
    df.release_date = pd.to_datetime(df.release_date)
    
    # print(df[:5])
    # print(df.dtypes)
    # print(df.describe())
    # print(df.isnull().sum())

    # Create the path of where to store the parquet file
    # - Use .as_posix() for easier GCS and BigQuery access
    # https://stackoverflow.com/questions/68369551/how-can-i-output-paths-with-forward-slashes-with-pathlib-on-windows
    path = Path(f'data/{file_name}.parquet').as_posix()
    # path_csv = Path(f'data/{file_name}.csv')  # .as_posix()
    # print(f'PATH: {path.as_posix()}')

    # Create the data directory if it does not exist
    # https://stackoverflow.com/questions/23793987/write-a-file-to-a-directory-that-doesnt-exist
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # Convert the DataFrame to a zipped parquet file and save to specified location
    print(f'Converting dataframe to a parquet file')
    df.to_parquet(path, compression='gzip')
    # df.to_csv(path_csv)

    """
    Ref: https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-python
    """
    # # WORKAROUND to prevent timeout for files > 6 MB on 800 kbps upload speed.
    # # (Ref: https://github.com/googleapis/python-storage/issues/74)
    # storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB
    # storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB

    # client = storage.Client()
    # bucket = client.bucket(bucket)
    blob = bucket.blob(f'data/{file_name}.parquet')
    blob.upload_from_filename(f'data/{file_name}.parquet')


def remove_files():
    # Remove the local parquet files
    # https://stackoverflow.com/questions/48892772/how-to-remove-a-directory-is-os-removedirs-and-os-rmdir-only-used-to-delete-emp
    shutil.rmtree('./data/')

# def upload_to_gcs(bucket, object_name, local_file):
#     """
#     Ref: https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-python
#     """
#     # # WORKAROUND to prevent timeout for files > 6 MB on 800 kbps upload speed.
#     # # (Ref: https://github.com/googleapis/python-storage/issues/74)
#     # storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB
#     # storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB

#     # client = storage.Client()
#     # bucket = client.bucket(bucket)
#     blob = bucket.blob(object_name)
#     blob.upload_from_filename(local_file)


if __name__ == '__main__':
    # web_to_gcs('2019', 'green', gcs_bucket)
    # web_to_gcs('2020', 'green', gcs_bucket)
    # web_to_gcs('2019', 'yellow', gcs_bucket)
    # web_to_gcs('2020', 'yellow', gcs_bucket)
    # web_to_gcs('2019', 'fhv', gcs_bucket)
    # remove_files()

    # print(api_key, movie_id)
    # movie_text = get_movie_data(api_key, movie_id)
    # write_movie_file('movie_test.csv', movie_text)
    popular_movies_list = get_popular_movies()
    # print(popular_movies_dict.keys())
    # print(len(popular_movies_dict))
    # print(popular_movies_dict)
    # print(popular_movies_dict['results'][0]['title'])

    # # keys
    # print(popular_movies_list[0].keys())
    # print(popular_movies_list[0])

    write_movie_file('movies_test', popular_movies_list)
    # write_movie_file_to_gcs('movies_test', popular_movies_list, gcs_bucket)
    # loop_through_movies(popular_movies_list)

    # upload_to_gcs(gcs_bucket)
    # upload_to_gcs(gcs_bucket, f'data/{file_name}', f'data/{file_name}') 

    remove_files()
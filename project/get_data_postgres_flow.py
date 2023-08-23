# import io
# import os
import requests
import json
import pandas as pd
from google.cloud import storage
from config import tmdb_api_key, tmdb_api_read_access_token, postgres_user, postgres_password, \
    postgres_host, postgres_port, postgres_database, postgres_movies_table_name
from pathlib import Path
# import shutil
from sqlalchemy import create_engine
from prefect import flow, task


@task(log_prints=True, retries=3)
# Takes the start of an API string, and using typehints (: str), returns a Python list
def extract(api_url: str) -> list:
    '''Read movie data in from the web via TMDB's API into a Python list'''

    dataset = []

    # https://developer.themoviedb.org/reference/movie-lists
    # Get 5 pages of data
    for page in range(1, 6):
        # https://web.archive.org/web/20210112170836/https://towardsdatascience.com/this-tutorial-will-make-your-api-data-pull-so-much-easier-9ab4c35f9af
        # Use requests package to query API and get back JSON
        url = f'{api_url}{page}'
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

@task(log_prints=True, retries=3)
# Takes in a list, and using typehints (: str), returns a pandas DataFrame
def transform(dataset: list) -> pd.DataFrame:
    '''Read in list of movie data and transform into a Pandas DataFrame'''

    print('Creating the DataFrame...')
    # Create empty dataframe with headers
    df = pd.DataFrame(columns=['id', 'title', 'original_language', 'popularity', 
                               'release_date', 'vote_average', 'vote_count'])

    # For each movie in the dataset, add its info to the dataframe
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#setting-with-enlargement
    for i in range(len(dataset)):
        # print(dataset[i]['title'])
        df.loc[i] = [dataset[i]['id'], dataset[i]['title'], dataset[i]['original_language'], 
                     dataset[i]['popularity'], dataset[i]['release_date'], 
                     dataset[i]['vote_average'], dataset[i]['vote_count']]
        
    # Convert release_date to datetime
    df.release_date = pd.to_datetime(df.release_date)

    return df
 

# @task(log_prints=True, retries=3)
# def load_local(df: pd.DataFrame, file_name: str) -> Path:
#     '''Read in a pandas DataFrame and write to a parquet file'''

#     # Create the path of where to store the parquet file
#     # - Use .as_posix() for easier GCS and BigQuery access
#     # https://stackoverflow.com/questions/68369551/how-can-i-output-paths-with-forward-slashes-with-pathlib-on-windows
#     path = Path(f'data/{file_name}.parquet').as_posix()
#     # path_csv = Path(f'data/{file_name}.csv')  # .as_posix()
#     # print(f'PATH: {path.as_posix()}')

#     # Create the data directory if it does not exist
#     # https://stackoverflow.com/questions/23793987/write-a-file-to-a-directory-that-doesnt-exist
#     os.makedirs(os.path.dirname(path), exist_ok=True)

#     # Convert the DataFrame to a zipped parquet file and save to specified location
#     print(f'Converting dataframe to a parquet file')
#     df.to_parquet(path, compression='gzip')


@task(log_prints=True, retries=3)
# Takes in a pandas DataFrame, returns nothing
def load_postgres(df: pd.DataFrame) -> None:
    '''Upload given pandas DataFrame to Postgres database'''

    print('Creating the Postgres engine...')
    # Need to convert this DDL statement into something Postgres will understand
    #   - Via create_engine([database_type]://[user]:[password]@[hostname]:[port]/[database], con=[engine])
    engine = create_engine(f'postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_database}')

    # Get the header/column names
    header = df.head(n=0)
    # print(header)

    # Add the column headers to the green_taxi_data table in the database connection, and replace the table if it exists
    print('Adding table column headers...')
    header.to_sql(name=postgres_movies_table_name, con=engine, if_exists='replace')

    # Add the movie info data
    print('Loading in data...')
    df.to_sql(name=postgres_movies_table_name, con=engine, if_exists='append')


# Make a Parent flow
@flow(name='ETL Flow')
def etl_web_to_postgres() -> None:
    '''Main ETL function'''
    dataset_url = f'https://api.themoviedb.org/3/movie/popular?language=en-US&page='

    # call Task functions to download (extract), clean (transform), and 
    #   load the data locally *and* to GCS as a parquet file
    df = extract(dataset_url)
    df = transform(df) 
    load_postgres(df)


if __name__ == '__main__':
    etl_web_to_postgres()
import io
import os
import requests
import json
import csv
import pandas as pd
from google.cloud import storage
from config import tmdb_api_key, tmdb_api_read_access_token, postgres_user, postgres_password, \
    postgres_host, postgres_port, postgres_database, postgres_movies_table_name
from pathlib import Path
import shutil
from sqlalchemy import create_engine, text
from bs4 import BeautifulSoup  # library to parse HTML documents


# https://web.archive.org/web/20210112170836/https://towardsdatascience.com/this-tutorial-will-make-your-api-data-pull-so-much-easier-9ab4c35f9af
# Use requests package to query API and get back JSON
# api_key = tmdb_api_key
# movie_id = '464052'

# # Postgres args
# user = postgres_user
# password = postgres_password
# host = postgres_host
# port = postgres_port
# database = postgres_database
# movie_info_table_name = postgres_movies_table_name

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
                # KEYS USED
                # dict_keys(['adult', 'backdrop_path', 'genre_ids', 'id', 'original_language', 
                # 'original_title', 'overview', 'popularity', 'poster_path', 'release_date', 
                # 'title', 'video', 'vote_average', 'vote_count'])
            # print(len(dataset))

        else:
            return "API Error"
        
    return dataset    


def write_movie_file_to_postgres(file_name, dataset):
    '''
    Function to read a JSON object returned from an API request from TMDB to get 
    information about the most popular movies on the website
    '''

    # csv_file = open(file_name, 'a')
    # csv_writer = csv.writer(csv_file)
    
    print('Starting movie information extraction...')
    print('Creating the Postgres engine...')
    # Need to convert this DDL statement into something Postgres will understand
    #   - Via create_engine([database_type]://[user]:[password]@[hostname]:[port]/[database], con=[engine])
    engine = create_engine(f'postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_database}')
    # print(engine)
    # print(engine.connect())

    print('Creating the DataFrame...')
    # Create empty dataframe with headers
    df = pd.DataFrame(columns=['id', 'title', 'original_language', 'popularity', 
                               'release_date', 'vote_average', 'vote_count'])

    # For each movie in the dataset, add its info to the dataframe
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#setting-with-enlargement
    print("Adding movie information to the DataFrame...")
    for i in range(len(dataset)):
        # print(dataset[i]['title'])
        df.loc[i] = [dataset[i]['id'], dataset[i]['title'], dataset[i]['original_language'], 
                     dataset[i]['popularity'], dataset[i]['release_date'], 
                     dataset[i]['vote_average'], dataset[i]['vote_count']]
        
    # Convert release_date to datetime
    df.release_date = pd.to_datetime(df.release_date)
    
    # print(df[:5])
    # print(df.dtypes)
    # print(df.describe())
    # print(df.isnull().sum())

    # # Create the path of where to store the parquet file
    # # - Use .as_posix() for easier GCS and BigQuery access
    # # https://stackoverflow.com/questions/68369551/how-can-i-output-paths-with-forward-slashes-with-pathlib-on-windows
    # path = Path(f'data/{file_name}.parquet').as_posix()
    # # path_csv = Path(f'data/{file_name}.csv')  # .as_posix()
    # # print(f'PATH: {path.as_posix()}')

    # # Create the data directory if it does not exist
    # # https://stackoverflow.com/questions/23793987/write-a-file-to-a-directory-that-doesnt-exist
    # os.makedirs(os.path.dirname(path), exist_ok=True)

    # # Convert the DataFrame to a zipped parquet file and save to specified location
    # print('Converting DataFrame to a parquet file...')
    # df.to_parquet(path, compression='gzip')
    # # df.to_csv(path_csv)

    # Get the header/column names
    header = df.head(n=0)
    # print(header)

    # Drop dependent tables
    # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html
    with engine.connect() as conn:
        conn.execute(text(f'DROP TABLE if exists {postgres_movies_table_name} cascade'))

    # Add the column headers to the green_taxi_data table in the database connection, and replace the table if it exists
    print('Adding table column headers...')
    header.to_sql(name=postgres_movies_table_name, con=engine, if_exists='replace')

    # Add the movie info data
    print('Loading in data...')
    df.to_sql(name=postgres_movies_table_name, con=engine, if_exists='append')


def write_languages_file_to_postgres():
    '''
    Function to read Wikipedia table of the list of ISO 639-1 language codes 
    and their abbreviations
    '''

    print('Starting languages extraction...')

    # https://medium.com/analytics-vidhya/web-scraping-a-wikipedia-table-into-a-dataframe-c52617e1f451
    print("Getting data...")
    wikiurl = "https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes"
    # table_class="wikitable sortable jquery-tablesorter"
    response = requests.get(wikiurl)
    # print(response.status_code)

    # Parse data from the HTML into a BeautifulSoup object
    soup = BeautifulSoup(response.text, 'html.parser')
    language_table = soup.find('table', {'class':"wikitable"})    
    # print(language_table)

    print("Creating the languages DataFrame...")
    df = pd.read_html(str(language_table))
    
    # Convert list to dataframe
    df = pd.DataFrame(df[0])
    # print(df.head())

    # Get only required columns
    df = df[['ISO language name', '639-1']]
    # print(df.head())

    # Rename columns
    # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.rename.html
    df.rename(columns={'ISO language name': 'full_language_name', '639-1': 'language_abbrev'},
              inplace=True)
    print(df.head())

    # print('Creating the Postgres engine...')
    # # Need to convert this DDL statement into something Postgres will understand
    # #   - Via create_engine([database_type]://[user]:[password]@[hostname]:[port]/[database], con=[engine])
    # engine = create_engine(f'postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_database}')
    # print(engine)
    # print(engine.connect())

    # print('Creating the DataFrame...')
    # # Create empty dataframe with headers
    # df = pd.DataFrame(columns=['639_1_code', 'language_name'])

    # # For each movie in the dataset, add its info to the dataframe
    # # https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#setting-with-enlargement
    # for i in range(len(dataset)):
    #     # print(dataset[i]['title'])
    #     df.loc[i] = [dataset[i]['id'], dataset[i]['title'], dataset[i]['original_language'], 
    #                  dataset[i]['popularity'], dataset[i]['release_date'], 
    #                  dataset[i]['vote_average'], dataset[i]['vote_count']]
        
    # # Convert release_date to datetime
    # df.release_date = pd.to_datetime(df.release_date)
    
    # # Get the header/column names
    # header = df.head(n=0)
    # # print(header)

    # # Add the column headers to the green_taxi_data table in the database connection, and replace the table if it exists
    # print('Adding table column headers...')
    # header.to_sql(name=postgres_movies_table_name, con=engine, if_exists='replace')

    # # Add the movie info data
    # print('Loading in data...')
    # df.to_sql(name=postgres_movies_table_name, con=engine, if_exists='append')    


# def remove_files():
#     print('Removing local files...')
#     # Remove the local parquet files
#     # https://stackoverflow.com/questions/48892772/how-to-remove-a-directory-is-os-removedirs-and-os-rmdir-only-used-to-delete-emp
#     shutil.rmtree('./data/')


if __name__ == '__main__':
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

    # write_movie_file('movies_test', popular_movies_list)
    write_movie_file_to_postgres('movies_test', popular_movies_list)
    # loop_through_movies(popular_movies_list)
    
    write_languages_file_to_postgres()

    # remove_files()
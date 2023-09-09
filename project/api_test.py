import io
import os
import requests
import json
import csv
import pandas as pd
from google.cloud import storage
from config import tmdb_api_key, tmdb_api_read_access_token, postgres_user, postgres_password, \
    postgres_host, postgres_port, postgres_database, postgres_movies_table_name, \
        postgres_movies_language_table_name
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
#         return 'API Error'


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
                # print(f'Dataset:\n {dataset}')
                # KEYS USED
                # dict_keys(['adult', 'backdrop_path', 'genre_ids', 'id', 'original_language', 
                # 'original_title', 'overview', 'popularity', 'poster_path', 'release_date', 
                # 'title', 'video', 'vote_average', 'vote_count'])
            # print(len(dataset))

        else:
            return 'API Error'
        
    return dataset    

def get_movie_info(movie_id: int):
        
    url = f'https://api.themoviedb.org/3/movie/{movie_id}'
    
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

    else:
        return 'API Error'           

    print(dataset_page.keys())
    # print(dataset_page['budget'])
    # print(dataset_page['runtime'])
    print(dataset_page['revenue'] / dataset_page['budget']) # earned back" (?)
    # print(dataset_page)


def get_movie_info2(movie_id: int):
        
    # url = f'https://api.themoviedb.org/3/movie/{movie_id}/rating'
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?append_to_response=rating'
    
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

    else:
        return 'API Error'        

    print(dataset_page.keys())
    # print(dataset_page['rating'])
    print(dataset_page['revenue'])
    print(dataset_page['budget'])
    print(dataset_page['runtime'])
    print(dataset_page['revenue'] / dataset_page['budget']) # earned back" (?)
    # print(dataset_page)


def get_genres(movie_id: int):
        
    # url = f'https://api.themoviedb.org/3/movie/{movie_id}/rating'
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?append_to_response=rating'
    
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

    else:
        return 'API Error'        

    # print(dataset_page['genres'])
    # print(dataset_page)
    # for i in dataset_page['genres']:
    #     print(i['id'])
    #     print(i['name'])

    # print('Creating the DataFrame...')
    # Create empty dataframe with headers
    df = pd.DataFrame(columns=['genre_id', 'genre_name'])

    # print('Adding genre information to the DataFrame...')
    for i in range(len(dataset_page['genres'])):
        # print(dataset_page['genres'][i]['id'])
        # print(dataset_page['genres'][i]['name'])
        # print(dataset[i]['title'])
        df.loc[i] = [dataset_page['genres'][i]['id'], dataset_page['genres'][i]['name']]
    
    # print(df.head())

    return df


def get_popular_movies_genres(dataset: list):
    print('Creating the DataFrame...')
    # Create empty dataframe with headers
    df = pd.DataFrame(columns=['genre_id', 'genre_name'])

    # For each movie in the dataset, add its info to the dataframe
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#setting-with-enlargement
    print('Adding genre information to the DataFrame...')
    for i in range(len(dataset)):
        # print(dataset[i]['title'])
        mini_df = get_genres(dataset[i]['id'])
        # print(mini_df.head())

        # Append DataFrame for the current movie to the overall DataFrame of genres and id's
        # Also drop the duplicates
        df = pd.concat([df, mini_df]).drop_duplicates(subset=['genre_id'], keep='first')
    
    print(df.head(25))

    df.reset_index(names=['id'])

    print('\n', df.head(25))



def get_financials(movie_id: int):
        
    # url = f'https://api.themoviedb.org/3/movie/{movie_id}/rating'
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?append_to_response=rating'
    
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

    else:
        return 'API Error'        

    # print(dataset_page['genres'])
    # print(dataset_page)
    # for i in dataset_page['genres']:
    #     print(i['id'])
    #     print(i['name'])

    # print('Creating the DataFrame...')
    # Create empty dataframe with headers
    df = pd.DataFrame(columns=['id', 'revenue', 'budget', 'runtime'])

    print(dataset_page)
    
    df.loc[0] = [dataset_page['id'], dataset_page['revenue'],
                 dataset_page['budget'], dataset_page['runtime']]
    
    # # print('Adding genre information to the DataFrame...')
    # for i in range(len(dataset_page)):
    #     # print(dataset_page['genres'][i]['id'])
    #     # print(dataset_page['genres'][i]['name'])
    #     # print(dataset[i]['title'])
    #     df.loc[i] = [dataset_page[i]['id'], dataset_page[i]['revenue'],
    #                  dataset_page[i]['budget'], dataset_page[i]['runtime']]
    
    print(df.head())  


if __name__ == '__main__':
    # get_popular_movies()
    popular_movies_list = get_popular_movies()
    # get_popular_movies_genres(popular_movies_list)

    # The Meg 2
    # get_movie_info(615656)
    # get_movie_info2(615656)
    get_genres(615656)
    get_financials(615656)
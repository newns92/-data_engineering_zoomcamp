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
                print(f'Dataset:\n {dataset}')
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
    print(dataset_page['rating'])
    # print(dataset_page['budget'])
    # print(dataset_page['runtime'])
    # print(dataset_page['revenue'] / dataset_page['budget']) # earned back" (?)
    # print(dataset_page)

if __name__ == '__main__':
    # get_popular_movies()

    # The Meg 2
    # get_movie_info(615656)
    get_movie_info2(615656)
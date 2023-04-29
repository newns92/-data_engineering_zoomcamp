import pandas as pd
from sqlalchemy import create_engine
import time
import argparse  # for named arguments like user, password, host, port, database, table, file locations, etc.
import os
from prefect import flow, task
from prefect.tasks import task_input_hash
from datetime import timedelta

@task(log_prints=True, retries=3, cache_key_fn=task_input_hash, cache_expiration=timedelta(days=1))
def download_data(taxi_url, zones_url):
    print('Starting...')
    # # add in the connection to the DDL statement
    # ddl = pd.io.sql.get_schema(df, name='yellow_taxi_data', con=engine)
    # print(ddl)

    # Download the data
    print("Downloading the taxi data...")
    taxi_csv_name = 'yellow_tripdata_2021-01.csv'
    os.system(f'wget {taxi_url} -O {taxi_csv_name}')  # -O = output to the given file name

    print("Downloading the taxi zone data...")
    zones_csv_name = 'taxi+_zone_lookup.csv'
    os.system(f'wget {zones_url} -O {zones_csv_name}')  # -O = output to the given file name

    # Add in the timezones first before the long loop
    df_zones = pd.read_csv(zones_csv_name)
    # df_zones.to_sql(name=zones_table_name, con=engine, if_exists='replace')
    # print('Loaded in time zone data')
    
    # Unzip dataset and chunk dataset into smaller sizes to load into the database
    df_iter = pd.read_csv(taxi_csv_name, compression='gzip', iterator=True, chunksize=100000)
    # return the next item in an iterator with next()
    df = next(df_iter) 
    # print(len(df))

    # Convert meter engaged and meter disengaged columns from text to dates
    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    return df, df_zones

@task(log_prints=True)
def transform_data(df):
    print(f"Pre: Missing passenger count: {df['passenger_count'].isin([0]).sum()}")
    
    # reset the dataframe to ignore those "trips" with passenger count of 0
    df = df[df['passenger_count'] != 0]

    print(f"Post: Missing passenger count: {df['passenger_count'].isin([0]).sum()}")
    
    return df

@task(log_prints=True, retries=3)
def load_data(user, password, host, port, database, taxi_table_name, df_taxi, zones_table_name, df_zones):
    # print("Creating the engine...")
    # need to convert a DDL statement into something Postgres will understand
    #   - via create_engine([database_type]://[user]:[password]@[hostname]:[port]/[database], con=[engine])
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}')    
    
    print('Loading in time zone data...')
    df_zones.to_sql(name=zones_table_name, con=engine, if_exists='replace')
    print('Loaded in time zone data')

    # get the header/column names
    header = df_taxi.head(n=0)
    # print(header)

    # add the column headers to the yellow_taxi_data table in the database connection, and replace the table if it exists
    header.to_sql(name=taxi_table_name, con=engine, if_exists='replace')
    
    print('Loading in taxi data...')
    # add first chunk of data
    start = time.time()
    df_taxi.to_sql(name=taxi_table_name, con=engine, if_exists='append')
    end = time.time()
    print('Time to insert first taxi data chunk: in %.3f seconds.' % (end - start))

    # def load_chunks(df):
    #     try:
    #         print("Loading next taxi data chunk...")
    #         start = time.time()

    #         # get next chunk
    #         df = next(df_iter)

    #         # fix datetimes
    #         df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    #         df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
            
    #         # add chunk
    #         df.to_sql(name=taxi_table_name, con=engine, if_exists='append')

    #         end = time.time()

    #         print('Inserted another taxi data chunk in %.3f seconds.' % (end - start))

    #     except:
    #         # will come to this clause when we throw an error after running out of data chunks
    #         print('All taxi data chunks loaded.')
    #         quit()

    # # insert the rest of the chunks until loop breaks when all data is added
    # while True:
    #     if load_chunks(taxi_df):
    #         break
    #     else:        
    #         continue

@flow(name="Ingest Flow")
def main_flow():
    user = "root"
    password = "root"
    host = "localhost"
    port = "5432"
    database = "ny_taxi"
    taxi_table_name = "yellow_taxi_data_2"
    taxi_url = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz"
    zones_table_name = "zones_2"
    zones_url = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv"

    raw_data_taxi, raw_data_zones = download_data(taxi_url, zones_url)
    transformed_data_taxi, transformed_data_zones = transform_data(raw_data_taxi), raw_data_zones
    load_data(user, password, host, port, database, taxi_table_name, 
              transformed_data_taxi, zones_table_name, transformed_data_zones)

if __name__ == '__main__':
    main_flow()
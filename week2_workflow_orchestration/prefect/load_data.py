import pandas as pd
from sqlalchemy import create_engine
import time
import argparse  # for named arguments like user, password, host, port, database, table, file locations, etc.
import os

def load_data(user, password, host, port, database, taxi_table_name, taxi_url, zones_table_name, zones_url):
    print('Starting...')
    print("Creating the engine...")
    # need to convert this DDL statement into something Postgres will understand
    #   - via create_engine([database_type]://[user]:[password]@[hostname]:[port]/[database], con=[engine])
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}')

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
    df_zones.to_sql(name=zones_table_name, con=engine, if_exists='replace')
    print('Loaded in time zone data')

    print('Loading in taxi data...')
    # Unzip dataset and chunk dataset into smaller sizes to load into the database
    df_iter = pd.read_csv(taxi_csv_name, compression='gzip', iterator=True, chunksize=100000)
    # return the next item in an iterator with next()
    df = next(df_iter) 
    # print(len(df))

    # Convert meter engaged and meter disengaged columns from text to dates
    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    # get the header/column names
    header = df.head(n=0)
    # print(header)

    # add the column headers to the yellow_taxi_data table in the database connection, and replace the table if it exists
    header.to_sql(name=taxi_table_name, con=engine, if_exists='replace')

    # add first chunk of data
    start = time.time()
    df.to_sql(name=taxi_table_name, con=engine, if_exists='append')
    end = time.time()
    print('Time to insert first chunk: in %.3f seconds.' % (end - start))

    def load_chunks(df):
        try:
            print("Loading next chunk...")
            start = time.time()

            # get next chunk
            df = next(df_iter)

            # fix datetimes
            df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
            df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
            
            # add chunk
            df.to_sql(name=taxi_table_name, con=engine, if_exists='append')

            end = time.time()

            print('Inserted another chunk in %.3f seconds.' % (end - start))

        except:
            # will come to this clause when we throw an error after running out of data chunks
            print('All data chunks loaded.')
            quit()

    # insert the rest of the chunks until loop breaks when all data is added
    while True:
        if load_chunks(df):
            break
        else:        
            continue

if __name__ == '__main__':
    user = "root"
    password = "root"
    host = "localhost"
    port = "5432"
    database = "ny_taxi"
    taxi_table_name = "yellow_taxi_data_2"
    taxi_url = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz"
    zones_table_name = "zones_2"
    zones_url = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv"

    load_data(user, password, host, port, database, taxi_table_name, taxi_url, zones_table_name, zones_url)
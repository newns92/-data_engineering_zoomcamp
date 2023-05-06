import io
import os
import requests
import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path
import shutil
import time

"""
Pre-reqs: 
1. Spin up the Postgres database via `docker-compose up -d` in this directory
2. If necessary, create the taxi_data server again
"""

# services = ['fhv','green','yellow']
init_url = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/'


def create_pg_engine(user, password, host, port, database):
    # Upload CSV to Postgres
    print("Creating the engine...")
    # need to convert a DDL statement into something Postgres will understand
    #   - via create_engine([database_type]://[user]:[password]@[hostname]:[port]/[database], con=[engine])
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}')

    return engine


def remove_files():
    # https://stackoverflow.com/questions/32834731/how-to-delete-a-file-by-extension-in-python
    dir_name = "./"
    local_data = os.listdir(dir_name)

    # remove the local CSV's
    for item in local_data:
        if item.endswith(".csv.gz"):
            os.remove(os.path.join(dir_name, item))

    # # Remove the local parquet files
    # # https://stackoverflow.com/questions/48892772/how-to-remove-a-directory-is-os-removedirs-and-os-rmdir-only-used-to-delete-emp
    # shutil.rmtree('./data/')


def clean_data(df, service):
    '''Fix datatype issues'''

    if service == 'yellow':
        # fix datetimes
        df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
        df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

        # this fixes fields for files that have NAN values and thus aren't INTs
        # when they should be INTs
        df.VendorID = df.passenger_count.fillna(999).astype('int')
        df.passenger_count = df.passenger_count.fillna(999).astype('int')
        df.payment_type = df.payment_type.fillna(999).astype('int')
        df.RatecodeID = df.RatecodeID.fillna(999).astype('int')
        df.VendorID = df.VendorID.fillna(999).astype('int')

    elif service == 'green':
        # fix datetimes
        df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
        df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)

        # this fixes fields for files that have NAN values and thus aren't INTs
        # when they should be INTs
        df.VendorID = df.passenger_count.fillna(999).astype('int')
        df.passenger_count = df.passenger_count.fillna(999).astype('int')
        df.payment_type = df.payment_type.fillna(999).astype('int')
        df.trip_type = df.trip_type.fillna(999).astype('int')
        df.RatecodeID = df.RatecodeID.fillna(999).astype('int')
        df.VendorID = df.VendorID.fillna(999).astype('int')

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
        df.PULocationID = df.PULocationID.fillna(999).astype('int')
        df.DOLocationID = df.DOLocationID.fillna(999).astype('int')            

    return df


def web_to_pg(year, service):

    # Loop through the months
    for i in range(12):
        
        # Set the month part of the file_name string
        month = '0'+str(i + 1)
        month = month[-2:]

        # create CSV file_name and path to write parquet file to
        file_name = f'{service}_tripdata_{year}-{month}.csv.gz'

        # Download CSV using requests via a Pandas DataFrame
        print(f'\nDownloading {file_name}...')
        request_url = f"{init_url}{service}/{file_name}"
        r = requests.get(request_url)
        open(file_name, 'wb').write(r.content)

        df_iter = pd.read_csv(file_name, compression='gzip', iterator=True, chunksize=100000)
        df = next(df_iter)

        # clean the data and fix the data types
        df = clean_data(df, service)

        # # get the header/column names
        # header = df.head(n=0)
        # # print(header)

        start = time.time()
        start_datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start))

        print(f'Uploading {file_name} to Postgres starting at {start_datetime}...')
        # add first chunk of data
        df.to_sql(f'{service}_trip_data',  con=engine, if_exists='append')
        end = time.time()
        print('Time to insert first chunk: in %.3f seconds.' % (end - start))        

        # add the column headers to the green_taxi_data table in the database connection, and replace the table if it exists
        # header.to_sql(name=f'{service}_trip_data', con=engine, if_exists='replace')

        def load_chunks(df):
            try:
                print("Loading next chunk...")
                start = time.time()

                # get next chunk
                df = next(df_iter)

                # clean the data and fix the data types
                df = clean_data(df, service)
                    
                # add chunk
                df.to_sql(name=f'{service}_trip_data', con=engine, if_exists='append')

                end = time.time()

                print('Inserted another of ' + file_name +  ' chunk in %.3f seconds.' % (end - start))

            except:
                # will come to this clause when we throw an error after running out of data chunks
                print('All data chunks loaded.')
                return('All data chunks loaded.')

        # insert the rest of the chunks until loop breaks when all data is added
        while True:
            if load_chunks(df):
                break
            else:        
                continue

        # # add data
        # print(f'Uploading {file_name} to Postgres...')
        # start = time.time()
        # df.to_sql(name=f'{service}_trip_data', con=engine, if_exists='append')
        # end = time.time()
        # print(f'Time to insert {file_name}: %.3f seconds.' % (end - start))    

if __name__ == '__main__':
    user = "root"  # admin@admin.com
    password = "root"
    host = "localhost"
    port = "5432"
    database = "ny_taxi"

    engine = create_pg_engine(user, password, host, port, database)

    web_to_pg('2019', 'green')
    web_to_pg('2020', 'green')
    web_to_pg('2019', 'yellow')
    web_to_pg('2020', 'yellow')
    web_to_pg('2019', 'fhv')

    remove_files()


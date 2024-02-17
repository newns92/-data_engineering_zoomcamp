import io
import os
import requests
import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path
import shutil
import time
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.compute as pc

"""
Pre-reqs: 
1. Spin up the Postgres database via `docker-compose up -d` in this directory
2. If necessary, create the ny_taxi_data server again
"""

# services = ['fhv','green','yellow']
# init_url = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/'
init_url = 'https://d37ci6vzurychx.cloudfront.net/trip-data'


def create_pg_engine(user, password, host, port, database):
    # Upload CSV to Postgres
    print("Creating the engine...")
    # need to convert a DDL statement into something Postgres will understand
    #   - via create_engine([database_type]://[user]:[password]@[hostname]:[port]/[database], con=[engine])
    # https://stackoverflow.com/questions/9298296/sqlalchemy-support-of-postgres-schemas/49930672#49930672
    dbschema = 'dev'
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}',
                            connect_args={'options': '-csearch_path={}'.format(dbschema)}
                        )

    return engine


def remove_files():
    # https://stackoverflow.com/questions/32834731/how-to-delete-a-file-by-extension-in-python
    dir_name = "./"
    local_data = os.listdir(dir_name)

    # remove the local CSV's
    for item in local_data:
        if item.endswith(".csv.gz"):
            os.remove(os.path.join(dir_name, item))
        elif item.endswith(".parquet"):
            os.remove(os.path.join(dir_name, item))

    # Remove the local parquet files
    # https://stackoverflow.com/questions/48892772/how-to-remove-a-directory-is-os-removedirs-and-os-rmdir-only-used-to-delete-emp
    shutil.rmtree('./data/')


def clean_data(df, service):
    '''Fix datatype issues'''

    if service == 'yellow':
        # Rename columns
        df.rename({'VendorID':'vendor_id',
                        'PULocationID':'pu_location_id',
                        'DOLocationID':'do_location_id',
                        'RatecodeID':'rate_code_id'}, 
                    axis='columns', inplace=True
                  )
                
        # Fix datetimes
        df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
        df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

        # this fixes fields for files that have NAN values and thus aren't INTs
        # when they should be INTs
        # https://pandas.pydata.org/pandas-docs/stable/user_guide/integer_na.html#integer-na
        df.vendor_id = pd.array(df.vendor_id, dtype=pd.Int64Dtype())
        df.passenger_count = pd.array(df.passenger_count, dtype=pd.Int64Dtype())
        df.payment_type = pd.array(df.payment_type, dtype=pd.Int64Dtype())
        df.rate_code_id = pd.array(df.rate_code_id, dtype=pd.Int64Dtype())

    elif service == 'green':
        # Rename columns
        df.rename({'VendorID':'vendor_id',
                        'PULocationID':'pu_location_id',
                        'DOLocationID':'do_location_id',
                        'RatecodeID':'rate_code_id'}, 
                    axis='columns', inplace=True
                  )
                
        # fix datetimes
        df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
        df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)

        # this fixes fields for files that have NAN values and thus aren't INTs
        # when they should be INTs
        # https://pandas.pydata.org/pandas-docs/stable/user_guide/integer_na.html#integer-na
        df.vendor_id = pd.array(df.vendor_id, dtype=pd.Int64Dtype())
        df.passenger_count = pd.array(df.passenger_count, dtype=pd.Int64Dtype())
        df.payment_type = pd.array(df.payment_type, dtype=pd.Int64Dtype())
        df.trip_type = pd.array(df.trip_type, dtype=pd.Int64Dtype())
        df.rate_code_id = pd.array(df.rate_code_id, dtype=pd.Int64Dtype())

    # elif service == 'fhv':
    else:
        # Rename columns
        df.rename({'dropOff_datetime':'dropoff_datetime',
                        'PUlocationID':'pu_location_id',
                        'DOlocationID':'do_location_id',
                        'SR_Flag':'sr_flag',
                        'Affiliated_base_number':'affiliated_base_number'},
                    axis='columns', inplace=True
                  )

        # fix datetimes
        df.pickup_datetime = pd.to_datetime(df.pickup_datetime)
        df.dropoff_datetime = pd.to_datetime(df.dropoff_datetime)

        # this fixes fields for files that have NAN values and thus aren't INTs
        # when they should be INTs
        # https://pandas.pydata.org/pandas-docs/stable/user_guide/integer_na.html#integer-na
        df.pu_location_id = pd.array(df.pu_location_id, dtype=pd.Int64Dtype())
        df.do_location_id = pd.array(df.do_location_id, dtype=pd.Int64Dtype())

        # Fix a DOUBLE that may be trying to be forced into an INT
        df.sr_flag = pd.array(df.sr_flag, dtype=pd.Int64Dtype())

    return df


def web_to_pg(year, service):
    # Keep track of total rows to compare with GCS
    total_rows = 0

    # Loop through the months
    for i in range(12):
        
        # Set the month part of the file_name string
        month = '0'+str(i + 1)
        month = month[-2:]

        # create CSV file_name and path to write parquet file to
        file_name = f'{service}_tripdata_{year}-{month}.parquet'
        path = Path(f'data/{service}_tripdata_{year}-{month}.parquet').as_posix()

        # Make the directory to hold the parquet file if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)        

        # Download CSV using requests via a Pandas DataFrame
        print(f'\nDownloading {file_name}...')
        request_url = f"{init_url}/{file_name}"
        r = requests.get(request_url)
        open(file_name, 'wb').write(r.content)

        # # FOR CSV's, DEFINE THE DATA TYPE
        # https://stackoverflow.com/questions/24251219/pandas-read-csv-low-memory-and-dtype-options
        # if service == 'yellow':
        #     # Map the data types
        #     taxi_dtypes = {
        #                     'VendorID': pd.Int64Dtype(),
        #                     'passenger_count': pd.Int64Dtype(),
        #                     'trip_distance': float,
        #                     'RatecodeID': pd.Int64Dtype(),
        #                     'store_and_fwd_flag': str,
        #                     'PULocationID': pd.Int64Dtype(),
        #                     'DOLocationID': pd.Int64Dtype(),
        #                     'payment_type': pd.Int64Dtype(),
        #                     'fare_amount': float,
        #                     'extra': float,
        #                     'mta_tax': float,
        #                     'tip_amount': float,
        #                     'tolls_amount': float,
        #                     'improvement_surcharge': float,
        #                     'total_amount': float,
        #                     'congestion_surcharge': float
        #                 }
        #     # Parse the datetime columns
        #     parse_dates = ['tpep_pickup_datetime', 'tpep_dropoff_datetime']
        
        # elif service == 'green':
        #     # Map the data types
        #     taxi_dtypes = {
        #                     'VendorID': pd.Int64Dtype(),
        #                     'passenger_count': pd.Int64Dtype(),
        #                     'trip_distance': float,
        #                     'RatecodeID': pd.Int64Dtype(),
        #                     'store_and_fwd_flag': str,
        #                     'PULocationID': pd.Int64Dtype(),
        #                     'DOLocationID': pd.Int64Dtype(),
        #                     'payment_type': pd.Int64Dtype(),
        #                     'fare_amount': float,
        #                     'extra': float,
        #                     'mta_tax': float,
        #                     'tip_amount': float,
        #                     'tolls_amount': float,
        #                     'improvement_surcharge': float,
        #                     'total_amount': float,
        #                     'congestion_surcharge': float,
        #                     'ehail_fee': float,
        #                     'trip_type': pd.Int64Dtype()
        #                 }
            
        #     # Parse the datetime columns
        #     parse_dates = ['lpep_pickup_datetime', 'lpep_dropoff_datetime']

        # df_iter = pd.read_csv(file_name, compression='gzip', iterator=True, chunksize=100000)
        # df = next(df_iter)

        df = pd.read_parquet(file_name)

        print(f'Number of rows: {len(df.index)}')

        # clean the data and fix the data types
        df = clean_data(df, service)

        # get the header/column names
        header = df.head(n=0)
        # print(header)

        # start = time.time()
        # start_datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start))

        # print(f'Uploading {file_name} to Postgres starting at {start_datetime}...')
        # # add first chunk of data
        # df.to_sql(f'{service}_trip_data',  con=engine, if_exists='append')
        # end = time.time()
        # print('Time to insert first chunk: in %.3f seconds.' % (end - start))        

        # add the column headers to the table in the database connection, and replace the table if it exists
        header.to_sql(name=f'{service}_trip_data', con=engine, if_exists='replace')

        # def load_chunks(df):
        #     try:
        #         print("Loading next chunk...")
        #         start = time.time()

        #         # get next chunk
        #         df = next(df_iter)

        #         # clean the data and fix the data types
        #         df = clean_data(df, service)
                    
        #         # add chunk
        #         df.to_sql(name=f'{service}_trip_data', con=engine, if_exists='append')

        #         end = time.time()

        #         print('Inserted another of ' + file_name +  ' chunk in %.3f seconds.' % (end - start))

        #     except:
        #         # will come to this clause when we throw an error after running out of data chunks
        #         print('All data chunks loaded.')
        #         return('All data chunks loaded.')

        # # insert the rest of the chunks until loop breaks when all data is added
        # while True:
        #     if load_chunks(df):
        #         break
        #     else:        
        #         continue

        # add data
        print(f'Uploading {file_name} to Postgres...')
        
        start = time.time()
        df.to_sql(name=f'{service}_trip_data', con=engine, if_exists='append')
        end = time.time()
        print(f'Time to insert {file_name}: %.3f seconds.' % (end - start))

    print(f'Total rows for {service} in {year}: {total_rows}')        

if __name__ == '__main__':
    user = "root"  # admin@admin.com
    password = "root"
    host = "localhost"
    port = "5432"
    database = "ny_taxi"

    engine = create_pg_engine(user, password, host, port, database)

    web_to_pg('2019', 'green')
    web_to_pg('2020', 'green')
    # web_to_pg('2019', 'yellow')
    # web_to_pg('2020', 'yellow')
    # web_to_pg('2019', 'fhv')

    remove_files()


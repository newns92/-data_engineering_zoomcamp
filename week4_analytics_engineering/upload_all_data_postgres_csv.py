import sys
import requests
import pandas as pd
# For removing files from a directory
import os
# import shutil
from sqlalchemy import create_engine
import time
# For checking if file exists
from pathlib import Path
# import shutil
import time
# # For Parquet manipulation
# import pyarrow as pa
# import pyarrow.parquet as pq
# import pyarrow.compute as pc

'''
Pre-reqs: 
1. Spin up the Postgres database via `winpty docker-compose up -d` in the current directory
2. If necessary, create the ny_taxi_data server again
'''

# services = ['fhv','green','yellow']
init_url = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/'
# init_url = 'https://d37ci6vzurychx.cloudfront.net/trip-data'


def create_pg_engine(user, password, host, port, database):
    ## Upload CSV to Postgres
    print('Creating the engine...')
    ## Need to convert a DDL statement into something Postgres will understand
    ##   - via create_engine([database_type]://[user]:[password]@[hostname]:[port]/[database], con=[engine])
    ## https://stackoverflow.com/questions/9298296/sqlalchemy-support-of-postgres-schemas/49930672#49930672
    # dbschema = 'dev'
    dbschema = 'public'
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}',
                            connect_args={'options': '-csearch_path={}'.format(dbschema)}
                        )

    return engine


def remove_files():
    print('Removing files...')
    ## https://stackoverflow.com/questions/32834731/how-to-delete-a-file-by-extension-in-python
    dir_name = './data'
    local_data = os.listdir(dir_name)

    ## Remove the local compressed and uncompressed CSV's
    for item in local_data:
        if item.endswith('.csv.gz'):
            os.remove(os.path.join(dir_name, item))
        elif item.endswith('.csv'):
            os.remove(os.path.join(dir_name, item))

    # ## Remove all other the local files in the 'data' directory
    # ## https://stackoverflow.com/questions/48892772/how-to-remove-a-directory-is-os-removedirs-and-os-rmdir-only-used-to-delete-emp
    # shutil.rmtree('./data/')


def clean_data(df, service):
    '''Fix datatype issues'''

    if service == 'yellow':
        ## Rename columns
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

        ## Fix fields for files that have NAN values and thus aren't INTs
        ##   when they should be INTs
        ## https://pandas.pydata.org/pandas-docs/stable/user_guide/integer_na.html#integer-na
        df.vendor_id = pd.array(df.vendor_id, dtype=pd.Int64Dtype())
        df.passenger_count = pd.array(df.passenger_count, dtype=pd.Int64Dtype())
        df.payment_type = pd.array(df.payment_type, dtype=pd.Int64Dtype())
        df.rate_code_id = pd.array(df.rate_code_id, dtype=pd.Int64Dtype())

        ## Replace payment_type of 0 or NULL with correct voided value of 6, according to data dictionary
        ## https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_green.pdf
        ## https://stackoverflow.com/questions/31511997/pandas-dataframe-replace-all-values-in-a-column-based-on-condition
        df.loc[df['payment_type'] == 0, 'payment_type'] = 6        

    elif service == 'green':
        ## Rename columns
        df.rename({'VendorID':'vendor_id',
                   'PULocationID':'pu_location_id',
                   'DOLocationID':'do_location_id',
                   'RatecodeID':'rate_code_id'
                }, 
            axis='columns', inplace=True
        )
                
        ## Fix datetimes
        df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
        df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)

        ## Fix fields for files that have NAN values and thus aren't INTs
        ##   when they should be INTs
        ## https://pandas.pydata.org/pandas-docs/stable/user_guide/integer_na.html#integer-na
        df.vendor_id = pd.array(df.vendor_id, dtype=pd.Int64Dtype())
        df.passenger_count = pd.array(df.passenger_count, dtype=pd.Int64Dtype())
        df.payment_type = pd.array(df.payment_type, dtype=pd.Int64Dtype())
        df.trip_type = pd.array(df.trip_type, dtype=pd.Int64Dtype())
        df.rate_code_id = pd.array(df.rate_code_id, dtype=pd.Int64Dtype())

        ## Replace payment_type of 0 or NULL with correct voided value of 6, according to data dictionary
        ## https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_green.pdf
        ## https://stackoverflow.com/questions/31511997/pandas-dataframe-replace-all-values-in-a-column-based-on-condition
        # df.loc[df['payment_type'] == 0, 'payment_type'] = 6
        df.loc[df['payment_type'].isnull() == True, 'payment_type'] = 6
        # print(df.payment_type.unique())

    # elif service == 'fhv':
    else:
        ## Rename columns
        df.rename({'dropOff_datetime':'dropoff_datetime',
                   'PUlocationID':'pu_location_id',
                   'DOlocationID':'do_location_id',
                   'SR_Flag':'sr_flag',
                   'Affiliated_base_number':'affiliated_base_number'
                },
            axis='columns', inplace=True
        )

        ## Fix datetimes
        df.pickup_datetime = pd.to_datetime(df.pickup_datetime)
        df.dropoff_datetime = pd.to_datetime(df.dropoff_datetime)

        ## Fix fields for files that have NAN values and thus aren't INTs
        ##   when they should be INTs
        ## https://pandas.pydata.org/pandas-docs/stable/user_guide/integer_na.html#integer-na
        df.pu_location_id = pd.array(df.pu_location_id, dtype=pd.Int64Dtype())
        df.do_location_id = pd.array(df.do_location_id, dtype=pd.Int64Dtype())

        ## Fix a DOUBLE that may be trying to be forced into an INT
        df.sr_flag = pd.array(df.sr_flag, dtype=pd.Int64Dtype())

    return df


def web_to_pg(year, service):

    ## Download zones data
    zones_url = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv'
    zones_csv_name = './data/taxi_zone_lookup.csv'
    zones_file = Path(zones_csv_name)

    ## If the file is not already downloaded/does not exist, download it
    if not zones_file.is_file():
        print(f'\nDownloading the taxi zone data...')
        os.system(f'wget {zones_url} -O {zones_csv_name}')  # -O = output to the given file name        

        ## Add in the smaller taxi zones table first before the long loop for the taxi data
        print('\nLoading in zone data...')
        df_zones = pd.read_csv(zones_csv_name)
        df_zones.to_sql(name='zones', con=engine, if_exists='replace')
        print('Loaded in zone data')

    ## Keep track of total rows to compare with GCS
    total_rows = 0

    ## Loop through the months
    for i in range(1, 13):
    # for i in range(3):
        
        ## Set the month part of the file_name string
        if len(str(i)) == 1:
            # print(f'Single digit: {i}')
            month = '0' + str(i)
        else:
            # print(f'Double digit: {i}')
            month = (i)
        # print(month)

        ## Create CSV file_name and path to write parquet file to
        file_name = f'{service}_tripdata_{year}-{month}.csv.gz'
        taxi_file = Path(f'data/{service}_tripdata_{year}-{month}.csv.gz') # .as_posix()

        ## Make the directory to hold the CSV file if it doesn't exist
        os.makedirs(os.path.dirname(taxi_file), exist_ok=True)        

        ## If the file is not already downloaded/does not exist, download it
        if not taxi_file.is_file():
            ## Download taxi CSV using `requests` via a Pandas DataFrame
            print(f'\nDownloading {file_name}...')
            request_url = f'{init_url}{service}/{file_name}'
            # print(request_url)
            r = requests.get(request_url)
            open(f'data/{file_name}', 'wb').write(r.content)

        ## FOR CSV's, MUST DEFINE THE DATA TYPE
        ## https://stackoverflow.com/questions/24251219/pandas-read-csv-low-memory-and-dtype-options
        if service == 'yellow':
            ## Map the data types
            taxi_dtypes = {
                            'vendor_id': pd.Int64Dtype(),
                            'passenger_count': pd.Int64Dtype(),
                            'trip_distance': float,
                            'rate_code_id': pd.Int64Dtype(),
                            'store_and_fwd_flag': str,
                            'pu_location_id': pd.Int64Dtype(),
                            'do_location_id': pd.Int64Dtype(),
                            'payment_type': pd.Int64Dtype(),
                            'fare_amount': float,
                            'extra': float,
                            'mta_tax': float,
                            'tip_amount': float,
                            'tolls_amount': float,
                            'improvement_surcharge': float,
                            'total_amount': float,
                            'congestion_surcharge': float
                        }
            ## Parse the datetime columns
            parse_dates = ['tpep_pickup_datetime', 'tpep_dropoff_datetime']
        
        elif service == 'green':
            ## Map the data types
            taxi_dtypes = {
                            'vendor_id': pd.Int64Dtype(),
                            'passenger_count': pd.Int64Dtype(),
                            'trip_distance': float,
                            'Ratecorate_code_iddeID': pd.Int64Dtype(),
                            'store_and_fwd_flag': str,
                            'pu_location_id': pd.Int64Dtype(),
                            'do_location_id': pd.Int64Dtype(),
                            'payment_type': pd.Int64Dtype(),
                            'fare_amount': float,
                            'extra': float,
                            'mta_tax': float,
                            'tip_amount': float,
                            'tolls_amount': float,
                            'improvement_surcharge': float,
                            'total_amount': float,
                            'congestion_surcharge': float,
                            'ehail_fee': float,
                            'trip_type': pd.Int64Dtype()
                        }
            
            ## Parse the datetime columns
            parse_dates = ['lpep_pickup_datetime', 'lpep_dropoff_datetime']

        print('\nLoading in taxi data in chunks...')
        ## Chunk dataset into smaller sizes to load into the database via the 'chunksize' arg
        df_iter = pd.read_csv(f'./data/{file_name}',
                              compression='gzip',
                              iterator=True,
                              chunksize=100000,
                              dtype=taxi_dtypes,
                              parse_dates=parse_dates)

        ## Return the next item in an iterator object with the 'next()' function
        df = next(df_iter)
        
        # # NOTE: one FHV file has an out-of-bounds timestamp
        # # https://stackoverflow.com/questions/74467923/pandas-read-parquet-error-pyarrow-lib-arrowinvalid-casting-from-timestampus
        # # df = pd.read_parquet(file_name)
        # table = pq.read_table(file_name)

        # if service == 'fhv':
        #     df = table.filter(
        #         pc.less_equal(table['dropOff_datetime'], pa.scalar(pd.Timestamp.max))
        #     ).to_pandas()
        # else:
        #     df = table.to_pandas()

        ## Clean the data and fix the data types
        df = clean_data(df, service)

        if i == 1:
            ## Get the header (column) names
            header = df.head(n=0)
            # print(header)

            ## Add the column headers to the table in the database connection, 
            ##  and replace the table if it exists (ONLY FOR MONTH 1/JANUARY)
            print(f'Creating the {service} trip data table with DataFrame headers...')
            header.to_sql(name=f'{service}_trip_data', con=engine, if_exists='replace')        

        start = time.time()
        start_datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start))

        ## Add (append) first chunk of data to the table and time how long it takes
        print(f'Uploading {file_name} to Postgres starting at {start_datetime}...')
        # print(f'Number of rows: {len(df.index)}')
        print(f'Adding {df.shape[0]} rows...')
        total_rows += df.shape[0]

        start = time.time()
        df.to_sql(f'{service}_trip_data',  con=engine, if_exists='append')
        end = time.time()
        print("Time to insert first chunk: in %.3f seconds." % (end - start))

        def load_chunks(df, total_rows):
            try:
                print('Loading next chunk...')
                start = time.time()

                ## Get next chunk
                df = next(df_iter)

                print(f'Adding {df.shape[0]} rows...')
                total_rows += df.shape[0]

                ## Clean the data and fix the data types
                df = clean_data(df, service)
                    
                ## Add chunk
                df.to_sql(name=f'{service}_trip_data', con=engine, if_exists='append')

                end = time.time()

                print('Inserted another of ' + file_name +  ' chunk in %.3f seconds.' % (end - start))

            except:
                ## Will come to this clause when we throw an error after running out of data chunks
                print('All data chunks loaded.')
                
                return total_rows

            # except:
            #     ## Program will come to this clause when it throws an error after
            #     ##   running out of data chunks
            #     print("All data chunks loaded.")

            #     return()

            #     # ## Exit with code of 1 (an error occured)
            #     # ## NOTE: quit() is only intended to work in the interactive Python shell
            #     # sys.exit(1)


        ## Insert the rest of the chunks until loop breaks when all data is added
        while True:
            if load_chunks(df, total_rows):
                break
            else:        
                continue

    print(f'Total rows for {service} in {year}: {total_rows}')

if __name__ == '__main__':
    user = 'root'  # admin@admin.com
    password = 'root'
    host = 'localhost'
    port = '5432'
    database = 'ny_taxi'

    engine = create_pg_engine(user, password, host, port, database)

    # web_to_pg('2019', 'green')
    # web_to_pg('2020', 'green')
    # web_to_pg('2019', 'yellow')
    web_to_pg('2020', 'yellow')
    # web_to_pg('2019', 'fhv')

    remove_files()

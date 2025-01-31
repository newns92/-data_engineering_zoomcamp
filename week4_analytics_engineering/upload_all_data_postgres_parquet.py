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
# For Parquet manipulation
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.compute as pc

"""
Pre-reqs: 
1. Spin up the Postgres database via `winpty docker-compose up -d` in the current directory
2. If necessary, create the ny_taxi_data server again
"""

# services = ['fhv','green','yellow']
# init_url = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/'
init_url = 'https://d37ci6vzurychx.cloudfront.net/trip-data'


def create_pg_engine(user, password, host, port, database):
    ## Upload CSV to Postgres
    print("Creating the engine...")
    ## Need to convert a DDL statement into something Postgres will understand
    ##   - via create_engine([database_type]://[user]:[password]@[hostname]:[port]/[database], con=[engine])
    ## https://stackoverflow.com/questions/9298296/sqlalchemy-support-of-postgres-schemas/49930672#49930672
    dbschema = 'dev'
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}',
                            connect_args={'options': '-csearch_path={}'.format(dbschema)}
                        )

    return engine


def remove_files():
    print("Removing files...")
    ## https://stackoverflow.com/questions/32834731/how-to-delete-a-file-by-extension-in-python
    dir_name = "./data"
    local_data = os.listdir(dir_name)

    ## Remove the local compressed and uncompressed CSV's
    for item in local_data:
        if item.endswith(".csv.gz"):
            os.remove(os.path.join(dir_name, item))
        elif item.endswith(".csv"):
            os.remove(os.path.join(dir_name, item))

    # ## Remove all other the local files in the "data" directory
    # ## https://stackoverflow.com/questions/48892772/how-to-remove-a-directory-is-os-removedirs-and-os-rmdir-only-used-to-delete-emp
    # shutil.rmtree("./data/")


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

        ## Create file_name to download
        file_name = f'{service}_tripdata_{year}-{month}.parquet'

        ## Create the path to write the eventual file to
        path = Path(f'./data/{file_name}').as_posix()

        ## Make the directory to hold the parquet file if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)

        ## Download zones data
        zones_url = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv'
        zones_csv_name = "./data/taxi_zone_lookup.csv"
        zones_file = Path(zones_csv_name)

        ## If the file is not already downloaded/does not exist, download it
        if not zones_file.is_file():
            print("\nDownloading the taxi zone data...")
            os.system(f"wget {zones_url} -O {zones_csv_name}")  # -O = output to the given file name        

        ## Add in the smaller taxi zones table first before the long loop for the taxi data
        print("\nLoading in zone data...")
        df_zones = pd.read_csv(zones_csv_name)
        df_zones.to_sql(name='zones', con=engine, if_exists="replace")
        print("Loaded in zone data")

        ## Download taxi CSV using `requests`
        print(f'\nDownloading {file_name}...')
        request_url = f"{init_url}/{file_name}"
        r = requests.get(request_url)
        open(file_name, 'wb').write(r.content)
        
        ## Use `pyarrow` to read the table
        print(f'Saving {file_name} to {path}...')
        # df = pd.read_parquet(file_name)
        table = pq.read_table(file_name)

        ## Convert to pandas DataFrame
        ## NOTE: one FHV file has an out-of-bounds timestamp
        ## https://stackoverflow.com/questions/74467923/pandas-read-parquet-error-pyarrow-lib-arrowinvalid-casting-from-timestampus
        if service == 'fhv':
            df = table.filter(
                pc.less_equal(table["dropOff_datetime"], pa.scalar(pd.Timestamp.max))
            ).to_pandas()
        else:
            df = table.to_pandas()        

        ## Add to total number of rows
        print(f'Number of rows: {len(df.index)}')
        total_rows += len(df.index)

        ## Clean the data and fix the data types
        df = clean_data(df, service)

        ## Add data
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

    # web_to_pg('2019', 'green')
    # web_to_pg('2020', 'green')
    web_to_pg('2019', 'yellow')
    web_to_pg('2020', 'yellow')
    # web_to_pg('2019', 'fhv')

    remove_files()


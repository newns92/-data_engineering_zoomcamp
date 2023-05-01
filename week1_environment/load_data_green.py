import pandas as pd
from sqlalchemy import create_engine
import time
import argparse  # for named arguments like user, password, host, port, database, table, file locations, etc.
import os

def main(params):
    # Gather the passed in params
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    database = params.database
    green_taxi_table_name = params.green_taxi_table_name
    green_taxi_url = params.green_taxi_url
    zones_table_name = params.zones_table_name
    zones_url = params.zones_url    


    print('Starting...')
    # # read in 1st 100 rows of dataset
    # df = pd.read_csv('green_tripdata_2021-01.csv', nrows=100)
    # # print(df.head())

    # # Convert meter engaged and meter disengaged columns from text to dates
    # df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
    # df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)

    # # Convert the dataframe into a Data Definition Language (DDL) statement to create the SQL table
    # # ddl = pd.io.sql.get_schema(df, name='green_taxi_data')
    # # print(ddl)

    print("Creating the engine...")
    # need to convert this DDL statement into something Postgres will understand
    #   - via create_engine([database_type]://[user]:[password]@[hostname]:[port]/[database], con=[engine])
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}')

    # # add in the connection to the DDL statement
    # ddl = pd.io.sql.get_schema(df, name='green_taxi_data', con=engine)
    # print(ddl)

    # Download the data
    print("Downloading the taxi data...")
    taxi_csv_name = 'green_tripdata_2021-01.csv'
    os.system(f'wget {green_taxi_url} -O {taxi_csv_name}')  # -O = output to the given file name

    print("Downloading the taxi zone data...")
    zones_csv_name = 'taxi+_zone_lookup.csv'
    os.system(f'wget {zones_url} -O {zones_csv_name}')  # -O = output to the given file name

    # Add in the timezones first before the long loop
    df_zones = pd.read_csv(zones_csv_name)
    df_zones.to_sql(name='zones', con=engine, if_exists='replace')
    print('Loaded in time zone data')

    print('Loading in taxi data...')
    # chunk dataset into smaller sizes to load into the database
    df_iter = pd.read_csv(taxi_csv_name, compression='gzip', iterator=True, chunksize=100000)
    # return the next item in an iterator with next()
    df = next(df_iter) 
    # print(len(df))

    # Convert meter engaged and meter disengaged columns from text to dates
    df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
    df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)

    # get the header/column names
    header = df.head(n=0)
    # print(header)

    # add the column headers to the green_taxi_data table in the database connection, and replace the table if it exists
    header.to_sql(name='green_taxi_data', con=engine, if_exists='replace')

    # add first chunk of data
    start = time.time()
    df.to_sql(name='green_taxi_data', con=engine, if_exists='append')
    end = time.time()
    print('Time to insert first chunk: in %.3f seconds.' % (end - start))

    def load_chunks(df):
        try:
            print("Loading next chunk...")
            start = time.time()

            # get next chunk
            df = next(df_iter)

            # fix datetimes
            df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
            df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)
            
            # add chunk
            df.to_sql(name='green_taxi_data', con=engine, if_exists='append')

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
    # Create a new ArgumentParser object to have text to display before the argument help (description)
    parser = argparse.ArgumentParser(description="Ingest CSV Data to Postgres")
    # Add all of our arguments
    parser.add_argument('--user', help='Username for Postgres')
    parser.add_argument('--password', help='Password for Postgres')
    parser.add_argument('--host', help='Host for Postgres')
    parser.add_argument('--port', help='Port for Postgres')
    parser.add_argument('--database', help='Database name for Postgres')
    parser.add_argument('--green_taxi_table_name', help='Name of table to write the taxi data to')
    parser.add_argument('--green_taxi_url', help='URL of the Taxi CSV file')
    parser.add_argument('--zones_table_name', help='Mame of table to write the taxi zones to')
    parser.add_argument('--zones_url', help='URl of the Taxi zones data')

    # Gather all the args we just made
    args = parser.parse_args()

    # Pass them into main
    main(args)

    '''
    Run in Git Bash with 
    
    URL1="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-01.csv.gz"
    URL2="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv"

    python load_data.py \
    --user=root \
    --password=root \
    --host=localhost \
    --port=5432 \
    --database=ny_taxi \
    --green_taxi_table_name=green_taxi_data \
    --green_taxi_url=${URL1} \
    --zones_table_name=zones \
    --zones_url=${URL2}
    '''
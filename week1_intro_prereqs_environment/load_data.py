import pandas as pd
import os
import shutil
from sqlalchemy import create_engine
import time
import argparse  # for named arguments like user, password, host, port, database, table, file locations, etc.


def remove_files():
    print("Removing files...")
    # https://stackoverflow.com/questions/32834731/how-to-delete-a-file-by-extension-in-python
    dir_name = "./"
    local_data = os.listdir(dir_name)

    # Remove the local CSV's
    for item in local_data:
        if item.endswith(".csv.gz"):
            os.remove(os.path.join(dir_name, item))

    # Remove the local files
    # https://stackoverflow.com/questions/48892772/how-to-remove-a-directory-is-os-removedirs-and-os-rmdir-only-used-to-delete-emp
    shutil.rmtree('./data/')


def main(args):
    print('Starting...')
    print("Gathering the arguments...")
    # Gather the passed-in parameters/arguments
    user = args.user
    password = args.password
    host = args.host
    port = args.port
    database = args.database
    yellow_taxi_table_name = args.yellow_taxi_table_name
    yellow_taxi_url = args.yellow_taxi_url
    # zones_table_name = args.zones_table_name
    # zones_url = args.zones_url

    # Make the directory to hold the file if it doesn't exist
    os.makedirs(os.path.dirname(f'./data/'), exist_ok=True)

    # # Specify the URL to download from
    # yellow_taxi_url = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz'

    # Download the data
    print("Downloading the taxi data...")
    taxi_csv_name = './data/yellow_tripdata_2021-01.csv'
    os.system(f'wget {yellow_taxi_url} -O {taxi_csv_name}')  # -O = output to the given file name

    # # Read in 1st 100 rows of dataset
    # df = pd.read_csv('./data/yellow_tripdata_2021-01.csv', compression='gzip', nrows=100)
    # # print(df.head())

    # # Convert meter engaged and meter disengaged columns from text to dates
    # df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    # df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    # # Convert the dataframe into a Data Definition Language (DDL) statement to CREATE the SQL table schema
    # ddl = pd.io.sql.get_schema(df, name='yellow_taxi_data')
    # print(ddl)

    print("Creating the engine...")
    # Need to convert this DDL statement into something Postgres will understand
    #   - via create_engine([database_type]://[user]:[password]@[hostname]:[port]/[database], con=[engine])
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}')
    # print(engine.connect())

    # # Add in the connection to the DDL statement
    # ddl = pd.io.sql.get_schema(df, name='yellow_taxi_data', con=engine)
    # # print(ddl)

    print('Loading in taxi data in chunks...')
    # Chunk dataset into smaller sizes to load into the database
    df_iter = pd.read_csv(taxi_csv_name, compression='gzip', iterator=True, chunksize=100000)
    # Return the next item in an iterator with next()
    df = next(df_iter) 
    # print(len(df))

    # Convert meter engaged and meter disengaged columns from text to dates
    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)    

    # Get the header/column names
    header = df.head(n=0)
    # print(header)

    # Add the column headers to the yellow_taxi_data table in the database connection, and replace the table if it exists
    header.to_sql(name=yellow_taxi_table_name, con=engine, if_exists='replace')

    # Add first chunk of data
    start = time.time()
    df.to_sql(name=yellow_taxi_table_name, con=engine, if_exists='append')
    end = time.time()
    print('Time to insert first chunk: in %.3f seconds.' % (end - start))

    def load_chunks(df):
        try:
            print("Loading next chunk...")
            start = time.time()

            # Get next chunk
            df = next(df_iter)

            # Fix datetimes
            df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
            df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
            
            # Add chunk
            df.to_sql(name=yellow_taxi_table_name, con=engine, if_exists='append')

            end = time.time()

            print('Inserted another chunk in %.3f seconds.' % (end - start))

        except:
            # Will come to this clause when we throw an error after running out of data chunks
            print('All data chunks loaded.')
            remove_files()
            quit()

    # Insert the rest of the chunks until loop breaks when all data is added
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
    parser.add_argument('--yellow_taxi_table_name', help='Name of table to write the taxi data to')
    parser.add_argument('--yellow_taxi_url', help='URL of the Yellow Taxi CSV file')
    # parser.add_argument('--zones_table_name', help='Name of table to write the taxi zones to')
    # parser.add_argument('--zones_url', help='URL of the Taxi zones data')

    # Gather all the args we just made
    args = parser.parse_args()

    main(args)

    '''
    Run in Bash with 
    
    URL1="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz"
    # URL2="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv"

    python load_data.py \
    --user=root \
    --password=root \
    --host=localhost \
    --port=5432 \
    --database=ny_taxi \
    --yellow_taxi_table_name=yellow_taxi_data \
    --yellow_taxi_url=${URL1}
    '''    

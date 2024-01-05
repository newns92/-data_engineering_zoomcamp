import pandas as pd
import os
import shutil
from sqlalchemy import create_engine
import time

def remove_files():
    print("Removing files")
    # https://stackoverflow.com/questions/32834731/how-to-delete-a-file-by-extension-in-python
    dir_name = "./"
    local_data = os.listdir(dir_name)

    # remove the local CSV's
    for item in local_data:
        if item.endswith(".csv.gz"):
            os.remove(os.path.join(dir_name, item))

    # Remove the local files
    # https://stackoverflow.com/questions/48892772/how-to-remove-a-directory-is-os-removedirs-and-os-rmdir-only-used-to-delete-emp
    shutil.rmtree('./data/')


def main():

    # Make the directory to hold the file if it doesn't exist
    os.makedirs(os.path.dirname(f'./data/'), exist_ok=True)

    print('Starting...')

    # Specify the URL to download from
    yellow_taxi_url = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz'

    # Download the data
    print("Downloading the taxi data...")
    taxi_csv_name = './data/yellow_tripdata_2021-01.csv'
    os.system(f'wget {yellow_taxi_url} -O {taxi_csv_name}')  # -O = output to the given file name

    # # read in 1st 100 rows of dataset
    # df = pd.read_csv('./data/yellow_tripdata_2021-01.csv', compression='gzip', nrows=100)
    # # print(df.head())

    # # Convert meter engaged and meter disengaged columns from text to dates
    # df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    # df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    # # Convert the dataframe into a Data Definition Language (DDL) statement to CREATE the SQL table schema
    # ddl = pd.io.sql.get_schema(df, name='yellow_taxi_data')
    # print(ddl)

    print("Creating the engine...")
    # need to convert this DDL statement into something Postgres will understand
    #   - via create_engine([database_type]://[user]:[password]@[hostname]:[port]/[database], con=[engine])
    engine = create_engine(f'postgresql://root:root@localhost:5432/ny_taxi')
    # print(engine.connect())

    # # add in the connection to the DDL statement
    # ddl = pd.io.sql.get_schema(df, name='yellow_taxi_data', con=engine)
    # # print(ddl)

    print('Loading in taxi data in chunks...')
    # chunk dataset into smaller sizes to load into the database
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
    header.to_sql(name='yellow_taxi_data', con=engine, if_exists='replace')

    # add first chunk of data
    start = time.time()
    df.to_sql(name='yellow_taxi_data', con=engine, if_exists='append')
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
            df.to_sql(name='yellow_taxi_data', con=engine, if_exists='append')

            end = time.time()

            print('Inserted another chunk in %.3f seconds.' % (end - start))

        except:
            # will come to this clause when we throw an error after running out of data chunks
            print('All data chunks loaded.')
            remove_files()
            quit()

    # insert the rest of the chunks until loop breaks when all data is added
    while True:
        if load_chunks(df):
            break
        else:        
            continue


if __name__ == '__main__':
    main()

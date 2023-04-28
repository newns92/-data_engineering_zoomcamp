import pandas as pd
from sqlalchemy import create_engine
import time
import argparse  # for named arguments like user, password, host, port, database, table, file locations, etc.
import os

def load_data(user, password, host, port, database, yellow_taxi_table_name, yellow_taxi_csv_file, zones_table_name, zones_csv_file, execution_date):   

    print('Starting...')
    # # read in 1st 100 rows of dataset
    # df = pd.read_csv('yellow_tripdata_2021-01.csv', nrows=100)
    # # print(df.head())

    # # Convert meter engaged and meter disengaged columns from text to dates
    # df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    # df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    # # Convert the dataframe into a Data Definition Language (DDL) statement to create the SQL table
    # # ddl = pd.io.sql.get_schema(df, name='yellow_taxi_data')
    # # print(ddl)

    print("Creating the engine...")
    # need to convert this DDL statement into something Postgres will understand
    #   - via create_engine([database_type]://[user]:[password]@[hostname]:[port]/[database], con=[engine])
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}')

    # # add in the connection to the DDL statement
    # ddl = pd.io.sql.get_schema(df, name='yellow_taxi_data', con=engine)
    # print(ddl)

    print("Getting the taxi zone data...")
    # Add in the timezones first before the long loop
    df_zones = pd.read_csv(zones_csv_file)
    df_zones.to_sql(name=zones_table_name, con=engine, if_exists='replace')
    print('Loaded in time zone data')

    print("Getting the taxi data...")
    # chunk dataset into smaller sizes to load into the database
    df_iter = pd.read_csv(yellow_taxi_csv_file, iterator=True, chunksize=100000)
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
    header.to_sql(name=yellow_taxi_table_name, con=engine, if_exists='replace')

    # add first chunk of data
    start = time.time()
    df.to_sql(name=yellow_taxi_table_name, con=engine, if_exists='append')
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
            df.to_sql(name=yellow_taxi_table_name, con=engine, if_exists='append')

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

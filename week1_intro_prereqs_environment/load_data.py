import sys
import pandas as pd
# For removing files from a directory
import os
# import shutil
from sqlalchemy import create_engine
import time
# For named arguments like user, password, host, port, database, table, file locations, etc.
import argparse
# For checking if file exists
from pathlib import Path


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


def main(args):
    print("Starting...")
    print("Gathering the arguments...")
    # Gather the passed-in parameters/arguments
    user = args.user
    password = args.password
    host = args.host
    port = args.port
    database = args.database
    yellow_taxi_table_name = args.yellow_taxi_table_name
    yellow_taxi_url = args.yellow_taxi_url
    zones_table_name = args.zones_table_name
    zones_url = args.zones_url

    # Make the directory to hold the file if it doesn't exist
    os.makedirs(os.path.dirname(f"./data/"), exist_ok=True)

    # Download the data via Unix-based GNU command "wget"    
    taxi_csv_name = "./data/yellow_tripdata_2021-01.csv"
    taxi_file = Path(taxi_csv_name)
    
    # If the file is not already downloaded/does not exist, download it
    if not taxi_file.is_file():
        print("Downloading the taxi data...")
        os.system(f"wget {yellow_taxi_url} -O {taxi_csv_name}")  # -O = output to the given file name

    zones_csv_name = "./data/taxi_zone_lookup.csv"
    zones_file = Path(zones_csv_name)

    # If the file is not already downloaded/does not exist, download it
    if not zones_file.is_file():
        print("\nDownloading the taxi zone data...")
        os.system(f"wget {zones_url} -O {zones_csv_name}")  # -O = output to the given file name

    # # TEST: Check for mixed data type columns
    # # https://stackoverflow.com/questions/29376026/find-mixed-types-in-pandas-columns
    # df = pd.read_csv(taxi_csv_name, compression="gzip")
    # for col in df.columns:
    #     # weird = (df[[col]].applymap(type) != df[[col]].iloc[0].apply(type)).any(axis=1)
    #     # if len(df[weird]) > 0:
    #     #     print(col)  # store_and_fwd_flag
    #     unique_types = df[col].apply(type).unique()
    #     if len(unique_types) > 1:
    #         mixed = True
    #         print(col, unique_types, df[col].unique())

    # # TEST: Convert meter engaged and meter disengaged columns from text to dates
    # df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    # df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
    # # print(df.head())
    # # print(df.dtypes)

    print("\nCreating the Postgres engine...")
    # Need to convert this DDL statement into something Postgres will understand using
    #   the sqlalchemy library's "create_engine" function
    # create_engine([database_type]://[user]:[password]@[hostname]:[port]/[database], con=[engine])
    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{database}")
    print(engine.connect())

    # # Convert the dataframe into a Data Definition Language (DDL) statement in order
    # #   to CREATE a SQL table schema on the fly, whilst adding in the connection to the
    # #   Postgres database via the "con" argument to the "get_schema" function
    # ddl = pd.io.sql.get_schema(df, name="yellow_taxi_data", con=engine)
    # print(ddl)

    # Add in the smaller taxi zones table first before the long loop for the taxi data
    print("\nLoading in zone data...")
    df_zones = pd.read_csv(zones_csv_name)
    df_zones.to_sql(name=zones_table_name, con=engine, if_exists="replace")
    print("Loaded in zone data")

    print("\nLoading in taxi data in chunks...")
    # Chunk dataset into smaller sizes to load into the database via the "chunksize" arg
    df_iter = pd.read_csv(taxi_csv_name, compression="gzip", iterator=True, chunksize=100000)
    
    # Return the next item in an iterator object with the "next()" function
    df = next(df_iter)
    # print(len(df))

    # Convert meter engaged and meter disengaged columns from text to dates
    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    # Get the header/column names from the dataset via the 0-indexed row
    header = df.head(n=0)
    # print("Column names:\n", header)

    # Add the column headers to the yellow_taxi_data table in the Postgres 
    #   database connection in order to create the table, and replace the
    #   table if it exists
    header.to_sql(name=yellow_taxi_table_name, con=engine, if_exists="replace")

    ## CAN NOW SEE THE EMPTY TABLE IN pgcli and inspect it via `\d yellow_taxi_data`

    # Add (append) first chunk of data to the table and time how long it takes
    start = time.time()
    df.to_sql(name=yellow_taxi_table_name, con=engine, if_exists="append")
    end = time.time()
    print("Time to insert first chunk: in %.3f seconds." % (end - start))

    # Create function to use when looping through chunks to load
    def load_chunks(df):
        try:
            print("Loading next chunk...")
            start = time.time()

            # Get next 100,000 row chunk
            df = next(df_iter)

            # Check for mixed data type columns
            # https://stackoverflow.com/questions/29376026/find-mixed-types-in-pandas-columns
            mixed = False
            for col in df.columns:
                # weird = (df[[col]].applymap(type) != df[[col]].iloc[0].apply(type)).any(axis=1)
                # if len(df[weird]) > 0:
                #     print(col)  # store_and_fwd_flag
                unique_types = df[col].apply(type).unique()
                if len(unique_types) > 1:
                    mixed = True
                    # print(col, unique_types, df[col].unique())

            # Fix datetimes again
            df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
            df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

            # Fix fields that have NAN values
            # https://pandas.pydata.org/pandas-docs/stable/user_guide/integer_na.html#integer-na
            if mixed:
                print("Fixing column data types...")
                # df.VendorID = pd.array(df.VendorID, dtype=pd.Int64Dtype())
                # df.passenger_count = pd.array(df.passenger_count, dtype=pd.Int64Dtype())
                # df.payment_type = pd.array(df.payment_type, dtype=pd.Int64Dtype())
                # df.RatecodeID = pd.array(df.RatecodeID, dtype=pd.Int64Dtype())
                df.store_and_fwd_flag = pd.array(df.store_and_fwd_flag, dtype=pd.StringDtype())

            # Append current chunk to Postgres table
            df.to_sql(name=yellow_taxi_table_name, con=engine, if_exists="append")

            end = time.time()

            print("Inserted next chunk in %.3f seconds." % (end - start))

        except:
            # Program will come to this clause when it throws an error after
            #   running out of data chunks
            print("All data chunks loaded.")

            # Remove all downloaded data files to free up space on machine
            remove_files()

            # Exit with code of 1 (an error occured)
            # NOTE: quit() is only intended to work in the interactive Python shell
            sys.exit(1)

    # Insert the rest of the chunks until loop breaks when all data is added
    while True:
        if load_chunks(df):
            break
        else:        
            continue


if __name__ == "__main__":
    # Create a new ArgumentParser object to have text to display before the argument help (description)
    parser = argparse.ArgumentParser(description="Ingest CSV Data to Postgres database")
    
    # Add all of our arguments
    parser.add_argument("--user", help="Username for Postgres")
    parser.add_argument("--password", help="Password for Postgres")
    parser.add_argument("--host", help="Host for Postgres")
    parser.add_argument("--port", help="Port for Postgres")
    parser.add_argument("--database", help="Database name for Postgres")
    parser.add_argument("--yellow_taxi_table_name", help="Name of table to write the taxi data to")
    parser.add_argument("--yellow_taxi_url", help="URL of the Yellow Taxi CSV file")
    parser.add_argument("--zones_table_name", help="Name of table to write the taxi zones to")
    parser.add_argument("--zones_url", help="URL of the Taxi zones data")

    # Gather all the args we just made
    args = parser.parse_args()

    # Run the main script function with our gathered args
    main(args)

    """
    Run in Git bash with 
    
    URL1="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz"
    URL2="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv"

    python load_data.py \
    --user=root \
    --password=root \
    --host=localhost \
    --port=5432 \
    --database=ny_taxi \
    --yellow_taxi_table_name=yellow_taxi_data \
    --yellow_taxi_url=${URL1} \
    --zones_table_name=zones \
    --zones_url=${URL2}
    """    

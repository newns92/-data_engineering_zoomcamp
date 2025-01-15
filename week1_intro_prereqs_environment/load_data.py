import pandas as pd
import os
import shutil
from sqlalchemy import create_engine
import time
# For named arguments like user, password, host, port, database, table, file locations, etc.
import argparse


def remove_files():
    print("Removing files...")
    # https://stackoverflow.com/questions/32834731/how-to-delete-a-file-by-extension-in-python
    dir_name = "./"
    local_data = os.listdir(dir_name)

    # Remove the local compressed and uncompressed CSV's
    for item in local_data:
        if item.endswith(".csv.gz"):
            os.remove(os.path.join(dir_name, item))
        elif item.endswith(".csv"):
            os.remove(os.path.join(dir_name, item))

    # Remove all other the local files in the "data" directory
    # https://stackoverflow.com/questions/48892772/how-to-remove-a-directory-is-os-removedirs-and-os-rmdir-only-used-to-delete-emp
    shutil.rmtree("./data/")


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
    # zones_table_name = args.zones_table_name
    # zones_url = args.zones_url

    # Make the directory to hold the file if it doesn't exist
    os.makedirs(os.path.dirname(f"./data/"), exist_ok=True)

    # # Specify the URL to download from
    yellow_taxi_url = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz"

    # Download the data via Unix-based GNU command "wget"
    print("Downloading the taxi data...")
    taxi_csv_name = "./data/yellow_tripdata_2021-01.csv"
    os.system(f"wget {yellow_taxi_url} -O {taxi_csv_name}")  # -O = output to the given file name

    # print("Downloading the taxi zone data...")
    # zones_csv_name = "./data/taxi+_zone_lookup.csv"
    # os.system(f"wget {zones_url} -O {zones_csv_name}")  # -O = output to the given file name  

    # Read in 1st 100 rows of dataset
    df = pd.read_csv("./data/yellow_tripdata_2021-01.csv", compression="gzip", nrows=100)
    print(df.head())
    print(df.dtypes)

    # Convert meter engaged and meter disengaged columns from text to dates
    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
    print(df.head())
    print(df.dtypes)


if __name__ == "__main__":
    # Create a new ArgumentParser object to have text to display before the argument help (description)
    parser = argparse.ArgumentParser(description="Ingest CSV Data to Postgres")
    
    # Add all of our arguments
    parser.add_argument("--user", help="Username for Postgres")
    parser.add_argument("--password", help="Password for Postgres")
    parser.add_argument("--host", help="Host for Postgres")
    parser.add_argument("--port", help="Port for Postgres")
    parser.add_argument("--database", help="Database name for Postgres")
    parser.add_argument("--yellow_taxi_table_name", help="Name of table to write the taxi data to")
    parser.add_argument("--yellow_taxi_url", help="URL of the Yellow Taxi CSV file")
    # parser.add_argument("--zones_table_name", help="Name of table to write the taxi zones to")
    # parser.add_argument("--zones_url", help="URL of the Taxi zones data")

    # Gather all the args we just made
    args = parser.parse_args()

    # Run the main script function with our gathered args
    main(args)

    """
    Run in Bash with 
    
    URL1="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz"
    URL2="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv"

    python load_data.py \
    --user=root \
    --password=root \
    --host=localhost \
    --port=5432 \
    --database=ny_taxi \
    --yellow_taxi_table_name=yellow_taxi_data \
    --yellow_taxi_url=${URL1}
    --zones_table_name=zones \
    --zones_url=${URL2}    
    """    

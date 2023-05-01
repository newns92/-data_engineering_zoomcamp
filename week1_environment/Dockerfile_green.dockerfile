# base image to run from/use -- base it on Python 3.9
FROM python:3.9 

# command to run (Install wget and Python packages)
RUN apt-get install wget
RUN pip install pandas sqlalchemy psycopg2

# specify the working directory of where in the image we work with the file below
WORKDIR /app

# copy pipeline file from current working directory to docker image
COPY load_data_green.py load_data_green.py

# override the entry point
# ENTRYPOINT [ "bash" ]
ENTRYPOINT [ "python", "load_data_green.py" ]


# build the image with `docker build -t taxi_ingest:v001 .` --> taxi_ingest = img name, v001 = tag
# run the image in git bash with with 
# URL1="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-01.csv.gz"
# URL2="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv"

# winpty docker run -it --network=pg-network taxi_ingest:v001     --user=root     --password=root     --host=pgdatabase     --port=5432     --database=ny_taxi     --green_taxi_table_name=green_taxi_data     --green_taxi_url=${URL1}     --zones_table_name=zones     --zones_url=${URL2}

# Kill Docker image with Ctrl+D
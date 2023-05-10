import pyspark
from pyspark.sql import SparkSession
import pandas as pd
from pyspark.sql import types


def process_data(service, year, month, green_schema, yellow_schema, spark_session):
    print(f'Processing data for {service}/{year}/{month}')

    if service == 'green':
        schema = green_schema
    elif service == 'yellow':
        schema = yellow_schema
    
    # IF RAN download_data.sh
    input_path = f'data/raw/{service}/{year}/{month:02d}/'

    # # IF DOWNLOADED PARQUET FILES FROM GCS BUCKET
    # # example file name: green_tripdata_2019-01.parquet
    # input_path = f'data/{service}/{service}_tripdata_{year}-{month:02d}.parquet'

    output_path = f'data/parquet/{service}/{year}/{month:02d}/'

    # df = spark.read \
    #     .option('header', 'true') \
    #     .schema(schema) \
    #     .parquet(input_path)
    print(f'Reading {input_path}')
    df = spark_session.read \
        .option('header', 'true') \
        .schema(schema) \
        .csv(input_path)

    print(f'Partitioning and saving {input_path} to {output_path}')
    df \
        .repartition(4) \
        .write.parquet(output_path)    


def create_parquet_files():
    # create the SparkSession
    print('Creating the SparkSession...')
    spark = SparkSession.builder \
        .master('local[*]') \
        .appName('test') \
        .getOrCreate()

    print('Creating the schemas...')
    # Define the schemas for the Spark DataFrame
    green_schema = types.StructType([
        types.StructField('VendorID', types.IntegerType(), True),
        types.StructField('lpep_pickup_datetime', types.TimestampType(), True),
        types.StructField('lpep_dropoff_datetime', types.TimestampType(), True),
        types.StructField('store_and_fwd_flag', types.StringType(), True),
        types.StructField('RatecodeID', types.IntegerType(), True),
        types.StructField('PULocationID', types.IntegerType(), True),
        types.StructField('DOLocationID', types.IntegerType(), True),
        types.StructField('passenger_count', types.IntegerType(), True),
        types.StructField('trip_distance', types.DoubleType(), True),
        types.StructField('fare_amount', types.DoubleType(), True),
        types.StructField('extra', types.DoubleType(), True),
        types.StructField('mta_tax', types.DoubleType(), True),
        types.StructField('tip_amount', types.DoubleType(), True),
        types.StructField('tolls_amount', types.DoubleType(), True),
        types.StructField('ehail_fee', types.DoubleType(), True),
        types.StructField('improvement_surcharge', types.DoubleType(), True),
        types.StructField('total_amount', types.DoubleType(), True),
        types.StructField('payment_type', types.IntegerType(), True),
        types.StructField('trip_type', types.IntegerType(), True),
        types.StructField('congestion_surcharge', types.DoubleType(), True)
    ])

    yellow_schema = types.StructType([
        types.StructField('VendorID', types.IntegerType(), True),
        types.StructField('tpep_pickup_datetime', types.TimestampType(), True),
        types.StructField('tpep_dropoff_datetime', types.TimestampType(), True),
        types.StructField('passenger_count', types.IntegerType(), True),
        types.StructField('trip_distance', types.DoubleType(), True),
        types.StructField('RatecodeID', types.IntegerType(), True),
        types.StructField('store_and_fwd_flag', types.StringType(), True),
        types.StructField('PULocationID', types.IntegerType(), True),
        types.StructField('DOLocationID', types.IntegerType(), True),
        types.StructField('payment_type', types.IntegerType(), True),
        types.StructField('fare_amount', types.DoubleType(), True),
        types.StructField('extra', types.DoubleType(), True),
        types.StructField('mta_tax', types.DoubleType(), True),
        types.StructField('tip_amount', types.DoubleType(), True),
        types.StructField('tolls_amount', types.DoubleType(), True),
        types.StructField('improvement_surcharge', types.DoubleType(), True),
        types.StructField('total_amount', types.DoubleType(), True),
        types.StructField('congestion_surcharge', types.DoubleType(), True)
    ])

    # Loop through files, partition them, and save as parquet files
    services = ['yellow', 'green']
    years = [2020, 2021]

    for service in services:
        for year in years:            
            if year == 2020:  # all 12 months
                for month in range(1, 13):
                    process_data(service, year, month, 
                                 green_schema, yellow_schema, spark_session=spark)                        
            if year == 2021:  # no august data
                for month in range(1, 8):
                    process_data(service, year, month, 
                                 green_schema, yellow_schema, spark_session=spark)                    


if __name__ == '__main__':
    # print(pyspark.__file__)
    create_parquet_files()
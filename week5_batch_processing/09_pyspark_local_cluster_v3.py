#!/usr/bin/env python
# coding: utf-8
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import argparse

# get the CLI args
parser = argparse.ArgumentParser()

parser.add_argument('--input_green', required=True)
parser.add_argument('--input_yellow', required=True)
parser.add_argument('--output', required=True)

args = parser.parse_args()

input_green = args.input_green
input_yellow = args.input_yellow
output = args.output

# start a SparkSession
spark = SparkSession.builder \
    .appName('test') \
    .getOrCreate()

# # run something before making a worker
# df_green = spark.read.parquet('data/parquet/green/*/*')

# read in the green data and clean it AFTER making a worker
df_green = spark.read.parquet(input_green)

# # check that we pulled in the data
# df_green.count()

# rename some columns via PySpark function to match up with yellow (will also be renamed)
df_green = df_green \
    .withColumnRenamed('lpep_pickup_datetime', 'pickup_datetime') \
    .withColumnRenamed('lpep_dropoff_datetime', 'dropoff_datetime')

# read in the yellow data and clean it AFTER making a worker
df_yellow = spark.read.parquet(input_yellow)

# rename some columns via PySpark function to match up with yellow (will also be renamed)
df_yellow = df_yellow \
    .withColumnRenamed('tpep_pickup_datetime', 'pickup_datetime') \
    .withColumnRenamed('tpep_dropoff_datetime', 'dropoff_datetime')    

common_colums = ['VendorID',
     'pickup_datetime',
     'dropoff_datetime',
     'store_and_fwd_flag',
     'RatecodeID',
     'PULocationID',
     'DOLocationID',
     'passenger_count',
     'trip_distance',
     'fare_amount',
     'extra',
     'mta_tax',
     'tip_amount',
     'tolls_amount',
     'improvement_surcharge',
     'total_amount',
     'payment_type',
     'congestion_surcharge'
]

# get all columns from green that are a part of the common columns
# and then add a new service_type column with value of 'green'
df_green_sel = df_green \
    .select(common_colums) \
    .withColumn('service_type', F.lit('green'))

# get all columns from yellow that are a part of the common columns
# and then add a new service_type column with value of 'yellow'
df_yellow_sel = df_yellow \
    .select(common_colums) \
    .withColumn('service_type', F.lit('yellow'))

# union the datasets together
df_trips_data = df_green_sel.unionAll(df_yellow_sel)

# tell Spark that our DataFrame is a table
# df_trips_data.registerTempTable('trips_data')  # deprecated
df_trips_data.createOrReplaceTempView('trips_data')

# save a SQL result to a NEW DataFrame, similar to our dbt models
# Get all revenue for each pickup zone/revenue location, for each service type, for each month
df_result = spark.sql("""
SELECT 
    -- Reveneue grouping 
    PULocationID AS revenue_zone,
    date_trunc('month', pickup_datetime) AS revenue_month, 
    service_type, 

    -- Revenue calculation 
    SUM(fare_amount) AS revenue_monthly_fare,
    SUM(extra) AS revenue_monthly_extra,
    SUM(mta_tax) AS revenue_monthly_mta_tax,
    SUM(tip_amount) AS revenue_monthly_tip_amount,
    SUM(tolls_amount) AS revenue_monthly_tolls_amount,
    SUM(improvement_surcharge) AS revenue_monthly_improvement_surcharge,
    SUM(total_amount) AS revenue_monthly_total_amount,
    SUM(congestion_surcharge) AS revenue_monthly_congestion_surcharge,

    -- Additional calculations
    AVG(passenger_count) AS avg_montly_passenger_count,
    AVG(trip_distance) AS avg_montly_trip_distance
FROM
    trips_data
GROUP BY
    1, 2, 3
""")

# save and use just 1 partition via .coalesce()
df_result.coalesce(1) \
    .write.parquet(output, mode='overwrite')
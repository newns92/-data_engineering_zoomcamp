#!/usr/bin/env python
# coding: utf-8

import pyspark
from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def create_report():
    # create the SparkSession locally with as many CPUs cores as possible
    print('Creating the SparkSession...')
    spark = SparkSession.builder \
        .master("local[*]") \
        .appName('test') \
        .getOrCreate()

    # Can open the Spark UI at http://localhost:4040/

    print('Loading in the data...')
    # load in all green data into a Spark DataFrame
    df_green = spark.read.parquet('./data/parquet/green/*/*')

    # rename some columns via PySpark function to match up with yellow (will also be renamed)
    df_green = df_green \
        .withColumnRenamed('lpep_pickup_datetime', 'pickup_datetime') \
        .withColumnRenamed('lpep_dropoff_datetime', 'dropoff_datetime')
    # print(df_green.head())

    # load in all yellow data into a Spark DataFrame
    df_yellow = spark.read.parquet('./data/parquet/yellow/*/*')

    # rename some columns via PySpark function to match up with green
    df_yellow = df_yellow \
        .withColumnRenamed('tpep_pickup_datetime', 'pickup_datetime') \
        .withColumnRenamed('tpep_dropoff_datetime', 'dropoff_datetime')
    # print(df_yellow.head())

    # We want to eventually combine these two datasets into one large dataset
    # print(df_green.count())
    # print(df_yellow.count())

    print('Combining the data...')
    # GET ALL COMMON COLUMNS BETWEEN THESE TWO DATASETS
    common_columns = []

    # get the set of unique columns from the yellow data
    yellow_columns = set(df_yellow.columns)
    # print(yellow_columns)

    # get all columns from the yellow dataset that are also in the green dataset
    #   and preserve order of cols
    for col in df_green.columns:
        if col in yellow_columns:
            common_columns.append(col)
    # print(common_columns)

    # `.withColumn()` is a transformation function of a Spark DataFrame which is used to change the value, 
    #   convert the datatype of an existing column, create a new column, and many more
    # - https://sparkbyexamples.com/pyspark/pyspark-withcolumn/
    # 
    # `pyspark.sql.functions.lit` is used to add a new column to DataFrame by assigning a literal or constant value
    # - https://sparkbyexamples.com/pyspark/pyspark-lit-add-literal-constant/

    # get all columns from green that are a part of the common columns
    #   and then add a new service_type column with value of 'green'
    df_green_sel = df_green \
        .select(common_columns) \
        .withColumn('service_type', F.lit('green'))

    # get all columns from yellow that are a part of the common columns
    #   and then add a new service_type column with value of 'yellow'
    df_yellow_sel = df_yellow \
        .select(common_columns) \
        .withColumn('service_type', F.lit('yellow'))

    # union the datasets together
    df_trips_data = df_green_sel.unionAll(df_yellow_sel)

    # # inspect the data
    # df_trips_data.groupBy('service_type').count().show()

    # # view the columns
    # df_trips_data.columns

    # In order to use Spark SQL, we have to tell Spark that our DataFrame is a table
    # df_trips_data.registerTempTable('trips_data')  # deprecated
    print("Doing Spark SQL...")
    df_trips_data.createOrReplaceTempView('trips_data')

    # # do some Spark SQL on the data
    # spark.sql("""
    # SELECT
    #     service_type,
    #     count(1)
    # FROM
    #     trips_data
    # GROUP BY 
    #     service_type
    # """).show()

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

    # df_result.show(5)
    # df_result.head(5)

    # `.coalesce(*cols)` returns the first column that is not null and is *used to decrease the number 
    #   of partitions in an efficient way***
    #       - use just 1 partition via .coalesce()
    # Can go to the Spark UI after running the next cell to see jobs/tasks running
    df_result.coalesce(1) \
        .write.parquet('data/report/revenue/', mode='overwrite')

if __name__ == '__main__':
    create_report()
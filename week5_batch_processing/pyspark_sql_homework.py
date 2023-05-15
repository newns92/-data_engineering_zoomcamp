import pyspark
from pyspark.sql import SparkSession
from pyspark.sql import types


def do_pyspark_sql():
    # instantiate a Spark session, an object that we use to interact with Spark
    spark = SparkSession.builder \
        .master("local[*]") \
        .appName('test') \
        .getOrCreate()

    # load in all data into a Spark DataFrame
    df_fhvhv = spark.read.parquet('./data/parquet/fhvhv/*/*')

    # tell Spark that our DataFrame is a table
    # df_trips_data.registerTempTable('trips_data')  # deprecated
    df_fhvhv.createOrReplaceTempView('fhvhv_trips_data')    
    
    # # Check the format of "day" for pickup_datetime column
    # spark.sql("""
    # SELECT
    #     date_trunc('day', pickup_datetime)
    # FROM
    #     fhvhv_trips_data
    # LIMIT 10
    # """).show()

    # get count of trips on June 15 via Spark SQL
    spark.sql("""
    SELECT
        COUNT(*) AS number_of_trips
    FROM
        fhvhv_trips_data
    WHERE
        date_trunc('day', pickup_datetime) = '2021-06-15 00:00:00'
    """).show()

    # calculate the duration for each trip and see the longest trip in hours via Spark SQL
    # DOES NOT WORK: date_trunc('hour', dropoff_datetime) - date_trunc('hour', pickup_datetime)
    # https://kontext.tech/article/830/spark-date-difference-in-seconds-minutes-hours
    spark.sql("""
    SELECT        
        unix_timestamp(dropoff_datetime) - unix_timestamp(pickup_datetime) AS trip_duration_seconds,
        (unix_timestamp(dropoff_datetime) - unix_timestamp(pickup_datetime))/60 AS trip_duration_minutes,
        ((unix_timestamp(dropoff_datetime) - unix_timestamp(pickup_datetime))/60)/60 AS trip_duration_hours
    FROM
        fhvhv_trips_data
    ORDER BY
        trip_duration_hours DESC
    LIMIT 5
    """).show()

    # bring in zone data
    df_zones = spark.read.parquet('./zones/')

    # do a new JOIN with our FHVHV data along with the zone data
    df_join = df_fhvhv.join(df_zones, on=df_fhvhv.PULocationID == df_zones.LocationID)

    # tell Spark that our DataFrame is a table/view
    # df_trips_data.registerTempTable('trips_data')  # deprecated
    df_join.createOrReplaceTempView('fhvhv_trips_data_zones')

    # find the name of the most frequent pickup location zone
    spark.sql("""
    SELECT        
        Zone AS pickup_zone,
        COUNT(*) AS number_of_trips
    FROM
        fhvhv_trips_data_zones
    GROUP BY
        Zone
    ORDER BY
        number_of_trips DESC
    LIMIT 5
    """).show()    


if __name__ == '__main__':
    do_pyspark_sql()
# Intro to Spark and Pyspark

## Reading Data with Spark
- We are using FHV data from January 2021, since it is high volume, and Spark is for high-volume data
- First, we start a **Spark Session** and then load in the data
    ```Python
        import pyspark
        from pyspark.sql import SparkSession

        # Instantiate a Spark session, an object that we use to interact with Spark
        spark = SparkSession.builder \
            .master("local[*]") \
            .appName('test') \
            .getOrCreate()

        # Read in the zone data
        df_zone = spark.read \
            .option("header", "true") \
            .csv('./data/taxi+_zone_lookup.csv')

        # Read in the high-volume FHV trip data with specified headers
        df_fhv = spark.read \
            .option("header", "true") \
            .option("inferSchema", True) \
            .csv('./data/fhvhv_tripdata_2021-01.csv')
    ```
- Note that every time we execute a job, we can see it being added in the Spark UI at http://localhost:4040/

## After Loading in Data with a Schema
- We currently have a **Spark Cluster**, inside of which are a bunch of **executors** (machines doing computational work)
- Let's say we have a bunch of files contained in our GCS Bucket
    - Each of these files will be pulled to an executor
        - If we have more executors than files, Spark waits until one executor is done with a file, and then that executor will grab one of the leftover files
    - Say there's only 1 large file and 6 executors
        - One executor will grab this file, and the other 5 will be idle
        - This is not efficient
        - We'd rather have a bunch of smaller files
    - We can break up the large file in Spark via **partitions**

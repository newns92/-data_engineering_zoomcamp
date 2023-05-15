import pyspark
from pyspark.sql import SparkSession
from pyspark.sql import types


def create_parquets():
    # instantiate a Spark session, an object that we use to interact with Spark
    spark = SparkSession.builder \
        .master("local[*]") \
        .appName('test') \
        .getOrCreate()

    # # read the FHVHV 2021-06 data via fhv_tripdata_2021-01.csv.gz 
    # df_fhvhv = spark.read \
    #     .option("header", "true") \
    #     .option("inferSchema", True) \
    #     .csv('./data/raw/fhvhv/2021/06/fhvhv_tripdata_2021_06.csv.gz')
    
    # # print(df_fhvhv.head(5))

    # specify expected schema, making sure the columsn can be nullable (that final "True" Boolean value)
    schema = types.StructType([
        # types.StructField('hvfhs_license_num', types.StringType(), True),
        types.StructField('dispatching_base_num', types.StringType(), True),
        types.StructField('pickup_datetime', types.TimestampType(), True),
        types.StructField('dropoff_datetime', types.TimestampType(), True),
        types.StructField('PULocationID', types.IntegerType(), True),
        types.StructField('DOLocationID', types.IntegerType(), True),
        types.StructField('SR_Flag', types.StringType(), True),
        types.StructField('Affiliated_base_num', types.StringType(), True)
    ])

    # read in the dataframe with the expected schema
    df_fhvhv = spark.read \
        .option("header", "true") \
        .schema(schema) \
        .csv('./data/raw/fhvhv/2021/06/fhvhv_tripdata_2021_06.csv.gz')
    
    # convert the large "file" into 12 partitions
    df_fhvhv = df_fhvhv.repartition(12)

    # save the dataframe (via its partitions)
    df_fhvhv.write.parquet('./data/parquet/fhvhv/2021/06/')


if __name__ == '__main__':
    create_parquets()
# pip install -U "dlt[duckdb]"
# pip install cchardet
import dlt
from dlt.sources.helpers.rest_client import RESTClient
from dlt.sources.helpers.rest_client.paginators import PageNumberPaginator


# your code is here
## 1) Use the `@dlt.resource` decorator to define the API source.
## Define the API resource for NYC taxi data
@dlt.resource(name="rides")   # <--- The name of the resource (will be used as the table name)

def ny_taxi():
    client = RESTClient(
        base_url="https://us-central1-dlthub-analytics.cloudfunctions.net",
        ## 2) Implement automatic pagination using dlt's built-in REST client.
        ## Define pagination strategy - page-based pagination
        paginator=PageNumberPaginator(   # <--- Pages are numbered (1, 2, 3, ...)
            base_page=1,   # <--- Start from page 1
            total_path=None    # <--- No total count of pages provided by API, pagination should stop when a page contains no result items
        )
    )
    
    for page in client.paginate("data_engineering_zoomcamp_api"):    # <--- API endpoint for retrieving taxi ride data
        yield page   # <--- yield data to manage memory

## Load the extracted data into DuckDB for querying.
## Provided code
pipeline = dlt.pipeline(
    pipeline_name="ny_taxi_pipeline",
    destination="duckdb",
    dataset_name="ny_taxi_data"
)


## Load the data into DuckDB to test
load_info = pipeline.run(ny_taxi)
print(f'LOAD INFO:\n {load_info}')


## Start a connection to your database using native `duckdb` connection 
## Look what tables were generated:
import duckdb
# from google.colab import data_table
# data_table.enable_dataframe_formatter()

## A database '<pipeline_name>.duckdb' was created in working directory so just connect to it

## Connect to the DuckDB database
print('Connect to the DuckDB database...')
conn = duckdb.connect(f"{pipeline.pipeline_name}.duckdb")

## Set search path to the dataset
conn.sql(f"SET search_path = '{pipeline.dataset_name}'")

## Describe the dataset
conn.sql("DESCRIBE").df()


## Question 3
df = pipeline.dataset(dataset_type="default").rides.df()
print(df)


## Question 4
with pipeline.sql_client() as client:
    res = client.execute_sql(
            """
            SELECT
            AVG(date_diff('minute', trip_pickup_date_time, trip_dropoff_date_time))
            FROM rides;
            """
        )
    # Prints column values of the first row
    print(res)
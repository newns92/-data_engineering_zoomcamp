import pyarrow as pa
import pyarrow.parquet as pq
import os # for working with environment variables

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


# SET an envrionment variable to be our JSON credentials file that we mounted
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = ''  # REMOVED FROM HOMEWORK FOR SECURITY

# Define the GCS Bucket name
bucket_name =  ''  # REMOVED FROM HOMEWORK FOR SECURITY

# Define the GCP project ID
project_id =  ''  # REMOVED FROM HOMEWORK FOR SECURITY

# Define the table name that will become the directory for the partitioned files in the GCS Bucket
table_name = 'green_taxi'

# Create a root path for the Bucket destination
root_path = f'{bucket_name}/{table_name}'


@data_exporter
def export_data(data, *args, **kwargs):
    """
    Exports data to some source.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Output (optional):
        Optionally return any object and it'll be logged and
        displayed when inspecting the block run.
    """
    # Specify your data exporting logic here

    # Define/Create the column to partition on
    data['lpep_pickup_date'] = data['lpep_pickup_datetime'].dt.date

    # Create the PyArrow table from our dataset
    pa_table = pa.Table.from_pandas(data)

    # Find/Define the GCS file system (.fs) object via our environment variable(s)
    gcs_fs = pa.fs.GcsFileSystem()

    # Write the PyArrow table to the dataset with partitions
    pq.write_to_dataset(
        table = pa_table, # must be a PyArrow table
        root_path = root_path,
        partition_cols = ['lpep_pickup_date'], # must be a list
        filesystem = gcs_fs
    )

    # dataset = pq.ParquetDataset(root_path, filesystem = gcs_fs)
    # print(dataset)

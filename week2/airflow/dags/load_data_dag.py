import os

from datetime import datetime

from airflow import DAG

from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from load_data_csv import load_data


AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")


PG_HOST = os.getenv('PG_HOST')
PG_USER = os.getenv('PG_USER')
PG_PASSWORD = os.getenv('PG_PASSWORD')
PG_PORT = os.getenv('PG_PORT')
PG_DATABASE = os.getenv('PG_DATABASE')


local_workflow = DAG(
    "load_data_dag",
    schedule_interval="0 6 2 * *",
    start_date=datetime(2021, 1, 1)
)


TAXI_URL_PREFIX = 'https://s3.amazonaws.com/nyc-tlc/trip+data' 
TAXI_URL_TEMPLATE = TAXI_URL_PREFIX + '/yellow_tripdata_{{ execution_date.strftime(\'%Y-%m\') }}.csv'
TAXI_OUTPUT_FILE_TEMPLATE = AIRFLOW_HOME + '/output_taxi_{{ execution_date.strftime(\'%Y-%m\') }}.csv'
TAXI_TABLE_NAME_TEMPLATE = 'yellow_taxi_{{ execution_date.strftime(\'%Y_%m\') }}'

ZONES_URL_PREFIX = 'https://s3.amazonaws.com/nyc-tlc/misc' 
ZONES_URL_TEMPLATE = ZONES_URL_PREFIX + '/taxi+_zone_lookup.csv'
ZONES_OUTPUT_FILE_TEMPLATE = AIRFLOW_HOME + '/output_zones_{{ execution_date.strftime(\'%Y-%m\') }}.csv'
ZONES_TABLE_NAME_TEMPLATE = 'zones_{{ execution_date.strftime(\'%Y_%m\') }}'

with local_workflow:
    wget_task = BashOperator(
        task_id='wget',
        bash_command=f'curl -sSL {ZONES_URL_TEMPLATE} > {ZONES_OUTPUT_FILE_TEMPLATE}'
    )

    ingest_task = PythonOperator(
        task_id="ingest",
        python_callable=load_data,
        op_kwargs=dict(
            user=PG_USER,
            password=PG_PASSWORD,
            host=PG_HOST,
            port=PG_PORT,
            db=PG_DATABASE,
            yellow_taxi_table_name=TAXI_TABLE_NAME_TEMPLATE,
            yellow_taxi_csv_file=TAXI_OUTPUT_FILE_TEMPLATE,
            zones_table_name=ZONES_TABLE_NAME_TEMPLATE,
            zones_csv_file=ZONES_OUTPUT_FILE_TEMPLATE            
        ),
    )

    wget_task >> ingest_task
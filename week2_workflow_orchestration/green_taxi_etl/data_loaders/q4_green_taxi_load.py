import io
import pandas as pd
import requests
if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@data_loader
def load_data_from_api(*args, **kwargs):
    """
    Template for loading data from API
    """
    # Create an empty DataFrame to append to later
    result = pd.DataFrame(columns = ['VendorID',
                        'lpep_pickup_datetime',
                        'lpep_dropoff_datetime',
                        'passenger_count',
                        'trip_distance',
                        'RatecodeID',
                        'store_and_fwd_flag',
                        'PULocationID',
                        'DOLocationID',
                        'payment_type',
                        'fare_amount',
                        'extra',
                        'mta_tax',
                        'tip_amount',
                        'tolls_amount',
                        'improvement_surcharge',
                        'total_amount',
                        'congestion_surcharge'])
    # print(result)

    # Set the final quarter (Q4) months in a list
    months = ['10', '11', '12']

    # Get the data for the Q4 months and append to a final dataframe
    for month in months:
        # print(month)
        url = f'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2020-{month}.csv.gz'
        print('Downloading from:', url)
        # response = requests.get(url)

        # return pd.read_csv(io.StringIO(response.text), sep=',')

        # Map the data types
        taxi_dtypes = {
                        'VendorID': pd.Int64Dtype(),
                        'passenger_count': pd.Int64Dtype(),
                        'trip_distance': float,
                        'RatecodeID':pd.Int64Dtype(),
                        'store_and_fwd_flag':str,
                        'PULocationID':pd.Int64Dtype(),
                        'DOLocationID':pd.Int64Dtype(),
                        'payment_type': pd.Int64Dtype(),
                        'fare_amount': float,
                        'extra':float,
                        'mta_tax':float,
                        'tip_amount':float,
                        'tolls_amount':float,
                        'improvement_surcharge':float,
                        'total_amount':float,
                        'congestion_surcharge':float
                    }
        
        # Parse the datetime columns
        parse_dates = ['lpep_pickup_datetime', 'lpep_dropoff_datetime']

        # Read the compressed CSV and return it
        df = pd.read_csv(url, sep=',', compression='gzip', dtype=taxi_dtypes, parse_dates=parse_dates)

        # Concatenate the current dataframe to the final dataframe
        result = pd.concat([result, df])

    # print(result.head())
    # print(result.tail())

    # print(len(result['lpep_pickup_datetime'].dt.date.unique()))
    # print(result['lpep_pickup_datetime'].sort_values().dt.date.unique())

    # print(result.sort_values(by=['lpep_pickup_datetime']))

    return result


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'

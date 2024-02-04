import pandas as pd

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@transformer
def transform(data, *args, **kwargs):
    """
    Template code for a transformer block.

    Add more parameters to this function if this block has multiple parent blocks.
    There should be one parameter for each output variable from each parent block.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    # Specify your transformation logic here
    print("Initial shape of the data:", data.shape)
    print('Initial number of rows =', len(data.index))

    print('Preprocessing: Number of rows with 0 passengers =', data['passenger_count'].isin([0, pd.NA]).sum())
    # data = data[data['passenger_count'] > 0]
    # print('Preprocessing: Number of rows after removing 0 passengers =', len(data))

    print('Preprocessing: Number of rows with 0 miles of trip distance =', data['trip_distance'].isin([0, pd.NA]).sum())

    print('Total number of rows removed =', data['passenger_count'].isin([0, pd.NA]).sum() + data['trip_distance'].isin([0, pd.NA]).sum())

    # Remove rows where the passenger count is equal to 0 OR the trip distance is equal to zero.
    # i.e., Return only the rows with passengers OR a valid mile amount for trip data (> 0 and NOT NA)
    # https://stackoverflow.com/questions/29219011/selecting-rows-based-on-multiple-column-values-in-pandas-dataframe
    # data = data[((data['passenger_count'] > 0) | (data['trip_distance'] > 0))].dropna(subset=['passenger_count', 'trip_distance'])
    data = data[data['passenger_count'] > 0]
    data = data[data['trip_distance'] > 0]
    print('New number of rows =', len(data.index))

    # Create a new column `lpep_pickup_date` by converting `lpep_pickup_datetime` to a date
    data['lpep_pickup_date'] = data['lpep_pickup_datetime'].dt.date

    # What are the existing values of `VendorID` in the dataset?
    print('Existing values of "VendorID" in the dataset:', data['VendorID'].unique())

    # Rename columns in Camel Case to Snake Case, e.g. `VendorID` to `vendor_id`
    data = data.rename(columns={"VendorID": "vendor_id",
                            "RatecodeID": "ratecode_id",
                            "PULocationID": "pu_location_id",
                            "DOLocationID": "do_location_id"
                        }
                )
    # print(data.head())

    return data


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    # print(output)

    assert output is not None, 'The output is undefined'

    assert 'vendor_id' in output.columns, 'vendor_id is not a column in the DataFrame'

    assert (output['passenger_count'] > 0).all(), 'There is a 0 in the passenger_count column'

    assert (output['trip_distance'] > 0).all(), 'There is a 0 in the trip_distance column'

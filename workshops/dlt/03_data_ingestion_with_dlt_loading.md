# Data Ingestion with dlt

## Incremental loading
- **Incremental loading** means we update (i.e., load into) our datasets with *new* data, as opposed to making a full copy of a source's data all over again and replacing the old version
- *By loading incrementally, our pipelines run faster and cheaper*
- Incremental loading goes hand in hand with *incremental extraction* and **state** (2 concepts which we will not delve into during this workshop)
    - **State** is information that keeps track of *what* was loaded and to know *what else remains to be loaded*
        - dlt stores the state at the destination in a separate table
    - **Incremental extraction** refers to only requesting the increment of data that we need, and nothing more
        - This is tightly connected to the state to determine the exact chunk that needs to be extracted and loaded
- You can learn more about incremental extraction and state by reading the dlt docs on how to do it:
    - https://dlthub.com/docs/general-usage/state
    - https://dlthub.com/docs/api_reference/extract/incremental/__init__
- dlt currently supports 2 ways of loading incrementally:
    1. **Append**: 
        - We can use this for immutable or stateless events (data that doesn't change), such as taxi rides
            - For example, every day that there are new rides, we could load the new ones only instead of the entire history
        - We could also use this to load *different versions* of stateful data
            - Such as creating a **slowly changing dimension (SCD)** table for auditing changes
                - For example: If we load a list of cars and their colors every day, and one day one car changes color, we need *both* sets of data to be able to discern that a change happened
    2. **Merge**: 
        - We can use this to update data that changes
            - For example, a taxi ride could have a payment status, which is originally "booked", but could later be changed into "paid", "rejected" or "cancelled"
- Here is how you can think about which method to use:
    - Is it stateful data?
        - NO
            - Use a write disposition of "append"
        - YES
            - Can you request it incrementally?
                - NO
                    - Use a write disposition of "replace"
                - YES
                    - Use a write disposition of "Merge (upsert)"
    - NOTE: If you want to keep track of when changes occur in stateful data (slowly changing dimension), then you will need to *append* the data
- **Merge Example**:
    - In our previously-mentioned example, payment status can change from "booked" to "cancelled"
    - The **merge** operation *replaces an old record with a new one based on a **key***
        - The key could consist of multiple fields, or a single unique ID
            - We will use record hash that we created for simplicity
            - If you do *NOT* have a unique key, you could *create* one deterministically out of several fields, say by concatenating the data and hashing it
    - A merge operation *replaces* rows, it does *NOT* update them
        - *If you want to update only parts of a row, you would have to load the new data by appending it and doing a custom transformation to combine the old and new data*
    - In this example, the score of the 2 drivers got lowered and we need to update the values
        - We do it by using **merge-write** disposition, replacing the records identified by `record_hash` present in the new data
            ```Python
                data = [
                    {
                        "vendor_name": "VTS",
                        "record_hash": "b00361a396177a9cb410ff61f20015ad",
                        "time": {
                            "pickup": "2009-06-14 23:23:00",
                            "dropoff": "2009-06-14 23:48:00"
                        },
                        "Trip_Distance": 17.52,
                        "coordinates": {
                            "start": {
                                "lon": -73.787442,
                                "lat": 40.641525
                            },
                            "end": {
                                "lon": -73.980072,
                                "lat": 40.742963
                            }
                        },
                        "Rate_Code": None,
                        "store_and_forward": None,
                        "Payment": {
                            "type": "Credit",
                            "amt": 20.5,
                            "surcharge": 0,
                            "mta_tax": None,
                            "tip": 9,
                            "tolls": 4.15,
                            "status": "cancelled"
                        },
                        "Passenger_Count": 2,
                        "passengers": [
                            {"name": "John", "rating": 4.4},
                            {"name": "Jack", "rating": 3.6}
                        ],
                        "Stops": [
                            {"lon": -73.6, "lat": 40.6},
                            {"lon": -73.5, "lat": 40.5}
                        ]
                    },
                ]

                # define the connection to load to. 
                # We now use duckdb, but you can switch to BigQuery later
                pipeline = dlt.pipeline(destination='duckdb', dataset_name='taxi_rides')

                # run the pipeline with default settings, and capture the outcome
                info = pipeline.run(data, 
                                    table_name="users", 
                                    write_disposition="merge", 
                                    merge_key="record_hash")

                # show the outcome
                print(info)
            ```

## What's Next?
- You could change the destination to Parquet and a local file system, or to a storage bucket
- You could also change the destination to BigQuery
    - For destination & credential setup documentation, see: 
        - https://dlthub.com/docs/dlt-ecosystem/destinations/
        - https://dlthub.com/docs/walkthroughs/add_credentials
- You could also use a **decorator** to convert the generator into a customised dlt resource:
    - https://dlthub.com/docs/general-usage/resource
- You can deep dive into building more complex dlt pipelines by following the guides:
    - https://dlthub.com/docs/walkthroughs
    - https://dlthub.com/docs/build-a-pipeline-tutorial
- You can also join the [dlt Slack community](https://dlthub.com/community) and engage there

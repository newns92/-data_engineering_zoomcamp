# Data Ingestion with dlt

## Normalizing Data
- You often hear that data people spend most of their time "cleaning" data, but what does this mean? 
- Let's look granularly into what people consider data cleaning
    - Usually we have 2 parts: 
        - Normalizing data *without changing its meaning*
        - Filtering data for a use case, *which changes its meaning*
- Part of what we often call "data cleaning" is just **metadata** work:
    - Add **types** (`string` to `number`, `string` to `timestamp`, etc.
    - **Rename** columns
        - In this activity, we ensure column names follow a supported standard downstream (such as no strange characters in the names)
    - **Flatten** nested dictionaries
        - This brings nested dictionary values into the top dictionary row
    - **Unnest** lists or arrays into child tables
        - Arrays or lists *cannot* be flattened into their parent record, so if we want flat data we need to break them out into separate tables
- We will look at a practical example next, as these concepts can be difficult to visualise from text

### **Why Prep Data?**
- If working with JSON, we do not easily know what is inside of a JSON document due to lack of a schema
- Types are *NOT* enforced between rows of JSON
    - We could have one record where age is `25`, and another where age is `twenty five`, and still *another* where it's `25.00`
- Or in some systems, you might have a *dictionary* for a single record, but a *list of dicttionaries* for *multiple* records
    - This could easily lead to applications downstream breaking
- We cannot just use JSON data in a simple manner
    - For example, we would need to convert strings to time types if we want to do a daily aggregation
- Reading JSON loads more data into memory, as the whole document is scanned
    - While in Parquet or in databases, we can scan a single column of a document
    - This whole-document scanning causes high costs and increased slowness
- JSON is not fast to aggregate, but *columnar formats* are
- JSON is also not fast to search
- Basically, JSON is designed as a "lowest common denominator format" for interchange/data transfer, and is unsuitable for direct analytical usage

### **Practical Example**
- In the case of the NY taxi rides data, the dataset is quite clean, so let's instead use a small example of more complex data
- Let's assume we know some information about passengers and stops
- For this example we modified the dataset as follows:
    - We added nested dictionaries
        ```JSON
            "coordinates": {
                        "start": {
                            "lon": -73.787442,
                            "lat": 40.641525
                            },
        ```
    - We added nested lists
        ```JSON
            "passengers": [
                        {"name": "John", "rating": 4.9},
                        {"name": "Jack", "rating": 3.9}
                        ],
        ```
    - We added a record hash that gives us an unique ID for the record, for easy identification
        ```JSON
            "record_hash": "b00361a396177a9cb410ff61f20015ad",
        ```        
- We want to load this data to a database, so do we want to clean the data?
    - We want to **flatten dictionaries into the base row**
    - We want to **flatten lists into a separate table**
    - We want to **convert time *strings* into *time* type**
- To summarize our data:
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
                    "status": "booked"
                },
                "Passenger_Count": 2,
                "passengers": [
                    {"name": "John", "rating": 4.9},
                    {"name": "Jack", "rating": 3.9}
                ],
                "Stops": [
                    {"lon": -73.6, "lat": 40.6},
                    {"lon": -73.5, "lat": 40.5}
                ]
            },
        ]
    ```
- Now let's **normalize** this data

## Introducing dlt
- **dlt** is a Python library created for the purpose of assisting data engineers to build simpler, faster, and more robust pipelines with minimal effort
    - You can think of dlt as a loading tool that implements the best practices of data pipelines, enabling you to just "use" those best practices in your own pipelines, in a declarative way
    - This enables you to stop reinventing the flat tyre and to leverage dlt to build pipelines much faster than if you did everything from scratch
- dlt automates much of the tedious work that a data engineer would do, and does it in a way that is *robust*
- dlt can handle things like:
    - Schema work, like inferring and evolving schema, alerting changes, using schemas as data contracts, etc.
    - Typing data, flattening structures, renaming columns to fit database standards, etc.
        - In our example we will pass the "data" you can see above and see it normalized
    - Processing a stream of events/rows *without filling memory*
        - This includes extraction from generators
    - Loading to a variety of dbs or file formats
- Let's use it to load our nested JSON to **duckdb**
    - Here's how you would do that on your local machine
        - First, install dlt
            ```bash
                # Make sure you are using Python 3.8-3.11 and have pip installed
                # Spin up a venv
                python -m venv ./env
                source ./env/bin/activate
                
                pip install dlt[duckdb]
            ```
        - Next, grab your data from above and run this snippet the snippit below that defines a pipeline (a connection to a destination) and runs the pipeline, printing out the outcome
            ```python
                # Define the connection to load to. 
                # We currently are using duckdb, but you can switch to BigQuery later
                pipeline = dlt.pipeline(pipeline_name="taxi_data",
                                        destination='duckdb', 
                                        dataset_name='taxi_rides')

                # Run the pipeline with default settings, and capture the outcome
                info = pipeline.run(data, 
                                    table_name="users", 
                                    write_disposition="replace")

                # show the outcome
                print(info)
            ```
    - If running dlt locally, you can use the built in Streamlit app by running the CLI command with the pipeline name we chose above
        ```bash
            dlt pipeline taxi_data show
        ```
    
## Incremental loading
- **Incremental loading** means that as we update (i.e., load into) our datasets with *new* data, as opposed to making a full copy of a source's data all over again and replacing the old version
- *By loading incrementally, our pipelines run faster and cheaper*
- Incremental loading goes hand in hand with *incremental extraction* and **state** (2 concepts which we will not delve into during this workshop)
    - **State** is information that keeps track of *what* was loaded and to know *what else remains to be loaded*
        - dlt stores the state at the destination in a separate table
    - **Incremental extraction** refers to only requesting the increment of data that we need, and nothing more
        - This is tightly connected to the state to determine the exact chunk that needs to be extracted and loaded
- You can learn more about incremental extraction and state by reading the dlt docs on how to do it
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
Here is how you can think about which method to use:
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
- You could change the destination to Parquet and local file system, or a storage bucket
- You could also change the destination to BigQuery
    For destination & credential setup documentation, seee: 
        - https://dlthub.com/docs/dlt-ecosystem/destinations/
        - https://dlthub.com/docs/walkthroughs/add_credentials
- You could also use a **decorator** to convert the generator into a customised dlt resource
    - See https://dlthub.com/docs/general-usage/resource
- You can deep dive into building more complex dlt pipelines by following the guides:
    - https://dlthub.com/docs/walkthroughs
    - https://dlthub.com/docs/build-a-pipeline-tutorial
- You can also join the [dlt Slack community](https://dlthub.com/community) and engage there

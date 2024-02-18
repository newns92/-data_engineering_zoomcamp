# Data Ingestion with dlt

## Normalizing Data
- You often hear that data people spend most of their time "cleaning" data, but what does this mean? 
- Let's look granularly into what people consider "data cleaning"
    - Usually we have 2 parts: 
        - **Normalizing** data *without changing its meaning*
        - **Filtering** data for a use case, *which changes its meaning*
- Part of what we often call "data cleaning" is just **metadata** work:
    - Add **types** (`string` to `number`, `string` to `timestamp`, etc.)
    - **Rename** columns
        - In this activity, we ensure column names follow a supported standard downstream (such as no strange characters in the names)
    - **Flatten** nested dictionaries
        - This brings nested dictionary values into the top dictionary row
    - **Unnest** lists or arrays into child tables
        - Arrays or lists *cannot* be flattened into their parent record, so if we want flat data we need to break them out into *separate* tables
- We will look at a practical example next, as these concepts can be difficult to visualise from text

### **Why Prep Data?**
- If working with JSON, we do not easily know what is inside of a JSON document due to *lack of a **schema***
- Types are *NOT* enforced between rows of JSON
    - We could have one record where age is `25`, and another where age is `twenty five`, and still *another* where it's `25.00`
- Or in some systems, you might have a *dictionary* for a single record, but a *list of dictionaries* for *multiple* records
    - This could easily lead to applications downstream breaking
- We cannot just use JSON data in a "simple" manner
    - For example, we would need to convert strings to time types if we want to do a daily aggregation
- Reading JSON loads more data into memory, as the *whole* document is scanned
    - While in Parquet or in databases, we can scan a single column of a document
    - This whole-document scanning causes high costs and increased slowness
- JSON is not fast to aggregate, but *columnar formats* are
- JSON is also not fast to search
- Basically, JSON is designed as a "lowest common denominator format" for interchange/data transfer, and is unsuitable for direct analytical usage

### **Practical Example**
- In the case of the NY taxi rides data, the dataset is quite clean, so let's instead use a small example of more complex data
- Let's assume we know some information about passengers and stops
- For this example we modified the dataset as follows:
    - We added nested **dictionaries**
        ```JSON
            "coordinates": {
                        "start": {
                            "lon": -73.787442,
                            "lat": 40.641525
                            },
        ```
    - We added nested **lists**
        ```JSON
            "passengers": [
                        {"name": "John", "rating": 4.9},
                        {"name": "Jack", "rating": 3.9}
                        ],
        ```
    - We added a **record hash** that gives us an unique ID for the record for easy identification
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

# Data Ingestion with dlt
- ​In this hands-on workshop, we'll learn how to build data ingestion pipelines with **dlt**
- ​We'll cover the following steps:
    - ​Extracting data from APIs (or files).
    - ​Normalizing and loading data
    - ​Incremental loading
- ​By the end of this workshop, you'll be able to write data pipelines like a senior data engineer: Quickly, concisely, scalable, and self-maintaining.


## Intro
- **Data ingestion** is the *process of extracting data from a producer, transporting it to a convenient environment, and preparing it for usage by normalizing it, sometimes cleaning it, and adding metadata*
- In many data science teams, data magically appears *because the data engineer loads it*
    - Sometimes the format in which it appears is structured, and with explicit schema(s)
        - In that case, they can go straight to using it
            - Examples: Parquet, Avro, or table in a database
    - Sometimes the format is weakly typed and *without* explicit schema(s)
        - In that case some extra normalization or cleaning might be needed before usage
            - Examples: CSV, JSON
    - The **schema** specifies the *expected format and structure of data* within a document or data store, defining the allowed keys, their data types, and any constraints or relationships
- Since you are here to learn about data engineering, *you* will be the one making datasets magically appear
- Here's what you need to learn to build pipelines
    - Extracting data
    - Normalizing and cleaning data, as well as adding metadata such as schema and types
    - Incremental loading, which is vital for fast and cost effective data refreshes
- What else does a data engineer do? What are we learning, and what are we *not* learning?
    - It might seem simplistic, but in fact **a data engineer's main goal is to ensure data flows from source systems to analytical destinations**
    - So, besides building, running, and fixing *pipelines*, a data engineer may *also* focus on optimizing data storage, ensuring data quality and integrity, implementing effective data governance practices, and continuously refining data architecture to meet the evolving needs of an organization
    - Ultimately, a data engineer's role extends *beyond* the mechanical aspects of pipeline development, encompassing the strategic management and enhancement of the entire data lifecycle
    - This workshop focuses on building robust, scalable, self maintaining pipelines, with built-in governance 
        - In other words, best practices are applied


## dlt
- **dlt** stands for "data load tool", and is an open-source software (OSS) library that enables data engineers to build products faster and better
- Data engineering is one of the few areas of software engineering where we do not have developer tools to do our work for us
- Building better pipelines would require more *code re-use*, since we cannot all just build perfect pipelines from scratch every time
- So, dlt was born as a library that automates the tedious part of data ingestion (Loading, schema management, data type detection, scalability, self healing, scalable extraction)
- It was essentially designed as a data engineer's "one stop shop" for best practice data pipelining
- Due to its simplicity of use, dlt enables even laymen to
    - Build pipelines 5-10x faster than without it
    - Build self-healing, self-maintaining pipelines with all the best data engineering practices
    - Automate schema changes to remove the bulk of maintenance efforts
    - Govern pipelines with schema evolution alerts and data contracts
    - Generally develop pipelines like a senior, commercial data engineer
- See more at:
    - https://dlthub.com/
    - https://dlthub.com/docs/intro

## 1) Extracting Data

### The Considerations of Extracting Data
- In this section we will learn about **extracting** data from source systems, and what to care about when doing so
- Most data is stored behind an API 
    - Sometimes that's a RESTful API for some business application, returning records of data
    - Sometimes the API returns a secure file path to something like a JSON or Parquet file in a bucket that enables you to grab the data in bulk
    - Sometimes the API is something else (MongoDB, SQL, or other databases or applications),and will generally return records as JSON (the most common interchange format)
- As an engineer, you will need to build pipelines that "just work". 
- So, here's what you need to consider on extraction to prevent the pipelines from breaking and to keep them running smoothly.
    - Hardware limits: During this course we will cover how to navigate the challenges of managing memory
    - Network limits: Sometimes networks can fail
        - We can't fix what could go wrong, but we can retry network jobs until they succeed
        - For example, the `dlt` library offers a requests "replacement" that has built in retries
            - See the [docs](https://dlthub.com/docs/reference/performance#using-the-built-in-requests-client)
                - We won't focus on this during the course, but you can read the docs on your own
    - Source API limits: Each source might have some limits such as how many requests you can do per second
        - We would call these **rate limits**
        - Read each source's documentation carefully to understand how to navigate these obstacles
        - You can find some examples of how to wait for rate limits in dlt's verified sources repositories
            - Example documentation on API limits: 
                - [Zendesk](https://developer.zendesk.com/api-reference/introduction/rate-limits/)
                - [Shopify](https://shopify.dev/docs/api/usage/rate-limits)

### Extracting Data Without Hitting Hardware Limits
- In the case of data extraction, the only kinds of limits you can hit on your machine are **memory** and **storage**
    - This refers to the RAM (or virtual memory) and the disk (or physical storage)

#### *Managing Memory*
- Many data pipelines run on **serverless functions** or on **orchestrators** that delegate the workloads to *clusters of small workers*
- These systems have a *small* memory (or share it between multiple workers), so filling the memory is very bad
    - It might lead to not only your pipeline crashing, but crashing the entire container or machine that might be shared with other worker processes, taking them down too
- The same can be said about disk
    - In most cases your disk is sufficient, *but in some cases it's not*
        - For those cases, mounting* an external drive mapped to a storage bucket is the way to go*
            - For example, Airflow supports a "data" folder that is used just like a local folder, but can be mapped to a bucket for unlimited capacity

#### *How Do We Avoid Filling the Memory?*
- We *often do not know the volume of data upfront*
- We also cannot scale dynamically or infinitely on hardware *during runtime*
- Therfore, the answer to this question is to **control the maximum memory you use**, which can be done by **streaming** the data
    - "Streaming" here refers to **processing the data event by event or chunk by chunk instead of doing bulk operations**
    - Let's look at some classic examples of streaming where data is transferred chunk by chunk or event by event
        - Between an audio broadcaster and an in-browser audio player
        - Between a server and a local video player
        - Between a smart home device or IoT device and your phone
        - between Google Maps and your navigation app
        - Between Instagram Live and your followers
    - Data engineers usually stream the data between **buffers**, such as 
        - From API to local file
        - From webhooks to event queues
        - From event queue (Kafka, Amazon Simple Queue Service (SQS)) to a cloud storage bucket

#### *Streaming in Python Via Generators*
- Let's focus on how we build most data pipelines:
    - To process data in a stream in Python, we use **generators**, which are *functions* that can return *multiple* times 
        - By allowing multiple returns, the data can be released *as it's produced* (as a *stream*), instead of returning it all at once as a batch
- Take the following theoretical example: 
    - We search Twitter for "cat pictures"
        - We do not know how many pictures will be returned - maybe 10, maybe 10M
        - Will they fit in memory? Who knows?!
    - So to grab this data *without running out of memory*, we would use a Python generator
- Here's an example of a regular returning function, and how that function looks if written as a generator:
    - **Regular function that collects data in memory**:
        ```Python
            def search_twitter(query):
                data = []
                for row in paginated_get(query):
                    data.append(row)
                return data

            # Collect all the cat picture data
            for row in search_twitter("cat pictures"):
                # Once collected, print row by row
                print(row)
        ```
        -  Here you can see how data is collected *row by row* in a `list` called `data`, before it is returned
        - *This will break if we have more data than memory*
        - When calling `for row in search_twitter("cat pictures"):`, all the data must first be downloaded before the first record is returned
    - **Generator for streaming the data**: 
        ```Python
            def search_twitter(query):
                for row in paginated_get(query):
                    yield row

            # Get one row at a time
            for row in extract_data("cat pictures"):
                # Print the row
                print(row)
                # Do something with the row such as cleaning it and writing it to a buffer
                # Then continue requesting and printing data
        ```
        - The memory usage here is minimal
        - As you can see, in the modified function, we `yield` each row as we get the data, *without collecting it into memory*
        - We can then run this generator and handle the data item by item
        - When calling `for row in extract_data("cat pictures"):`, the function *only runs until the first data item is yielded*, *before* printing, so we do not need to wait long for the first value
        - It will then continue until there is no more data to get
        - If we wanted to get ALL the values at once from a generator instead of one by one, we would need to first "run" the generator and collect the data
            - For example, if we wanted to get all the data in memory, we could do `data = list(extract_data("cat pictures"))`, which would run the generator and collect all the data in a list before continuing

### Extraction Examples:
- **Example 1: Grabbing data from an API**
    - For the purposes of this course, an API was created that can serve the data we are already familiar with, the NYC taxi dataset
    - The API documentation is as follows:
        - There are a limited number of records behind the API
        - The data can be requested page by page, with each page containing 1000 records
        - If we request a page with no data, we will get a successful response with no data
            - This means that when we get an empty page, we know there is no more data and we can *stop* requesting pages
                - This is a common way to **paginate** (a technique for breaking up large datasets into smaller, more manageable chunks), but not the only one, since each API may be different
    - The details:
        - Method: `get`
        - URL: `https://us-central1-dlthub-analytics.cloudfunctions.net/data_engineering_zoomcamp_api`
        - Parameters: `page`, which is an integer that represents the page number you are requesting, and which defaults to 1
    - To design our requester, we need to request page by page *until we get no more data*
    - At this current starting point, *we do not know how much data is behind the API*
        - It could be 1000 records or it could be 10GB of records
    - So, let's grab the data with a **generator** to avoid having to fit an undetermined amount of data into RAM
    - In this approach to grabbing data from API's, we have some pros and cons:
        - Pros: **Easy memory management**, thanks to the API returning events/pages
        - Cons: **Low throughput**, due to the data transfer being constrained via an API
    - Here is the code
        ```Python
            import requests

            BASE_API_URL = "https://us-central1-dlthub-analytics.cloudfunctions.net/data_engineering_zoomcamp_api"

            # Call this a "paginated getter" as it's a function that gets data
            #   and also paginates until there is no more data
            # By yielding pages, we "microbatch", which speeds up downstream processing

            def paginated_getter():
                page_number = 1

                while True:
                    # Set the query parameters
                    params = {'page': page_number}

                    # Make the GET request to the API
                    response = requests.get(BASE_API_URL, params=params)
                    response.raise_for_status()  # Raise an HTTPError for bad responses
                    page_json = response.json()
                    print(f'Got page number {page_number} with {len(page_json)} records')

                    # If the page has no records, stop iterating
                    if page_json:
                        yield page_json
                        page_number += 1
                    else:
                        # No more data, break the loop
                        break

            if __name__ == '__main__':
                # Use the generator to iterate over pages
                for page_data in paginated_getter():
                    # Process each page as needed
                    print(page_data)
        ```

- **Example 2: Grabbing the same data from file (simple download)**
- When you do this in the future, you will remember there is a best practice you can apply for **scalability**
- Some API's respond with *files* instead of pages of data
    - The reason for this is simple: **Throughput** and **cost**
        - A RESTful API that returns data *has to* read the data from storage, process it, and then return it to you by some logic
        - If this data is very large, this costs time, money, *and* creates a bottleneck
    - A better way is to offer the data as *files* that someone can download from storage *directly*, without going through the RESTful API layer
        - This is common for API's that offer large volumes of data, such as ad impressions data
- In this example, we grab exactly the same data as we did in the API example above, but now we get it from the *underlying file* instead of going through the API
- To summarize this strategy:
    - Pros: **High throughput**
    - Cons: **Memory** is used to hold all the data
- Below is how the code could look
    - As you can see in this case, our `data` and `parsed_data` variables hold the *entirety* of the file's data in memory before returning it, which is *not great*
        ```Python
            import requests
            import json

            url = "https://storage.googleapis.com/dtc_zoomcamp_api/yellow_tripdata_2009-06.jsonl"

            def download_and_read_jsonl(url):
                response = requests.get(url)
                response.raise_for_status()  # Raise an HTTPError for bad responses
                data = response.text.splitlines()
                parsed_data = [json.loads(line) for line in data]
                return parsed_data
            
            downloaded_data = download_and_read_jsonl(url)

            if downloaded_data:
                # Process or print the downloaded data as needed
                print(downloaded_data[:5])  # Print the first 5 entries as an example
        ```
- **Example 3: Same file via a streaming download**
- This example is the bread and butter of data engineers pulling data
- So, downloading files is simple, but what if we want to do a *stream download*?
- That's possible too, in effect giving us the best of both worlds
- In this case a **JSONL (JSON Lines)** file was prepared, which is already split into lines, making our code simple
- But JSON (*not* JSONL) files could also be downloaded in this fashion
    - For example, by using the `ijson` Python library
- For the pros and cons of this method of grabbing data:
    - Pros: **High throughput and easy memory management,** because we are downloading a file
    - Cons: **Difficult to do for *columnar* file formats**, as *entire blocks* need to be downloaded before they can be deserialised to rows
        - Sometimes, this type of code is very complex, too
- Here's what the code looks like
    - NOTE: In a JSONL file, *each line is a JSON document*, or a "row" of data
    - So, we *yield* them as they get downloaded
    - This allows us to download one row and process it before getting the next row
        ```Python
            import requests
            import json

            def download_and_yield_rows(url):
                response = requests.get(url, stream=True)
                response.raise_for_status()  # Raise an HTTPError for bad responses

                for line in response.iter_lines():
                    if line:
                        yield json.loads(line)

            # Replace the URL with your actual URL
            url = "https://storage.googleapis.com/dtc_zoomcamp_api/yellow_tripdata_2009-06.jsonl"

            # Use the generator to iterate over rows with minimal memory usage
            for row in download_and_yield_rows(url):
                # Process each row as needed
                print(row)
        ```
- What is worth keeping in mind at this point is that our *loader* library that we will use later (`dlt`) will respect the streaming concept of the generator and will process it in an efficient way keeping memory usage low and using parallelism where possible

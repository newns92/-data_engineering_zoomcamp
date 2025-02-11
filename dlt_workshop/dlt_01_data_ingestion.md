# Data Ingestion With dlt

- In this workshop, we'll learn to build efficient and scalable data ingestion pipelines
- We will learn the core skills required to build and manage such data pipelines:
    - How to **build robust, scalable, and self-maintaining pipelines**
    - **Best practices**, like built-in data governance, for ensuring clean and reliable data flows
    - **Incremental loading** techniques to refresh data quickly and cost-effectively
    - How to build a **Data Lake** with **dlt**


## What is data ingestion?
- **Data ingestion** is the process of extracting data from a source, transporting it to a suitable environment, and preparing it for use
- This often includes **normalizing**, cleaning, and adding metadata
- In many data science teams, data seems to appear out of nowhere, but only because an engineer loads it
    - For example, the well-known NYC Taxi dataset looks well-structured and ready to use, making it easy to query and analyze
- *However, not all datasets arrive in such a clean format*
    - Well-structured data (with an explicit **schema**) can be used *immediately*
        - Examples: Parquet, Avro, or database tables where data types and structures are predefined
    - Unstructured (or weakly-typed) data (*without* a defined schema) often needs cleaning and formatting first
        - Examples: CSV and JSON, where fields might be inconsistent, nested, or missing key details
- A **schema** defines the expected format and structure of data, including field names, data types, and relationships
- To build effective pipelines, you need to master:
    - **Extracting** data from various sources (Application Programming Interfaces (APIs), databases, files)
    - **Normalization** data by transforming, cleaning, and defining schemas
    - **Loading** data where it can be used (data warehouse, lake, database, etc.)


## Why are data pipelines so amazing?
- Data pipelines are the backbone of modern data-driven organizations, as they transform raw, scattered data into actionable insights
- They ensure data flows seamlessly from its source to its final destination, where it can drive decision-making, analytics, and innovation
- But pipelines don't just move data, they also enable an entire ecosystem of functionality that makes them indispensable


## What makes data pipelines so essential?
- You can think of 5 main steps of a data pipeline:
    - **1\) Collect**:
        - Data pipelines gather information from a variety of sources, such as databases, data streams, and applications
            - This ensures no data is overlooked
            - Example: Retrieving sales data from an online store or capturing user activity logs from an app
    - **2\) Ingest**:
        - The collected data flows into an **event queue**, where it's organized and prepared for the next steps
        - Structured data (like Parquet files or database tables) can be processed *immediately*
        - *Unstructured* data (like CSV or JSON files) often needs cleaning and normalization
            - Example: Cleaning a JSON response by standardizing its fields or formatting dates in a CSV file
    - **3\) Store**:
        - Pipelines send the processed data to data lakes, data warehouses, or data lakehouses for efficient storage and easy access
            - Example: Storing marketing campaign data in a data warehouse to analyze its performance
    - **4\) Compute**:
        - Data is processed either in batches (large chunks) or as streams (real-time updates) to make it ready for analysis
            - Example: Calculating monthly revenue or processing live stock market data
    - **5\) Consume**:
        - Finally, the prepared data is delivered to users in forms they can act on:
            - Dashboards for executives and analysts
            - Self-service analytics (such as Business Intelligence (BI)) tools for teams exploring trends
            - Machine learning (ML) models for predictions and automation


## Why are data engineers so important in this process?
- Data engineers are the architects behind these pipelines
- They don't just *build* pipelines, they also make sure they're **reliable**, **efficient**, and **scalable**
- Beyond pipeline development, data engineers:
    - **Optimize data storage** to keep costs low and performance high
    - Ensure **data quality** and **integrity** by addressing duplicates, inconsistencies, and missing values
    - Implement **governance** for secure, compliant, and well-managed data
    - Adapt **data architectures** to meet the changing needs of the organization
- Ultimately, their role is to *strategically manage the entire data lifecycle*, from collection to consumption


## Data ingestion steps (ETL)
- **Extracting** data from various sources (APIs, databases, files)
- **Normalization** data by transforming, cleaning, and defining schemas
- **Loading** data where it can be used (data warehouse, lake, or database)


## Extracting data
- 99% of data you're extracting are stored in SQL databases, APIs, or files
- It's possible that most of the data you'll work with is stored behind an **API**, which is like a doorway to the data
    - Their data is usually unstructured/weakly-structured, and sometimes very complex, but APIs are also the most common way to access data
    - Here are the most common types:
        - **RESTful APIs**: Provide records of data from business applications
            - Example: Getting a list of customers from a CRM system
        - **File-based APIs**: Return secure file paths to bulk data like JSON or Parquet files stored in buckets
            - Example: Downloading monthly sales reports
        - **Database APIs**: Connect to databases like MongoDB or SQL, often returning data as JSON, the most common interchange format
- As an engineer, you will need to build pipelines that "just work"
- So here's **what you need to consider on extraction**, to prevent the pipelines from breaking, and to keep them running smoothly:
    - **Hardware limits**: Be mindful of memory (RAM) and storage (disk space)
        - Overloading these can crash your system.
    - **Network reliability**: Networks can fail! 
        - Always account for retries to make your pipelines more robust
        - Tip: Use libraries like `dlt` that have built-in retry mechanisms
    - **API rate limits**: APIs often restrict the number of requests you can make in a given time
        - Tip: Check the API documentation to understand its limits (e.g., [Zendesk](https://developer.zendesk.com/api-reference/introduction/rate-limits/), [Shopify](https://shopify.dev/docs/api/usage/rate-limits))
- There are even more challenges to consider when working with APIs — such as pagination and authentication
- Let's explore how to handle these effectively when working with REST APIs


## Working with REST APIs
- **REST (Representational State Transfer)** APIs are one of the most common ways to extract data
- They allow you to retrieve structured data using simple HTTP requests (`GET`, `POST`, `PUT`, `DELETE`)
- However, working with APIs comes with its own challenges
- Also, there is no common way how to design an API, so each of them is unique in a way
- Example API HTTP request:
    ```Python
    import requests

    result = requests.get("https://api.github.com/orgs/dlt-hub/repos").json()
    print(result[:2])
    ```

### Common REST API Challenges
- **1\) Rate limits**
    - Many APIs *limit* the number of requests you can make within a certain time frame to prevent overloading their servers
    - If you exceed this limit, the API may reject your requests temporarily or even block you for a period
    - To avoid hitting these limits, we can:
        - **Monitor API rate limits**
            – Some APIs provide headers that tell you how many requests you have left
        - **Pause requests** when needed
            – If we're close to the limit, we wait before making more requests
        - Implement **automatic retries**
            – If a request fails due to rate limiting, we can wait and retry after some time
    - *NOTE*: Some APIs provide a retry-after header, which tells you how long to wait before making another request
    - **Always check the API documentation for best practices!**
- **2\) Authentication**
    - Many APIs require an **API key** or **token** to access data securely
    - Without authentication, requests may be limited or denied
    - Types of Authentication in APIs:
        - **API Keys** – A simple token included in the request header or URL
        - **OAuth Tokens** – A more secure authentication method requiring user authorization
        - **Basic Authentication** – Using a username and password (which is less common today)
    - NEVER share your API token publicly!
        - Store it in environment variables or use a secure secrets manager
- **3\) Pagination**
    - Many APIs return data in **chunks** (or **pages**) rather than sending everything at once
    - This prevents overloading the server and improves performance, especially for large datasets
    - To retrieve *all* the data, we need to make *multiple* requests and **keep track of pages until we reach the last one**
    - Example: Request data from an API that serves the NYC taxi dataset
        - *For these purposes an API was created that can serve the data we are already familiar with*
        - API documentation:
            - Data: Comes in pages of 1,000 records.
            - Pagination: When there’s no more data, the API returns an empty page.
            - Details:
                - Method: `GET`
                - URL: https://us-central1-dlthub-analytics.cloudfunctions.net/data_engineering_zoomcamp_api
                - Parameters:
                    - `page`: Integer (page number), defaults to 1
        - The API returns 1,000 records per page, and we must request multiple pages to retrieve the full dataset
            ```Python
            import requests

            BASE_API_URL = "https://us-central1-dlthub-analytics.cloudfunctions.net/data_engineering_zoomcamp_api"

            page_number = 1
            while True:
                params = {'page': page_number}
                response = requests.get(BASE_API_URL, params=params)
                page_data = response.json()

                if not page_data:
                    break

                print(page_data)
                page_number += 1

                ## Limit the number of pages for testing
                if page_number > 2:
                break
            ```
        - What happens here:
            - The script starts at page 1 and makes a `GET` request to the API
            - It retrieves JSON data and checks if the page contains records
            - If data exists, it prints it and moves to the next page
            - If the page is empty, it stops requesting more data
    - Different APIs handle pagination differently (some use offsets, cursors, or tokens instead of page numbers)
    - **Always check the API documentation for the correct method!**
- **4\) Avoiding memory issues during extraction**
    - To prevent your pipeline from crashing, you need to control memory usage
    - Challenges with memory:
        - Many pipelines run on systems with limited memory, like serverless functions or shared clusters
        - If you try to load all the data into memory at once, it can crash the entire system
        - Even disk space can become an issue if storing large amounts of data
    - **The solution: *streaming* data**
        - **Streaming** means processing data in small chunks or events, rather than loading everything at once
            - This keeps memory usage low and ensures a pipeline remains efficient
        - As a data engineer, you'll use streaming to transfer data between **buffers**, such as:
            - From APIs to local files
            - From Webhooks to event queues
            - From Event queues (like Kafka) to storage buckets


## Example of Extracting Data: Grabbing Data from an API
- In this example, we request data from an API that serves the NYC taxi dataset
- Again, for these purposes an API was created that can serve the data we are already familiar with
- API documentation:
    - Data: Comes in pages of 1,000 records.
    - Pagination: When there’s no more data, the API returns an empty page.
    - Details:
        - Method: `GET`
        - URL: https://us-central1-dlthub-analytics.cloudfunctions.net/data_engineering_zoomcamp_api
        - Parameters:
            - `page`: Integer (page number), defaults to 1
- Here's how we will design our requester:
    - 1\)Request page by page until we hit an empty page
        - Since we don't know how much data is behind the API, we must assume it could be as little as 1,000 records or as much as 10GB
    - 2\) Use a **generator** to handle this efficiently and avoid loading all data into memory
        ```Python
        import requests

        BASE_API_URL = "https://us-central1-dlthub-analytics.cloudfunctions.net/data_engineering_zoomcamp_api"

        def paginated_getter():
            page_number = 1
            while True:
                params = {'page': page_number}
                try:
                    response = requests.get(BASE_API_URL, params=params)
                    response.raise_for_status()
                    page_json = response.json()
                    print(f'Got page {page_number} with {len(page_json)} records')

                    if page_json:
                        yield page_json
                        page_number += 1
                    else:
                        break
                except Exception as e:
                    print(e)
                    break


        for page_data in paginated_getter():
            print(page_data)
            break
        ```
- In this approach to grabbing data from APIs, there are both pros and cons:
    -  **Pros**: Easy memory management since the API returns data in small pages or events
    - **Cons**: Low **throughput** because data transfer is limited by API constraints (rate limits, response time, etc.)
- To simplify data extraction, use *specialized tools* that follow best practices like streaming
    - For example, [**dlt (data load tool)**](https://dlthub.com/) efficiently processes data while keeping memory usage low and leveraging **parallelism** for better performance


## Extracting Data With dlt
- Extracting data from APIs *manually* requires handling
    - Pagination
    - Rate limits
    - Authentication
    - Errors
    - And potentially more...
- Instead of writing custom scripts, **dlt** simplifies the process with a [built-in REST API Client](https://dlthub.com/docs/general-usage/http/rest-client), making extraction efficient, scalable, and reliable
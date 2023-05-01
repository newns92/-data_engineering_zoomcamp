# DE Zoomcamp - Week 2 - Workflow Orchestration

## Data Lake (GCP)
- A **data lake** = a central repository that holds "Big Data" from many sources
- Ingests structured, unstructured, and semi-structured data
- Idea = to ingest data as quickly as possible and make it available/accessible to other people/services
- Catalogs and indexes for analysis without data movement
    - Generally in data lakes, you associate data with some metadata for faster access
- Stores, secures, and protects at "unlimited" scale
    - It should scale and the hardware should be inexpensive
- Connects data with analytics and ML tools
- Started as a solution for companies to store and access large amounts of data quickly as companies realized the value of data, and there was a need for cheap storage of Big Data
- Cannot always define the structure of data, so a solution was needed to store it
- Sometimes usefulness of data was not realized until later parts of project lifecycles, so it needed to be stored somewhere until it was useful
- The increase in data scientists and R&D on data products was likely a cause in the need for data lakes
- "Gotcha's"
    - Risk of turning into a **data swamp** = hard to be useful
    - No versioning, generally
    - Incompatible schemas for the same data without versioning
    - If no metadata is associated with the data, the data is hard to use
    - If JOINs are not possible, the data is worthless
- Cloud providers for data lakes:
    - Google = GCP Cloud storage
    - AWS = S3 buckets
    - Azure = Azure Blob

## Data Lake vs. Data Warehouse
- Data Lake
    - Unstructured
    - Target users = Data scientists and data analysts
    - Use cases = stream processing, ML, real-time analysis
    - It's
        - Raw = structured, unstructured, and semi-structured data with minimal processing and can be used to store "unconventional" data like log and sensor data
        - Undefined = used for a wide variety of applications such as ML, streaming analytics, and AI
        - Large = Order of PB's, and since data can be of any form and/or size, large amounts of unstructured data can be stored *indefinitely* and transformed in use only
- Data Warehouse
    - Structured
    - Target users = Business analysts
    - Use cases = batch processing, BI, reporting
    - It's
        - Refined = contains highly structured data that's cleaned, pre-processed, and refined, to be stored for specific use cases such as BI
        - Relational = Contain historic and relational data, such as transaction systems, operations, etc.
        - Smaller = Contain less data, in the order of TB's, and must be processed before ingestion and periodically purged of data in order to maintain data cleanliness and health of the warehouse        

## ETL vs. ELT
- ETL = mainly for smaller amounts of data ()
    - Data warehouse solution (**Schema on write** = schema (relationships) is provided as data is written to the warehouse)
- ETL = used for larger amounts
    - Provides data lake support (**Schema on read**)
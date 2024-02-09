# Analytics Engineering

## What is Analytics Engineering?
- To answer this, we have look back at some recent developments in the data domain:
    1. Growth of **Massive parallel processing (MPP) databases**
        - We've seen how cloud data warehouses (BigQuery, RedShift, Snowflake, etc.) have lowered the cost of storage and computing
    2. Growth of **Data-pipelines-as-a-service**
        - We've also seen how tools like Stitch and Fivetran simplify the ETL process
    3. A pivot towards a **"SQL-first"** ideology
    4. Adoption of **version control systems**
        - Tools like Looker introducing version control systems to the data workflow        
    5. Growth of **self-service analytics**
        - Different BI tools (Tableau, Mode, etc.) enable this
    6. Focus on **data governance**
        - This has changed the way that data teams work and also the way stakeholders consume data
- All of the above developments left gaps in the roles that were present in a data team
- There usually were three different roles in a traditional data team:
    - **Data Engineer**: prepares and maintain the infrastructure that the data team needs
    - **Data Analyst**: uses data to answer questions and solve problems (insights)
    - **Analytics Engineer**: introduces good software engineering (SWE) practices to the efforts of data analysts and data scientists
        - Data analysts and data scientists are not meant to be writing SWE-level code
        - Data engineers don't have the training in how the data is actually going to be used by business users
        - The analytics engineer role fills this gap
- There are various toolings used by analytics engineers:
    - Data loading (Fivetran, Stitch, etc.)
    - Data storing (Cloud (Snowflake, BigQuery, RedShift) or on-prem data warehouses, etc.)
    - Data modeling (dbt, Dataform, etc.)
    - Data presentation (BI tools like Google Data Studio, Looker, Mode, Tableau, etc.)


## Data Modeling Concepts
- **ETL vs ELT**
    - *ETL (Extract-Transform-Load)*
        - Takes *longer to implement *   
        - Results in *slightly more stable and compliant data analysis*
        - Higher storage and compute *costs*
    - *ELT (Extract-Load-Transform)*
        - Waiting to transform data until it's in the data warehouse
        - *Faster* and *more flexible data analysis*
        - *Lower cost and lower maintenance* (thanks to cloud solutions)
- **Kimball’s Dimensional Modeling**
    - *Objective*:
        - To deliver data that's understandable to the business users
        - To simultaneously deliver fast query performance
    - *Approach*:
        - Prioritize understandibility and query performance over non-redundant data (i.e., third normal form, or "3NF")
    - Other dimensional modeling approaches also exist, like Bill Inmon, Data Vault (2.0)
    - **Elements of Kimball Dimensional Modeling (*Star* Schema)**
        - **Fact** tables:
            - These contain **measurements** and/or metrics (the "facts")
            - They correspond to a business *process*
            - They are usually named after verbs (like "Sales" or "Orders")
        - **Dimension** tables
            - These orresponds to a business **entity**
            - They provide context to a business process (i.e., a fact)
            - They are usually named after nouns (like Customer or Products)
    - **Architecture of Dimensional Modeling**
        - The data warehouse and the ETL/ELT processes could be described with a restaurant metaphor:
            - **Staging** layer:
                - Contains the *raw* data
                - It's *not* meant to be exposed to *everyone*, just to those who know how to use it
            - **Processing** layer:
                - This is going from raw data to data models
                - It's focus is *efficiency* and *ensuring standards*
            - **Presentation** layer:
                - This is the final presentation of the data
                - This is where there is exposure to business stakeholders

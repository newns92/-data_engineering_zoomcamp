# Stream Processing

## What is Stream Processing?
- ***Stream processing*** = data management technique that involves ingesting a **continuous** data stream to quickly analyze, filter, transform or enhance the data **in real time**
    - https://huyenchip.com/2022/08/03/stream-processing-for-data-scientists.html
        - As ML moves towards "real-time", streaming technology is becoming increasingly important for data scientists
        - Once data is stored in files, data lakes, or data warehouses, it becomes **historical data**
        - **Streaming data** = data that is *still flowing through a system* (e.g. moving from one microservice to another)
        - **Batch vs. stream processing**:
            - Historical data is often processed in **batch jobs** (kicked off periodically, say, once a day kick off a batch job to generate recommendations for all users)
            - When data is processed in batch jobs, we refer to it as **batch processing**.
            - This has been a research subject for many decades, and companies have come up with distributed systems like **MapReduce** and **Spark** to process batch data efficiently
            - **Stream processing** = doing computation on *streaming* data, and this processing is relatively new
            - A company should have infrastructure to help building and/or maintaining a **streaming system**
            - However, understanding where streaming is useful and why streaming is hard could help evaluate the right tools and allocate sufficient resources for your needs
- **Data exchange** allows data to be shared between different CPU programs
    - One CPU is sharing some sort of data, and that data is being exchanged over various services (REST API's, webhooks, etc.  )
    - Generally, a **producer** can create messages that **consumers** can read (or take actions on)
        - Consumers may be interested in certain **topics**
        - The producer indicates the topic of their messages
        - The consumer can subscribe to the topics of their choice
        - When a producer posts a message on a particular topic, consumers who have subscribed to that topic receive the message *in real time*
        - ***"Real time" does *not* mean immediately***, but rather **a few seconds later**, or more generally, **much faster than batch processing**


## What is Apache Kafka?
- https://javadoc.io/doc/org.apache.kafka, https://kafka.apache.org/documentation/
- **Apache Kafka** = an open-source distributed event *streaming* platform for high-performance data pipelines, *streaming* analytics, data integration, and mission-critical applications
- Provides a **high-throughput** and **low-latency** platform for handling real-time data feeds
- Runs as a **cluster** in 1+ servers
    - A Kafka cluster stores streams of **records** in categories called **topics**
        - Each **record** has a key, value, and a timestamp
- Originally developed at LinkedIn and subsequently open-sourced under the Apache Software Foundation in 2011
- Widely used for high-performance use cases like streaming analytics and data integration
- Kafka **Topic** = a continuous stream of **events**
    - An **event** refers to a *single* data point collected at a specific timestamp
    - The **collection** of a sequence of events goes into a topic and is read by a **consumer**
    - In Kafka, events are stored as **logs** in a topic (i.e., how the data is stored inside a topic) and *each event contains a **message***
- We have **topics** created by **producers** and interacted with by **consumers**
    - Multiple producers are able to **publish** to a topic, picking a **partition** at will
        - A Kafka Topic is grouped into several **partitions** for scalability
        - Each one is an sequence of records that are continually added to a structured commit log
        - A sequential ID number called the **offset** is assigned to each record in the partition
        - A partition may be selected directly (by specifying a partition number) or indirectly (by way of a record key, which deterministically hashes to a partition number)
        - Each topic can have one or many consumers which subscribe to the data written to the topic
- **Topics:**
    - Nothing but a continous stream of **events** (i.e., single data point at a certain timestamp)
    - The collection of events goes into a topic and the events are read by consumers of the topic
    - In Kafka, events are stored as **logs** within a topic (i.e., how the data is stored inside a topic)
        - Kafka log = a collection of various data segments present on disk, having a name as that of a form-topic partition or any specific topic-partition
            - Each Kafka log provides a logical representation of a unique topic-based partitioning
            - Logs are how data is actually stored in a topic.    
    - Each event contains a **message** (a structure that stores a key, a value and a timestamp)
        - Messages can have different properties, but the contain 3 structures: 
            - **Key** = used to identify a message and for additional Kafka work, such as partitions
            - **Value** = the actual information that producers push and consumers are interested in
            - **Timestamp** = for logging

## Why Kafka?
- Brings **robustness** to a topic
    - Ex: When a server goes down, we can still recieve/access the data
    - Kafka achieves a certain level of **resiliency** through **replication** (of data), both across machines in a cluster *and* across multiple clusters in multiple data centers
- Offers a lot of **flexibility**: The **data exchange application** can be small or very large (can have 100s of consumers)
    - Kafka can be connected to multiple different databases with Kafka Connect (pluggable, declarative data integration framework for Kafka)
- Provides **scalability**
    - Has no problem handling a number of events that increases dramatically in a short time

## How Do We Exhange Data in Kafka?
- We produce a message to a Kafka topic, or put it out on a noticeboard
- Consumers register to the topic and are then able to read the message
- When a consumer reads a message, that message is *not* lost and is still available to other consumers
    - There *is* some kind of expiration date for messages, though

## Need For Stream Processing
- https://kafka.apache.org/intro
- Before, we often had an architecture of monolithic applications that talked to a central database
- Nowadays, we have an architecture of several **microservices** that have to talk to each other (through API's, message passes, another central database, etc.)
- Kafka helps **simplify data exchange between these microservices**
- As the number of microservices or data size or API size in an architecture grows, we need a consistent message pass/streaming service for microservices to communicate through
- Generally, one of the microservices writes to a Kafka topic in terms of events
- Whenever another microservice is interested in consuming this Kafka message, they can (generally) do so
- Kafka *also* allows us to do **Change Data Capture (CDC)**
    - https://www.confluent.io/learn/change-data-capture/
    - With a central database and microservices, sometimes it's required to have multiple data sources
    - The database will be able to write to Kafka topics, and any microservice interested can read from this topic
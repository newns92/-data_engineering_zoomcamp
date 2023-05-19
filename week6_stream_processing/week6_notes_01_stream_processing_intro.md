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

## Confluent Cloud
- https://docs.confluent.io/cloud/current/overview.html
- https://docs.confluent.io/home/overview.html
- Allows us to have Kafka Clusters
- Free 30-day account, and easily connects to GCP
    - Can also do so locally via a Dockerfile
- Go to https://confluent.cloud/signup and create an account
- Click "Add Cluster" to create a cluster.
    - Click "Begin configuration" from the Basic tier on the far left
    - Select Google Cloud and then select a Region near you (ideally offering low carbon intensity) and click "Continue"
        - We can also click "Skip payment" for now
- Under "Create Cluster", enter a Cluster name `kafka_tutorial_cluster`, then click "Lauch"
- API Keys
    - An **API key** consists of a **key** and a **secret**
    - *Kafka* API keys are *required* to interact with Kafka clusters in Confluent Cloud
        - Each Kafka API key is valid for a specific Kafka cluster
    - Under "Cluster Overview" on the left, click "API Keys", and then click "Create key"
    - Select "Global access" and click "Next"
    - Enter a description like `kafka_cluster_tutorial_api_key`, then click "Download and Continue"
    - The API key will download to the local, and we should also see the Endpoints Bootstrap server and the REST endpoint "in Cluster Settings" on the left
- Topic:
    - Remember, a **Topic** is a *category*/feed name to which records are stored and published
        - *All Kafka records are organized into topics*
        - **Producer** applications write data to topics and **consumer** applications read from topics
        - Records published to the cluster stay in the cluster until a configurable retention period has passed by
    - Select "Topics" on the left, and click "Create topic"
    - Then, enter a Topic name like `tutorial_topic` and the number of partitions being **2**
    - Click on "Show advanced settings" and set the retention time for our "Detete" cleanup policy to be "1 day"
    - Click "Save and create"
- Message:
    - We can now produce a message
    - On the topic's page, select the "Messages" tab, and click on "Produce a new message to this topic"
    - On this page, keep the default message, and on the bottom-right, click "Produce"
    - The message produced has a Value, an empty Header and a Key
- Connector:
    - We will now create a dummy Connector
    - Confluent Cloud offers pre-built, fully managed Kafka **connectors** that make it easy to instantly connect clusters to popular data sources and sinks
        - We can connect to external data systems effortlessly with simple configurations and no ongoing operational burden
    - On the left, select "Connectors" and then click on "Datagen Source"
    - For our topic, select `tutorial_topic` and click "Continue" on the bottom-right
    - Select "Global Access" and click "Continue" on the bottom-right
    - Under "Select output record value format", select "JSON", and then under "Select a template", select "Orders", then click "Continue" on the bottom-right
    - Keep the default connector size and click "Continue" on the bottom-right
    - Then, change our connector's name to something like `OrdersConnector_tutorial` and click "Continue" on the bottom-right, then we should see the created connector and is being **provisioned** (which can take a couple of minutes)
    - Once done, click on the `OrderConnector_tutorial` connector and we should see that it's active and running
    - Click "Explore metrics", and we should see that data is already being produced
        - We can now take time to learn some of the available metrics
- Go back to "Topics" on the left
    - Open the `tutorial_topic` that we just configured our new connector to produce to in order to view more details
    - Under the "Overview" tab, we see the production rate (Bytes per second) and consumption rate (Bytes per second)
    - Under the "Messages" tab, we see that a number of messages have been created
- Shut down:
    - To shut down our connector as to not incur costs out of the $400 free credit dollars, select "Connectors" on the left
    - Then, select connector `OrdersConnector_tutorial` and click on Pause button
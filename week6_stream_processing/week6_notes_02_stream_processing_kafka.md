# Stream Processing With Kafka

## Producers and Consumers
- Now, we are going to produce and consume some messages *programatically* via Kafka and Java using our NYC taxi rides data
    - Kafka Java libraries are very well-maintained
    - To use Python, there’s a Docker image out there

## Creating a Topic
- First, we create a Topic for the rides data by going to the Confluent Cloud homepage, clicking on "Environments", and then selecting the Default cluster, `kafka_tutorial_cluster`
- Then, click "Topics" on the left of the cluster homepage and click "Add Topic" on the top-right
- We name this `rides` and give it 2 partitions with a "Delete" Cleanup policy of "1 day", then click "Save and create"
- We now have a topic (which currently does not have any schema, configuration, nor any messages)
- Next, we will try to connect this Topic to a **Client**

## Clients
- The "Client" section on the left provides us with some examples of how to create one
- In the "Client" section, click "New client" on the top-right
- Then, select Java as the programming language in order to see the example configuration code snippet
    ```bash
        # Required connection configs for Kafka producer, consumer, and admin
        bootstrap.servers=pkc-41voz.northamerica-northeast1.gcp.confluent.cloud:9092
        security.protocol=SASL_SSL
        sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required username='{{ CLUSTER_API_KEY }}' password='{{ CLUSTER_API_SECRET }}';
        sasl.mechanism=PLAIN
        # Required for correctness in Apache Kafka clients prior to 2.6
        client.dns.lookup=use_all_dns_ips

        # Best practice for higher availability in Apache Kafka clients prior to 3.0
        session.timeout.ms=45000

        # Best practice for Kafka producer to prevent data loss
        acks=all

        # Required connection configs for Confluent Cloud Schema Registry
        schema.registry.url=https://{{ SR_ENDPOINT }}
        basic.auth.credentials.source=USER_INFO
        basic.auth.user.info={{ SR_API_KEY }}:{{ SR_API_SECRET }}
    ```
- In the `/java/kafka_examples/src/main/java/org/example/data` directory, we have `Ride.java`, which creates a **Java class** `Ride` with the same structure as the NYC taxi trip files
    - It contains a **Constructor** `Ride(String[] arr)`, which gets passed a String array to convert into the class object itself
- Then, in `/java/kafka_examples/src/main/java/org/example`, we have the `JsonProducer` class, which contains a `getRides()` method that reads a CSV file and return a list of `Ride`
    ```bash
        public List<Ride> getRides() throws IOException, CsvException {
            var ridesStream = this.getClass().getResource("/rides.csv");
            var reader = new CSVReader(new FileReader(ridesStream.getFile()));
            reader.skip(1);
            return reader.readAll().stream().map(arr -> new Ride(arr))
                    .collect(Collectors.toList());
        }
    ```
- After reading the data in, we want to actually **produce** it
- We create a `.publishRides()` method that takes in a list of rides: `List<Ride>`
- We use this within our `main()` method, which will create a new producer, get a list of Ride(s), and publish these rides
    ```bash
        public static void main(String[] args) throws IOException, CsvException,
            ExecutionException, InterruptedException {

            var producer = new JsonProducer();
            var rides = producer.getRides();
            producer.publishRides(rides);
        }
    ```
    - NOTE: **Java streams** enable functional-style operations on *streams* of elements 
        - A **stream** = an abstraction of a non-mutable collection of functions applied in some order to data
            - A stream is *NOT* a collection where you can store elements
            - https://www.jrebel.com/blog/java-streams-in-java-8
- 
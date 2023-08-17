package org.example;

import com.opencsv.CSVReader;
import com.opencsv.exceptions.CsvException;
import org.apache.kafka.clients.producer.*;
import org.apache.kafka.streams.StreamsConfig;
import org.example.data.Ride;

import java.io.FileReader;
import java.io.IOException;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Properties;
import java.util.concurrent.ExecutionException;
import java.util.stream.Collectors;

public class JsonProducer {
    // Create constructor
    private Properties props = new Properties();

    // Instantiate with constructor
    public JsonProducer() {
        // # Required connection configs for Kafka producer, consumer, and admin
        // bootstrap.servers=<INSERT SERVER FROM CONFLUENT HERE>
        props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "<>");
        // security.protocol=SASL_SSL
        props.put("security.protocol", "SASL_SSL");
        // sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required
        // username='{{ CLUSTER_API_KEY }}' password='{{ CLUSTER_API_SECRET }}';
        props.put("sasl.jaas.config", "org.apache.kafka.common.security.plain.PlainLoginModule required username='"+Secrets.KAFKA_CLUSTER_KEY+"' password='"+Secrets.KAFKA_CLUSTER_SECRET+"';");
        // sasl.mechanism=PLAIN
        props.put("sasl.mechanism", "PLAIN");
        // # Required for correctness in Apache Kafka clients prior to 2.6
        // client.dns.lookup=use_all_dns_ips
        props.put("client.dns.lookup", "use_all_dns_ips");
        // # Best practice for higher availability in Apache Kafka clients prior to 3.0
        // session.timeout.ms=45000
        props.put("session.timeout.ms", "45000");
        // # Best practice for Kafka producer to prevent data loss
        // acks=all
        props.put(ProducerConfig.ACKS_CONFIG, "all");
        // # Required connection configs for Confluent Cloud Schema Registry
        // schema.registry.url=https://{{ SR_ENDPOINT }}
        // basic.auth.credentials.source=USER_INFO
        // basic.auth.user.info={{ SR_API_KEY }}:{{ SR_API_SECRET }}
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, "org.apache.kafka.common.serialization.StringSerializer");
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, "io.confluent.kafka.serializers.KafkaJsonSerializer");
    }

    // Function to read in the data
    public List<Ride> getRides() throws IOException, CsvException {
        var ridesStream = this.getClass().getResource("/rides.csv");
        var reader = new CSVReader(new FileReader(ridesStream.getFile()));
        reader.skip(1);
        return reader.readAll().stream().map(arr -> new Ride(arr))
                .collect(Collectors.toList());

    }

    // Function to publish the data as messages
    public void publishRides(List<Ride> rides) throws ExecutionException, InterruptedException {
        // start the Kafka Producer
        KafkaProducer<String, Ride> kafkaProducer = new KafkaProducer<String, Ride>(props);

        // 
        for(Ride ride: rides) {
            ride.tpep_pickup_datetime = LocalDateTime.now().minusMinutes(20);
            ride.tpep_dropoff_datetime = LocalDateTime.now();
            var record = kafkaProducer.send(new ProducerRecord<>("rides", String.valueOf(ride.DOLocationID), ride), (metadata, exception) -> {
                if(exception != null) {
                    System.out.println(exception.getMessage());
                }
            });
            System.out.println(record.get().offset());
            System.out.println(ride.DOLocationID);
            Thread.sleep(500);
        }
    }

    public static void main(String[] args) throws IOException, CsvException, ExecutionException, InterruptedException {
        var producer = new JsonProducer();
        var rides = producer.getRides();
        producer.publishRides(rides);
    }
}
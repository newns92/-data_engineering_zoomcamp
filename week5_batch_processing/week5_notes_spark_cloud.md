## Running Spark in the Cloud

#### Uploading data to GCS
- We have a `data/parquet` directory that we move to the VM
- We will be moving this to GCS via the `gsutil` command (Python application that lets you access GCS from the CLI)
    - https://cloud.google.com/storage/docs/gsutil
- In Git Bash, `cd` into the `week5/data/` directory, then run `gsutil -m cp -r parquet/ <gsutil URI for the GCS bucket>`
    - `-m` means parallel multi-threaded/multi-processing copy, since we're copying over a lot of files
    - `-r` means recursively copy an entire directory tree
    - https://cloud.google.com/storage/docs/gsutil/commands/cp
- Next, download the GCS connector for Hadoop *3*: https://cloud.google.com/dataproc/docs/concepts/connectors/cloud-storage#clusters
    - Or via `wget https://storage.googleapis.com/hadoop-lib/gcs/gcs-connector-hadoop3-latest.jar`
    - This `.jar` file is what essentially connects PySpark with GCS
- Then, move this `gcs-connector-hadoop3-latest.jar` to the `spark/jars` directory on your machine
- Then, follow the instructions in the `9_pyspark_gcs.ipynb` notebook to connect to GCS to our local Spark cluster

#### Creating a Local Spark Cluster

#### Creating a Cloud Spark Cluster
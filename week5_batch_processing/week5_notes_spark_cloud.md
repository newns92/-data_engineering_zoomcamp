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
- So far, we've created local Spark clusters from Jupyter notebooks
- Once we stop a notebook, the cluster disappears immediately
- Now, we want to create a "local" (i.e., in the VM) Spark cluster *outside* of a notebook
- Spark provides a simple standalone deploy mode.
    - https://spark.apache.org/docs/latest/spark-standalone.html
    - "To install Spark Standalone mode, you simply place a compiled version of Spark on each node on the cluster"
- In the VM, run `echo $SPARK_HOME` to see where Spark is located
- `cd` to that directory, then run `./sbin/start-master.sh` to start a standalone master server
    - We can use this to connect workers to the master, or to pass as the “master” argument to `SparkContext`
- In a VSCode window connected to the VM, open port `8080`
- Then, open `http://localhost:8080` on your local machine to see the Spark *Master* UI for the VM
- Then, *in the VM, `cd` back to `~/spark_testing`
- Then, run `jupyter notebook` in the VM, forward ports `8888` and `4040` in the VSCode window connected to the VM, and open up `http://localhost:8888` and `http://localhost:4040/` on your local machine
- In this Jupyter notebook `09_pyspark_local_cluster.ipynb`, we can create a `SparkSession` using this master
- After attempting to load in data at first, we get an error: `WARN TaskSchedulerImpl: Initial job has not accepted any resources; check your cluster UI to ensure that workers are registered and have sufficient resources`
    - This means that we do not yet have a **Worker** available
    - In *another* Git Bash terminal SSH'ed into the VM, run `cd $SPARK_HOME`
    - Then, start a worker via `./sbin/start-worker.sh <Spark master URL>`
    - Refresh `http://localhost:8080/`, and you should see a new Worker
- Then, we want to create our current notebook into a Python script via `jupyter nbconvert --to=script 09_pyspark_local_cluster.ipynb` to make `09_pyspark_local_cluster.py`
- Open this script up in the VSCode window connected to the VM and clean it up a bit
    - i.e., re-create `https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/week_5_batch_processing/code/06_spark_sql.py`, BUT with:
        ```bash
            spark = SparkSession.builder \
                .master("<master URL>") \
                .appName('test') \
                .getOrCreate()    
        ```
    - Save it as `09_pyspark_local_cluster_v1.py`
- Then, in the VM, run `python 09_pyspark_local_cluster_v1.py`
    - **NOTE:** If we get the warning `WARN TaskSchedulerImpl: Initial job has not accepted any resources; check your cluster UI to ensure that workers are registered and have sufficient resources.`, check the cluster UI to ensure workers are registered and have sufficient resources
        - i.e., we have 2 applications for a single worker, and the 1st (our notebook) takes all the resources   
        - This would pop up because we have not set the resources that our `SparkSession` in the Jupyter notebook would use and, for such a reason, it uses *all* resources available
        - *If that is the case, just kill the process in the Spark Web UI*
            - We have to kill the 1st process so that the 2nd can run
            - In the Spark master UI, click "kill" under "Running Applications" so that our notebook is no longer connected to the master
    - Once the job finishes, we should see our `revenue_local_cluster` in the `data/report/` directory
- Download the notebook and the script to the `week5/` directory via the VSCode window connected to the VM
- Then, in the VM, update `09_pyspark_local_cluster_v1.py` to use command line arguments via `argparse` and save it as `09_pyspark_local_cluster_v2.py`
    - In the VM, we can then run:
        ```bash
            python 09_pyspark_local_cluster_v2.py \
                --input_green=data/parquet/green/2020/*/ \
                --input_yellow=data/parquet/yellow/2020/*/ \
                --output=data/report-2020
        ```
    - Should see the `report-2020/` directory in the VM

#### Creating a Cloud Spark Cluster
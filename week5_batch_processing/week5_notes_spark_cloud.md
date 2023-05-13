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
    - Should see the `report-2020/` directory in the VM once the job is finished
- Download `09_pyspark_local_cluster_v2.py` via the VSCode window connected to the VM
- Now, if we have *multiple* clusters, specifying the Spark master URL inside our script is not very practical
    - Instead, we will specifiy the master outside in the CLI with `spark-submit` via:
    ```bash
        URL="<URL to Spark master>"

        spark-submit \
            --master="${URL}" \
            09_pyspark_local_cluster_v3.py \
                --input_green=data/parquet/green/2021/*/ \
                --input_yellow=data/parquet/yellow/2021/*/ \
                --output=data/report-2021
    ```
    - You will see a lot more CLI output, and then should see the `report-2021/` directory in the VM once the job is finished
    - `spark-submit`'s script in Spark’s `bin\` directory is used to launch applications on a cluster.  
        - https://spark.apache.org/docs/latest/submitting-applications.html
- Download `09_pyspark_local_cluster_v3.py` via the VSCode window connected to the VM
- Before finishing, we have to stop the workers and stop the master in the VM CLI via:
    - `cd $SPARK_HOME`
    - `./sbin/stop-worker.sh`
    - `./sbin/stop-master.sh`
- Then, exit the VM in all windows via `Ctrl + D` and shut down the VM in the Google Cloud Console

#### Creating a Cloud Spark Cluster
- Now we will create a Spark cluster on Google Cloud
- Google Cloud **Dataproc** = a *managed service* for running Apache Hadoop and Spark jobs
    - Can be used for big data processing and ML
    - Actually uses Compute Engine instances under the hood, but takes care of the management details for you
    - It’s a layer on top that makes it easy to spin up and down clusters as you need them
    - Main **benefits**:
        - **Managed service** (don’t need a sysadmin to set it up)
        - **Fast** (can spin up a cluster in about 90 seconds)
        - **Cheaper** than building your own cluster (because you can spin up a Dataproc cluster when you need to run a job and shut it down afterward, so you *only pay when jobs are running*)
        - **Integrated with other Google Cloud services** (including GCS, BigQuery, and Cloud Bigtable, so it’s easy to get data into and out of it)
    - More info: https://cloudacademy.com/course/introduction-to-google-cloud-dataproc/what-is-cloud-dataproc-1/
- In Google Cloud, use search to search for "Dataproc", and then enable the API, if needed
    - Then, click "Create Cluster", then click on "Create" next to "Cluster on Compute Engine"
    - Then, enter "de-zoomcamp-cluster" for the cluster name, the same region as your GCS bucket for "region" (try "northamerica-northeast2" if your Bucket is multi-region), "Single Node (1 master, 0 workers)" (because we are only experimenting with a relatively small dataset) for cluster type, and select Jupyter Notebook and Docker for components
    - Click "Create", and then this will take a little bit of time to create
    - Once it is done, you should see a VM instance named "de-zoomcamp-cluster-m" under your VM instances
- Now, we can submit a **job** to the cluster
- With Dataproc, we *don’t* need to use the same instructions as before to establish a connection with GCS, since **Dataproc is already configured to access GCS**
    - First, we upload `09_pyspark_local_cluster_v3.py` file to the GCS bucket (the file with the CLI args that we pass in)
    - Before we do, make sure you are not specifying the master when creating the SparkSession:
        ```bash
            # start a SparkSession
            spark = SparkSession.builder \
                .appName('test') \
                .getOrCreate()
        ```
    - After checking that, in the directory where said file is located, run `gsutil cp 09_pyspark_local_cluster_v3.py gs://de-zoomcamp-384821-taxi-data/code/09_pyspark_local_cluster_v3.py`
    - You should see the new `code/` directory with this file in your GCS Bucket
- To **create/submit a new job**:
    - In Dataproc, select our cluster "de-zoomcamp-cluster" and click "Submit Job" at the top
    - For job type, select "PySpark", for main python file, put `gs://de-zoomcamp-384821-taxi-data/code/09_pyspark_local_cluster_v3.py`, and then add the following 3 args separately:
        - `--input_green=gs://de-zoomcamp-384821-taxi-data/parquet/green/2021/*/`
        - `--input_yellow=gs://de-zoomcamp-384821-taxi-data/parquet/yellow/2021/*/`
        - `--output=gs://de-zoomcamp-384821-taxi-data/reports/report-2021`
    - Then, click "Submit, and this will again take some time
    - When the job is finished, you should see a line in the output that says `Successfully repaired` and that "Status" is "Succeeded" at the top of the web page
    - You should then be able to see the new `reports/report-2021` in the GCS Bucket
- So, we've submitted a job through the UI, which isn't that convienent
    - On the web page where we ran the job, under the "Configuration" tab, at the bottom, you should see a button "Equivalent REST"
        - This makes Dataproc have the Google Console construct an equivalent REST API request or `gcloud` tool command to use in code or from the CLI to create a cluster:
        - It looks something like:
            ```bash
                {
                    "reference": {
                        "jobId": "job-c6ee59da",
                        "projectId": "de<>Your Project ID"
                    },
                    "placement": {
                        "clusterName": "de-zoomcamp-cluster"
                    },
                    "status": {
                        "state": "DONE",
                        "stateStartTime": "2023-05-13T23:38:37.597784Z"
                    },
                    "yarnApplications": [
                        {
                        "name": "test",
                        "state": "FINISHED",
                        "progress": 1,
                        "trackingUrl": "http://de-zoomcamp-cluster-m:8088/proxy/application_1684020424028_0002/"
                        }
                    ],
                    "statusHistory": [
                        {
                        "state": "PENDING",
                        "stateStartTime": "2023-05-13T23:37:43.045331Z"
                        },
                        {
                        "state": "SETUP_DONE",
                        "stateStartTime": "2023-05-13T23:37:43.147308Z"
                        },
                        {
                        "state": "RUNNING",
                        "details": "Agent reported job success",
                        "stateStartTime": "2023-05-13T23:37:43.653333Z"
                        }
                    ],
                    "driverControlFilesUri": "gs://dataproc-staging-northamerica-northeast2-404348555020-lh0oatca/google-cloud-dataproc-metainfo/d0ae4e50-a49d-434e-93c1-d9a91d52a6ca/jobs/job-c6ee59da/",
                    "driverOutputResourceUri": "gs://dataproc-staging-northamerica-northeast2-404348555020-lh0oatca/google-cloud-dataproc-metainfo/d0ae4e50-a49d-434e-93c1-d9a91d52a6ca/jobs/job-c6ee59da/driveroutput",
                    "jobUuid": "212e17cb-a903-46e4-bbcc-1428bd04c510",
                    "done": true,
                    "pysparkJob": {
                        "mainPythonFileUri": "gs://de-zoomcamp-384821-taxi-data/code/09_pyspark_local_cluster_v3.py",
                        "args": [
                        "--input_green=gs://de-zoomcamp-384821-taxi-data/parquet/green/2021/*/",
                        "--input_yellow=gs://de-zoomcamp-384821-taxi-data/parquet/yellow/2021/*/",
                        "--output=gs://de-zoomcamp-384821-taxi-data/reports/report-2021"
                        ]
                    }
                }
            ```
    - Can also do this via the CLI using **Google Cloud SDK**
        - https://cloud.google.com/dataproc/docs/guides/submit-job
        - First, add the role "Dataproc Administrator" to the permissions for user "de_zoomcamp_user"
        - Then, to submit a job to a Dataproc cluster, run the command below from the CLI:
            ```bash
                gcloud dataproc jobs submit pyspark \
                    --cluster=de-zoomcamp-cluster \
                    --region=northamerica-northeast2 \
                    gs://de-zoomcamp-384821-taxi-data/code/09_pyspark_local_cluster_v3.py \
                    -- \
                        --input_green=gs://de-zoomcamp-384821-taxi-data/parquet/green/2020/*/ \
                        --input_yellow=gs://de-zoomcamp-384821-taxi-data/parquet/yellow/2020/*/ \
                        --output=gs://de-zoomcamp-384821-taxi-data/reports/report-2020        
            ```
        - You can then see in the CLI output if the job finished successfully 
        - If so, in the GCS Bucket, you should see that the report is created successfully in the `reports/` directory

### Connecting Spark to BigQuery
- We can use Spark to connect directly to BigQuery/our data warehouse
## Installing Spark on Windows
- Via Git Bash MINGW terminal
- Installing Java
    - Spark needs Java 11: https://www.oracle.com/de/java/technologies/javase/jdk11-archive-downloads.html
    - Select “Windows x64 Compressed Archive” (may have to create an Oracle account)
    - Configure it and add it to `PATH` via `export JAVA_HOME="C:\jdk"` then `export PATH="${JAVA_HOME}/bin:${PATH}"`
    - Check that Java works correctly via `java --version`
- Installing **Hadoop**
    - Need to have Hadoop binaries from Hadoop 3.2 which we'll get from: https://github.com/cdarlint/winutils/tree/master/hadoop-3.2.0
    - Create a folder (`C:\hadoop`) and `cd` to that directory
    - To get the files, run `HADOOP_VERSION="3.2.0"`, then `PREFIX="https://raw.githubusercontent.com/cdarlint/winutils/master/hadoop-${HADOOP_VERSION}/bin/"`, then `FILES="hadoop.dll hadoop.exp hadoop.lib hadoop.pdb libwinutils.lib winutils.exe winutils.pdb"`
    - Then, run :
        ```bash
            for FILE in ${FILES}; do
                wget "${PREFIX}/${FILE}"
            done
        ```
    - Add it to `PATH` via `export HADOOP_HOME="C:\hadoop"` then `export PATH="${HADOOP_HOME}/bin:${PATH}"`
- Installing Spark
    - Download Spark version 3.3.2 via `wget https://dlcdn.apache.org/spark/spark-3.3.2/spark-3.3.2-bin-hadoop3.tgz`
    - Unpack it in some location `C:\spark` via `tar xzfv spark-3.3.2-bin-hadoop3.tgz`
    - Add it to `PATH` via `export SPARK_HOME="C:\spark` then `export PATH="${SPARK_HOME}/bin:${PATH}"`
- Testing
    - ***In an Anaconda command prompt***, `cd` to `C:\spark\bin`
    - Run spark-shell via `spark-shell.cmd`
        - At this point, you may get a message from Windows Firewall, just allow it
        - There could be some warnings, like this:
        ```bash
            WARNING: An illegal reflective access operation has occurred
            WARNING: Illegal reflective access by org.apache.spark.unsafe.Platform (file:/C:/spark/jars/spark-unsafe_2.12-3.3.2.jar) to constructor java.nio.DirectByteBuffer(long,int)
            WARNING: Please consider reporting this to the maintainers of org.apache.spark.unsafe.Platform
            WARNING: Use --illegal-access=warn to enable warnings of further illegal reflective access operations
            WARNING: All illegal access operations will be denied in a future release
        ```
    - Now run:
    ```bash
    val data = 1 to 10000
    val distData = sc.parallelize(data)
    distData.filter(_ < 10).collect()
    ```
- Installing PySpark
    - Assuming we already have Python, to run PySpark, we first need to add it to `PYTHONPATH`
    - Do so via `export PYTHONPATH="C:\ProgramData\Miniconda3\python.exe"`, then `export PYTHONPATH="%SPARK_HOME%\python\:$PYTHONPATH"`, then `export PYTHONPATH="%SPARK_HOME%\python\lib\py4j-0.10.9.5-src.zip:$PYTHONPATH"`
        - Or **do this manually on Windows**
        - **Make sure that the version under `$%SPARK_HOME%\python\lib\` matches the filename of `py4j` or you will encounter `ModuleNotFoundError: No module named 'py4j'` while executing `import pyspark`**
    - Now you can run Jupyter or IPython to test if things work
    - Go back to `week5/` via `cd`, and download the zone lookup data via `wget https://s3.amazonaws.com/nyc-tlc/misc/taxi+_zone_lookup.csv` and also get the January FHV data from https://github.com/DataTalksClub/nyc-tlc-data/releases/tag/fhvhv
    - In a `zoom` conda environment, create a new notebook after running `jupyter notebook`
    - Run:
        ```bash
            import pyspark
            from pyspark.sql import SparkSession

            spark = SparkSession.builder \
                .master("local[*]") \
                .appName('test') \
                .getOrCreate()

            df = spark.read \
                .option("header", "true") \
                .csv('taxi+_zone_lookup.csv')

            df.show()
        ```
        - In the above code:
            - `SparkSession` is the class of the object that we instantiate
                - This class is the entry point into all functionality in Spark 
                - A `SparkSession` can be used create DataFrames, register DataFrames as tables, execute SQL over tables, cache tables, and read parquet files
            - `builder` is the builder method
                - It's a class attribute that is an instance of `pyspark.sql.session.SparkSession.Builder` that is used to construct SparkSession instances
            - `master()` sets the Spark master URL to connect to
                - The `local[*]` string means Spark will run on a local cluster (local machine)
                    - `[*]` means Spark will run with as many CPU cores as possible
                        - i.e., tells Spark to use all available cores (e.g., if we wanted to use only 2 cores, we would write `local[2]`)
            - `appName()` defines the name of our application/session, which will show in the Spark UI at http://localhost:4040/
            - `getOrCreate()` will create the session or recover the object if it was previously created
                - i.e., returns an existing `SparkSession`, if available, or creates a new one
        - Can also test that writing works via `df.write.parquet('zones')`
- To see conda environments in Juptyter notebooks:
    - Run `conda install nb_conda_kernels` in your base environment
    - In the `zoom` environment, run `conda install ipykernel`
    - Restart Jupyter Notebooks
    - Should see the conda environments as options under the "Kernel" tab

## Installing Spark on Google Cloud VM
- https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/week_5_batch_processing/setup/linux.md
- Restart the `de-zoomcamp` VM instance under "Compute Engine", "VM Instances" in the Google Cloud Console
- Get the new External IP address and add it to the `~/.ssh` file in the `config` file
- SSH into it in a new VSCode window via a *Git Bash or Google Cloud command prompt*
- Download OpenJDK 11 or Oracle JDK 11 (It's important that the version is 11 - spark requires 8 or 11)
    - Make a `/spark/` directory, `cd` into it, then run `wget https://download.java.net/java/GA/jdk11/9/GPL/openjdk-11.0.2_linux-x64_bin.tar.gz` inside of it
    - Then run `tar xzfv openjdk-11.0.2_linux-x64_bin.tar.gz` to unpack/unzip it
    - Define `JAVA_HOME` and add it to `PATH` via `export JAVA_HOME="${HOME}/spark/jdk-11.0.2"` and then `export PATH="${JAVA_HOME}/bin:${PATH}"`
    - Check that it worked via `java --version`
    - Remove the archive via `rm openjdk-11.0.2_linux-x64_bin.tar.gz`
- Installing Spark 
    - Download Spark version 3.3.2 via `wget https://dlcdn.apache.org/spark/spark-3.3.2/spark-3.3.2-bin-hadoop3.tgz`
    - Then unpack via `tar xzfv spark-3.3.2-bin-hadoop3.tgz`
    - Remove the archive via `rm spark-3.3.2-bin-hadoop3.tgz`
    - Add it to `PATH` via `export SPARK_HOME="${HOME}/spark/spark-3.3.2-bin-hadoop3"` then `export PATH="${SPARK_HOME}/bin:${PATH}"`
    - Test it with `spark-shell`
        - Then run the following
            ```bash
                val data = 1 to 10000
                val distData = sc.parallelize(data)
                distData.filter(_ < 10).collect()
            ```
- Intalling PySpark
    - To run PySpark, we first need to add it to `PYTHONPATH` via `export PYTHONPATH="${SPARK_HOME}/python/:$PYTHONPATH"` and `export PYTHONPATH="${SPARK_HOME}/python/lib/py4j-0.10.9.5-src.zip:$PYTHONPATH"`
        - *Make sure that the version under `${SPARK_HOME}/python/lib/` matches the filename of `py4j` or you will encounter `ModuleNotFoundError: No module named 'py4j'` while executing `import pyspark`*
    - Then `cd` to `~`, open the bash file via `nano .bashrc`, and add the following at the end of the file:
        ```bash
            export JAVA_HOME="${HOME}/spark/jdk-11.0.2"
            export PATH="${JAVA_HOME}/bin:${PATH}"

            export SPARK_HOME="${HOME}/spark/spark-3.3.2-bin-hadoop3"
            export PATH="${SPARK_HOME}/bin:${PATH}"

            export PYTHONPATH="${SPARK_HOME}/python/:$PYTHONPATH"
            export PYTHONPATH="${SPARK_HOME}/python/lib/py4j-0.10.9.5-src.zip:$PYTHONPATH"    
        ```
    - Then quit the server via `logout`, then SSH back in
    - Can now also see where are code/software is via `where pyspark` and `where java` while in the VM
    - You can run Jupyter or IPython to test if things work
        - *First, shutdown the local notebook server if its running*
        - Then, in the VM terminal, go to any other directory where you want the notebooks saved (I'm making a in `~/spark_testing/` directory and `cd`-ing into there)
        - Download a CSV file that we'll use for testing via `wget https://s3.amazonaws.com/nyc-tlc/misc/taxi+_zone_lookup.csv`
        - Then, open a Remote Window in VSCode to the host `de-zoomecamp` VM and enter the GPC passphrase
        - Hit Ctrl + ` to open the menu at the bottom, and go the the "Ports" tab
        - Click "Forward a Port" and enter `8888` to open that port, which Jupyter uses
        - Back in the VM terminal, run `ipython` (or `jupyter notebook`)
        - Copy the link from the resulting VM terminal output, and put that into a browser *locally* to see the notebook server from the VM
        - Open a new notebook and run `import pyspark` in a cell
        - Then run
            ```bash
                from pyspark.sql import SparkSession

                spark = SparkSession.builder \
                    .master("local[*]") \
                    .appName('test') \
                    .getOrCreate()

                df = spark.read \
                    .option("header", "true") \
                    .csv('taxi+_zone_lookup.csv')

                df.show()        
            ```
    - Then, in the VM VSCode window, add port `4040` to see the Spark UI for the current Spark cluster and you can see the UI at http://localhost:4040/
    - Once done, kill the notebook server and close the remote window in VSCode to get our ports back

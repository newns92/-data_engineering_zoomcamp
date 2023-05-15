## Week 5 Homework 

In this homework we'll put what we learned about Spark in practice.

For this homework we will be using the FHVHV 2021-06 data found here: [FHVHV Data](https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhvhv/fhvhv_tripdata_2021-06.csv.gz )


### Question 1: 

**Install Spark and PySpark** 

- Install Spark
- Run PySpark
- Create a local spark session
- Execute spark.version

- ***`cd` to `C:/spark/bin`***
- ***Run `spark-shell.cmd`***
- ***Run `spark.version`***

What's the output?
- ***3.3.2***
- ~~2.1.4~~
- ~~1.2.3~~
- ~~5.4~~
</br></br>


### Question 2: 

**HVFHW June 2021**

Read it with Spark using the same schema as we did in the lessons, as we will use this dataset for all the remaining questions.

Repartition it to 12 partitions and save it to parquet.

What is the average size of the parquet (ending with .parquet extension) files that were created (in MB)? Select the answer which most closely matches.</br>

- ***`cd` to the `week5/` directory***
- ***Run `./download_data_homework.sh`***
- ***In a `zoom` Conda environment, run `pyspark_create_parquet_homework.py`***
- ***Check the `week5\data\parquet\fhvhv\2021\06` directory for the average file size***
- ~~2MB~~
- ***24MB***
- ~~100MB~~
- ~~250MB~~
</br></br>


### Question 3: 

**Count records**  

How many taxi trips were there on June 15? (Consider only trips that *started* on June 15)

- ***In the `week5\` directory, run `pyspark_sql_homework.py`***

- ~~308,164~~
- ~~12,856~~
- ***452,470***
- ~~50,982~~
</br></br>


### Question 4: 

**Longest trip for each day**  

Now calculate the duration for each trip. How long was the longest trip in Hours?

- ***In the `week5\` directory, run `pyspark_sql_homework.py`***

- ***66.87 Hours***
- ~~243.44 Hours~~
- ~~7.68 Hours~~
- ~~3.32 Hours~~
</br></br>

### Question 5: 

**User Interface**

 Spark’s User Interface which shows application's dashboard runs on which local port?</br>

- ***From notes `week5_notes_spark_install.md`***

- ~~80~~
- ~~443~~
- ***4040***
- ~~8080~~
</br></br>


### Question 6: 

**Most frequent pickup location zone**

Load the [Zone Lookup Data](https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv) into a temp *view* in Spark. Using this zone lookup data *and* the fhvhv June 2021 data, what is the name of the most frequent *pickup* location zone?

- ***In the `week5\` directory, run `pyspark_sql_homework.py`***

- ~~East Chelsea~~
- ~~Astoria~~
- ~~Union Sq~~
- ***Crown Heights North***
</br></br>



## Submitting the solutions

* Form for submitting: https://forms.gle/EcSvDs6vp64gcGuD8
* You can submit your homework multiple times. In this case, only the last submission will be used. 

Deadline: 06 March (Monday), 22:00 CET


## Solution

* Video: https://www.youtube.com/watch?v=ldoDIT32pJs
* Answers:
  * Question 1: 3.3.2
  * Question 2: 24MB
  * Question 3: 452,470
  * Question 4: 66.87 Hours
  * Question 5: 4040
  * Question 6: Crown Heights North

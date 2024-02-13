# Visualizing the Transformed dbt Data

# Before Creating The Visualizations
- Upload all the data to GCS if needed (via `upload_all_data_parquet.py`)
- Create the tables in BigQuery if needed
    ```SQL
            CREATE OR REPLACE EXTERNAL TABLE `<project-id>.ny_taxi.external_yellow_trip_data`
            OPTIONS (
            format = 'PARQUET',
            uris = ['gs://<bucket-name>/data/yellow/yellow_tripdata_2019-*.parquet', 'gs://<bucket-name>/data/yellow/yellow_tripdata_2020-*.parquet']
            );

            CREATE OR REPLACE EXTERNAL TABLE `<project-id>.ny_taxi.external_green_trip_data`
            OPTIONS (
            format = 'PARQUET',
            uris = ['gs://<bucket-name>/data/green/green_tripdata_2019-*.parquet', 'gs://<bucket-name>/data/green/green_tripdata_20209-*.parquet']
            );

            CREATE OR REPLACE EXTERNAL TABLE `<project-id>.ny_taxi.external_fhv_trip_data`
            OPTIONS (
            format = 'PARQUET',
            uris = ['gs://<bucket-name>/data/fhv/fhv_tripdata_2019-*.parquet']
            );        

            CREATE OR REPLACE TABLE `<project-id>.ny_taxi.yellow_trip_data`
            AS
            SELECT * FROM `<project-id>.ny_taxi.external_yellow_trip_data`;

            CREATE OR REPLACE TABLE `<project-id>.ny_taxi.green_trip_data`
            AS
            SELECT * FROM `<project-id>.ny_taxi.external_green_trip_data`;

            CREATE OR REPLACE TABLE `<project-id>.ny_taxi.fhv_trip_data`
            AS
            SELECT * FROM `<project-id>.ny_taxi.external_fhv_trip_data`;
    ```
- Add *ALL* our of *transformed* data to BigQuery via `dbt build --var 'is_test_run: false'` in the dbt Cloud for the DEV environment
- In the dbt Cloud job, edit `dbt run` to be `dbt run --var 'is_test_run: false'` for the PROD environment


## Visualizing in Google Looker Studio
- Navigate to https://lookerstudio.google.com/u/0/navigation/reporting
- First, we must create a data source, and we choose BigQuery
- From the list of available projects, choose the one for the course, then choose the PROD dataset, then choose the `fact_trips` table, and click "Connect" on the top right-hand page
- We now see all of our columns, with the option to do some default aggregations and write some descriptions, if desired
    - *Edit the default aggregations so that only `passenger_count` has a "Sum" on it*
- Lower down on the page, see the "Metrics" section, where we can see a default metric of "Record Count", which is useful to see how many trips we're looking at
- We *could* create our own, new fields and metrics here to only be present on the BI side, but we will do that later on
- Also note that we could add descriptions to the fields and metrics, if desired
- We can also define data freshness at the top of the web page, as well as change the name of the table from `fact_trips` in the upper-left (which we *should* do if presenting to stakeholders who are not aware of dimensional modeling terms)
- Click "Create report" at the top right-hand part of the page to start working on a new Looker Studio report
    - Remove the default table that Looker places in the report
    - Go to "Add a chart" in the toolbar, and select a "Sparkline" chart under "Time series", and see that Looker *automatically* populates it with a dimension (`pickup_datetime`) and metric (`Record Count`)
    - Add a **breakdown dimension** of `service_type` to see the chart broken out by "Yellow" and "Green"
    - This chart looks a bit too small, so change the chart to a normal "Time series" chart on the top of the right-hand pane
    - If any **outliers** popped up in your data (years beyond what the data *should* contain, for example), Looker has some **controls** like "Date range" controls
        - So, add the "Date range" control via the toolbar and set the date range from 1/1/2019 to 12/31/2020
    - We can also add **filters** under the "Data" tab on the right-hand side of the page
        - And under the "Style" tabe, we can play around with different settings like grid type, background colors, borders, etc.
    - We can add text boxes to be our chart titles
        - For example, we can add one that says "Amount of Trips Per Day" to our current chart
    - Let's now add a "Scorecard with compact numbers" chart, and remove the dimension that's automatically added in order to see the total number of records (in the current date range)
        - Then add a text box to give it a title of "Total Trips Recorded"
    - Next, add a pie chart to see the service type distribution (This should happen automatically), and remove the dimension (which also removes the filter since there's nothing to filter on)
        - Then add a text box to give it a title of "Service Type Distribution"
    - So far, we can note the dominance of yellow taxis (via the pie chart) as well as the huge drop in rides in March 2020 due to COVID (via the line chart)
    - Add a "Table with heatmap", remove the date range dimension, and change the dimension to `pickup_zone` to see trips per pickup zone
        - Then add a text box to give it a title of "Trips Per Pickup Zone"    
    - Then, for visualizing trips per month, add a "Column chart", and then change the dimension to `pickup_datetime` and remove the *breakdown* dimension
        - We will now add (create) a new field to allow us to filter by month in this chart
        - At the bottom right-hand part of the web page, click "Add a field"
        - Call the new field `pickup_month` and add the formula `MONTH(pickup_datetime)`
        - Then save it, click "Done", then add it as the dimension for the column chart
        - But, since we know there is a big discrepency between 2019 and 2020, we *actually* want to drill down by *year*
            - Create the `pickup_year` field and add the formula `YEAR(pickup_datetime)`, and then add it as the breakdown dimension to the column chart
        - Make sure the column chart is sorted by `pickup_month` in ascending order and *not* `Record Count`, and remove the secondary sort
        - Now, *change this to a stacked column chart*
        - Then, under "Style", make sure there are 12 bars, one per month
        - Then, add a text box to give it a title of "Trips Per Month and Year"
    - Next, add a new control of a drop-down list, and make the dimension `service_type` to make this available to filter on
    - Finally, title the report "Taxi Trips Analysis: 2019-2020"
- In the upper-right hand part of the UI, we can click "View" to preview the report in an interactive mode
- We can then either go back into "Edit" mode to continune working, or we can *share* the report by inviting people to it, sharing a link, downloading the report as a PDF, or scheduling an email with it (Like sending it every Monday with the last week's data, for example)
    - Current report link: 

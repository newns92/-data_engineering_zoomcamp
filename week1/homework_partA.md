## Week 1 Homework- COMPLETED (see italicized and bolded comments)

In this homework we'll prepare the environment 
and practice with Docker and SQL


## Question 1. Knowing docker tags

Run the command to get information on Docker 

```docker --help```

Now run the command to get help on the "docker build" command

- ***i.e., run `docker --help build`***

Which tag has the following text? - *Write the image ID to the file* 

- `--imageid string`
- ***`--iidfile string`***
- `--idimage string`
- `--idfile string`


## Question 2. Understanding docker first run 

Run docker with the python:3.9 image in an interactive mode and the entrypoint of bash.
Now check the python modules that are installed ( use pip list). 
How many python packages/modules are installed?

- Make a `Dockerfile` with:
```bash
# base image to run from/use -- base it on Python 3.9
FROM python:3.9 

# command to run
# RUN pip install pandas

# override the entry point
ENTRYPOINT [ "bash" ]

# build the image with `docker build -t test:pandas .` --> test = img name, pandas = tag
# run the image with `winpty docker run -it test:pandas`
# kill python with Ctrl+C
# Kill Docker image with Ctrl+D
```

- 1
- 6
- ***3: pip, setuptools, wheel***
- 7

# Prepare Postgres

Run Postgres and load data as shown in the videos
We'll use the ***green*** taxi trips from January 2019:

```wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-01.csv.gz```

You will also need the dataset with zones:

```wget https://s3.amazonaws.com/nyc-tlc/misc/taxi+_zone_lookup.csv```

Download this data and put it into Postgres (with jupyter notebooks or with a pipeline)

***If already done, just spin up the Postgres server in detached mode via `docker-compose up -d`***
***Go to `localhost:8080` in a browser, and log in***
***Use the `load_data_green.py` file in the `Docker` file to load in the Green taxi database***
***Run the ``docker build -t taxi_ingest:v001 .` command, then the `docker run` command in the `Dockerfile` comments***
***Should see the Green taxi table***

## Question 3. Count records 

How many taxi trips were totally made on January 15?

Tip: started and finished on 2019-01-15. 

Remember that `lpep_pickup_datetime` and `lpep_dropoff_datetime` columns are in the format timestamp (date and hour+min+sec) and not in date.

- i.e., ***Run the following:***
```bash
-- How many taxi trips were totally made on January 15?
SELECT 
	COUNT(*)
FROM 
	public.green_taxi_data as taxi
WHERE
	-- start and end on the required date
	CAST(DATE_TRUNC('DAY', taxi.lpep_dropoff_datetime) AS DATE) = '2019-01-15'
	AND CAST(DATE_TRUNC('DAY', taxi.lpep_pickup_datetime) AS DATE) = '2019-01-15'
;
```

- 20689
- ***20530***
- 17630
- 21090

## Question 4. Largest trip for each day

Which was the day with the largest trip distance? Use the pick up time for your calculations.

- i.e., ***Run the following:***
```bash
-- Which was the day with the largest trip distance (Use the pick up time for your calculations)?
SELECT 
	CAST(DATE_TRUNC('DAY', taxi.lpep_pickup_datetime) AS DATE) AS pickup_day
	,MAX(taxi.trip_distance) AS max_trip_dist
FROM 
	public.green_taxi_data as taxi
GROUP BY
	pickup_day
ORDER BY 
	max_trip_dist DESC
;
```

- 2019-01-18
- 2019-01-28
- ***2019-01-15***
- 2019-01-10

## Question 5. The number of passengers

In 2019-01-01 how many trips had 2 and 3 passengers?
 
- i.e., ***Run the following:***
```bash
-- On 2019-01-01, how many trips had 2 and 3 passengers??
SELECT 
	COUNT(*)
FROM 
	public.green_taxi_data as taxi
WHERE
	-- start and end on the required date
	CAST(DATE_TRUNC('DAY', taxi.lpep_pickup_datetime) AS DATE) = '2019-01-01'
	-- AND CAST(DATE_TRUNC('DAY', taxi.lpep_dropoff_datetime) AS DATE) = '2019-01-01'
	AND (taxi.passenger_count = 2 OR taxi.passenger_count = 3)
;
```

- ***OR run THIS***
```bash
-- On 2019-01-01, how many trips had 2 and 3 passengers??
SELECT
	taxi.passenger_count
	,COUNT(*) AS trips_with_passengers
FROM
	public.green_taxi_data AS taxi
WHERE 
	CAST(DATE_TRUNC('DAY', taxi.lpep_pickup_datetime) AS DATE) = '2019-01-01'
	-- AND CAST(DATE_TRUNC('DAY', taxi.lpep_dropoff_datetime) AS DATE) = '2019-01-01'
	AND (taxi.passenger_count = 2 OR taxi.passenger_count = 3)
GROUP BY
	taxi.passenger_count
-- HAVING
-- 	COUNT(*) = 2 OR COUNT(*) = 3
;\
```

- 2: 1282 ; 3: 266
- 2: 1532 ; 3: 126
- ***2: 1282 ; 3: 254***
- 2: 1282 ; 3: 274


## Question 6. Largest tip

For the passengers picked up in the Astoria Zone which was the drop off zone that had the largest tip? We want the name of the zone, not the id.
- Note: it's not a typo, it's `tip` , not `trip`

- i.e., ***Run the following:***
```bash
-- For the passengers picked up in the Astoria Zone which was the drop off zone that had the largest tip? 
-- We want the NAME of the zone, *not* the id.
SELECT 
	-- taxi.*,
	-- pu_zones."Zone" AS pickup_zone,
	do_zones."Zone" AS dropoff_zone,
	taxi.tip_amount
FROM 
	public.green_taxi_data AS taxi
LEFT JOIN public.zones AS pu_zones
	ON taxi."PULocationID" = pu_zones."LocationID"
LEFT JOIN public.zones AS do_zones
	ON taxi."DOLocationID" = do_zones."LocationID"
WHERE 
	pu_zones."Zone" = 'Astoria'
ORDER BY 
	taxi.tip_amount DESC
LIMIT 100
;
```

- ***OR run THIS***
- i.e., ***Run the following:***
```bash
-- For the passengers picked up in the Astoria Zone which was the drop off zone that had the largest tip? 
-- We want the NAME of the zone, *not* the id.
SELECT 
	-- taxi.*,
	-- pu_zones."Zone" AS pickup_zone,
	do_zones."Zone" AS dropoff_zone,
	MAX(taxi.tip_amount) AS max_tip_amount
FROM 
	public.green_taxi_data AS taxi
LEFT JOIN public.zones AS pu_zones
	ON taxi."PULocationID" = pu_zones."LocationID"
LEFT JOIN public.zones AS do_zones
	ON taxi."DOLocationID" = do_zones."LocationID"
WHERE 
	pu_zones."Zone" = 'Astoria'
GROUP BY
    dropoff_zone
ORDER BY 
	max_tip_amount DESC
LIMIT 1
;
```

- Central Park
- Jamaica
- South Ozone Park
- ***Long Island City/Queens Plaza***


## Submitting the solutions

* Form for submitting: [form](https://forms.gle/EjphSkR1b3nsdojv7)
* You can submit your homework multiple times. In this case, only the last submission will be used. 

Deadline: 30 January (Monday), 22:00 CET


## Solution

See here: https://www.youtube.com/watch?v=KIh_9tZiroA

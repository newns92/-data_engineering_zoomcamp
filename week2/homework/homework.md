## Week 2 Homework- COMPLETED (see italicized and bolded comments)

The goal of this homework is to familiarise users with workflow orchestration and observation. 


## Question 1. Load January 2020 data

Using the `etl_web_to_gcs.py` flow that loads taxi data into GCS as a guide, create a flow that loads the green taxi CSV dataset for January 2020 into GCS and run it. Look at the logs to find out how many rows the dataset has.

How many rows does that dataset have?

- ***Make sure the Orion server is running at `http://localhost:4200/`, or run `prefect orion start` in the Anaconda `zoom` prompt if not***
- ***In the `week2/homework` dir, run `python etl_web_to_gcs.py` updated for this specified dataset***
- ***Check the logs for the flow run***
- ***Should also see the data in the GCS Bucket***

* ***447,770***
* ~~766,792~~
* ~~299,234~~
* ~~822,132~~


## Question 2. Scheduling with Cron

Cron is a common scheduling specification for workflows. 

Using the flow in `etl_web_to_gcs.py`, create a deployment to run on the first of every month at 5am UTC. What’s the cron schedule for that?

- ***First, create a `parameterized_flow.py` for this same flow code***
- ***The typical format of a cron job is: `Minute(0-59) Hour(0-24) Day_of_month(1-31) Month(1-12) Day_of_week(0-6) Command_to_execute`***
    - https://ostechnix.com/a-beginners-guide-to-cron-jobs/
    - ***The asterisk means that the cron will fire on every change of that value***
        - ***For example, when used in the minute column, it will fire the cron every minute***
        - https://pimylifeup.com/cron-jobs-and-crontab/
- ***So, in an Anaconda `zoom` CLI, in the `week2/homework` dir, run `prefect deployment build ./parameterized_flow.py:etl_parent_flow -n homework-etl-flow --cron "0 5 1 * *" -a`, where `-a` is to apply the schedule***
- ***Check for the Deployment and its specified schedule at `http://127.0.0.1:4200/deployments`***



- ***Then, create the `docker_deploy.py` for it, making sure the deployment name is `name='homework-docker-flow'`***
- ***In the `week2/homework` dir, run `python docker_deploy.py`, and once it's done, you should see `etl-parent-flow/homework-docker-flow` in your Deployments on the Orion UI***
 
- ***`0 5 1 * *`***
- ~~`0 0 5 1 *`~~
- ~~`5 * 1 0 *`~~
- ~~`* * 5 1 0`~~


## Question 3. Loading data to BigQuery 

Using `etl_gcs_to_bq.py` as a starting point, modify the script for extracting data from GCS and loading it into BigQuery. This new script should not fill or remove rows with missing values. (The script is really just doing the E and L parts of ETL).

The main flow should print the total number of rows processed by the script. Set the flow decorator to log the print statement.

Parametrize the entrypoint flow to accept a list of months, a year, and a taxi color. 

Make any other necessary changes to the code for it to function as required.

Create a deployment for this flow to run in a local subprocess with local flow code storage (the defaults).

Make sure you have the parquet data files for Yellow taxi data for Feb. 2019 and March 2019 loaded in GCS. Run your deployment to append this data to your BiqQuery table. How many rows did your flow code process?

- ***First, do a Quick Run of the deployment made in Question 2.***
- ***Check that the green taxi data is there in the GCS Bucket***
- ***Then, load in the Yellow taxi data for Feb. 2019 and March 2019 with `week2/gcp/etl_web_to_gcs.py` via the `etl-parent-flow/Parameterized ETL` Deployment in the Orion UI***
    - ***Do this via a "Custom Run" of the flow with the correct parameters***
- ***Check that the yellow taxi data is there in the GCS Bucket***
- ***Truncate the `de_zoomcamp.rides` in BigQuery***
- ***Create a `parameterized_flow_bq.py` for this same flow code***
- ***In an Anaconda `zoom` CLI, in the `week2/homework` dir, run `prefect deployment build ./parameterized_flow_bq.py:etl_parent_flow -n homework-etl-flow-bq --cron "0 5 1 * *" -a`, where `-a` is to apply the schedule***
- ***Do a Quick Run of this deployment***
- ***Should see the row count printed out in the logs for the parent flow run in the Orion UI, or run `SELET COUNT(*)` in BigQuery***

- ***14,851,920***
- ~~12,282,990~~
- ~~27,235,753~~
- ~~11,338,483~~



## Question 4. Github Storage Block

Using the `web_to_gcs` script from the videos as a guide, you want to store your flow code in a GitHub repository for collaboration with your team. Prefect can look in the GitHub repo to find your flow code and read it. Create a GitHub storage block from the UI or in Python code and use that in your Deployment instead of storing your flow code locally or baking your flow code into a Docker image. 

Note that you will have to push your code to GitHub, Prefect will not push it for you.

Run your deployment in a local subprocess (the default if you don’t specify an infrastructure). Use the Green taxi data for the month of November 2020.

How many rows were processed by the script?

- ***First, create a GitHub block with the `make_github_block.py` file with your specific GitHub repo URL and run it via `python make_github_block.py`***
- ***Check for it at `http://127.0.0.1:4200/blocks` or via `prefect blocks ls`***
- ***Go back to the parent directory for the repo, `/de_zoomcamp/`***
- ***Build the deployment via `prefect deployment build week2/homework/parameterized_flow.py:etl_parent_flow -n zoom-hw-4 -sb github/github-zoom -a`***
- ***See the deployment in the Orion UI as `etl-parent-flow/zoom-hw-4`***
- ***Do a custom run for the Green taxi data for the month of November 2020***

- 88,019
- 192,297
- 88,605
- 190,225



## Question 5. Email or Slack notifications

Q5. It’s often helpful to be notified when something with your dataflow doesn’t work as planned. Choose one of the options below for creating email or slack notifications.

The hosted Prefect Cloud lets you avoid running your own server and has Automations that allow you to get notifications when certain events occur or don’t occur. 

Create a free forever Prefect Cloud account at app.prefect.cloud and connect your workspace to it following the steps in the UI when you sign up. 

Set up an Automation that will send yourself an email when a flow run completes. Run the deployment used in Q4 for the Green taxi data for April 2019. Check your email to see the notification.

Alternatively, use a Prefect Cloud Automation or a self-hosted Orion server Notification to get notifications in a Slack workspace via an incoming webhook. 

Join my temporary Slack workspace with [this link](https://join.slack.com/t/temp-notify/shared_invite/zt-1odklt4wh-hH~b89HN8MjMrPGEaOlxIw). 400 people can use this link and it expires in 90 days. 

In the Prefect Cloud UI create an [Automation](https://docs.prefect.io/ui/automations) or in the Prefect Orion UI create a [Notification](https://docs.prefect.io/ui/notifications/) to send a Slack message when a flow run enters a Completed state. Here is the Webhook URL to use: https://hooks.slack.com/services/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

Test the functionality.

Alternatively, you can grab the webhook URL from your own Slack workspace and Slack App that you create. 


How many rows were processed by the script?

- `125,268`
- `377,922`
- `728,390`
- `514,392`


## Question 6. Secrets

Prefect Secret blocks provide secure, encrypted storage in the database and obfuscation in the UI. Create a secret block in the UI that stores a fake 10-digit password to connect to a third-party service. Once you’ve created your block in the UI, how many characters are shown as asterisks (*) on the next page of the UI?

- 5
- 6
- 8
- 10


## Submitting the solutions

* Form for submitting: https://forms.gle/PY8mBEGXJ1RvmTM97
* You can submit your homework multiple times. In this case, only the last submission will be used. 

Deadline: 8 February (Wednesday), 22:00 CET


## Solution

* Video: https://youtu.be/L04lvYqNlc0
* Code: https://github.com/discdiver/prefect-zoomcamp/tree/main/flows/04_homework
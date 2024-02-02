# ETL: From API to Google Cloud Storage

## Configuring GCS
- First, we must create a GCS **bucket** if we don't already have one
    - Name it `mage-zoomcamp-[username]`
        - *These MUST be globally unique names*
    - We can keep all the default options before creating it
- Mage uses **service accounts** to connect to GCP, so we must create a new one
    - These are just a set of permissions we're granting and credentials for those permissions
    - Name the service account `mage-zoomcamp`
    - Give it an **owner** role
    - Under the list of all service accounts, open this new account, go to "Keys", and select "Create new key" from the "Add key" drop-down
    - Use a JSON key and receive the downloaded file
    - Copy this file into the Mage project directory (`mage-zoomcamp/`)
        - *Don't worry, this is in the `.gitignore` file, so these credentials will not be uploaded to GitHub*
- Now, notice that in the `docker-compose.yml` file in `mage-zoomcamp`, that we have a **volume** defined for the Mage instance (local files are going to `./home/src` in the Mage container)
    - So, our recently-copied JSON credentials file will be **mounted** to our Mage volume
    - We can then use these credentials to authenticate with GCP
- At http://localhost:6789/, go to the "Files" section of the project
    - Open `io_config.yaml` and note that there are 2 ways to authenticate with Google service accounts
        - 1) Paste the JSON payload into the file
        - 2) Use the JSON service account key *file path*
    - We will be using the 2nd option, which will just be `GOOGLE_SERVICE_ACC_KEY_FILEPATH: "/home/src/<name-of-key-file>.json"`
        - *Do this under the `default` profile in `io_config.yaml`*
    - Mage will now use this service account's credentials (in the file) to interact with GCP
- Go back to the `test_config` pipeline from earlier
    - In the `test_postgres` data loader block, change the connection to be `BigQuery`, and set the profile to be `default`
    - Then test `SELECT 1` in the SQL data loader block to see if we can connect to Google BigQuery
- To test GCS to make sure we can read *and* write files, go to the `example_pipeline` pipeline
    - Remember that this pipeline reads Titanic data from an API into a dataframe and then writes it to a file
    - The full pipline exports a CSV to the Mage project directory (`mage-zoomcamp/`)
    - We can then load this CSV to GCS just by dragging-and-dropping it from Windows Explorer (or VSCode or whatever you have) into the GCS Bucket console in GCP in a browser
    - Once that's been uploaded to GCS, go back to the `test_config` pipeline
    - Then, under "Edit pipeline", create a new GCS Python data loader block named `test_gcs`
    - Within the `load_from_google_cloud_storage` loader function in the resulting file, add you Bucket name and **object key** (AKA the file name, `titanic_clean.csv`) as follows:
        ```Python
        bucket_name = 'mage-zoomcamp-<username>'
        object_key = 'titanic_clean.csv'
        ```
    - Then run the block to make sure we can connect to GCS (you should see a preview of the CSV returned in Mage)

## Writing an ETL Pipeline
- 

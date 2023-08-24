## Environment Setup
- Download [Anaconda](https://www.anaconda.com/download) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html#)
- First, create a **conda environment** via `conda create -n zoom_project python=3.9`
- Activate it via `conda activate zoom_project`
- Check packages:
    - If the environment isn't activated, then do so via `conda list -n zoom_project`
    - If the environment *is* activated, then do so via `pip list` or `conda list`
- Install the package requirements found in `requirements.txt` via `pip install -r requirements.txt`
- Check packages again if desired (recommended)


## Setup Postgres Database
- If needed:
    - Install a client for Postgres via `pip install pgcli` or `conda install -c conda-forge pgcli`
    - Add to the system path: `C:\ProgramData\Miniconda3\Scripts`
- Test that Postgres is there with `pgcli --help`

### Docker and Dockerfile
- Start Docker Desktop
    - If needed, log in
- In the Anaconda prompt for the `zoom_project` environment, check that Docker is installed and working with `docker run hello-world`
- Check if any containers are running with `docker ps`
    - If needed, kill any containers with `docker kill [containter_id]`
- Build an image from the `Dockerfile` via `docker build`
    - We first build the Postgres image as a test via `docker build -t test:postgres .`
        - `-t` argument is a tag to name the image
        - `.` means we want to build the image in the current directory
- Then run the image via `docker run -it test:postgres`
    - `-it` instructs Docker to allocate a pseudo-TTY connected to the container’s stdin; creating an interactive `bash` shell in the container.
        - https://docs.docker.com/engine/reference/commandline/run/
- Exit the Docker container via `CTRL + d`

### Docker and `docker compose`
- Run `docker-compose up -d` to run Docker Compose in detached mode and get control of the terminal back once the command is executed
- Once everything is running, open a browser and go to `http://localhost:8080/` to see the landing page for pgAdmin
- Sign in with the `pgadmin` credentials from the `docker-compose.yml` file
- Create a new server named `Local Docker` by right-clicking on "Servers" and hit "Register" --> "Server"
- Need to specify the host address in the "Connection" tab, which should be `pgdatabase` (from `docker-compose.yml`), port is `5432`, and both username and password are `root`
- Should see our new server with our `movies_data` database up and running
- **To make pgAdmin configuration persistent**, create a folder `data_pgadmin`
    - Change its permission potentially (on Linux, `sudo chown 5050:5050 data_pgadmin`)
        - On Windows, make sure under "Properties" that it is NOT "read-only"
    - Mount it to the `/var/lib/pgadmin` folder under `volumes` in the `pgadmin1` service in `docker-compose.yml`
- Kill all Docker containers once done via `docker-compose down`
- **To run and load the data into Postgres via the CLI and Docker:**
    - Run `docker build -t movie_ingest:v001 .`
    - Once complete, run the same command as manually running the Python script to ingest data, but via Docker starting with `docker run -it --network=pg-network movie_ingest:v001`
    - You should see the data loaded into the Postgres database in pgAdmin

### Prefect
- Next, we add **parameterization** to our flows and create deployments by expanding upon `get_data_postgres.py`
- 


### dbt
#### Local
- In the `zoom_project` Conda environment, run `pip install dbt-postgres` to will install `dbt-core` and any other dependencies
- Create a `dbt_postgres/` directory, `cd` into it, and run `dbt init`
- Name the project `movie_data` and select the Postgres option of a database
- `profiles.yml` should be updated with stock **outputs**
    - Update these outputs to be the correct root username, password, host, port, etc. for the Postgres database
- Run `dbt debug --profiles-dir ../` from within the `movie_data/` directory
    - This will find the `profiles.yml` file in the parent directory of the dbt project (parent of `movie_data/`) and check the database connection and display any errors or warnings that it finds
- Copy in the green staging SQL file, the `schema.yml` file, the macros file
- Create the `packages.yml` file
- Then run `dbt deps --profiles-dir=../`
- Then attempt `dbt run -m stg_green_trip_data --profiles-dir=../`
- This *should* work, and you should see the View in the `public` schema of Postgres
    - ***If needed, create `staging` and `prod` schemas now***
- Then create the yellow staging SQL file
- Then attempt `dbt run -m stg_yellow_trip_data --profiles-dir=../`
- You should see the second View in the `public` schema of Postgres
#### Cloud (GCP)
- In the `zoom_project` Conda environment, run `pip install dbt-bigquery`





## Setup GCP Account
- Create account and get the GCP free trial if needed
- Create a new project and note the Project ID
- Go to "IAM" (Identity and Access Management) --> Service Accounts
    - **Service account** = an account with limited permissions that is assigned to a service (ex: a server or VM)
        - Allows us to create a set of credentials that does not have full access to the owner/admin account
- Create a service account: "de_zoomcamp_user"
- Grant access as "Basic" --> "Viewer"
    - We will fine tune the permissions in a later step
- We do not need to "grant users access to this service account"
    - But this is useful in a PROD environment where it may be useful for multiple users to share the same permissions
- To create a key, click the three dots under "Actions" --> "Manage keys"
- Click "Add key" --> "Create new key" --> "JSON"
    - This downloads a *private* key JSON File
    - Do NOT save it in git
- Install the Google Cloud CL (https://cloud.google.com/sdk/docs/install-sdk)
- **If you uncheck bundled Python**:
    - In Google Cloud SDK Shell, check `python -c "import os, sys; print(os.path.dirname(sys.executable))"` to see where Python is installed
    - Check the environment variable in Git Bash via `printenv CLOUDSDK_PYTHON`
    - Use a python (Miniconda) you have installed in a special location via `export CLOUDSDK_PYTHON=C:\ProgramData\Miniconda3\python.exe`
    - Also attempt to set it up via Environment Variables for User and System
    - Re-run the SDK installer
    - Test in Git Bash via `gcloud -h`
- Set environment variable to point to your downloaded GCP keys via `export GOOGLE_APPLICATION_CREDENTIALS="<path/to/your/service-account-authkeys>.json"`
    - This is how we authenticate our other resources (OAuth)
- Refresh token/session, and verify authentication via `gcloud auth application-default login`
    - The browser will open up, so choose the right email and then click "Allow" to see the "You are now authenticated with the gcloud CLI!" webpage
- Next we will set up 2 resources in the Google environment (Google Cloud Storage data lake and BigQuery data warehouse)
    - Cloud storage is a bucket in our GCP environment where we can store data in flat files
    - This data lake is where we will store data in a more organized fashion
    - In our BigQuery data warehouse, our data will be in a more structured format (Fact and Dimension tables)
- 1st, we will add more permissions to our service account
    - Click on "IAM" on the left
    - Click "edit principal" pencil on the right for the user account we just created
    - Add "Storage Admin" to create and the GCP data lake
        - Allows us to create and modify buckets and packets (Terraform) and files
        - In PROD, we'd actually create *custom* roles to limit user access to a particular bucket/certain resources
            - We'd create separate service accounts for Terraform, for the data pipeline, etc. (In this course we are only making *one* for simplicity's sake)
    - Add "Storage Object Admin" to add/control things within our bucket/data lake
    - Add "BigQuery Admin"
    - Click "Save"
- Next, we need to enable API's
    - When the local environment interacts with the cloud enviroment, it does not interact *directly* with the resource
    - These API's are the form of communication
    - We have 2 API's for the IAM itself
        - Click on the 3 bars to the left of "Google Cloud" in the upper-left
        - Click "API's and Services" --> "Library" --> Search for "Identity and Access Management"
        - Choose "Identity and Access Management (IAM) API" --> "Enable"
        - Go back to the library and search for "IAM"


# Setting up Environment on GCP
- Need to generate an SSH key to log into the VM instance that we will create
- First, create an `.ssh/` directory via `mkdir` in the Git Bash terminal if it doesn't already exist
- Then use the `ssh-keygen` command with a `-C` flag to create a new SSH key pair
    - Do this via `ssh-keygen -t rsa -f ~/.ssh/[name for SSH key file] -C [username on the VM] -b 2048`
        - Username = `nimz`
    - Enter a passphrase if desired
    - Should see `gcp` and `gcp.pub` key files via `ls`
    - **Never** show the private key
- Next go to "Compute --> "Compute Engine" on the left --> "Settings" --> "Metadata"
    - Enable the Compute Engine API if prompted
    - See the SSH Keys tab, click "Add SSH key"
    - Get the public SSH key in the terminal via `cat gcp.pub` and copy it to the browser, and click "Save" at the bottom
        - All instances in the project will be able to use this SSH key
- Go to "Compute --> "Compute Engine" on the left --> "VM instances"
    - Click "Create an instance"
    - Name it something, like "de-zoomcamp"
    - Add relevant time zone
    - Select the "e2-standard-4 (4vCPU 16 GB memory)" machine
    - Under "Boot Disk", choose "Ubuntu", "Ubuntu 20.04 LTS" OS, and "30GB" of "balanced persistant disk" storage
    - Click "Create"
- The VM should spin up
    - Copy the external IP to the terminal and SSH into it with the `-i` flag to indicate the private key file
        - Do this via `ssh -i ~/.ssh/gcp [Username]@[external IP]`
            - `ssh -i ~/.ssh/gcp nimz@[external IP]`
        - Click "yes" if prompted to continue connecting
        - Enter the passphrase if used and prompted
        - Should see `Welcome to Ubuntu 20.04.5 LTS (GNU/Linux 5.15.0-1030-gcp x86_64)` to start
        - Can check the machine via `htop`
        - Check that `gcloud` is installed via `gcloud --version`
        - Exit with Ctrl + D
- Configure the SSH connection on your local machine for a better experience by, inside of the `.ssh` directory, create a file called `config` via `touch config`, and open it with `code config` and add the following contents:
    ``` bash 
    Host de-zoomcamp
        HostName [External IP]
        User [Username]
        IdentityFile C:\[rest of path]\.ssh\gcp
    ```
    - Now, in order to connect to the host via SSH ssh, just enter `ssh de-zoomcamp`, rather than use all the additional arguments above
- To configure the VM instance:
    - Download the Anaconda installer via `wget https://repo.anaconda.com/archive/Anaconda3-2023.03-1-Linux-x86_64.sh`
        - Start the install via `bash Anaconda3-2023.03-1-Linux-x86_64.sh`
        - Accept license agreement and press Enter to begin installation
        - Enter "yes" when prompoted about `conda init`
        - When Anaconda is finished, logout and log back in, *or* run `source .bashrc`
            - Can look at `.bashrc` via `less .bashrc`
            - This file is executed every time we log into the machine
        - Should see `(base)` in front of the line in the command prompt
    - Can optionally install the Fish shell (a Unix shell with a focus on interactivity and usability)
        - After running the code below, - Can enter via `exec fish` or just `fish`
        - Can then add `exec fish` to the end of the `.bashrc` file
        - Exit via Ctrl + D
    ```bash
    sudo apt update
    sudo apt-get install fish
    curl https://raw.githubusercontent.com/oh-my-fish/oh-my-fish/master/bin/install | fish
    omf install agnoster
    ```        
    - Install Docker via `sudo apt-get update` then `sudo apt-get install docker.io`
        - Run `sudo groupadd docker` if it doesn't already exist
        - Then run `sudo gpasswd -a $USER docker` (`$USER` adds current user)
        - Then `sudo service docker restart` to restart the Docker daemon
        - Then logout and log back (Ctrl + D) so that we don't have to type `sudo` everytime we use a `docker` command
        - Test with `docker run hello-world`
    - Clone the course repo
        - `git clone https://github.com/newns92/data_engineering_zoomcamp.git`
    - To configure VSCode to access the VM:
        - Install the remote extension for VS Code if needed
        - Connect to the remote host by clicking the little green square in the bottom left corner of VSCode --> "Connect to host" --> select "de-zoomcamp", which should be there due to the config
        - VSCode should be connected to the GCP VM
    - Install docker-compose
        - First, create a directory for storing binary files called `~/bin` via `mkdir bin` and `cd bin/`
        - Enter `wget https://github.com/docker/compose/releases/download/v2.17.3/docker-compose-linux-x86_64 -O docker-compose` (specifying the output to be `docker-compose` via the `-O` arg)
            - **NOTE: check for latest version**
        - Check that `docker-compose` is in `/bin/` via `ls`
        - Enter `chmod +x docker-compose` to make it executable
            - Should be green text now after running `ls`
            - Check the version via `./docker-compose version`
        - To make `docker-compose` visible from any directory, add it to path by adding `export PATH="${HOME}/bin:${PATH}"` to the `.bashrc` file
            - **DO THIS OUTSIDE OF FISH SHELL**
            - `cd` up to the home directory
            - Open `.bashrc` via `nano .bashrc`
            - Go to the bottom and add `export PATH="${HOME}/bin:${PATH}"`
            - Save with Ctrl + O, then Enter
            - Exit via Ctrl + X 
            - Run `source .bashrc`
            - Test with `which docker-compose` and `docker-compose version`
        - Then, navigate to the directory with our Postgres `docker-compose.yml` file from the cloned repo
        - Run `docker-compose up -d`
        - Check that everything is running with `docker ps`
    - Install pgcli
        - `cd` back to the home directory, `~`
        - Run `conda update conda`
        - Enter `conda install -c conda-forge pgcli` then `pip install -U mycli`
            - There is some weird error if you only try one of these
        - Run `pgcli -h localhost -u root -d ny_taxi`, enter password "root"
        - Should see a new command line, test with `\dt` to list the tables (will be empty right now)
        - Exit with Ctrl + D
    - To access the VM Postgres via the local machine
        - Forward the port from VCSode port forwarding for ports `5432` for postgres and `8080` for pgAdmin
            - Open a terminal in the SSH VSCode window connected to the VM
            - Go to the "Ports" tab
            - Click "Forward a Port"
            - Enter "5432" in the "Port" column. Now we will be able to access this port from our local machine
            - In a new Git Bash terminal, *without SSH-ing into the VM*, run `pgcli -h localhost -u root -d ny_taxi`
            - Might see an "only 3 protocol supported" error, but just hit Enter and you should see the `pgcli` command line
            - Test with `\dt`
            - Then add port "8080" in VSCode
            - Then open `localhost:8080/` in a browser window, and you should see pgAdmin like before locally
                - ***GETTING TIMED OUT ERROR HERE 4/26/2023, CHECK LATER***
            - Install jupyter on the VM via `conda install -c conda-forge notebook`
            - Then add port "8888" in VSCode
            - Run `jupyter notebook` in the GCP Git Bash terminal window, copy the URL, and open it locally in a browswer to see everything
            - Download the taxi data to the VM if needed
            - Run the ingestion script via `python load_data.py` 
                - **DON'T ACTUALLY DO THIS YET 4/26/2023**
    - Install Terraform
        - `cd` to the `~/bin/` directory
        - Run `wget https://releases.hashicorp.com/terraform/1.4.6/terraform_1.4.6_linux_amd64.zip`
        - Install `unzip` via `sudo apt-get install unzip`
        - Then run `unzip terraform_1.4.6_linux_amd64.zip`
        - Should see it via `ls`
        - Remove the ZIP via `rm terraform_1.4.6_linux_amd64.zip`
    - Need that credentials JSON file from earlier in order to run Terraform
        - Go to the direcotry with the JSON file in a Git Bash terminal (my local User's Documents folder)
        - Do this with SFTP via:
        ```bash
        sftp de-zoomcamp
        mkdr .gc
        cd .gc
        put <path/to/your/service-account-authkeys>.json
        ```        
        - Check that it's there via `ls`
        - Then, in the VM, run `export GOOGLE_APPLICATION_CREDENTIALS=~/.gc/[file name].json`
        - Then run `gcloud auth activate-service-account --key-file $GOOGLE_APPLICATION_CREDENTIALS` to use this JSON file to authenticate our CLI
        - Then, `cd` to the `/terraform/` directory in the cloned repo
        - Then, run the 4 terraform commands `terraform init`, `terraform plan`, `terraform apply`, `terraform destroy`, if desired
            - Update the `variables.tf` file to automatically use the GCP Project ID if needed
            ```bash
            variable "project" {
            description = "Your GCP Project ID"
            default = "[actual project ID]"
            type = string
            }
            ```
            - **Note**: In week 2, we move and rename this file to `~/.google/credentials/google_credentials.json`
- ***SHUT OFF THE INSTANCE ONCE YOU'RE DONE***
    - Run `sudo shutdown now` if not stopping via the browser
    - Check that it's shutdown in the GCP console
    - When restarting, the external IP may have changed, so update `Host Name` in `.ssh/config`


## Grab Data and Upload to GCP
- Run `get_data.py` in the `zoom_project` Conda environment to collect data from THDB's API and put that into a parquet file and upload to a GCP bucket
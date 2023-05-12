# Docker: 
- https://docs.docker.com/desktop/install/windows-install/
- https://medium.com/@verazabeida/zoomcamp-2023-week-1-f4f94cb360ae
- Check for running containers with `docker ps`
# Docker Compose
- way of running multiple Docker images
# Postgres
- `winpty docker run -it -e POSTGRES_USER="root" -e POSTGRES_PASSWORD="root" -e POSTGRES_DB="ny_taxi" -v C://Users//[rest of path]//ny_taxi_postgres_data:/var/lib/postgresql/data:rw -p 5432:5432 postgres:13`
- Install a client for Postgres: `conda install -c conda-forge pgcli`
- Add to the system path: `C:\ProgramData\Miniconda3\Scripts`
- Test with `pgcli --help`
- Install keyring with `conda install keyring`
- Connect to Postgres IN A SEPARATE COMMAND WINDOW with `pgcli -h localhost -p 5432 -u root -d ny_taxi` where -d = database, -u = user, -p = port, -h = host
- Test by checking for tables with `\dt` and also doing `SELECT 1`
- Exit with CTRL+D
- See `load_data.py` to load in data
- Test with `SELECT COUNT(*) FROM yellow_taxi_data` (1369765) and `SELECT COUNT(*) FROM zones` (265)
- Test again with `SELECT MAX(tpep_pickup_datetime), MIN(tpep_pickup_datetime), max(total_amount) FROM yellow_taxi_data`
    - should get `2021-02-22 16:52:16`, `2008-12-31 23:05:16`, and `7661.28`
# pgAdmin
- It’s not convenient to use `pgcli` for data exploration and querying
- `pgAdmin` - the standard web-based GUI for Postgres data exploration and querying (both local and remote servers)
- Don't need to install it since we have Docker, so we can just pull an image that contains this tool
- Google `pgadmin docker`, select the first link (to the container)
- Click the "instructions on Dockerhub" link
- Will have to use `docker pull dpage/pgadmin4`
- Full command: `docker run -it -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" -e PGADMIN_DEFAULT_PASSWORD="root" -p 8080:80 dpage/pgadmin4`
    - notice we port 8080 on our machine to 80 in the container
- Once you see `Listening at: http://[::]:80 (1)`, open browser and go to `http://localhost:8080/` to see the landing page for pgAdmin
- Sign in with the credentials from the command above
- Create a new server: `Local Docker` by right-clicking on "Servers" and hit "Register" --> "Server"
- Need to specify the host address in the "Connection" tab, which should be `localhost`, port is `5432`, username and password is `root`
- Will see an error of unable to connect to this server because we're running pgAdmin inside of a container, and this is trying to find postgres localhost within this container, though it is in *another* container
# Docker Networks
- In other words, this pgAdmin Docker container cannot access the Postgres container, and we need to **link them** via a **Docker network**
- Shut down both containers
- Create a network with:
    - 1) Create the network itself with `docker network create pg-network`
    - 2) Run Postgres, specifying it should be run in the network, with `winpty docker run -it -e POSTGRES_USER="root" -e POSTGRES_PASSWORD="root" -e POSTGRES_DB="ny_taxi" -v C://Users//nimz//Dropbox//de_zoomcamp//week1//ny_taxi_postgres_data:/var/lib/postgresql/data:rw -p 5432:5432 --name pgdatabase --network=pg-network postgres:13`
        - a) Check that the data has persisted with `SELECT COUNT(*) FROM yellow_taxi_data` (1369765)
    - 3) In a separate command window, run pgAdmin, specifying it should be run in the network, with `docker run -it -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" -e PGADMIN_DEFAULT_PASSWORD="root" -p 8080:80 --name pgadmin --network=pg-network dpage/pgadmin4`
    - *Notice the commands are similar but we added `--name` and `--net` arguments*
- Create the server again in same manner as above, BUT host name/address should be `pgdatabase`, port is `5432`, username and password is `root`
- Should have been able to connect and see "Local Docker" under "Servers" on the left of pgAdmin
- Can see our tables under "Local Docker" --> "Databases (2)" --> "ny_taxi" --> "Schemas (1)" --> "Tables (2)"
- Can view data with `SELECT * FROM public.yellow_taxi_data LIMIT 100`
- Can write the same query by going to "Tools" --> "Query Tool"
- Next, we will put those two `docker run -it` commands into a single YAML file to run both containters with one terminal via `docker compose`
# Docker Compose
- Docker Compose lets us run multiple containers and link them in a network
- Docker compose lets us codify the Docker shell commands into a YAML file so that we don't have to remember the correct sequence to run network commands, + all of the flags and environment variables
- Create the `docker-compose.yml` file
    - Don't need to write the full path for the volumes\
    - Docker provides `restart` policies to control whether your containers start automatically when they exit, or when Docker restarts, and these that linked containers are started in the correct order
    - The containers automatically become part of a network, so we don't have to specify it here
- Check that nothing is running with `docker ps`
- Then run `docker-compose up`
    - will have to create a new instance of the database server in the browser since we didn't do volumes mappings
- Or run in detached mode with `docker-compose up -d` to get control of the terminal back once things are spun up
- Open browser and go to `http://localhost:8080/` to see the landing page for pgAdmin
- Shut it down with `docker-compose down`
- **To make pgAdmin configuration persistent**, create a folder `data_pgadmin`
    - Change its permission potentially (on Linux, `sudo chown 5050:5050 data_pgadmin`)
    - Mount it to the `/var/lib/pgadmin` folder under `volumes` in the `pgadmin1` service in `docker-compose.yml`
# Dockerize Data Load Script
- If you have a Jupyter notebook, convert it to a Python script via `jupyter nbconvert --to=script [notebook name].ipynb`
- Update the `load_data.py` script
- Drop the 2 tables in pgAdmin
- Run `load_data.py` with all args to recreate them
- Create a `.bash_profile` file in `C:\Users\[Username]` and add the line `alias python='winpty /c/ProgramData/Miniconda3/python.exe'` to use the right python version in Git Bash
- Make sure the Docker container for Postgres is running (via `docker run -it` or `docker-compose up`)
- Run the command
- Double-check that the tables were remade
- **Now, to put this into Docker**
- Add `sqlalchemy` and `psycopg2` to the `pip install pandas` line in `Dockerfile` file
- Add `RUN apt-get install wget` to the `Dockerfile` file
- Change all instances of `pipeline.py` to `load_data.py`
- In `docker-compose.yml`, add the `networks` to each service, then add the `network`
- Run `docker build -t taxi_ingest:v001 .`
- Once complete, run the same command as manually running the Python script to ingest data, but via Docker starting with `docker run -it --network=pg-network taxi_ingest:v001`
# SQL Refresher
- Run the network via `docker-compose.yml` via `docker-compose up -d` in Git Bash or command prompt
# GCP 
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
        - Choose "IAM Service Account Credentials API" (which may already be enabled)
# Terraform
- Open source tool for provisioning infrastructure resources
- Supports DevOps best practices for **change management**
- **Infrastructure as Code (IaC)** - check in cloud infrastucture configuration to version control
    - Framework that allows us to build, change, and manage infrastructure in a safe, consistent, and repeatable way by defining resource configurations that you can version, reuse, and share
    - Can manage infrastructure with `config` files alone rather than via a GUI
- Advantages
    - Infrastructure lifecycle management
    - Version control commits
    - Very useful for stack-based deployments, and with cloud providers such as AWS, GCP, Azure, K8S…
    - State-based approach to track resource changes throughout deployments
- Install chocolatey
    - Run `Get-ExecutionPolicy` in Windows Powershell. If it returns `Restricted`, then run `Set-ExecutionPolicy AllSigned` or `Set-ExecutionPolicy Bypass -Scope Process`
    - Run `Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))`
- Install with `choco install terraform`
- Have some required files:
    - `.teraform-version` = defines the version of Terraform
    - `main.tf` = defines the resources needed
    - `variables.tf` = defines runtime arguments that will be passed to Terraform
        - Default values can be defined in which case a run time argument is not required
- Execution steps
    - `terraform init`:
        - Initializes & configures the backend, installs plugins/providers, & checks out an existing configuration from a version control
    - `terraform plan`:
        - Matches/previews local changes against a remote state, and proposes an Execution Plan.
        - Describes the actions Terraform will take to create an infrastructure that will to match with our configuration
        - Does not actually create the resources
    - `terraform apply`:
        - Asks for approval to the proposed plan from the previous command, and applies changes to the cloud
        - Actually creates the resources
    - `terraform destroy`:
        - Removes your stack from the Cloud
- After getting the requires files, run `terraform init` in the `terraform` directory containing said files
- Run `ls -la` in Git Bash to see some new files, like `.terraform`, which is like any package installer like `pip`
- Run `cd .terraform` and run `ls` to see its files
- Go back with `cd ..` and run `terraform plan`
- If we did not enter our GCP project ID into `variables.tf`, enter it here when prompted
    - Or just run `terraform plan -var="project=<your-gcp-project-id>"`
- Run `terraform apply` and enter the GCP project ID again
    - Or just run `terraform apply -var="project=<your-gcp-project-id>"`
- Enter `yes` and should see `Apply complete! Resources: 2 added, 0 changed, 0 destroyed`
- Go to "Cloud Storage" on the left of the project page in the browser, and should see our new data lake
- Go to "Big Query" on the left of the project page in the browser, and should see our new instance in the "Explorer" tab on the left
- Delete this infrastructure after our work as to avoid costs on any running services via `terraform destroy`
    - If we did not enter our GCP project ID into `variables.tf`, enter it here when prompted
    - Should see `Destroy complete! Resources: 2 destroyed.`
    - Afterwards, should see nothing after going to "Cloud Storage" or "BigQuery" on the left-hand side of GCP
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
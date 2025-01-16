# Setting Up the GCP VM Environment


## Generating SSH Keys
- First, before creating a VM instance, we need to generate a **Secure Shell (SSH)** key to log into the VM instance that we will create in the future
- First, create an `.ssh/` directory via `mkdir` in your User's main directory (`C:/Users/<username>`) via the Git Bash terminal if it doesn't already exist
- Then, use the `ssh-keygen` command with a `-C` flag to create a new SSH key pair
    - https://cloud.google.com/compute/docs/connect/create-ssh-keys
    - Do this via `ssh-keygen -t rsa -f ~/.ssh/<name-for-SSH-key-file> -C <username-on-the-VM> -b 2048`
    - Enter a passphrase if desired
    - You should see `<name-for-SSH-key-file>` and `<name-for-SSH-key-file>.pub` key files via the `ls` command in the `.ssh/` directory
- Next, we need to add the *public* key to GCP
    - ***Never*** show the private key
- Navigate to GCP and go to "Compute Engine" on the left-hand side
    - Enable the Compute Engine API if need be/if prompted
- Next, on the left-hand side, navigate to the "Settings" header, and underneath it, click "Metadata"
    - *If you get an error in GCP, click on "VM Instances" under "VIRTUAL MACHINES" on the left-hand side and enable the Compute Engine API *
    - See the "SSH Keys" tab, and navigate to it, then click "Add SSH key"
    - Get the public SSH key in the terminal via `cat <name-for-SSH-key-file>.pub` (or open it in VSCode), copy it to the input box in GCP, and then click "Save" at the bottom of the page
- Now, all VM instances in the project will be able to use this public SSH key


## Generating the VM Instance
- So, we can now create a VM by first navigating to "VM Instances" underneath "VIRTUAL MACHINES" when in the "Compute Engine" section of GCP
    - Click "Create an instance" at the top of the page
    - Select "Machine Configuration" on the left-hand side
        - Name it something, like `de-zoomcamp-2025`
        - Add a relevant time zone (Region and Zone)
        - Make sure "General Purpose" is selected for machine type, and then in the "Series" column, select **E2**
        - Underneath the table, for machine type, select "Standard" from the drop-down and then select the **"e2-standard-4 (4vCPU (2 core) 16 GB memory)"** machine
    - Then, click on "OS and storage" on the left-hand side
        - Click "Change"
        - For OS, choose **"Ubuntu"**, then **"Ubuntu 20.04 LTS"** for the version, then **"balanced persistant disk"** storage, and finally choose a size of **"30GB"**
    - At the bottom of the page, click "Create", and the VM should spin up
- Once the VM has spun up, copy the **external IP** from the VM instance's page on GCP into the terminal and SSH into the VM with the `-i` flag to indicate the private key file
    - We do this via `ssh -i ~/.ssh/<ssh-private-key-file> <ssh-username>@<external IP>`
    - Click "yes" if prompted to continue connecting
    - Enter the passphrase (if you used one and are prompted)
    - Should see `Welcome to Ubuntu 20.04.6 LTS (GNU/Linux 5.15.0-1074-gcp x86_64)` to start off
    - You can check the machine via the `htop` command (see how many cores, GB, etc.)
    - Check that `gcloud` is installed on the VM via `gcloud --version`
    - Exit the VM with `Ctrl + D`
- We can **configure the SSH connection on the local machine for a better experience** by, inside of the `.ssh/` directory, creating a file called `config` (via a `touch config` command in Git Bash, for example)
    - Open this file via a `code config` command in Git Bash and add the following contents:
        ```bash 
        Host de_zoomcamp_2025
            HostName <external-IP>
            User <username>
            IdentityFile C:\<rest-of-path>\.ssh\<private-key-file-name>
        ```
    - Now, in order to connect to the host via SSH, just enter `ssh de_zoomcamp_2025`, rather than use all the additional arguments above


## Configuring the VM Instance
- While SSH-ed into the VM, download the **Anaconda** installer via `wget https://repo.anaconda.com/archive/Anaconda3-2023.03-1-Linux-x86_64.sh`
    - Start the install via `bash Anaconda3-2023.03-1-Linux-x86_64.sh`
    - Press `ENTER`, accept the license agreement, and then press `ENTER` again to begin the installation
    - Enter "yes" when prompted about `conda init`
    - When Anaconda is finished, log out and back into the VM, *or* run `source .bashrc`
        - You can look at the contents of `.bashrc` via `less .bashrc`
            - This file is executed every time we log into the machine
        - You should now see `(base)` in front of the line in the command prompt
    - Can optionally install the **Fish** shell (a Unix shell with a focus on interactivity and usability)
        - After running the code below, you can enter the shell via `exec fish` or just `fish`
            ```bash
            sudo apt update
            sudo apt-get install fish
            curl https://raw.githubusercontent.com/oh-my-fish/oh-my-fish/master/bin/install | fish
            omf install agnoster
            ```            
        - You can then add `exec fish` to the end of the `.bashrc` file
        - You can then exit the shell via `CTRL + D`
- Next, install **Docker** via `sudo apt-get update`, and then `sudo apt-get install docker.io`
    - *NOTE: `apt-get` is used to install or upgrade packages. It is followed by one or more package names the user wishes to install*
    - Next, run `sudo groupadd docker` (if it doesn't already exist)
    - Then run `sudo gpasswd -a $USER docker` (`$USER` adds the current user to Docker)
    - Then run `sudo service docker restart` to restart the Docker daemon
    - Then log out and log back into the VM (`CTRL + D`) so that we don't have to type `sudo` everytime we use a `docker` command
    - Test that the install was successful with `docker run hello-world`
    - Next, clone the course repo from your own GitHub account
        - `git clone <link-to-your-repo>.git`
- ***To configure VSCode to access the VM***:
    - Install the remote extension for VSCode if needed
    - Connect to the remote host by clicking the little green (or blue) square in the bottom left corner of VSCode and select "Connect to host"
    - Select `de_zoomcamp_2025`, which should be there due to the config bash file
    - Select "Linux" as the OS, and then enter the VM's passphrase when prompted
    - Now, VSCode should be connected to the GCP VM
- Next, install **docker-compose**
    - First, create a directory for storing binary files called `~/bin` via `mkdir bin` and `cd bin/` in the VM
    - Enter `wget https://github.com/docker/compose/releases/download/v2.17.3/docker-compose-linux-x86_64 -O docker-compose` (specifying the output to be `docker-compose` via the `-O` arg)
        - **NOTE: check for latest version**
    - Check that `docker-compose` is in `/bin/` via `ls`
    - Enter `chmod +x docker-compose` to make it executable
        - `chmod` is the command and system call used to change the access permissions and the special mode flags, and `+x` means to make a file executable
        - You should see the `docker-compose` displayed in green text now after running `ls`
        - Check the version via `./docker-compose version`
    - To make `docker-compose` visible from *any* directory, add it to path by adding `export PATH="${HOME}/bin:${PATH}"` to the `.bashrc` file
        - In other words, `cd` up to the home directory
        - Open `.bashrc` via `nano .bashrc`
        - Go to the bottom of the file and add `export PATH="${HOME}/bin:${PATH}"`
        - Save with `CTRL + O`, then hit `ENTER`
        - Exit via `CTRL + X`
        - Run the `source .bashrc` command
        - Test with `which docker-compose` and `docker-compose version`
- Then, navigate to the directory with our **Postgres** `docker-compose.yml` file from the cloned repo
    - Run `docker-compose up -d`
    - Check that everything is running on the VM with `docker ps`
        - If there is a `network pg-network declared as external, but could not be found` error, create the network via `docker network create pg-network`, and then run `docker-compose up -d` again
- Install **pgcli**
    - `cd` back to the home directory, `~`
    - Run `conda update conda` to update Anaconda and any packages
    - Once that's done, enter `conda install -c conda-forge pgcli`, and then `pip install -U mycli`
        - NOTE: *There is some weird error if you only try one of these*
    - Run `pgcli -h localhost -u root -d ny_taxi`, enter password: `root`
    - You should see a *new* command line, which you can test with `\dt` to list the tables (the database will be empty right now)
    - Exit `pgcli` via `CTRL + D`
- To **access the VM's Postgres instance via the local machine**:
    - **Forward the port** from VCSode port forwarding for ports `5432` for postgres and `8080` for pgAdmin
        - To do so, open a terminal at the bottom of the SSH-attached VSCode window, which is connected to the VM
        - Go to the "Ports" tab
        - Click "Forward a Port"
        - Enter `5432` in the "Port" column
            - Now we will be able to access this port from our local machine
        - In a *new* Git Bash terminal, *without SSH-ing into the VM*, run `winpty pgcli -h localhost -u root -d ny_taxi`
        - Might see an *"only 3 protocol supported"* error, but just hit `ENTER`, and you should see the `pgcli` command line
        - Test with `\dt`
        - Next, add port `8080` in our SSH-ed VSCode window
        - Then, open `localhost:8080/` in a browser window, and you should see pgAdmin like before when we did this locally
            - ***NOTE: GETTING TIMED OUT ERROR HERE 1/16/2025, CHECK LATER***
- Install `jupyter` on the VM via `conda install -c conda-forge notebook`
    - Then add port `8888` in VSCode
    - Run `jupyter notebook` in the Git Bash terminal window where you are signed into the GCP VM, copy the resulting URL, and then open it *locally* in a browser to see everything
    - Shut down Jupyter via `CTRL + C`
- ***Download the taxi data to the VM if needed***
    - Run the ingestion script via
        ```bash
        URL1="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz"
        URL2="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv"

        python load_data.py \
        --user=root \
        --password=root \
        --host=localhost \
        --port=5432 \
        --database=ny_taxi \
        --yellow_taxi_table_name=yellow_taxi_data \
        --yellow_taxi_url=${URL1} \
        --zones_table_name=zones \
        --zones_url=${URL2}
        ```
        - *NOTE*: Delete the CSV's if they are already there for some reason and causing an "empty data" error
        - *NOTE*: Run `pip install pandas sqlalchemy psycopg2` if needed
            - If getting an error when installing `psycopg`, see here: https://stackoverflow.com/questions/5420789/how-to-install-psycopg2-with-pip-on-python
                - Run `sudo apt install libpq-dev python3-dev`, then `sudo apt install build-essential`, then run `pip install` again
- Install **Terraform**
    - `cd` to the `~/bin/` directory
    - Run `wget https://releases.hashicorp.com/terraform/1.4.6/terraform_1.4.6_linux_amd64.zip`
    - Install `unzip` via `sudo apt-get install unzip`
    - Then run `unzip terraform_1.4.6_linux_amd64.zip`
    - You should see `terraform` displayed in green text via `ls`
    - Remove the ZIP version of Terraform via `rm terraform_1.4.6_linux_amd64.zip`
- We **need a credentials JSON file** from GCP in order to run Terraform
    - Go to "IAM" (Identity and Access Management) on GCP and click "Service Accounts"
        - **Service account** = an account with limited permissions that is assigned to a service (ex: a server or VM)
            - This allows us to create a set of credentials in an account that does not have full access to the owner/admin account
        - Create a service account: "de_zoomcamp_user"
        - Grant access as "Basic" and then "Viewer"
            - We will fine tune the permissions in a later step
        - We do not need to "grant users access to this service account" (Step 3)
            - But this is useful in a production (PROD) environment where it may be useful for multiple users to share the same permissions
        - Once done creating the service account, to create a key, click the three dots under the "Actions" column on the far right, and then click "Manage keys"
        - Click "Add key", then "Create new key", then "JSON"
            - This downloads a *private* key JSON File
            - *Do NOT save it in repository*
            - Move it to `C:/Users/<username>`
    - Go to the directory with the JSON file you just downloaded, while in a Git Bash terminal on your local machine
    - Move it to the VM with **SFTP** via:
        ```bash
        sftp de_zoomcamp_2025
        mkdir .gc
        cd .gc
        put <path/to/your/service-account-authkeys>.json
        ```        
    - Check that the JSON file there via `ls` (or first `cd` into `.gc` in the GCP VM, then do `ls`)
    - Then, in the VM, run `export GOOGLE_APPLICATION_CREDENTIALS=~/.gc/<credentials-file-name>.json`
    - Then run `gcloud auth activate-service-account --key-file $GOOGLE_APPLICATION_CREDENTIALS` to use this JSON file to authenticate our CLI
    - Then, `cd` to the `/terraform_demo/` directory in the cloned repo
    - ***Create the `variables.tf` file in the VM as needed***
        - *NOTE*: Also move over the Terraform credentials JSON file from the local machine
            ```bash
            sftp de_zoomcamp_2025
            mkdir .gc
            cd .gc
            put <path/to/your/terraform-service-account-authkeys>.json
            ```
        - Then edit `variables.tf` to use this JSON location: `~/.gc/<terraform-credentials-file-name>.json`
    - Then, run the 4 terraform commands: `terraform init`, `terraform plan`, `terraform apply`, `terraform destroy`, if desired
        - *Update the `variables.tf` file to automatically use the GCP Project ID if needed*
            ```bash
            variable "project" {
            description = "Your GCP Project ID"
            default = "<actual-project-id>"
            type = string
            }
            ```
        - **Note**: In week 2, we move and rename this file to `~/.google/credentials/google_credentials.json`
- ***SHUT OFF THE INSTANCE ONCE YOU'RE DONE***
    - Run `sudo shutdown now` if not stopping via the browser
    - Check that the VM is actually shutdown in the GCP console
    - ***NOTE:*** *When restartin (`ssh de_zoomcamp_2025`), the external IP may have changed, so update `Host Name` in `.ssh/config`*
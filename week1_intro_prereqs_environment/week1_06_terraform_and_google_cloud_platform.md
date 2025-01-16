# Google Cloud Platform and Terraform


## Intro
- **Google Cloud Platform (GCP)** are managed cloud computing resources offered by Google
- It includes a range of hosted services for **compute, storage, and application**
- It runs on the same hardware that Google uses for its own internal services
- It can be divided into several different categories: Management, Networking, Storage & Databases, Big Data, Identity & Security, and Machine Learning
    - For this course, we will be using **Storage & Databases** and **Big Data**


## Terraform
- **Terraform** (HashiCorp) is an open-source tool used for provisioning **infrastructure** (places where you code can live and your software can run) resources via declarative configuration files (Resources for VM's, containers, networking, storage, etc.)
    - "Infrastructure automation to provision and manage resources in any cloud or data center"
        - https://www.terraform.io/    
    - It comes from HashiCorp (https://developer.hashicorp.com/terraform/intro):
        - "Terraform is an infrastructure as code (IaC) tool that lets you define both cloud and on-prem resources in human-readable configuration files that you can version, reuse, and share. You can then use a consistent workflow to provision and manage all of your infrastructure throughout its lifecycle"
        - "Terraform can manage low-level components like compute, storage, and networking resources, as well as high-level components like DNS entries and Software as a Service (SaaS) features"
- Terraform supports DevOps best practices for **change management**
    - This lets you manage configuration files via source control to maintain an ideal provision state for testing and production environments
- It's also known as **Infrastructure as a Service (IaaS)** or ***Infrastructure as Code (IaC)***
    - **IaC** is a framework that allows us to build, change, and manage infrastructure in a safe, consistent, and repeatable way by defining resource configurations that you can version, reuse, and share
        - *Think of it like git version control, but for infrastructure*
    - You can manage infrastructure via `config` files alone, rather than via a GUI
- **Advantages:**
    - Infrastructure lifecycle management assistance (in a stack-based deployment style)
        - You can deploy an entire cluster of resources/create an entire set of resources together and destroy them at any time
    - Version control commits for configurations
        - This helps to safely collaborate on infrastructure
    - Very useful for **stack-based deployments**, and with cloud providers such as AWS, GCP, Azure, Kubernetes (K8's), etc.
    - **State-based approach** to track resource changes throughout deployments
- *Why use Terraform?*:
    - Simplicity in keeping track of infrastructure by defining it in a readable file
        - You can read the file and see what is going to be made, parameters, what size the discs and types of storage will make up, etc.
    - Easier collaboration
        - Via version control (like on GitHub) for the specific file(s)
    - Reproducibility
        - You can build resources in a development (DEV) environment, test, and then update certain parameters to deploy into a production (PROD) environment
        - Or you can recreate someone else's project
    - Ensure resources are removed
        - Via a quick Terraform command to avoid unnecessary charges for resources being used
- *What Terraform is NOT:*
    - It does not manage and update code on infrastructure
        - i.e., it's not made to update or deploy software
    - It does not give you the ability to change immutable resources
        - Example: You want to change your VM type or GCP Storage location, you can't do it via Terraform
    - It's not used to manage resources that are NOT defined in your Terraform files
        - It's not meant to deploy resources (say, a K8's cluster) that aren't defined in its files
- *How does Terraform work?*
    - You have the Terraform software downloaded to your local machine, which gives you a **provider**
    - A **provider** allows you to communicate with different services that allow you to bring up infrastructure
        - Example: To use the AWS provider, define that in your Terraform file, which will then reach out to wherever it pull from, and Terraform will use that provider to connect with the chosen AWS provider
            - NOTE: You'll need some way of authorizing your access, such as a service account or access token, etc.
- **Providers**
    - Providers are the code that allows Terraform to communicate with managed resources on platforms such as AWS, GCP, Microsoft Azure, K8's, VSphere, Alibaba Cloud, Oracle Cloud Infrastructure, Active Directory, etc.
    - https://registry.terraform.io/browse/providers
- **Key Terraform Commands**:
    - **init**: Once you have defined your provider, run this command to get the code from the provider down to your local machine
    - **plan**: Once you have defined some resources, run this to show you the resources that will be created by your code
    - **apply**: Builds what is in the `.tf` files to create your infrastructure
    - **destroy**: Removes everything in the `.tf` files
- There are 2 things needed as pre-requisites to use Terraform: **the Terraform client** and a **cloud provider account**
    - The Terraform client can be installed via https://developer.hashicorp.com/terraform/install
    - ***For the GCP provider account:*** 
        - Create a Google account and get the GCP free trial if needed
        - Create a new project named `de-zoomcamp-2025` and *note the Project ID*    


## GCP Service Account Setup
- Before coding, you need to set up a way for Terraform on your local machine to be able to tell GCP that we are who we say were are and to have a way to create **resources**
- We will do this via a **service account**, which is an account with limited permissions that is *assigned to a service* (ex: a server or VM) that is not meant to be logged in to and is meant to be used by software to run tasks/programs
    - It allows us to create a set of credentials that does not have full access to the owner/admin account
    - Again, it's like a "regular" user account, but is never meant to be logged into
- In your project on GCP, on the left-hand side of the page, navigate to "IAM & Admin", then to "Service Accounts"
    - **IAM** stands for "Identity and Access Management"
- At the top of the page, click "Create a Service Account"
- Name the service account `terraform-runner`, add a description if needed, then click "CREATE AND CONTINUE"
- Next, we add in the permissions to give it access to specific services
- Since we're making a GCP bucket, we need to, under "By product or service", select **cloud storage** and then the **Storage Admin** role
    - This allows us to create and modify buckets, packets (Terraform), and files
- Then, since we're also making a BigQuery dataset, under "By product or service", select **BigQuery** and then the **BigQuery Admin** role
- ***NOTE:*** In real life, you'd want to *limit* these roles/permissions
    - Right now, they're very broad and give you a lot of access
    - Since we're only using Terraform to create and take down resources, we'd only need permissions to create and destroy storage buckets, for example, or to create and destroy BigQuery datasets
    - So, in production (PROD) environments, we'd actually create *custom* roles to limit user access to a particular bucket/certain resources
        - And we'd create *separate* service accounts for Terraform, for the data pipeline, etc.
- We can then create the service account by clicking "Continue" and then "Done"
- To add another permission/role to this service account, navigate to the "IAM" section under "IAM & Admin", and click the **edit principal** pencil on the right-hand side of the service account we just created
    - Then, click "Add Another Role"
    - Then, for the **Compute Engine** service, select the **Compute Admin** role
- Now, we need to set up permissions to let us actually *use* this service account:
    - Navigate to the "Service Accounts" section under "IAM & Admin", click the 3 dots to the right of the service account, and then select "Manage Keys"
    - Select "ADD KEY", then "Create a new key", and make sure the key type is JSON
        - This downloads a *private* key within a JSON file full of credentials
        - ***Do NOT save it in a repository***
        - Save to `C:\Users\<username>`


## Terraform Variables
- You can create Terraform variables in a `variables.tf` file in the same directory as your `main.tf` and save the values for them in said file like we have been doing in the examples above
- Documentation: https://developer.hashicorp.com/terraform/language/values/variables
- `variables.tf` contains default values can be defined in which case a run time argument is not required


## Terraform Basics Demo Part 1
- Create a directory `terraform_demo`, and add a subdirectory `keys/`, and ***be sure to not upload this subdirectory to a repository***
- Copy the JSON key file into this `terraform_demo/keys/` directory
- Create a `main.tf` file, which will define the resources needed
- Navigate to the GCP Provider page in the Terraform docs: https://registry.terraform.io/providers/hashicorp/google/latest/docs
- In the top right, click "Use Provider", and copy the provided code
- Paste this code into your `main.tf` file:
    ```YML
    terraform {
        required_providers {
            google = {
            source = "hashicorp/google"
            version = "6.16.0"
            }
        }
    }

    provider "google" {
        # Configuration options
    }
    ```
- Then, edit the "Configuration options" section to have your GCP project ID and region:
    ```YML
    project = "<Your Project ID>"
    region  = "us-central1"
    ```
- You can store the values for such configurations in a `variables.tf` file so that you can upload `main.tf` to a repository without exposing your GCP Project ID:
    ```YML
    ## Variables are generally passed at runtime
    ## Those with 'default' values are optional at runtime, those without 'default' values are mandatory runtime args
    variable "project" {
        description = "Your GCP Project ID"
        default = "<Your Project ID>"
        type = string  
    }

    variable "region" {
        description = "Region for GCP resources. Choose as per your location: https://cloud.google.com/about/locations"
        default = "us-central1"
        type = string
    }
    ```
- You can then access them as so:
    ```YML
    provider "google" {
        ## Terraform relies on plug-ins called "providers" to interact with cloud providers, SaaS providers, and other API's
        project = var.project
        region = var.region # all processes are pointing towards the same region
        # credentials = file(var.credentials)  # Use this if you do not want to set env-var GOOGLE_APPLICATION_CREDENTIALS
    }
    ```
- Now, we need some way for Terraform to know to *use* this credential we just created
- You can hard-code it in `variables.tf` and use it as above: `credentials = file(var.credentials)`
- *Or* you can set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to point to your downloaded GCP key(s)
    - Install the Google Cloud CLI (https://cloud.google.com/sdk/docs/install-sdk) and ***do NOT uncheck "bundled Python"
        - **If you uncheck bundled Python**:
            - In Google Cloud SDK Shell, check `python -c "import os, sys; print(os.path.dirname(sys.executable))"` to see where Python is installed
            - Check the environment variable in Git Bash via `printenv CLOUDSDK_PYTHON`
            - Use a version of Python (such as Miniconda) that you have installed in a special location via `export CLOUDSDK_PYTHON=C:\ProgramData\Miniconda3\python.exe`
            - Can also attempt to set it up via Environment Variables for User and System
            - Then, re-run the SDK installer
            - You can then test in Git Bash via `gcloud -h`
    - Next, ***in a Linux CLI or Git Bash*** run `export GOOGLE_APPLICATION_CREDENTIALS="<path/to/your/service-account-authkeys>.json"`
        - This is how we authenticate our other resources (OAuth)
    - Then test via `echo $GOOGLE_APPLICATION_CREDENTIALS`
- Next, before creating a resource, we must run `terraform init` in the `terraform_demo/` directory in Git Bash to get the provider (the piece of code that Terraform is going to use to talk to GCP)
    - The `init` command initializes and configures the backend, installs plugins/providers, and checks out an existing configuration from a version control
- You should see a "Terraform has been successfully initialized!" message/output and a new `.terraform` directory in your current directory (`terraform_demo/`)


## Create a GCP Bucket
- Navigate to the Terraform docs for GCP Cloud Storage buckets: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket
- Then, copy the provided code and add to your `main.tf` file:
    ```YML
    resource "google_storage_bucket" "data-lake-bucket" {
        # name          = "<Your Unique Bucket Name>"
        # location      = "US"
        name          = "${local.data_lake_bucket}_${var.project}" # Concatenate DL bucket & Project name for unique naming
        location      = var.region  

        ## Optional, but recommended settings:
        # storage_class = "STANDARD"
        storage_class = var.storage_class
        uniform_bucket_level_access = true

        versioning {
            enabled     = true
        }

        lifecycle_rule {
            action {
                type = "Delete"
            }
            condition {
                age = 30  // days
            }
        }

        force_destroy = true
    }
    ```
- Save `main.tf`, and next, in Git Bash, run `terraform plan`
    - This command matches/previews local changes against a remote state, and proposes an **Execution Plan**
    - It describes the actions Terraform will take to create an infrastructure that will to match with our configuration
    - *It does not actually create the resources*
- You should see a successful Terraform plan in the output
- Next, to deploy the plan, in Git Bash, run `terraform apply`
    - This asks for approval to the proposed plan from the previous `terraform plan` command, and applies changes to the cloud
    - It actually *creates* the resources
- Enter `yes` if you're ready to run and implement the plan, and you should see a success message in the output:
    ```bash
    google_storage_bucket.data-lake-bucket: Creating...
    google_storage_bucket.data-lake-bucket: Creation complete after 0s
    ```
    - Notice that when we run this command, we get a **state file** called `terraform.tfstate` in the current working directory
        - `terraform.tfstate` will contain all Terraform state information
- Then, go back to the GCP dashboard for your project
- On the left-hand side of the page, navigate to "Cloud Storage" and then "Buckets", and then select the correct GCP project
- You should see this newly-created bucket in the GCP Cloud Storage Buckets UI
- To get rid of this bucket, run `terraform destroy` and then enter `yes`
    - This takes down/destroys resources, and will remove our current Terraform stack from the cloud
- You should no longer see that bucket in the GCP Cloud Storage Buckets UI


## Create a BigQuery Dataset
- Navigate to the Terraform docs for GCP BigQuery datasets: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/bigquery_dataset
- The documentation gives quite a complicated "basic" example
- The only *real* "required" fields are `dataset_id`, `project`, and `location`
- Input the following code to your `main.tf` file:
    ```YML
    ## Create a RESOURCE: a BigQuery Data Warehouse
    ## Ref: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/bigquery_dataset
    resource "google_bigquery_dataset" "dataset" {
        dataset_id = var.BQ_DATASET
        project    = var.project
        location   = var.region
    }
    ```
- Save `main.tf`, and next, in Git Bash, run `terraform plan`
- Again, you should see a successful Terraform plan in the output
- Next, to deploy the plan, in Git Bash, run `terraform apply` and then enter `yes`
- Navigate to BigQuery Studio in GCP and you should see the dataset under the project ID
- To get rid of the bucket and the dataset, run `terraform destroy` and then enter `yes`


## GCP Extra Info
- Above, we set up 2 resources in the Google environment (a GCP Cloud Storage **data lake** and GCP BigQuery **data warehouse**)
    - Cloud storage is a bucket in our GCP environment where we can store data in flat files
        - This data lake is where we will store data in a more organized fashion
    - In our BigQuery data warehouse, our data will be in a more structured format (Fact and Dimension tables)
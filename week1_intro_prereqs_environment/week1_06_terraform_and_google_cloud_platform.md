# Google Cloud Platform

## Intro
- **Google Cloud Platform (GCP)** are managed cloud computing resources offered by Google
- It includes a range of hosted services for **compute, storage, and application**
- It runs on the same hardware that Google uses for its own internal services
- It can be divided into categories: Management, Networking, Storage & Databases, Big Data, Identity & Security, and Machine Learning
    - For this course, we will be using Storage & Databases and Big Data

## Terraform
- **Terraform** (HashiCorp) is an open-source tool used for provisioning **infrastructure** (places where you code can live and your software can run) resources via declarative configuration files (Resources for VM's, containers, networking, storage, etc.)
    - From HashiCorp (https://developer.hashicorp.com/terraform/intro):
        - "Terraform is an infrastructure as code (Iac) tool that lets you define both cloud and on-prem resources in human-readable configuration files that you can version, reuse, and share. You can then use a consistent workflow to provision and manage all of your infrastructure throughout its lifecycle"
        - "Terraform can manage low-level components like compute, storage, and networking resources, as well as high-level components like DNS entries and SaaS features"
    - "Infrastructure automation to provision and manage resources in any cloud or data center"
        - https://www.terraform.io/
- Terraform supports DevOps best practices for **change management**
    - This lets you manage configuration files via source control to maintain an ideal provision state for testing and production environments
- It's also known as **Infrastructure as a Service (IaaS)** or ***Infrastructure as Code (IaC)***
    - IaC is a framework that allows us to build, change, and manage infrastructure in a safe, consistent, and repeatable way by defining resource configurations that you can version, reuse, and share
        - Think of it like git version control, but for infrastructure
    - You can manage infrastructure via `config` files alone rather than via a GUI
- **Advantages:**
    - Infrastructure lifecycle management assistance (in a stack-based deployment style)
        - You can deploy an entire cluster of resources/create an entire set of resources together abd destroy them at any time
    - Version control commits for configurations
        - This helps to safely collaborate on infrastructure
    - Very useful for **stack-based deployments**, and with cloud providers such as AWS, GCP, Azure, Kubernetes (K8's), etc.
    - **State-based approach** to track resource changes throughout deployments
- *Why use Terraform?*:
    - Simplicity in keeping track of infrastructure by defining it in a readable file
    - Easier collaboration
        - Via version control for the specific file(s)
    - Reproducibility
        - Can build resources in a development environment, test, and then update certain parameteres to deploy into production
        - Or recreate someone else's project
    - Ensure resources are removed
        - Via a quick command to avoid unnecessary charges
- *What Terraform is not:*
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
    - These are the code that allows Terraform to communicate with managed resources on platforms such as AWS, GCP, Microsoft Azure, K8's, VSphere, Alibaba Cloud, Oracle Cloud Infrastructure, Active Directory, etc.
    - https://registry.terraform.io/browse/providers
- There are 2 things needed as pre-requisites: **Terraform client** and a **cloud provider account**
    - The Terraform client can be installed via https://developer.hashicorp.com/terraform/install
    - ***For the GCP provider account:*** 
        - Create a Google account and get the GCP free trial if needed
        - Create a new project named `de-zoomcamp-2024` and note the Project ID





- Install **chocolatey**
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
        - i.e., gets us the providers we need once we defined it (brings it down to the local machine)
    - `terraform plan`:
        - Matches/previews local changes against a remote state, and proposes an Execution Plan.
        - Describes the actions Terraform will take to create an infrastructure that will to match with our configuration
        - Does not actually create the resources
        - i.e., "What am I about to do?" = shows you the resources that are about to be created
    - `terraform apply`:
        - Asks for approval to the proposed plan from the previous command, and applies changes to the cloud
        - Actually creates the resources
        - i.e., "Do what is in the Terraform (`.tf`) files/build that defined infrastructure"
    - `terraform destroy`:
        - Removes your stack from the Cloud
        - i.e., "Remove everything defined in the Terraform (`.tf`) files"
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


## GCP Service Account Setup
- Before coding, you need to set up a way for Terraform on your local machine to be able to tell GCP we are who we say were are and to have a way to create **resources**
- We will do this via a **service account**, which is an account with limited permissions that is *assigned to a service* (ex: a server or VM)
        - It allows us to create a set of credentials that does not have full access to the owner/admin account
        - It's like a "regular" user account, but is never meant to be logged into
- In your project on GCP, on the left-hand side of the page, navigate to "IAM & Admin", then to "Service Accounts"
    - **IAM** stands for Identity and Access Management
- At the top of the page, click "Create a Service Account"
- Name the service account `terraform-runner`, add a description if needed, then click "CREATE AND CONTINUE"
- Next, we add in the permissions to give it access to specific services
- Since we're making a GCP bucket, we need to, under "By product or service", select **cloud storage** and then the **Storage Admin** role
    - This allows us to create and modify buckets, packets (Terraform), and files
- Then, since we're also making a BigQuery dataset, under "By product or service", select **BigQuery storage** and then the **BigQuery Admin** role
- ***NOTE:*** In real life, you'd want to *limit* these roles/permissions
    - Right now, they're very broad and give you a lot of access
    - Since we're only using Terraform to create and take down resources, we'd only need permissions to create and destroy storage buckets, for example, or to create and destroy BigQuery datasets
    - So, in production environments, we'd actually create *custom* roles to limit user access to a particular bucket/certain resources
        - And we'd create separate service accounts for Terraform, for the data pipeline, etc.
- We can then create the service account by clicking "Continue" and then "Done"
- To add another permission/role to this service account, navigate to the "IAM" section under IAM & Admin, and click the **edit principal** pencil on the right-hand side of the service account we just created
    - Then, click "Add Another Role"
    - Then, for the **Compute Engine** service, select the **Compute Admin** role
- Now we need to set up permissions to let us actually *use* this service account
- Navigate to the "Service Accounts" section under IAM & Admin, click the 3 dots to the right of the service account, and then select "Manage Keys"
- Select "ADD KEY", then "Create a new key", and make sure the key type is JSON
    - This downloads a *private* key JSON file full of credentials
    - ***Do NOT save it in a repository***


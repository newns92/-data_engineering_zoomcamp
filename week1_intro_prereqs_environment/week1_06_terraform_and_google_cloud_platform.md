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
- 

- There are 2 things needed as pre-requisites: **Terraform client** and a **cloud provider account**
    - The Terraform client can be installed via https://developer.hashicorp.com/terraform/install
    - ***For the GCP provider account:*** 
        - Create a Google account and get the GCP free trial if needed
        - Create a new project named `de-zoomcamp-2024` and note the Project ID
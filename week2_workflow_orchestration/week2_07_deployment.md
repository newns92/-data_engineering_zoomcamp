# Deployment
- In this section, we'll cover *deploying Mage* using **Terraform** and **Google Cloud**
- This is helpful if you're interested in creating a fully deployed project
    - If you're using Mage in your final project, you'll need to deploy it to the cloud

## Mage Deployment Prerequisites
- This section *may* be a bit technically complex, and may be more of a **DevOps** operation
    - But data engineers (say on a small team) may be responsible for deployment of your systems/services
    - Regardless, it's important to be aware of and hopefully understand the tech used in system/service deployments
- The actual prerequisites:
    1) **Terraform** installed on the local machine
        - https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli
        - https://docs.mage.ai/production/deploying-to-cloud/using-terraform
        - Reminder, Terraform is an **infrastructure** management solution (**Infrastructure as code (IaC)**) that lets us create a bunch of resources in one fell swoop
            - We are going to **create an app** using Google **Cloud Run** (via `gcloud run deploy`), spin up a **backend database** in Google, and create **persistent storage** in Google Cloud
                - Provisioning all these things separately would take a long time and *wouldn't be version controlled (i.e., stored as code) anywhere*
    2) The **gcloud CLI**, a programmatic way of interfacing with Google Cloud that hooks into Terraform and allows us to authenticate and run commands
        - https://cloud.google.com/sdk/docs/install
        - https://docs.mage.ai/production/deploying-to-cloud/gcp/setup
    3) Specific Google Cloud permissions configured to allow our service account to create the resources needed for our Mage product
    4) Mage Terraform templates that we will pull down and run `terraform apply` on, rather than write a bunch of Terraform code from scratch
        - https://github.com/mage-ai/mage-ai-terraform-templates

## Google Cloud Permissions
- So, first, *after installing Terraform and the gcloud CLI*, we will make sure we have all the Google Cloud permissions we need to run a Mage project
- The specific permissions/roles we'll need are:
    - Artifact Registry Read
    - Artifact Registry Writer
    - Cloud Run Developer
    - Cloud SQL (Admin)
    - Service Account Token Creator
- In the GCP console for your project, navigate to the "IAM" page and look for the service account for the user that you are interacting with Mage via
- Right now, this service account should have a role of "Owner", which is a bit of overkill, not a best practice, and not something you would typically see in a production environment
- To be more granular, start by clicking the "edit principal" pen icon on the far right of the service account row, then add those 5 permissions mentioned above, and save the settings


## Deploying to Google Cloud
- Now we're going to confirm that Terraform and Google Cloud are both working the way we expect and then spin up a Mage server using one of Mage's Terraform templates
- To test that gcloud CLI is working:
    - In a terminal window, run `gcloud auth list` to display the authorized/active accounts and their emails
    - You can then list the buckets in you Google Cloud instance via `gcloud storage ls`
        - To update the authorized accounts, set the credentials environment variable to point to a new set of downloaded GCP keys via `export GOOGLE_APPLICATION_CREDENTIALS="<path/to/your>/service-account-authkeys.json"`
        - Refresh the token/session, and verify authentication via `gcloud auth application-default login`
        - A browser window will open up, then choose the right email and then click "Allow" to see the "You are now authenticated with the gcloud CLI!" webpage
        - Then run `gcloud storage ls` again to make sure you can see your bucket
            - If you need to change projects, run `gcloud config set project <project-id>`
                - https://stackoverflow.com/questions/42445424/google-cloud-storage-switch-projects
- Next, we need to pull down Mage's Terraform templates
    - Do this by running `git clone https://github.com/mage-ai/mage-ai-terraform-templates.git`
    - You can `cd` into that directory and run `ls` or `ls -la` to see Terraform templates for different cloud deployments (AWS, Azure, Digital Ocean, GCP)
    - Since we're using GCP, run `cd gcp` to see the specific Terraform template files that we need (`main.tf`, `variables.tf`, `db.tf`, etc.)
- We've already defined the permissions that we need for next steps via Google Cloud, but note that ***some GCP API's may need to be enabled***
- So, we can open up this `mage-ai-terraform-templates/gcp/` folder/directory in a code editor like VSCode
    - Then, we must edit `variables.tf` to configure this Terraform build
        - Edit the `project_id` variable (and optionally the `zone` and `region` variables)
    - Then, run `terraform init` while in this directory
    - Then, run `terraform plan` and enter the Postgres database password found in `variables.tf` if you added one
    - Then, run `terraform apply` and enter `yes` when prompted to create the resources
        - NOTE: This may take over 10 minutes
- Once the resources are deployed, in the GCP console, on the left-hand side, navigate to "Cloud run"
    - Here, you should see the resource that we just created with it's specific name (By default, `mage-data-prep`)
    - Click into it to see a bunch of different details about the resource    
    - In the UI for the resource, go to the "Networking" tab
        - Here, notice that we by default have an internal traffic control limitation/restriction (Ingress Control)
        - So, we *could* whitelist our our IP to be able to access the services
        - But for now, just allow "All" to have direct access to the service and click "Save"
- Now, we can click on the URL for Mage at the top of the `mage-data-prep` resource page in the console to open up an instance of Mage with a project name of `default_repo`
- We can develop whatever we want here and it will persist to Google Cloud because we set up a filestore instance that is storing the file system for this specific project via Terraform
    - i.e., everything will still be there even if you stop and then start your project
- Again, whatever we develop will persist in the cloud
    - So, if we schedule jobs, so long as the Mage instance is running, the jobs will be executed
- Now, some may ask "We just created all of these resources, where are they?" or "How do I develop this locally?"
    - The way to do this is via version control/**git sync** functionality
        - There are a number of ways to enable version control, collaboration, and easy deployment using Git in Mage
            - https://docs.mage.ai/getting-started/setting-up-git
    - Arguably the best way to develop and then deploy a repo to the cloud is via some form of git sync functionality, which Mage has a number of
        - Go to "Settings" in the top right-hand corner of the Mage UI
        - See "Git settings" on the left-hand side
        - To enable Git Sync, first you must configure Git *in* Mage via SSH or HTTPS/access token: https://docs.mage.ai/development/git/configure
        - Then, navigate back to the Settings page and tick the `Git Sync` box
    - Once this is set up, we can develop locally, push to a GitHub repo that is linked to our hosted Mage instance
- Afterwards, run `terraform destroy` and enter `yes` when prompted to destroy the resources and avoid incurring a large Google Cloud bill
    - NOTE: This may take over 10 minutes
    - **NOTE: May have to run it multiple times for some reason**
- So, we have now stood up and then tore down Mage using Terraform and GCP in order to learn how to host Mage outside of a local machine (which is the hallmark of a deployable, production-grade service)
- For next steps, once you have Mage hosted, you can think about:
    - How do you sync to a GitHub repo?
    - How do you integrate CI/CD processes?
    - How do you manage, maintain, and potentially scale a cloud deployment?
    - And more
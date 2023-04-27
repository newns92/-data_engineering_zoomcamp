## Week 1 Homework

In this homework we'll prepare the environment by creating resources in GCP with Terraform.

In your VM on GCP install Terraform. Copy the files from the course repo
[here](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/week_1_basics_n_setup/1_terraform_gcp/terraform) to your VM.

Modify the files as necessary to create a GCP Bucket and Big Query Dataset.

- i.e.
    - ***Start the VM***
    - ***Log in via Git Bash with `ssh de-zoomcamp***
    - ***`cd` into the dir with the Terraform files for week 1***
    - ***Do `cat variables.tf` to check that the following is there:***
    ```bash
    # Variables are generally passed at runtime
    # Those with 'default' values are optional at runtime, those without 'default' values are mandatory runtime args
    variable "project" {
    description = "Your GCP Project ID"
    default = "[actual GCP Project ID]"
    type = string
    }
    ```
    - ***In the same directory, refresh `service-account`'s auth-token for this session via `gcloud auth application-default login`***
    - ***Follow the commands from the command line and the browser window from the provided link***
    - ***Run `terraform init` to initialize the state file (`.tfstate`)***
    - ***Check changes to new infra plan via `terraform plan`***
    - ***Create new infrastructure via `terraform apply`***
        - ***This will create the BigQuert dataset and the GCP Storage bucket***
        - ***Should see `Apply complete! Resources: 2 added, 0 changed, 0 destroyed.`***
    - ***Destroy the infrastructure via `terraform destroy`***
        - ***Should see `Destroy complete! Resources: 2 destroyed.`***
    - ***Shut down the VM via `sudo shutdown now`***

## Question 1. Creating Resources

After updating the main.tf and variable.tf files run:

```
terraform apply
```

Paste the output of this command into the homework submission form.


## Submitting the solutions

* Form for submitting: [form](https://forms.gle/S57Xs3HL9nB3YTzj9)
* You can submit your homework multiple times. In this case, only the last submission will be used. 

Deadline: 30 January (Monday), 22:00 CET


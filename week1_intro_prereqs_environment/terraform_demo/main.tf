# https://registry.terraform.io/providers/hashicorp/google/latest/docs
terraform {
    required_providers {
        google = {
            source = "hashicorp/google"
            version = "6.16.0"
        }
    }
}

## Terraform relies on plug-ins called "providers" to interact with cloud providers, SaaS providers, and other API's
provider "google" {
    ## Configuration options (from the variables.tf file)
    project = var.project
    region = var.region
    credentials = file(var.credentials)  # Use this line if you do NOT want to set env-var GOOGLE_APPLICATION_CREDENTIALS
}

## Create a RESOURCE: a GCP Data Lake Bucket
## Ref: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket
## var.[xxxxxxx] are coming from the variables.tf file
resource "google_storage_bucket" "data-lake-bucket" {
    # name          = "<Your Unique Bucket Name>"
    # location      = "US"
    name = "${local.data_lake_bucket}_${var.project}" # Concatenate DL bucket & Project ID for unique naming
    location = var.region  

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
            age = 30  # in days
        }
    }

    force_destroy = true
}

## Create a RESOURCE: a BigQuery Data Warehouse
## Ref: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/bigquery_dataset
resource "google_bigquery_dataset" "dataset" {
    dataset_id = var.bq_dataset
    project = var.project
    location = var.region
}
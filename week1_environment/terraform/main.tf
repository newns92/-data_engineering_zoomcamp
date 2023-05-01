terraform {
  required_version = ">= 1.0"
  # we are storing things locally in a tf-state file
  # For production, can change from "local" to "gcs" (for google) or "s3" (for aws), if you would like to preserve your tf-state online
  backend "local" {}  
  # below is optional since we are declaring a provider "google" just under this whole statement
  # think of this like importing a library in Python
  required_providers {
    google = {
      source  = "hashicorp/google"
    }
  }
}

provider "google" {
  # Terraform relies on plug-ins called "providers" to interact with cloud providers, SaaS providers, and other API's
  #
  project = var.project
  region = var.region # all processes are pointing towards the same region
  // credentials = file(var.credentials)  # Use this if you do not want to set env-var GOOGLE_APPLICATION_CREDENTIALS
}

# Data Lake Bucket
# Ref: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket
# var.[xxxxxxx] are coming from the variables.tf file
resource "google_storage_bucket" "data-lake-bucket" {
  name          = "${local.data_lake_bucket}_${var.project}" # Concatenating DL bucket & Project name for unique naming
  location      = var.region

  # Optional, but recommended settings:
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

# DWH
# Ref: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/bigquery_dataset
resource "google_bigquery_dataset" "dataset" {
  dataset_id = var.BQ_DATASET
  project    = var.project
  location   = var.region
}

provider "google" {
  # Terraform relies on plug-ins called "providers" to interact with cloud providers, SaaS providers, and other API's
  #

  // Use variables from variables.tf file
  project = var.project
  region = var.region # all processes are pointing towards the same region
  // credentials = file(var.credentials)  # Use this if you do not want to set env-var GOOGLE_APPLICATION_CREDENTIALS
}

resource "google_storage_bucket" "data-lake-bucket" {
  // name          = "<Your Unique Bucket Name>"
  // location      = "US"
  name          = "${local.data_lake_bucket}_${var.project}" # Concatenating DL bucket & Project name for unique naming
  location      = var.region  

  # Optional, but recommended settings:
  // storage_class = "STANDARD"
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
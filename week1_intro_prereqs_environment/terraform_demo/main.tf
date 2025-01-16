terraform {
    required_providers {
        google = {
            source = "hashicorp/google"
            version = "6.16.0"
        }
    }
}

# Terraform relies on plug-ins called "providers" to interact with cloud providers, SaaS providers, and other API's
provider "google" {
    # Configuration options (from the variables.tf file)
    project = var.project
    region = var.region
    credentials = file(var.credentials)  # Use this line if you do NOT want to set env-var GOOGLE_APPLICATION_CREDENTIALS
}


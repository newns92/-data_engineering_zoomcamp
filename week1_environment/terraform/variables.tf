# A local value assigns a name to an expression
# So, you can use the name multiple times within a module instead of repeating the expression.
# Compare Terraform modules to function definitions --> Local values are like a function's temporary local variables
# https://developer.hashicorp.com/terraform/language/values/locals
# Any time we refer to 'data_lake_bucket', then it will always refer to 'dtc_data_lake'
locals {
  data_lake_bucket = "dtc_data_lake"
}

# Variables are generally passed at runtime
# Those with 'default' values are optional at runtime, those without 'default' values are mandatory runtime args
variable "project" {
  description = "Your GCP Project ID"
}

variable "region" {
  description = "Region for GCP resources. Choose as per your location: https://cloud.google.com/about/locations"
  default = "northamerica-northeast2"
  type = string
}

variable "storage_class" {
  description = "Storage class type for your bucket. Check official docs for more info."
  default = "STANDARD"
}

variable "BQ_DATASET" {
  description = "BigQuery Dataset that raw data (from GCS) will be written to"
  type = string
  default = "trips_data_all"
}

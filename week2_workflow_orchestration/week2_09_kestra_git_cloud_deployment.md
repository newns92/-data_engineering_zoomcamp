# Deploy Workflows to the Cloud with Git in Kestra


## Intro
- Here, we will deploy Kestra to the cloud using GCP
- We will then use the Git Sync plugin in order to allow us to synchronize things together


## Install Kestra on GCP
- See: https://www.youtube.com/watch?v=qwA7-hm7d2o
- This guide instructs you on how to setup storage using GCS, use Google Compute to run Kestra itself, and setup a Postgres database to store all the data related to Kestra
- By the end, you will have an instance of Kestra running in Production


## Moving from Dev to Prod
- See: https://www.youtube.com/watch?v=iM4mjIEsxMY
- Dev here refers to the local environment that we have been using for all of the prior Kestra examples
- Prod here refers to the cloud Kestra environment
- Then, we can use GitHub **actions** to synchronize the data between them as well as using a git repo that contains data that's been pushed from the local environment and sync it to the cloud on a schedule or via a webhook (event-based)
    - See: https://www.youtube.com/watch?v=4MqtD9VtGVs


## Kestra Git Plugins
- See: https://www.youtube.com/watch?v=OPlNKQZFeho&list=PLEK3H8YwZn1p7tyd9RV5-WDxh_ZGpMpA3
- The Kestra git plugin consists of two tasks: synch tasks and push tasks
- In the local environment, you use push tasks to push flows and namespace files to a git repo directly from Kestra
- Then, we can use a sync flows task inside of the Prod instance in order to sync flows from the git repo to Kestra on the cloud
- Once we've done that, we can then automatically move flows from Dev to Prod using GitHub

# Base image to run from/use -- base it on Python 3.9
FROM python:3.9

# Specify the working directory of where in the image we work with the file below
WORKDIR /app

# Copy the pipeline file from current working directory to the Docker image
# COPY get_data_postgres.py get_data_postgres.py
# COPY config.py config.py

# Copy requirements file for packages to install
COPY get_data_postgres.py .
COPY config.py .
COPY requirements.txt .

# Command(s) to run (Install wget and Python packages into the Docker image)
# RUN apt-get install wget
# RUN pip install pandas sqlalchemy psycopg2 requests

# Command to install specified packages from a requirements text file via pypi
RUN pip install -r requirements.txt --trusted-host pypi.python.org --no-cache-dir

# Override the entry point
# 'bash' allows us to navigate the container via a bash CLI
# ENTRYPOINT [ 'bash' ]
# This runs the provided Python file via Python
ENTRYPOINT [ "python", "get_data_postgres.py" ]
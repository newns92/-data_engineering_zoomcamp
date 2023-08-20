# Base image to run from/use -- base it on Python 3.9
FROM python:3.9

# Copy requirements file for packages to install
COPY requirements.txt .

# Command(s) to run (Install wget and Python packages in Docker image)
# RUN apt-get install wget
# RUN pip install pandas sqlalchemy psycopg2 requests
RUN pip install -r requirements.txt --trusted-host pypi.python.org --no-cache-dir

# Specify the working directory of where in the image we work with the file below
WORKDIR /app

# Copy the pipeline file from current working directory to the Docker image
# COPY get_data_postgres.py get_data_postgres.py
# COPY config.py config.py
COPY get_data_postgres.py .
COPY config.py .

# Override the entry point
# 'bash' allows us to navigate the container via a bash CLI
# ENTRYPOINT [ 'bash' ]
# This runs the provided Python file via Python
ENTRYPOINT [ "python", "get_data_postgres.py" ]
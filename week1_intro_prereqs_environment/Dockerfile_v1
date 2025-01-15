## Base image to run from/use
FROM python:3.9

## Command to run
RUN pip install pandas

## Specify the working directory of where in the Image we work with the file below
WORKDIR /app

## Copy pipeline.py file from host's current working directory
##   into the Docker image and keep the same file name
COPY pipeline.py pipeline.py

## Override the entry point
# ENTRYPOINT [ "bash" ]

## Run the python file via the Python entrypoint
ENTRYPOINT ["python", "pipeline.py"]